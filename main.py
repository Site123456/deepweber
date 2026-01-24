import asyncio
import json
import logging
import sys
import os
import re
import psutil
import gc
import warnings
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
from datetime import datetime, timezone
from typing import Optional, Set, Dict, List, Tuple

import aiohttp
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Suppress BeautifulSoup warnings about parsers
warnings.filterwarnings('ignore', module='bs4')
warnings.filterwarnings('ignore', message='.*unrecognized*')

# CONFIG
MAX_DOMAINS_DEFAULT = 5000  # Increase to get more domains this may need more RAM
MAX_DEPTH = 15  # Increased depth with 8GB RAM
MAX_DEPTH_UNLIMITED = 30  # Deeper crawling support
TIMEOUT = 15
THREADS = 64  # Doubled threads with more memory
BATCH_SIZE = 500  # Larger batches (5x) with 8GB available
MEMORY_LIMIT_MB = 8000  # 8GB default RAM limit
MEMORY_LIMIT_SSD_MB = 10240  # 10GB SSD temporary storage
LOG_FLUSH_INTERVAL = 10  # Flush log every 10 URLs
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)
DOMAINS_FILE = "domains.json"
LOG_FILE = "log.json"
ERROR_FILE = "errors.json"  # NEW: Track errors with details
CACHE_DIR = "cache"  # Temporary cache for SSD storage
CACHE_MAX_SIZE_MB = 10240  # 10GB cache limit

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
    "twitch.tv",
    "github.com",
    "stackoverflow.com",
    "medium.com",
}

# Common file extensions to skip (non-html resources) for faster crawling
SKIP_EXTENSIONS = {
    ".pdf", ".zip", ".exe", ".dmg", ".pkg", ".tar", ".gz",
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico", ".webp",
    ".mp3", ".mp4", ".avi", ".mov", ".wav", ".flac",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".iso", ".bin", ".dll", ".so", ".dylib"
}

# LOGGING
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)
logger = logging.getLogger("domain_crawler")

# Suppress verbose libraries
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('aiohttp').setLevel(logging.ERROR)
logging.getLogger('asyncio').setLevel(logging.ERROR)


def get_memory_usage_mb() -> float:
    """Get current process memory usage in MB."""
    try:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    except Exception:
        return 0

def check_memory_limit() -> bool:
    """Check if memory usage exceeds limit."""
    usage = get_memory_usage_mb()
    return usage > MEMORY_LIMIT_MB

def cleanup_memory():
    """Aggressively clean up memory."""
    try:
        gc.collect()
        return True
    except Exception:
        return False


def initialize_cache():
    """Initialize cache directory for SSD storage."""
    if not os.path.exists(CACHE_DIR):
        try:
            os.makedirs(CACHE_DIR)
        except OSError:
            pass


def get_cache_usage_mb() -> float:
    """Get current cache directory size in MB."""
    try:
        total_size = 0
        if os.path.exists(CACHE_DIR):
            for root, dirs, files in os.walk(CACHE_DIR):
                for file in files:
                    total_size += os.path.getsize(os.path.join(root, file))
        return total_size / 1024 / 1024
    except Exception:
        return 0


def check_ssd_limit() -> bool:
    """Check if SSD cache usage exceeds limit."""
    usage = get_cache_usage_mb()
    if usage > CACHE_MAX_SIZE_MB:
        logger.warning(f"SSD cache limit exceeded: {usage:.1f}MB > {CACHE_MAX_SIZE_MB}MB")
        return True
    return False


