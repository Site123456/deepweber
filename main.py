import asyncio
import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
from datetime import datetime

import aiohttp
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# CONFIG
MAX_DOMAINS_DEFAULT = 500
MAX_DEPTH = 5
TIMEOUT = 10
THREADS = 16
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)
DOMAINS_FILE = "domains.json"
LOG_FILE = "log.json"

DOMAIN_BLACKLIST = {
    "facebook.com",
    "instagram.com",
    "tiktok.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "pinterest.com",
    "snapchat.com",
    "discord.com",
    "reddit.com",
    "whatsapp.com",
    "wechat.com",
    "qq.com",
    "vk.com",
    "ok.ru",
    "telegram.org",
    "youtube.com",
}


# LOGGING
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)
logger = logging.getLogger("domain_crawler")


# JSON HELPERS
def load_json_array(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [x for x in data if isinstance(x, dict)]
            return []
    except Exception:
        return []


def save_json_array(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_domains():
    data = load_json_array(DOMAINS_FILE)
    return [x for x in data if "domain" in x]


def append_domain_safe(domain: str, server: str | None):
    data = load_domains()
    if any(entry["domain"] == domain for entry in data):
        return
    data.append(
        {
            "id": len(data) + 1,
            "domain": domain,
            "server": server,
        }
    )
    save_json_array(DOMAINS_FILE, data)


# DOMAIN / URL UTILITIES
def normalize_domain(url: str) -> str | None:
    try:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        if not host:
            return None
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return None


def base_domain(domain: str) -> str:
    parts = domain.split(".")
    if len(parts) <= 2:
        return domain
    return ".".join(parts[-2:])


def is_blacklisted(domain: str) -> bool:
    return base_domain(domain) in DOMAIN_BLACKLIST


def extract_links(html: str, base_url: str) -> set[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: set[str] = set()

    for tag in soup.find_all(href=True):
        href = tag["href"]
        full = urljoin(base_url, href).split("#")[0]
        if full.startswith(("mailto:", "tel:", "javascript:")):
            continue
        links.add(full)

    for tag in soup.find_all(src=True):
        src = tag["src"]
        full = urljoin(base_url, src).split("#")[0]
        if full.startswith(("mailto:", "tel:", "javascript:")):
            continue
        links.add(full)

    return links


def summarize_domains(domains: set[str]) -> dict:
    total_domains = len(domains)
    base_counts: dict[str, set[str]] = {}
    for d in domains:
        bd = base_domain(d)
        base_counts.setdefault(bd, set()).add(d)

    total_base = len(base_counts)
    total_subdomains = sum(len(v) - 1 for v in base_counts.values() if len(v) > 1)

    return {
        "total_domains": total_domains,
        "total_base_domains": total_base,
        "total_subdomains": total_subdomains,
        "details": {
            bd: {
                "count": len(v),
                "subdomains": sorted(v),
            }
            for bd, v in base_counts.items()
        },
    }


def write_log(domains: set[str], mode: str, unlimited: bool):
    summary = summarize_domains(domains)
    log_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "mode": mode,
        "unlimited": unlimited,
        "summary": summary,
    }
    save_json_array(LOG_FILE, [log_data])


# SYNC CRAWLER
class SyncDomainCrawler:
    def __init__(self, entry_url: str, max_domains: int | None):
        self.entry = entry_url
        self.max_domains = max_domains
        self.visited_urls: set[str] = set()

        existing = load_domains()
        self.domains: set[str] = {e["domain"] for e in existing}

        self.executor = ThreadPoolExecutor(max_workers=THREADS)
        total = self.max_domains if self.max_domains is not None else None
        self.progress = tqdm(total=total, desc="Sync domains", unit="domain")

    def fetch(self, url: str) -> tuple[str | None, str | None]:
        try:
            headers = {"User-Agent": USER_AGENT}
            r = requests.get(url, timeout=TIMEOUT, headers=headers)
            r.raise_for_status()
            html = r.text
            server = r.headers.get("Server", "").strip() or None
            return html, server
        except Exception:
            return None, None

    def should_stop(self) -> bool:
        if self.max_domains is None:
            return False
        return len(self.domains) >= self.max_domains

    def process_url(self, url: str, depth: int):
        if depth > MAX_DEPTH:
            return
        if self.should_stop():
            return
        if url in self.visited_urls:
            return

        self.visited_urls.add(url)

        html, server = self.fetch(url)
        if html is None:
            return

        domain = normalize_domain(url)
        if not domain:
            return
        if is_blacklisted(domain):
            return

        if domain not in self.domains:
            self.domains.add(domain)
            append_domain_safe(domain, server)
            if self.progress.total is not None:
                self.progress.update(1)
            else:
                self.progress.update(0)

        if self.should_stop():
            return

        links = extract_links(html, url)
        futures = []
        for link in links:
            if self.should_stop():
                break
            futures.append(self.executor.submit(self.process_url, link, depth + 1))

        for f in futures:
            f.result()

    def run(self):
        logger.info(f"Starting sync domain crawl from: {self.entry}")
        self.process_url(self.entry, 0)
        self.progress.close()
        logger.info(f"Sync crawl finished with {len(self.domains)} domains.")
        write_log(self.domains, mode="sync", unlimited=self.max_domains is None)


# ASYNC CRAWLER
class AsyncDomainCrawler:
    def __init__(self, entry_url: str, max_domains: int | None):
        self.entry = entry_url
        self.max_domains = max_domains
        self.visited_urls: set[str] = set()

        existing = load_domains()
        self.domains: set[str] = {e["domain"] for e in existing}

        self.sem = asyncio.Semaphore(50)
        total = self.max_domains if self.max_domains is not None else None
        self.progress = tqdm(total=total, desc="Async domains", unit="domain")

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> tuple[str | None, str | None]:
        try:
            async with self.sem:
                async with session.get(url, timeout=TIMEOUT) as resp:
                    resp.raise_for_status()
                    html = await resp.text(errors="ignore")
                    server = resp.headers.get("Server", "").strip() or None
                    return html, server
        except Exception:
            return None, None

    def should_stop(self) -> bool:
        if self.max_domains is None:
            return False
        return len(self.domains) >= self.max_domains

    async def process_url(self, session: aiohttp.ClientSession, url: str, depth: int):
        if depth > MAX_DEPTH:
            return
        if self.should_stop():
            return
        if url in self.visited_urls:
            return

        self.visited_urls.add(url)

        html, server = await self.fetch(session, url)
        if html is None:
            return

        domain = normalize_domain(url)
        if not domain:
            return
        if is_blacklisted(domain):
            return

        if domain not in self.domains:
            self.domains.add(domain)
            append_domain_safe(domain, server)
            if self.progress.total is not None:
                self.progress.update(1)
            else:
                self.progress.update(0)

        if self.should_stop():
            return

        links = extract_links(html, url)
        tasks = []
        for link in links:
            if self.should_stop():
                break
            tasks.append(self.process_url(session, link, depth + 1))

        if tasks:
            await asyncio.gather(*tasks)

    async def run_async(self):
        logger.info(f"Starting async domain crawl from: {self.entry}")
        headers = {"User-Agent": USER_AGENT}
        async with aiohttp.ClientSession(headers=headers) as session:
            await self.process_url(session, self.entry, 0)
        self.progress.close()
        logger.info(f"Async crawl finished with {len(self.domains)} domains.")
        write_log(self.domains, mode="async", unlimited=self.max_domains is None)

    def run(self):
        return asyncio.run(self.run_async())


# ENTRY POINT
def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <url> [--mode sync|async] [--unlimited]")
        return

    entry = sys.argv[1]
    mode = "sync"
    unlimited = False

    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            mode = sys.argv[idx + 1].lower()

    if "--unlimited" in sys.argv:
        unlimited = True

    max_domains = None if unlimited else MAX_DOMAINS_DEFAULT

    if mode == "sync":
        crawler = SyncDomainCrawler(entry, max_domains=max_domains)
        crawler.run()
    else:
        crawler = AsyncDomainCrawler(entry, max_domains=max_domains)
        crawler.run()

    print("Crawling complete.")
    print(f"Domains in {DOMAINS_FILE}, summary in {LOG_FILE}")


if __name__ == "__main__":
    main()
