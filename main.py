#!/usr/bin/env python3
import json
import os
import asyncio
import aiohttp
import time
import gzip
from urllib.parse import urljoin, urldefrag, urlparse
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# ANSI colors (safe on most terminals)
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def clear_block():
    print("\033[2J\033[H", end="")  # Clear screen + move cursor to top-left

# CONFIG
CONCURRENCY = 100
DOMAIN_DELAY = 10
GLOBAL_URLS_PER_SEC = 200
AUTO_SHUTDOWN_SECONDS = 600

START_FILE = "startsearch.txt"

BUILD_DIR = "./crawler_build"
os.makedirs(BUILD_DIR, exist_ok=True)

QUEUE_FILE = f"{BUILD_DIR}/queue.json"
VISITED_FILE = f"{BUILD_DIR}/visited.json"
FOUND_FILE = f"{BUILD_DIR}/found.json"
ERROR_FILE = f"{BUILD_DIR}/error.json"
STATS_FILE = f"{BUILD_DIR}/stats.json"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.3"
    )
}

# JSON HELPERS
def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def append_json(path, entry):
    data = load_json(path, [])
    data.append(entry)
    save_json(path, data)

# SEED LOADING
def load_seeds():
    seeds = []
    with open(START_FILE, "r") as f:
        for line in f:
            url = line.strip()
            if url:
                seeds.append((normalize(url), 0))
    return seeds

# STATE
def load_state():
    queue = load_json(QUEUE_FILE, load_seeds())
    visited = set(load_json(VISITED_FILE, []))
    found = set(load_json(FOUND_FILE, []))
    return queue, visited, found

def save_state(queue, visited, found):
    save_json(QUEUE_FILE, queue)
    save_json(VISITED_FILE, list(visited))
    save_json(FOUND_FILE, list(found))

# NORMALIZATION
def normalize(url):
    if not url:
        return ""
    clean, _ = urldefrag(url)
    return clean.rstrip("/")

def should_skip(url, visited, found):
    return not url or url in visited or url in found

# URL EXTRACTION
def extract_all_urls(soup, base_url):
    urls = set()

    def add(attr, tag):
        for t in soup.find_all(tag, **{attr: True}):
            try:
                urls.add(urljoin(base_url, t[attr]))
            except:
                pass

    add("href", "a")
    add("src", "script")
    add("href", "link")
    add("src", "img")
    add("action", "form")
    add("formaction", "button")

    return {normalize(u) for u in urls if u}

# FETCHERS
async def fetch_html(session, url):
    try:
        async with session.get(url, headers=HEADERS, timeout=15) as resp:
            if resp.status != 200:
                return None, resp.status, None, "HTTP"
            ctype = resp.headers.get("Content-Type", "").lower()
            if "text/html" not in ctype:
                return None, resp.status, ctype, "NONHTML"
            text = await resp.text()
            if not text.strip():
                return None, resp.status, ctype, "EMPTY"
            return text, resp.status, ctype, None
    except:
        return None, None, None, "ERROR"

async def fetch_text(session, url):
    try:
        async with session.get(url, headers=HEADERS, timeout=20) as resp:
            if resp.status != 200:
                return None
            return await resp.text()
    except:
        return None

async def fetch_bytes(session, url):
    try:
        async with session.get(url, headers=HEADERS, timeout=30) as resp:
            if resp.status != 200:
                return None
            return await resp.read()
    except:
        return None

# SITEMAP PARSER
def parse_sitemap_xml(xml_text):
    urls = set()
    links = set()

    try:
        root = ET.fromstring(xml_text)
    except:
        return urls, links

    for elem in root.iter():
        tag = elem.tag.lower()
        if tag.endswith("loc") and elem.text:
            t = elem.text.strip()
            if t.endswith(".xml") or t.endswith(".xml.gz"):
                links.add(t)
            else:
                urls.add(t)

    return urls, links

# RATE LIMITER
class UrlRateLimiter:
    def __init__(self, max_per_sec):
        self.max = max_per_sec
        self.count = 0
        self.start = time.time()
        self.lock = asyncio.Lock()

    async def wait(self):
        while True:
            async with self.lock:
                now = time.time()
                if now - self.start >= 1:
                    self.start = now
                    self.count = 0
                if self.count < self.max:
                    self.count += 1
                    return
                sleep = 1 - (now - self.start)
            if sleep > 0:
                await asyncio.sleep(sleep)