def cleanup_cache():
    """Clean up old cache files."""
    try:
        if os.path.exists(CACHE_DIR):
            for file in os.listdir(CACHE_DIR):
                file_path = os.path.join(CACHE_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    except Exception as e:
        logger.debug(f"Cache cleanup error: {e}")


# ERROR LOGGER
class ErrorLogger:
    """Track and log errors to errors.json with detailed information."""
    
    def __init__(self):
        self.errors: List[Dict] = self.load_errors()
    
    def load_errors(self) -> List[Dict]:
        """Load existing errors from file."""
        try:
            with open(ERROR_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except FileNotFoundError:
            return []
        except Exception:
            return []
    
    def log_error(self, url: str, error_type: str, message: str, location: str = "unknown", context: str = ""):
        """Log an error with full details."""
        try:
            error_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "url": url,
                "error_type": error_type,
                "error_message": str(message)[:500],  # Limit message length
                "location": location,
                "context": context[:200] if context else "",
            }
            self.errors.append(error_entry)
            
            # Keep only last 1000 errors to prevent file explosion
            if len(self.errors) > 1000:
                self.errors = self.errors[-1000:]
            
            self.save_errors()
        except Exception as e:
            logger.debug(f"Error logging error: {e}")
    
    def save_errors(self):
        """Save errors to file."""
        try:
            with open(ERROR_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.errors, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Failed to save errors: {e}")
    
    def get_summary(self) -> Dict:
        """Get error summary statistics."""
        error_types = {}
        for error in self.errors:
            et = error.get('error_type', 'Unknown')
            error_types[et] = error_types.get(et, 0) + 1
        return {
            "total_errors": len(self.errors),
            "error_types": error_types,
            "recent_errors": self.errors[-10:] if self.errors else []
        }


# Global error logger instance
error_logger = ErrorLogger()

# JSON HELPERS (SAFE)
def load_json_array(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [x for x in data if isinstance(x, dict)]
            return []
    except FileNotFoundError:
        return []
    except Exception as e:
        logger.warning(f"Error loading {path}: {e}")
        return []


def save_json_array(path: str, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving to {path}: {e}")


def load_domains():
    """Load existing domains from file."""
    data = load_json_array(DOMAINS_FILE)
    return [x for x in data if "domain" in x]


def append_domain_safe(domain: str, server: Optional[str]):
    """Safely append domain to file (prevents duplicates)."""
    try:
        data = load_domains()
        if any(entry["domain"] == domain for entry in data):
            return False
        
        data.append({
            "id": len(data) + 1,
            "domain": domain,
            "server": server or "Unknown",
        })
        save_json_array(DOMAINS_FILE, data)
        return True
    except Exception as e:
        logger.warning(f"Error appending domain {domain}: {e}")
        return False


# DOMAIN / URL UTILITIES
def is_valid_url(url: str) -> bool:
    """Validate URL format."""
    try:
        if not url or len(url) > 2048:
            return False
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except Exception:
        return False


def has_skip_extension(url: str) -> bool:
    """Check if URL has a file extension to skip."""
    try:
        path = urlparse(url).path.lower()
        return any(path.endswith(ext) for ext in SKIP_EXTENSIONS)
    except Exception:
        return False


def normalize_domain(url: str) -> Optional[str]:
    """Extract and normalize domain from URL."""
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
    """Extract base domain (e.g., 'example.com' from 'subdomain.example.com')."""
    try:
        parts = domain.split(".")
        if len(parts) <= 2:
            return domain
        return ".".join(parts[-2:])
    except Exception:
        return domain


def is_blacklisted(domain: str) -> bool:
    """Check if domain is blacklisted."""
    return base_domain(domain) in DOMAIN_BLACKLIST


def extract_links(html: str, base_url: str) -> Set[str]:
    """Extract all unique links from HTML (advanced multi-source extraction)."""
    links: Set[str] = set()
    
    try:
        # Use lxml parser explicitly for better performance and fewer warnings
        try:
            soup = BeautifulSoup(html, "lxml")
        except Exception:
            # Fallback to html.parser if lxml not available
            soup = BeautifulSoup(html, "html.parser")
        
        # Extract from href attributes (a, link, area tags)
        for tag in soup.find_all(['a', 'link', 'area']):
            try:
                href = tag.get("href", "").strip()
                if href and not href.startswith(("mailto:", "tel:", "javascript:", "data:", "#", "?")):
                    full = urljoin(base_url, href).split("#")[0]
                    if is_valid_url(full) and not has_skip_extension(full):
                        links.add(full)
            except Exception:
                continue
        
        # Extract from src attributes (script, img, iframe, source tags)
        for tag in soup.find_all(['src', 'script', 'img', 'iframe', 'source']):
            try:
                src = tag.get("src", "").strip()
                if src and not src.startswith(("data:", "javascript:", "blob:")):
                    full = urljoin(base_url, src).split("#")[0]
                    if is_valid_url(full) and not has_skip_extension(full):
                        links.add(full)
            except Exception:
                continue
        
        # Extract from meta tags (og:url, canonical, etc.)
        for meta in soup.find_all("meta"):
            try:
                properties = ["content", "href", "url"]
                for prop in properties:
                    content = meta.get(prop, "").strip()
                    if content and is_valid_url(content) and not has_skip_extension(content):
                        links.add(content)
            except Exception:
                continue
        
        # Extract from form actions
        for form in soup.find_all("form"):
            try:
                action = form.get("action", "").strip()
                if action and not action.startswith(("javascript:", "#")):
                    full = urljoin(base_url, action).split("#")[0]
                    if is_valid_url(full) and not has_skip_extension(full):
                        links.add(full)
            except Exception:
                continue
        
        # Extract from JSON-LD structured data
        for script in soup.find_all("script", {"type": "application/ld+json"}):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    for key in ["url", "sameAs", "image", "logo"]:
                        value = data.get(key)
                        if isinstance(value, str) and is_valid_url(value):
                            links.add(value)
                        elif isinstance(value, list):
                            for item in value:
                                if isinstance(item, str) and is_valid_url(item):
                                    links.add(item)
            except Exception:
                continue
        
        # Extract from onclick and other event handlers
        for tag in soup.find_all():
            try:
                for attr in ["onclick", "onload", "data-url", "data-href"]:
                    value = tag.get(attr, "")
                    if value and "http" in value.lower():
                        # Simple URL extraction from event handlers
                        import re
                        urls = re.findall(r'https?://[^\s\'")<]+', value)
                        for url in urls:
                            if is_valid_url(url) and not has_skip_extension(url):
                                links.add(url)
            except Exception:
                continue
    
    except Exception as e:
        logger.debug(f"Error extracting links: {e}")
    
    # Limit links per page to prevent memory explosion
    return set(list(links)[:200])


def summarize_domains(domains: Set[str]) -> dict:
    """Create summary statistics from domains."""
    total_domains = len(domains)
    base_counts: Dict[str, Set[str]] = {}
    
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
                "subdomains": sorted(list(v)[:10]),  # Limit to top 10 per base domain
            }
            for bd, v in sorted(base_counts.items())[:100]  # Limit to top 100 base domains
        },
    }


def write_log(domains: Set[str], mode: str, unlimited: bool):
    """Write crawl summary to log file."""
    summary = summarize_domains(domains)
    log_data = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "mode": mode,
        "unlimited": unlimited,
        "memory_mb": f"{get_memory_usage_mb():.2f}",
        "total_urls_crawled": 0,
        "summary": summary,
    }
    save_json_array(LOG_FILE, [log_data])


