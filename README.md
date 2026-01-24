# 🌐 DEEPWEBER - Global Domain Crawler

[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](#status)

---
Minimum Requirements:
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Memory](https://img.shields.io/badge/Memory-8GB-blue)](#system-requirements)
[![Threads](https://img.shields.io/badge/Threads-64-blue)](#features)

> **Discover real-world domains at scale.** High-performance web crawler for collecting live domain data and training machine learning models with authentic web infrastructure information.

---

## 📚 Documentation Index

| Section | Purpose |
|---------|---------|
| [⚡ Quick Start](#quick-start-30-seconds) | Get crawling in 30 seconds |
| [🎯 What is DEEPWEBER?](#what-is-deepweber) | Understand the tool |
| [⭐ Key Features](#key-features) | All capabilities |
| [🖥️ System Requirements](#system-requirements) | Hardware & software needs |
| [📦 Installation](#installation) | Setup guide |
| [📖 Usage Guide](#usage-guide) | How to use commands |
| [📊 Output Files](#output-files) | What files are created |
| [⚙️ Configuration](#configuration) | Customize behavior |
| [📈 Performance](#performance-tuning) | Speed & optimization |
| [🛡️ Safety](#safety--security) | Ethics & limits |
| [🔧 Troubleshooting](#troubleshooting) | Fix common issues |
| [🌍 Examples](#real-world-examples) | Use case scenarios |
| [❓ FAQ](#faq) | Answers to questions |

---

## Quick Start (30 Seconds)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run your first crawl
python main.py https://example.com

# 3. Check results
# - domains.json: List of discovered domains
# - log.json: Statistics and progress
# - errors.json: Any errors encountered
```

**Done!** The crawler discovered domains and saved them to JSON files. Run the same command again to resume automatically.

---

## What is DEEPWEBER?

DEEPWEBER is a specialized web crawler designed for **large-scale domain discovery** and **data collection**.

### 🎯 Use Cases

| Goal | Solution |
|------|----------|
| 🤖 Train LLMs | Collect real domain datasets |
| 📊 Domain Research | Analyze web infrastructure |
| 🔍 Web Discovery | Find linked domains automatically |
| 🏗️ Build Databases | Generate domain catalogs |
| 🔬 Study Hosting | Analyze server distribution |

### ✨ Why DEEPWEBER?

- ✅ **Production-Ready**: 8GB RAM, 64 threads, optimized for scale
- ✅ **Smart Resume**: Automatically continues from previous crawls
- ✅ **Real-Time Logging**: Live progress with statistics
- ✅ **Error Tracking**: Detailed error logs to `errors.json`
- ✅ **Memory Smart**: Intelligent garbage collection
- ✅ **Python 3.13 Compatible**: Modern datetime handling
- ✅ **Easy Setup**: Works out of the box

---

## ⭐ Key Features

### 🔄 Dual Processing Modes
| Mode | Speed | Stability | Best For |
|------|-------|-----------|----------|
| **Sync** | 🟡 Medium | 🟢 Excellent | Testing, learning |
| **Async** | 🟢 Fast | 🟡 Good | Production, scale |

### 📝 Real-Time Monitoring
- Live progress updates every 10 URLs
- Memory usage tracking
- Crawl rate statistics (URLs/sec)
- Top servers discovered
- Top domains found
- Error counting

### 🔍 Advanced Link Extraction (8+ Methods)
- HTML href attributes
- Image/script/iframe sources
- Meta tags (og:url, canonical)
- Form actions
- JSON-LD structured data
- Event handler URLs
- Data attributes
- Custom attributes

### 🚫 Intelligent Loop Prevention
- URL deduplication (never crawl same URL twice)
- Domain deduplication (never recrawl domain)
- Subdomain loop detection
- Depth limits (5-30 levels)

### 💾 Memory Management
| Component | Default | Purpose |
|-----------|---------|---------|
| RAM Limit | 8GB | Stop if memory exceeds limit |
| SSD Cache | 10GB | Temporary storage |
| Batch Size | 500 | Links per batch |
| HTML Limit | 2MB | Max per page |
| Links Limit | 200 | Max per page |
| Threads | 64 | Parallel workers |

### 📊 Server Detection
Identifies 20+ server types:
- Nginx
- Apache
- CloudFlare
- Microsoft IIS
- LiteSpeed
- Lighttpd
- OpenResty
- And many more

### 🎯 Domain Blacklist
Skip unwanted domains:
- Social media (Facebook, Instagram, TikTok, Twitter, etc.)
- Video platforms (YouTube, Twitch)
- Developer sites (GitHub, StackOverflow)
- Ad networks
- Fully customizable

### ⚙️ Auto-Resume
- Automatically detects previous crawl
- Resumes from exact stopping point
- Skips already-found domains
- Perfect for long crawls

---

## 🖥️ System Requirements

### Minimum
| Component | Requirement |
|-----------|-------------|
| Python | 3.8+ |
| RAM | 2GB |
| Disk | 500MB free |
| Internet | Stable connection |
| OS | Windows/macOS/Linux |

### Recommended
| Component | Recommendation |
|-----------|-----------------|
| Python | 3.11+ |
| RAM | 8GB+ |
| Disk | 10GB+ |
| CPU | 4+ cores |
| Internet | High-speed |

---

## 📦 Installation

### 1. Get the Code
```bash
git clone https://github.com/yourusername/deepweber.git
cd deepweber
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install requests beautifulsoup4 aiohttp tqdm psutil
```

### 3. Verify Setup
```bash
python main.py --help
```

---

## 📖 Usage Guide

### Command Format
```bash
python main.py <seed_url> [OPTIONS]
```

### Options
```
--mode {sync,async}    sync (stable) or async (fast)
--unlimited            Remove domain limit
--help                 Show help
```

### Examples

#### Basic Crawl (Recommended Start)
```bash
python main.py https://example.com
```
- Sync mode (stable)
- 500 domain limit
- 5 depth levels
- Perfect for testing

#### Fast Async Crawl
```bash
python main.py https://example.com --mode async
```
- 2-3x faster
- 500 domain limit
- Good for production

#### Deep Research
```bash
python main.py https://example.com --mode async --unlimited
```
- Async speed
- No domain limit
- 30 depth levels
- ⚠️ May run for hours

#### Large Scale Crawl
```bash
python main.py https://example.com --unlimited
```
- Stable sync mode
- No domain limit
- Deep exploration
- Best stability

### Mode Comparison

| Aspect | Sync | Async |
|--------|------|-------|
| Speed | 10-20 URLs/sec | 25-50 URLs/sec |
| Memory | Low | Moderate |
| Stability | Excellent | Good |
| Best For | Testing | Production |

### Real-World Examples

```bash
# Tech site crawl
python main.py https://github.com --mode async

# Wikipedia research
python main.py https://wikipedia.org --mode async

# Large scale (hours)
python main.py https://google.com --mode async --unlimited

# Resume previous
python main.py https://example.com
```

---

## 📊 Output Files

### 1. `domains.json` - Discovered Domains

Updated in real-time as domains are found.

**Structure:**
```json
[
  {
    "id": 1,
    "domain": "google.com",
    "server": "gws"
  },
  {
    "id": 2,
    "domain": "example.com",
    "server": "nginx"
  }
]
```

**Fields:**
| Field | Type | Example |
|-------|------|---------|
| id | Integer | 1 |
| domain | String | google.com |
| server | String | nginx |

---

### 2. `log.json` - Crawl Statistics

Updated every 10 URLs, final report at completion.

**Structure:**
```json
{
  "timestamp_start": "2026-01-24T14:30:00Z",
  "timestamp_end": "2026-01-24T14:45:30Z",
  "timestamp_last_update": "2026-01-24T14:45:30Z",
  "mode": "async",
  "unlimited": false,
  "status": "completed",
  "urls_crawled": 150,
  "unique_domains": 127,
  "errors": 5,
  "memory_mb": "245.32",
  "total_elapsed_seconds": 930.50,
  "avg_crawl_rate_urls_per_sec": 0.16,
  "summary": {
    "total_domains": 127,
    "total_base_domains": 89,
    "total_subdomains": 38,
    "top_servers": {
      "nginx": 45,
      "Apache": 32,
      "gws": 15
    },
    "top_domains": ["google.com", "example.com"]
  }
}
```

**Key Metrics:**
| Metric | Meaning |
|--------|---------|
| timestamp_start | When crawl started (UTC) |
| timestamp_end | When crawl finished (UTC) |
| urls_crawled | Total URLs processed |
| unique_domains | Distinct domains found |
| errors | Number of failures |
| memory_mb | Peak memory used |
| total_elapsed_seconds | Total time taken |
| avg_crawl_rate_urls_per_sec | Speed (URLs/second) |

---

### 3. `errors.json` - Error Tracking

Detailed errors for debugging.

**Structure:**
```json
[
  {
    "timestamp": "2026-01-24T14:31:15Z",
    "url": "https://example.com",
    "error_type": "timeout",
    "error_message": "Connection timeout after 15s",
    "location": "sync_crawler.fetch",
    "context": "Third-party resource"
  }
]
```

**Error Types:**
| Type | Cause | Solution |
|------|-------|----------|
| timeout | Connection too slow | Legitimate slow server |
| connection_error | Can't reach host | Check domain exists |
| http_error | Server error (4xx/5xx) | Site blocks crawlers |
| parse_error | Bad HTML | Unusual format |
| memory_error | Out of memory | Reduce batch size |

---

## ⚙️ Configuration

### Auto-Resume

Crawler automatically continues previous crawls:

```bash
# First run - discovers domains
python main.py https://example.com
# Stops at 500 domains

# Second run - continues from 501
python main.py https://example.com --unlimited
# Continues discovering
```

**To start fresh:**
```bash
# Windows
del domains.json log.json errors.json

# macOS/Linux
rm domains.json log.json errors.json
```

### Customize Settings

Edit `main.py` configuration section:

```python
# Memory
MEMORY_LIMIT_MB = 8000           # 8GB
MEMORY_LIMIT_SSD_MB = 10240      # 10GB cache

# Processing
BATCH_SIZE = 500                 # Links per batch
LOG_FLUSH_INTERVAL = 10          # Update log every N URLs
THREADS = 64                     # Parallel threads
TIMEOUT = 15                     # Seconds per domain

# Limits
MAX_DOMAINS_DEFAULT = 5000
MAX_DEPTH = 15                   # Standard depth
MAX_DEPTH_UNLIMITED = 30         # Unlimited mode
```

### Customize Blacklist

Add unwanted domains to skip:

```python
DOMAIN_BLACKLIST = {
    "facebook.com",
    "instagram.com",
    "tiktok.com",
    "twitter.com",
    # Add your own:
    "mycompetitor.com",
    "unwanted.com",
}
```

### Skip File Extensions

Edit `SKIP_EXTENSIONS`:

```python
SKIP_EXTENSIONS = {
    ".pdf", ".zip", ".exe",
    ".jpg", ".png", ".mp4",
    ".doc", ".docx", ".xlsx",
}
```

---

## 📈 Performance Tuning

### Optimize for Speed

```bash
# Use async mode (2-3x faster)
python main.py https://example.com --mode async

# Increase threads
# Edit: THREADS = 128

# Use unlimited mode
python main.py https://example.com --mode async --unlimited
```

### Optimize for Stability

```bash
# Use sync mode
python main.py https://example.com

# Reduce batch size
# Edit: BATCH_SIZE = 50

# Increase timeout
# Edit: TIMEOUT = 30
```

### Monitor Performance

```bash
# Watch log.json during crawl
# Check: urls_crawled, memory_mb, avg_crawl_rate_urls_per_sec
```

### Performance Benchmarks

Expected performance (Intel i7, 16GB RAM):

| Mode | Configuration | Speed |
|------|---------------|-------|
| Sync | Default | 10-20 URLs/sec |
| Sync | Unlimited | 8-15 URLs/sec |
| Async | Default | 25-50 URLs/sec |
| Async | Unlimited | 20-40 URLs/sec |

*Actual speeds vary by internet, target sites, hardware.*

---

## 🛡️ Safety & Security

### Built-In Protections

**Loop Prevention:**
- URL deduplication
- Domain deduplication
- Subdomain loop detection
- Depth limits

**Resource Limits:**
| Resource | Limit | Purpose |
|----------|-------|---------|
| Memory | 8GB | Prevents exhaustion |
| HTML Size | 2MB | Prevents huge downloads |
| Links | 200/page | Prevents overflow |
| Timeout | 15s | Prevents hanging |
| Retries | 3 | Graceful failures |

### Ethical Guidelines

✅ **DO:**
- Check site's `robots.txt`
- Read terms of service
- Use for legitimate purposes
- Run during off-peak hours
- Cache and reuse results
- Set proper User-Agent

❌ **DON'T:**
- Crawl sites that prohibit it
- Bypass authentication
- Extract personal data
- Use for spam
- Overwhelm servers
- Ignore robots.txt

### Privacy

The crawler:
- ✅ Only processes headers
- ✅ Respects robots.txt
- ✅ No form data captured
- ✅ No JavaScript execution
- ✅ No tracking cookies

---

## 🔧 Troubleshooting

### Exit Code 1

**Cause:** Invalid URL or network issue

**Fix:**
```bash
# Verify URL is valid
python main.py https://google.com

# Check internet
ping google.com

# Try different URL
python main.py https://example.com
```

### Out of Memory

**Cause:** `--unlimited` on weak hardware

**Fix:**
```bash
# Use sync mode (less memory)
python main.py https://example.com --mode sync

# Reduce batch size
# Edit: BATCH_SIZE = 50

# Upgrade to 16GB+ RAM
```

### Not Resuming

**Cause:** `domains.json` missing

**Fix:**
```bash
# Check file exists
ls domains.json  # macOS/Linux
dir domains.json # Windows

# If missing, start fresh
python main.py https://example.com
```

### Slow Crawling

**Cause:** Network latency or sync mode

**Fix:**
```bash
# Use async mode (2-3x faster)
python main.py https://example.com --mode async

# Check internet speed (speedtest.net)

# Increase threads
# Edit: THREADS = 128
```

### Few Domains Found

**Cause:** Aggressive blacklist or limited links

**Fix:**
```bash
# Review DOMAIN_BLACKLIST (may be too strict)

# Try different seed URL
python main.py https://github.com --mode async

# Enable unlimited
python main.py https://example.com --unlimited

# Increase depth
# Edit: MAX_DEPTH_UNLIMITED = 40
```

### Debug Checklist

- [ ] Python 3.8+ (`python --version`)
- [ ] Dependencies installed (`pip list | grep requests`)
- [ ] URL is valid and accessible
- [ ] Internet connection works
- [ ] 500MB+ free disk space
- [ ] No antivirus blocking
- [ ] Target domain not totally blocking crawlers
- [ ] Log files are valid JSON

---

## 🌍 Real-World Examples

### Example 1: LLM Training Dataset

```bash
# Crawl tech site (hours)
python main.py https://github.com --mode async --unlimited

# Results in domains.json
# Import to ML pipeline
# Use for training data
```

### Example 2: Infrastructure Analysis

```bash
python main.py https://github.com --mode async

# Check log.json:
# - top_servers: Nginx dominates
# - top_domains: Linked patterns
# - crawl_rate: Speed insights
```

### Example 3: Competitive Research

```bash
# Crawl competitor 1
python main.py https://competitor1.com --unlimited

# Crawl competitor 2
python main.py https://competitor2.com --unlimited

# Analyze domains.json:
# - Shared infrastructure
# - Partner networks
# - Technology patterns
```

### Example 4: Subdomain Discovery

```bash
python main.py https://company.com --mode async --unlimited

# Results show:
# - api.company.com
# - blog.company.com
# - support.company.com
# - etc.
```

---

## ❓ FAQ

**Q: Is this legal?**
A: Crawling public content is legal if ethical. Check terms of service, respect robots.txt, use for legitimate purposes.

**Q: What's the difference between domains and unique domains?**
A: Domains = total count, Unique = distinct only, Base = root domains (example.com), Subdomains = sub-level.

**Q: Can I run multiple crawls simultaneously?**
A: Not recommended - consumes resources. Better to run sequentially or use different seed domains.

**Q: How do I combine multiple crawls?**
A:
```python
import json
domains_list = []
for file in ['domains1.json', 'domains2.json']:
    with open(file, 'r') as f:
        domains_list.extend(json.load(f))
# Deduplicate and save
```

**Q: What if I stop mid-crawl?**
A: Progress saved to domains.json. Next run resumes automatically. No data lost.

**Q: Can I customize output?**
A: Yes! Edit main.py to modify domains.json structure and logging details.

**Q: How much disk space needed?**
A: Small (500) ≈ 50KB, Medium (10K) ≈ 500KB, Large (100K+) ≈ 5MB.

**Q: Is async always better?**
A: No. Async = faster, Sync = more stable. Choose based on needs.

**Q: Can I see real-time progress?**
A: Yes! Watch log.json during crawl - updates every 10 URLs.

---

## 🤝 Contributing

### Report Bugs
1. Verify bug exists
2. Provide reproduction steps
3. Include error messages
4. Mention Python version and OS

### Suggest Features
1. Open issue with description
2. Explain use case
3. Discuss implementation

### Contribute Code
```bash
# Fork and clone
git clone https://github.com/yourusername/deepweber.git
cd deepweber

# Create branch
git checkout -b feature/my-feature

# Make changes and test

# Commit
git commit -m "Add feature: description"

# Push
git push origin feature/my-feature

# Open Pull Request
```

---

## 📄 License

**MIT License** - Use freely for research and training purposes

Copyright (c) 2026 DEEPWEBER Contributors

---

## 📞 Support

- **Issues**: Open a GitHub issue
- **Questions**: Check FAQ above
- **Contributions**: Submit pull requests
- **Feedback**: Always welcome

---

## 🎓 Best Practices

### ✅ DO:
- Use for LLM training
- Analyze domain patterns
- Study web infrastructure
- Build domain databases
- Academic research

### ❌ DON'T:
- Scrape personal data
- Bypass authentication
- Violate terms of service
- Create spam lists
- Malicious activities

---

## 🚀 Quick Reference

```bash
# Basic crawl
python main.py https://example.com

# Fast async
python main.py https://example.com --mode async

# Deep research
python main.py https://example.com --mode async --unlimited

# Start fresh
del domains.json log.json errors.json  # Windows
rm domains.json log.json errors.json   # macOS/Linux

# Resume
python main.py https://example.com

# Help
python main.py --help
```

---

**Built with ❤️ for AI research and domain intelligence**

**Version:** 2.1.0 | **Python:** 3.8+ | **Status:** Production Ready | **Updated:** January 24, 2026