# DOMAIN QUEUE
class DomainQueue:
    def __init__(self, visited, found, limiter):
        self.queues = {}
        self.last = {}
        self.domains = []
        self.lock = asyncio.Lock()

        self.visited = visited
        self.found = found
        self.limiter = limiter

        self.sitemap_done = set()
        self.sitemap_processed = set()

    def add_seed(self, url, depth):
        url = normalize(url)
        if should_skip(url, self.visited, self.found):
            return
        self.found.add(url)
        dom = urlparse(url).netloc
        if dom not in self.queues:
            self.queues[dom] = asyncio.Queue()
            self.domains.append(dom)
        self.queues[dom].put_nowait((url, depth))

    async def add_url(self, url, depth):
        url = normalize(url)
        if should_skip(url, self.visited, self.found):
            return

        await self.limiter.wait()

        if should_skip(url, self.visited, self.found):
            return

        self.found.add(url)
        dom = urlparse(url).netloc
        if dom not in self.queues:
            self.queues[dom] = asyncio.Queue()
            self.domains.append(dom)
        self.queues[dom].put_nowait((url, depth))

    async def get(self):
        while True:
            async with self.lock:
                now = time.time()
                for dom in self.domains:
                    q = self.queues[dom]
                    if q.empty():
                        continue
                    if now - self.last.get(dom, 0) < DOMAIN_DELAY:
                        continue
                    item = await q.get()
                    self.last[dom] = now
                    return item
            await asyncio.sleep(0.05)

    def task_done(self, url):
        dom = urlparse(url).netloc
        if dom in self.queues:
            self.queues[dom].task_done()

    def dump_state(self):
        out = []
        for q in self.queues.values():
            out.extend(list(q._queue))
        return out

    def empty(self):
        return all(q.empty() for q in self.queues.values())

    async def ensure_sitemaps(self, session, domain):
        if domain in self.sitemap_done:
            return
        self.sitemap_done.add(domain)

        base_http = f"http://{domain}"
        base_https = f"https://{domain}"

        robots_list = [
            f"{base_https}/robots.txt",
            f"{base_http}/robots.txt",
        ]

        sitemaps = set()

        for r in robots_list:
            txt = await fetch_text(session, r)
            if not txt:
                continue
            for line in txt.splitlines():
                if line.lower().startswith("sitemap:"):
                    sm = line.split(":", 1)[1].strip()
                    if sm:
                        sitemaps.add(sm)

        common = [
            f"{base_https}/sitemap.xml",
            f"{base_https}/sitemap_index.xml",
            f"{base_https}/sitemap.xml.gz",
            f"{base_https}/sitemap_index.xml.gz",
            f"{base_http}/sitemap.xml",
            f"{base_http}/sitemap_index.xml",
            f"{base_http}/sitemap.xml.gz",
            f"{base_http}/sitemap_index.xml.gz",
        ]

        for sm in common:
            sitemaps.add(sm)

        for sm in sitemaps:
            await self.process_sitemap(session, sm)

    async def process_sitemap(self, session, sm_url):
        sm_url = normalize(sm_url)
        if not sm_url or sm_url in self.sitemap_processed:
            return
        self.sitemap_processed.add(sm_url)

        xml_text = None

        if sm_url.endswith(".gz"):
            data = await fetch_bytes(session, sm_url)
            if not data:
                return
            try:
                xml_text = gzip.decompress(data).decode("utf-8", "replace")
            except:
                return
        else:
            xml_text = await fetch_text(session, sm_url)

        if not xml_text:
            return

        urls, links = parse_sitemap_xml(xml_text)

        for u in urls:
            await self.add_url(u, 0)

        for l in links:
            await self.process_sitemap(session, l)

# WORKER
# Global counters
TOTAL_ATTEMPTS = 0
ATTEMPT_TIMES = []
SUCCESS_TIMES = []
ERROR_TIMES = []

# Global counters
TOTAL_ATTEMPTS = 0
ATTEMPT_TIMES = []
SUCCESS_TIMES = []
ERROR_TIMES = []