class IncrementalLogger:
    """Real-time logging system that updates log.json as crawling progresses."""
    
    def __init__(self, mode: str, unlimited: bool):
        self.mode = mode
        self.unlimited = unlimited
        self.start_time = datetime.now(timezone.utc)
        self.urls_crawled = 0
        self.domains_found = set()
        self.servers_found: Dict[str, int] = {}
        self.errors_count = 0
        self.last_flush = 0
        self.initialize_log()
    
    def initialize_log(self):
        """Initialize log file with starting data."""
        log_data = {
            "timestamp_start": self.start_time.isoformat() + "Z",
            "timestamp_last_update": self.start_time.isoformat() + "Z",
            "mode": self.mode,
            "unlimited": self.unlimited,
            "status": "crawling",
            "urls_crawled": 0,
            "unique_domains": 0,
            "errors": 0,
            "memory_mb": f"{get_memory_usage_mb():.2f}",
            "elapsed_seconds": 0,
            "estimated_completion": "N/A",
            "summary": {
                "total_domains": 0,
                "total_base_domains": 0,
                "total_subdomains": 0,
                "top_servers": {},
                "top_domains": []
            }
        }
        save_json_array(LOG_FILE, [log_data])
    
    def add_domain(self, domain: str, server: Optional[str] = None):
        """Log a newly discovered domain."""
        self.domains_found.add(domain)
        if server:
            self.servers_found[server] = self.servers_found.get(server, 0) + 1
        self.urls_crawled += 1
        
        # Flush every LOG_FLUSH_INTERVAL URLs
        if self.urls_crawled % LOG_FLUSH_INTERVAL == 0:
            self.flush()
    
    def add_error(self):
        """Log an error during crawling."""
        self.errors_count += 1
    
    def flush(self):
        """Update log file with current progress."""
        try:
            elapsed = (datetime.now(timezone.utc) - self.start_time).total_seconds()
            summary = summarize_domains(self.domains_found)
            
            # Calculate top servers
            top_servers = dict(sorted(self.servers_found.items(), key=lambda x: x[1], reverse=True)[:10])
            
            # Get top domains
            top_domains = sorted(list(self.domains_found))[:50]
            
            log_data = {
                "timestamp_start": self.start_time.isoformat() + "Z",
                "timestamp_last_update": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "mode": self.mode,
                "unlimited": self.unlimited,
                "status": "crawling",
                "urls_crawled": self.urls_crawled,
                "unique_domains": len(self.domains_found),
                "errors": self.errors_count,
                "memory_mb": f"{get_memory_usage_mb():.2f}",
                "elapsed_seconds": round(elapsed, 2),
                "crawl_rate_urls_per_sec": round(self.urls_crawled / elapsed, 2) if elapsed > 0 else 0,
                "summary": {
                    **summary,
                    "top_servers": top_servers,
                    "top_domains": top_domains,
                }
            }
            save_json_array(LOG_FILE, [log_data])
        except Exception as e:
            logger.debug(f"Error flushing log: {e}")
    
    def finalize(self):
        """Finalize log with completion status."""
        try:
            elapsed = (datetime.now(timezone.utc) - self.start_time).total_seconds()
            summary = summarize_domains(self.domains_found)
            top_servers = dict(sorted(self.servers_found.items(), key=lambda x: x[1], reverse=True)[:10])
            top_domains = sorted(list(self.domains_found))[:100]
            
            log_data = {
                "timestamp_start": self.start_time.isoformat().replace('+00:00', 'Z'),
                "timestamp_end": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "mode": self.mode,
                "unlimited": self.unlimited,
                "status": "completed",
                "urls_crawled": self.urls_crawled,
                "unique_domains": len(self.domains_found),
                "errors": self.errors_count,
                "memory_mb": f"{get_memory_usage_mb():.2f}",
                "total_elapsed_seconds": round(elapsed, 2),
                "avg_crawl_rate_urls_per_sec": round(self.urls_crawled / elapsed, 2) if elapsed > 0 else 0,
                "summary": {
                    **summary,
                    "top_servers": top_servers,
                    "top_domains": top_domains,
                }
            }
            save_json_array(LOG_FILE, [log_data])
        except Exception as e:
            logger.error(f"Error finalizing log: {e}")


# SYNC CRAWLER (Enhanced with real-time logging)
class SyncDomainCrawler:
    def __init__(self, entry_url: str, max_domains: Optional[int], unlimited: bool = False):
        self.entry = entry_url
        self.max_domains = max_domains
        self.unlimited = unlimited
        self.max_depth = MAX_DEPTH_UNLIMITED if unlimited else MAX_DEPTH
        self.visited_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.url_queue: deque = deque()

        # Initialize cache and memory management
        initialize_cache()

        existing = load_domains()
        self.domains: Set[str] = {e["domain"] for e in existing}

        self.executor = ThreadPoolExecutor(max_workers=THREADS)
        total = self.max_domains if self.max_domains is not None else None
        self.progress = tqdm(total=total, desc="Sync domains", unit="domain", ncols=100)
        
        # Initialize incremental logger
        self.logger_obj = IncrementalLogger("sync", unlimited)

    def fetch(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Fetch URL with enhanced error handling and retries."""
        if url in self.failed_urls:
            return None, None
        
        # Check SSD cache limit
        if check_ssd_limit():
            cleanup_cache()
        
        retries = 3
        for attempt in range(retries):
            try:
                headers = {
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                }
                r = requests.get(url, timeout=TIMEOUT, headers=headers, allow_redirects=True)
                r.raise_for_status()
                
                # Check content type
                content_type = r.headers.get("Content-Type", "").lower()
                if "text/html" not in content_type and "application/xhtml" not in content_type:
                    return None, None
                
                html = r.text[:2000000]  # Limit HTML size to 2MB
                server = r.headers.get("Server", "").strip() or None
                return html, server
            except requests.Timeout:
                if attempt < retries - 1:
                    continue
                self.failed_urls.add(url)
                error_logger.log_error(url, "Timeout", "Request timeout", "SyncDomainCrawler.fetch", f"Attempt {attempt+1}")
                self.logger_obj.add_error()
                return None, None
            except requests.RequestException as e:
                if attempt < retries - 1:
                    continue
                self.failed_urls.add(url)
                error_logger.log_error(url, type(e).__name__, str(e)[:200], "SyncDomainCrawler.fetch", f"Attempt {attempt+1}")
                self.logger_obj.add_error()
                return None, None
            except Exception as e:
                if attempt < retries - 1:
                    continue
                self.failed_urls.add(url)
                error_logger.log_error(url, type(e).__name__, str(e)[:200], "SyncDomainCrawler.fetch", f"Attempt {attempt+1}")
                self.logger_obj.add_error()
                return None, None
        
        return None, None

    def should_stop(self) -> bool:
        """Check stop conditions."""
        if check_memory_limit():
            logger.warning(f"Memory limit exceeded ({get_memory_usage_mb():.2f}MB > {MEMORY_LIMIT_MB}MB)")
            return True
        if self.max_domains is None:
            return False
        return len(self.domains) >= self.max_domains

    def process_url(self, url: str, depth: int):
        """Process single URL safely."""
        if depth > self.max_depth:
            return
        if self.should_stop():
            return
        if url in self.visited_urls:
            return
        if not is_valid_url(url):
            return
        if has_skip_extension(url):
            return

        self.visited_urls.add(url)

        html, server = self.fetch(url)
        if html is None:
            return

        domain = normalize_domain(url)
        if not domain or is_blacklisted(domain):
            return

        if domain not in self.domains:
            if append_domain_safe(domain, server):
                self.domains.add(domain)
                self.logger_obj.add_domain(domain, server)
                self.progress.update(1)

        if self.should_stop():
            return

        # Periodically clean memory
        if len(self.visited_urls) % 50 == 0:
            cleanup_memory()

        links = extract_links(html, url)
        futures = []
        
        for link in links:
            if self.should_stop():
                break
            futures.append(self.executor.submit(self.process_url, link, depth + 1))

        for f in futures:
            try:
                f.result(timeout=30)
            except Exception:
                pass

    def run(self):
        """Run sync crawler."""
        try:
            logger.info(f"Starting sync domain crawl from: {self.entry}")
            logger.info(f"Max domains: {self.max_domains or 'Unlimited'}, Max depth: {self.max_depth}")
            self.process_url(self.entry, 0)
        except KeyboardInterrupt:
            logger.info("Crawl interrupted by user")
        except Exception as e:
            logger.error(f"Sync crawl error: {e}")
        finally:
            self.progress.close()
            self.executor.shutdown(wait=True)
            cleanup_memory()
            logger.info(f"Sync crawl finished with {len(self.domains)} domains.")
            self.logger_obj.finalize()  # Finalize incremental logging


# ASYNC CRAWLER (Enhanced with real-time logging)
class AsyncDomainCrawler:
    def __init__(self, entry_url: str, max_domains: Optional[int], unlimited: bool = False):
        self.entry = entry_url
        self.max_domains = max_domains
        self.unlimited = unlimited
        self.max_depth = MAX_DEPTH_UNLIMITED if unlimited else MAX_DEPTH
        self.visited_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.processing_count = 0

        # Initialize cache and memory management
        initialize_cache()

        existing = load_domains()
        self.domains: Set[str] = {e["domain"] for e in existing}

        # Adaptive semaphore based on unlimited mode
        semaphore_size = 150 if unlimited else 100
        self.sem = asyncio.Semaphore(semaphore_size)
        
        total = self.max_domains if self.max_domains is not None else None
        self.progress = tqdm(total=total, desc="Async domains", unit="domain", ncols=100)
        
        # Initialize incremental logger
        self.logger_obj = IncrementalLogger("async", unlimited)

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Fetch URL asynchronously with error handling and retries."""
        if url in self.failed_urls:
            return None, None
        
        # Check SSD cache limit
        if check_ssd_limit():
            cleanup_cache()
        
        retries = 3
        for attempt in range(retries):
            try:
                async with self.sem:
                    async with session.get(url, timeout=TIMEOUT, allow_redirects=True) as resp:
                        # Check status and content type
                        if resp.status not in (200, 301, 302, 307, 308):
                            if attempt < retries - 1:
                                await asyncio.sleep(0.5)
                                continue
                            self.failed_urls.add(url)
                            error_logger.log_error(url, f"HTTP {resp.status}", f"Non-success HTTP status", "AsyncDomainCrawler.fetch")
                            self.logger_obj.add_error()
                            return None, None
                        
                        content_type = resp.headers.get("Content-Type", "").lower()
                        if "text/html" not in content_type and "application/xhtml" not in content_type:
                            return None, None
                        
                        try:
                            html = await resp.text(errors="ignore")
                        except Exception:
                            if attempt < retries - 1:
                                await asyncio.sleep(0.5)
                                continue
                            return None, None
                        
                        # Limit HTML size
                        if len(html) > 2000000:
                            html = html[:2000000]
                        
                        server = resp.headers.get("Server", "").strip() or None
                        return html, server
            except asyncio.TimeoutError:
                if attempt < retries - 1:
                    await asyncio.sleep(1)
                    continue
                self.failed_urls.add(url)
                error_logger.log_error(url, "AsyncTimeout", "Async request timeout", "AsyncDomainCrawler.fetch", f"Attempt {attempt+1}")
                self.logger_obj.add_error()
                return None, None
            except aiohttp.ClientError as e:
                if attempt < retries - 1:
                    await asyncio.sleep(0.5)
                    continue
                self.failed_urls.add(url)
                error_logger.log_error(url, type(e).__name__, str(e)[:200], "AsyncDomainCrawler.fetch", f"Attempt {attempt+1}")
                self.logger_obj.add_error()
                return None, None
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(0.5)
                    continue
                self.failed_urls.add(url)
                error_logger.log_error(url, type(e).__name__, str(e)[:200], "AsyncDomainCrawler.fetch", f"Attempt {attempt+1}")
                self.logger_obj.add_error()
                return None, None
        
        return None, None

    def should_stop(self) -> bool:
        """Check stop conditions."""
        if check_memory_limit():
            logger.warning(f"Memory limit exceeded ({get_memory_usage_mb():.2f}MB > {MEMORY_LIMIT_MB}MB)")
            return True
        if self.max_domains is None:
            return False
        return len(self.domains) >= self.max_domains

    async def process_url(self, session: aiohttp.ClientSession, url: str, depth: int):
        """Process single URL asynchronously."""
        if depth > self.max_depth:
            return
        if self.should_stop():
            return
        if url in self.visited_urls:
            return
        if not is_valid_url(url):
            return
        if has_skip_extension(url):
            return

        self.visited_urls.add(url)
        self.processing_count += 1

        html, server = await self.fetch(session, url)
        if html is None:
            self.processing_count -= 1
            return

        domain = normalize_domain(url)
        if not domain or is_blacklisted(domain):
            self.processing_count -= 1
            return

        if domain not in self.domains:
            if append_domain_safe(domain, server):
                self.domains.add(domain)
                self.logger_obj.add_domain(domain, server)
                self.progress.update(1)

        self.processing_count -= 1
        
        if self.should_stop():
            return

        # Periodically clean memory
        if len(self.visited_urls) % 50 == 0:
            cleanup_memory()

        links = extract_links(html, url)
        
        # Process links in batches to manage memory
        batch_tasks = []
        for i, link in enumerate(links):
            if self.should_stop():
                break
            
            task = self.process_url(session, link, depth + 1)
            batch_tasks.append(task)
            
            # Process in batches
            if len(batch_tasks) >= BATCH_SIZE:
                await asyncio.gather(*batch_tasks, return_exceptions=True)
                batch_tasks = []
        
        # Process remaining tasks
        if batch_tasks:
            await asyncio.gather(*batch_tasks, return_exceptions=True)

    async def run_async(self):
        """Run async crawler."""
        headers = {"User-Agent": USER_AGENT}
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_read=10)
        
        async with aiohttp.ClientSession(headers=headers, connector=connector, timeout=timeout) as session:
            try:
                logger.info(f"Starting async domain crawl from: {self.entry}")
                logger.info(f"Max domains: {self.max_domains or 'Unlimited'}, Max depth: {self.max_depth}")
                await self.process_url(session, self.entry, 0)
            except KeyboardInterrupt:
                logger.info("Crawl interrupted by user")
            except Exception as e:
                logger.error(f"Async crawl error: {e}")
        
        # Wait for any remaining processing
        max_wait = 10
        while self.processing_count > 0 and max_wait > 0:
            await asyncio.sleep(0.1)
            max_wait -= 1

    def run(self):
        """Run async crawler (sync wrapper)."""
        try:
            return asyncio.run(self.run_async())
        except Exception as e:
            logger.error(f"Run error: {e}")
        finally:
            self.progress.close()
            cleanup_memory()
            logger.info(f"Async crawl finished with {len(self.domains)} domains.")
            self.logger_obj.finalize()  # Finalize incremental logging