async def worker(dq, session, visited, found, lock):
    global TOTAL_ATTEMPTS, ATTEMPT_TIMES, SUCCESS_TIMES, ERROR_TIMES

    while True:
        try:
            url, depth = await dq.get()
        except asyncio.CancelledError:
            return

        url = normalize(url)
        ts = int(time.time())
        dom = urlparse(url).netloc

        # Count attempt
        TOTAL_ATTEMPTS += 1
        ATTEMPT_TIMES.append(ts)

        if url in visited:
            dq.task_done(url)
            continue

        if dom:
            await dq.ensure_sitemaps(session, dom)

        html, status, ctype, err = await fetch_html(session, url)

        if err:
            ERROR_TIMES.append(ts)
            append_json(ERROR_FILE, {
                "u": url,
                "t": ts,
                "e": f"{err}_{status}" if status else err
            })
            dq.task_done(url)
            continue

        try:
            soup = BeautifulSoup(html, "html.parser")
        except:
            ERROR_TIMES.append(ts)
            append_json(ERROR_FILE, {
                "u": url,
                "t": ts,
                "e": "PARSE_ERROR"
            })
            dq.task_done(url)
            continue

        # SUCCESS
        SUCCESS_TIMES.append(ts)
        visited.add(url)

        urls = extract_all_urls(soup, url)
        for u in urls:
            if should_skip(u, visited, found):
                continue
            await dq.add_url(u, depth + 1)

        async with lock:
            save_state(dq.dump_state(), visited, found)

        dq.task_done(url)


async def progress_timer(visited):
    global TOTAL_ATTEMPTS, ATTEMPT_TIMES, SUCCESS_TIMES, ERROR_TIMES

    start = time.time()
    last_print = 0

    while True:
        await asyncio.sleep(1)
        now = time.time()
        elapsed = int(now - start)

        # Count events in sliding windows
        def count_in_window(times, seconds):
            cutoff = now - seconds
            return sum(1 for t in times if t >= cutoff)

        # Totals
        total_success = len(visited)
        total_errors = len(ERROR_TIMES)
        total_attempts = TOTAL_ATTEMPTS

        # Global error rate
        global_rate = (total_errors / total_attempts) if total_attempts else 0.0

        # Recent 10s
        recent_attempts = count_in_window(ATTEMPT_TIMES, 10)
        recent_errors = count_in_window(ERROR_TIMES, 10)
        recent_rate = (recent_errors / recent_attempts) if recent_attempts else 0.0

        # 30s / 60s windows
        attempts_30 = count_in_window(ATTEMPT_TIMES, 30)

        errors_30 = count_in_window(ERROR_TIMES, 30)

        success_30 = count_in_window(SUCCESS_TIMES, 30)

        # Moving averages
        error_rate_30 = (errors_30 / attempts_30) if attempts_30 else 0.0

        success_rate_30 = (success_30 / attempts_30) if attempts_30 else 0.0

        # Print every 10 seconds
        if elapsed - last_print >= 10:
            last_print = elapsed

            print(
                f"[{elapsed:6d}s] "
                f"att={total_attempts} "
                f" - succ={total_success} " # more is better
                f" - err={total_errors}" # less is better
                f" - rate.err={global_rate:.3f} " # less is better
                f" - 10s.err={recent_rate:.3f} " # less is better
                f" - 30s.err={error_rate_30:.3f} " # less is better
                f" - 30s.succ={success_rate_30:.3f} " # more is better
            )


# MAIN
async def crawl_async():
    queue_list, visited, found = load_state()

    limiter = UrlRateLimiter(GLOBAL_URLS_PER_SEC)
    dq = DomainQueue(visited, found, limiter)

    for url, depth in queue_list:
        dq.add_seed(url, depth)

    lock = asyncio.Lock()
    start = time.time()
    empty_since = None

    async with aiohttp.ClientSession() as session:
        workers = [
            asyncio.create_task(worker(dq, session, visited, found, lock))
            for _ in range(CONCURRENCY)
        ]

        timer_task = asyncio.create_task(progress_timer(visited))

        try:
            while True:
                if time.time() - start > AUTO_SHUTDOWN_SECONDS:
                    break

                if dq.empty():
                    if empty_since is None:
                        empty_since = time.time()
                    elif time.time() - empty_since > 5:
                        break
                else:
                    empty_since = None

                await asyncio.sleep(0.2)

        finally:
            for t in workers:
                t.cancel()
            timer_task.cancel()
            await asyncio.gather(*workers, return_exceptions=True)

    save_state(dq.dump_state(), visited, found)

if __name__ == "__main__":
    asyncio.run(crawl_async())