# ENTRY POINT
def main():
    """Main entry point with improved argument handling."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <url> [--mode sync|async] [--unlimited]")
        print("\nExamples:")
        print("  python main.py https://example.com")
        print("  python main.py https://example.com --mode async")
        print("  python main.py https://example.com --mode async --unlimited")
        return

    entry = sys.argv[1]
    mode = "sync"
    unlimited = False

    # Parse arguments
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            mode = sys.argv[idx + 1].lower()
            if mode not in ("sync", "async"):
                logger.error(f"Invalid mode: {mode}. Use 'sync' or 'async'.")
                return

    if "--unlimited" in sys.argv:
        unlimited = True

    # Validate entry URL
    if not is_valid_url(entry):
        logger.error(f"Invalid URL: {entry}")
        return

    # Determine max domains
    max_domains = None if unlimited else MAX_DOMAINS_DEFAULT

    # Log configuration
    logger.info(f"Configuration: mode={mode}, max_domains={max_domains or 'unlimited'}, threads={THREADS}")
    logger.info(f"Memory: RAM limit {MEMORY_LIMIT_MB}MB (8GB), SSD cache {CACHE_MAX_SIZE_MB}MB (10GB)")
    logger.info(f"Batch size: {BATCH_SIZE}, Depth: {MAX_DEPTH if not unlimited else MAX_DEPTH_UNLIMITED}")

    try:
        # Run crawler
        if mode == "sync":
            crawler = SyncDomainCrawler(entry, max_domains=max_domains, unlimited=unlimited)
            crawler.run()
        else:
            crawler = AsyncDomainCrawler(entry, max_domains=max_domains, unlimited=unlimited)
            crawler.run()

        logger.info("✓ Crawling complete.")
        logger.info(f"✓ Domains saved to: {DOMAINS_FILE}")
        logger.info(f"✓ Summary saved to: {LOG_FILE}")
        
        # Show error summary if any errors occurred
        error_summary = error_logger.get_summary()
        if error_summary["total_errors"] > 0:
            logger.info(f"⚠ {error_summary['total_errors']} errors logged to: {ERROR_FILE}")
            logger.info(f"  Error types: {error_summary['error_types']}")
        
    except KeyboardInterrupt:
        logger.info("\n⚠ Crawling interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code or 0)
