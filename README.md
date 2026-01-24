# DEEPWEBER, A Global Domain Crawler

> **Discover real-world domains at scale.** A powerful web crawler designed to collect live domain data for training machine learning models with authentic web infrastructure information.

---

## 📑 Table of Contents

- [What is This?](#-what-is-this)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Output Files](#-output-files)
- [Advanced Configuration](#-advanced-configuration)
- [Safety & Protection](#-safety--protection)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## 🎯 What is This?

A specialized **web crawler and domain discovery engine** built for:

- 🤖 **LLM Training** - Collect real-world domain data for machine learning datasets
- 📊 **Domain Analysis** - Research web infrastructure and hosting patterns
- 🔍 **Web Discovery** - Systematically explore domain relationships
- 🏗️ **Dataset Building** - Generate clean, structured domain databases

**Why use this?**
- ✅ Automatically resumes from previous crawls
- ✅ Detects server software (nginx, Apache, CloudFlare, etc.)
- ✅ Prevents infinite loops and duplicates
- ✅ Built-in safety limits and blacklisting
- ✅ Clean JSON output for data pipelines
- ✅ Fast async mode or stable sync mode
---

## ⚡ Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| 🔄 **Dual Processing Modes** | Sync (multithreaded) or Async (aiohttp) for optimal performance |
| 📝 **Smart Auto-Resume** | Automatically continues from last crawl state in `domains.json` |
| 🔍 **Server Detection** | Identifies nginx, Apache, CloudFlare, IIS, and 20+ server types |
| 🚫 **Loop Prevention** | Prevents duplicate URLs, domains, and subdomains |
| 🎯 **Blacklist Support** | Skip unwanted domains (social media, ads networks, etc.) |
| ⚙️ **Safety Limits** | Configurable depth (default: 5) and domain limits (default: 500) |
| ∞ **Unlimited Mode** | Optional unrestricted crawling with `--unlimited` flag |
| 📊 **Structured Output** | Clean JSON format ready for data pipelines |

---

## 🚀 Quick Start

### 1️⃣ Install Dependencies

```bash
pip install requests beautifulsoup4 aiohttp tqdm
```

### 2️⃣ Run Your First Crawl

```bash
python main.py https://example.com
```

That's it! The crawler will:
- Start from your seed URL
- Discover new domains automatically
- Save results to `domains.json` and `log.json`
- Resume from this point if run again

**Default configuration:**
| Setting | Value |
|---------|-------|
| Mode | Sync (stable, multithreaded) |
| Domain Limit | 500 |
| Max Depth | 5 |
| Resume | Enabled |

---

## 📖 Usage Guide

### Basic Commands

#### 🎯 Default (Recommended for starting)
```bash
python main.py https://example.com
```

#### ⚡ Async Mode (Faster)
```bash
python main.py https://example.com --mode async
```

#### 📈 Unlimited Crawling
```bash
python main.py https://example.com --unlimited
```

#### 🚀 Speed + Scale (Best for LLM training)
```bash
python main.py https://example.com --mode async --unlimited
```
I would recommend to start with a heavy domain like google.com to get the most out of the web.

### Mode Comparison

| Aspect | Sync | Async |
|--------|------|-------|
| **Speed** | 🟡 Moderate | 🟢 Fast |
| **Stability** | 🟢 Excellent | 🟡 Good |
| **Memory** | 🟢 Low | 🟡 Moderate |
| **Best For** | Testing, small crawls | Production, large datasets |

---

## 📤 Output Files

### `domains.json` 📋

**Live, growing list of discovered domains with metadata.**

```json
[
  {
    "id": 1,
    "domain": "google.com",
    "server": "gws"
  },
  {
    "id": 2,
    "domain": "wikipedia.org",
    "server": "Apache"
  }
]
```

**Updated in real-time after each new domain discovery.**

### `log.json` 📊

**Summary report generated at crawl completion.**

```json
{
  "timestamp": "2024-01-24T10:30:00Z",
  "mode": "async",
  "unlimited": false,
  "summary": {
    "total_domains": 500,
    "total_base_domains": 320,
    "total_subdomains": 180
  }
}
```

---

## 🔧 Advanced Configuration

### Auto-Resume from Previous Crawls

The crawler **automatically detects** `domains.json` and resumes:

```bash
# First crawl - discovers domains
python main.py https://example.com

# Second crawl - resumes automatically (skips already-discovered domains)
python main.py https://example.com
```

**To start fresh:**
```bash
del domains.json log.json
python main.py https://example.com
```

### Custom Domain Blacklist

Edit the `DOMAIN_BLACKLIST` in `main.py` to skip unwanted domains:

```python
DOMAIN_BLACKLIST = [
    'facebook.com',
    'instagram.com',
    'tiktok.com',
    'twitter.com',
    'youtube.com',
    'reddit.com',
    'linkedin.com',
    'github.com'
]
```

### Server Software Detection

The crawler automatically captures HTTP `Server` headers:

```
Server: nginx
Server: Apache/2.4.41
Server: cloudflare
Server: LiteSpeed
Server: Microsoft-IIS/10.0
Server: nginx/1.18.0
```

All results stored in `domains.json` for analysis and filtering.

---

## 🛡️ Safety & Protection

### Loop Prevention 🔁

The crawler intelligently prevents infinite loops by tracking:

- ✅ **URL Loops** - Never crawls the same URL twice
- ✅ **Domain Loops** - Never re-crawls the same domain
- ✅ **Subdomain Loops** - Prevents subdomain recursion
- ✅ **Depth Limits** - Stops at MAX_DEPTH to prevent rabbit holes

### Built-in Safety Limits ⚙️

| Limit | Default | Purpose |
|-------|---------|---------|
| `MAX_DEPTH` | 5 | Prevents infinite recursion into deep link structures |
| `MAX_DOMAINS` | 500 | Prevents accidental web-scale crawling (use `--unlimited` to override) |
| Timeout | 10s | Per-domain connection timeout |
| Retries | 3 | Automatic retry on network failures |

---

## 💡 Recommended Commands

### 🏃 **For Speed** (Recommended for LLM training)
```bash
python main.py https://example.com --mode async
```
Best for: Large-scale domain collection, machine learning datasets

### 🔬 **For Deep Research**
```bash
python main.py https://example.com --mode async --unlimited
```
Best for: Comprehensive domain analysis, research projects

### 🛡️ **For Stability** (Default)
```bash
python main.py https://example.com
```
Best for: Testing, small crawls, constrained environments

---

## 🔄 Reset / Start Over

To clear all progress and start fresh:

```bash
# Windows
del domains.json log.json

# Linux/Mac
rm domains.json log.json
```

Then run your command again - the crawler will start from scratch.

---

## 📊 Understanding Your Data

### `domains.json` Structure
| Field | Type | Example |
|-------|------|---------|
| `id` | Integer | `1` |
| `domain` | String | `"google.com"` |
| `server` | String | `"gws"` or `"Apache"` |

### `log.json` Structure
| Field | Type | Purpose |
|-------|------|---------|
| `timestamp` | ISO 8601 | When crawl completed |
| `mode` | String | `"sync"` or `"async"` |
| `unlimited` | Boolean | Whether domain limit was disabled |
| `summary.total_domains` | Integer | All discovered domains |
| `summary.total_base_domains` | Integer | Root domain count |
| `summary.total_subdomains` | Integer | Subdomain count |

---

## ⚙️ Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Exit code 1 | Network/URL issue | Check internet connection, verify URL is accessible |
| Out of memory | `--unlimited` on weak machine | Use standard mode with 500 limit, or upgrade hardware |
| Not resuming | Missing `domains.json` | File must be in working directory |
| Slow crawling | Network latency | Try `--mode async`, check your internet speed |
| Duplicate domains | Script interruption | Delete `domains.json` and restart |

### Debug Mode

Check your `log.json` for:
```json
{
  "timestamp": "...",
  "mode": "async",
  "unlimited": false,
  "summary": {
    "total_domains": 500,
    "total_base_domains": 320,
    "total_subdomains": 180
  }
}
```

If domains seem low, try:
1. Checking your blacklist isn't filtering too aggressively
2. Verifying the seed URL is accessible
3. Increasing domain limit with `--unlimited`
4. Trying `--mode async` for better performance

---

## 📝 License

MIT License - Use freely for research and training purposes

---

## 🤝 Contributing

Found a bug? Have an idea? We welcome contributions!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -m 'Add improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

---

## 📚 Use Cases

### Training Large Language Models
```bash
python main.py https://example.com --mode async --unlimited
# Results → `domains.json` → Training dataset
```

### Domain Infrastructure Research
```bash
python main.py https://example.com
# Analyze server distribution in `log.json`
```

### Building Domain Databases
```bash
python main.py https://seed1.com --unlimited
python main.py https://seed2.com --unlimited
# Combine domains.json files for larger dataset
```

---

## 🎓 Tips & Best Practices

✅ **DO:**
- Start with a seed URL in your target niche
- Use `--mode async` for faster crawling
- Regularly back up `domains.json` (it's your data!)
- Run during off-peak hours to reduce server load
- Respect `robots.txt` and terms of service

❌ **DON'T:**
- Use on sites that prohibit crawling
- Run with `--unlimited` without monitoring
- Share crawl results without attribution
- Crawl at extremely high speeds
- Ignore rate limiting indicators

---

**Built for LLM training and research**

---
New version update: # ✨ Advanced Domain Crawler - V2 Enhancements

## 🎯 Major Improvements Implemented

### 1. **Real-Time Incremental Logging** 📊
Your `log.json` now updates **as crawling progresses** instead of only at the end!

**Features:**
- ✅ Live progress tracking in `log.json`
- ✅ Flushes every 10 URLs crawled
- ✅ Shows current status: `crawling` → `completed`
- ✅ Real-time statistics:
  - URLs crawled so far
  - Unique domains discovered
  - Error count
  - Memory usage
  - Crawl rate (URLs/sec)
  - Elapsed time
- ✅ Top servers and domains list updates live
- ✅ Final completion summary with total time

**Sample incremental log.json:**
```json
{
  "timestamp_start": "2026-01-24T10:30:00Z",
  "timestamp_last_update": "2026-01-24T10:31:15Z",
  "status": "crawling",
  "urls_crawled": 250,
  "unique_domains": 82,
  "errors": 3,
  "memory_mb": "145.32",
  "elapsed_seconds": 75.5,
  "crawl_rate_urls_per_sec": 3.31,
  "top_servers": {
    "cloudflare": 45,
    "Apache": 28,
    "nginx": 15
  },
  "summary": {...}
}
```

### 2. **Vastly Improved Link Extraction** 🔗
Now extracts links from **8+ different sources** instead of just 3!

**Extraction Sources:**
- ✅ `href` attributes (a, link, area tags)
- ✅ `src` attributes (script, img, iframe, source)
- ✅ Meta tags (og:url, canonical, description, etc.)
- ✅ Form action URLs
- ✅ JSON-LD structured data (url, sameAs, image, logo)
- ✅ Event handlers (onclick, onload, data-url, data-href)
- ✅ Regex extraction from event handlers
- ✅ Multiple property extraction from tags

**Improvements:**
- 🔍 Finds 2-3x more links per page
- 🎯 Extracts from hidden/dynamic sources
- 📈 Up to 200 links per page (vs 100 before)

### 3. **Deeper Crawling Capability** 📈
Enhanced depth management for more thorough exploration!

**Depth Configuration:**
- Standard mode: 10 levels deep (was 5)
- Unlimited mode: 20 levels deep (was 15)
- Better for discovering nested domain structures
- Adaptive based on crawl type

### 4. **Safer & More Powerful** 🛡️⚡

**Enhanced Safety:**
- ✅ **Retry Logic**: 3 retry attempts per URL with exponential backoff
- ✅ **Better Error Handling**: Comprehensive exception catching
- ✅ **Status Code Validation**: Handles 200, 301, 302, 307, 308
- ✅ **Error Tracking**: Counts and logs errors in real-time
- ✅ **Timeout Management**: Better async timeout handling
- ✅ **HTML Size Limits**: 2MB per response (up from 1MB)
- ✅ **Connection Pooling**: Optimized for concurrent requests

**More Powerful:**
- ⚡ **Larger Thread Pool**: 32 threads (was 16)
- ⚡ **Adaptive Semaphores**: 150 for unlimited, 100 for standard async
- ⚡ **Larger Batch Size**: 100 links per batch (was 50)
- ⚡ **Better Concurrency**: More concurrent requests
- ⚡ **Improved Timeouts**: 15 second connection timeout
- ⚡ **2MB HTML limit**: Better data capture

### 5. **Complete Logging System** 📝

**What's Logged in Real-Time:**
```
[INFO] Configuration: mode=async, max_domains=500
[INFO] Memory limit: 2000MB, Batch size: 100
[INFO] Starting async domain crawl from: https://example.com
[INFO] Max domains: 500, Max depth: 20
...crawling progress updates...
[INFO] ✓ Crawling complete
[INFO] ✓ Domains saved to: domains.json
[INFO] ✓ Summary saved to: log.json
```

**Final log.json includes:**
- Start and end timestamps
- Total URLs crawled
- Total unique domains
- Error count
- Final memory usage
- Total elapsed time
- Average crawl rate
- Top 10 servers found
- Top 100 domains found
- Complete summary statistics

---

## 📊 Configuration Changes

```python
# Enhanced Configuration
MAX_DOMAINS_DEFAULT = 500        # Sensible default
MAX_DEPTH = 10                   # Deeper standard crawling
MAX_DEPTH_UNLIMITED = 20         # Much deeper exploration
TIMEOUT = 15                     # Longer timeout for reliability
THREADS = 32                     # More threads for power
BATCH_SIZE = 100                 # Larger batches
MEMORY_LIMIT_MB = 2000           # 2GB limit for power users
LOG_FLUSH_INTERVAL = 10          # Update log every 10 URLs
```

---

## 🔍 Advanced Link Extraction Example

The new extractor finds links from:

```html
<!-- Standard links -->
<a href="/page">Link</a>

<!-- Meta tags -->
<meta property="og:url" content="https://other-domain.com">

<!-- Form actions -->
<form action="https://submit.example.com">

<!-- JSON-LD data -->
<script type="application/ld+json">
{
  "url": "https://another-domain.com",
  "sameAs": "https://also-mentioned.com"
}
</script>

<!-- Event handlers -->
<div onclick="window.location='https://dynamic-domain.com'"></div>

<!-- Data attributes -->
<button data-url="https://api.example.com">Click</button>
```

All of these will now be discovered and crawled!

---

## ⏱️ Real-Time Logging Benefits

### During Crawl
You can now **monitor progress in real-time** by watching `log.json`:

```bash
# In another terminal while crawler is running:
watch -n 1 "cat log.json | jq '.elapsed_seconds, .urls_crawled, .unique_domains'"
```

### Early Stopping
Stop whenever you have enough domains - partial results are already saved!

### Progress Tracking
See live crawl rate, memory usage, and error count without waiting for completion.

---

## 🚀 Usage & Performance

### For Maximum Power
```bash
python main.py https://example.com --mode async --unlimited
# 20 levels deep, 2GB memory, 32 threads, real-time logging
```

### For Balanced Performance
```bash
python main.py https://example.com --mode async
# 10 levels deep, adaptive settings, real-time logging
```

### For Safe Exploration
```bash
python main.py https://example.com
# 10 levels, sync mode, detailed logging
```

---

## 📈 Performance Improvements

| Metric | Before | After | Gain |
|--------|--------|-------|------|
| Links Extracted | 100/page | 200/page | +100% |
| Extraction Sources | 3 | 8+ | +167% |
| Thread Count | 16 | 32 | +100% |
| Max Depth (std) | 5 | 10 | +100% |
| Max Depth (unlimited) | 15 | 20 | +33% |
| HTML Size Limit | 1MB | 2MB | +100% |
| Batch Size | 50 | 100 | +100% |
| Async Semaphore | 50-100 | 100-150 | +50% |
| Retry Attempts | 0 | 3 | Infinite |
| Logging | Final only | Real-time | Live! |

---

## 🛡️ Safety Features

### Retry Logic
- 3 automatic retries with exponential backoff
- Handles temporary failures gracefully
- Better reliability on unstable networks

### Error Tracking
- Real-time error counting
- Error details in logs
- Failed URLs tracked to prevent re-attempting

### Resource Management
- Memory monitoring every 50 URLs
- 2GB hard limit (configurable)
- Automatic garbage collection
- Batch processing prevents memory spikes

### Connection Safety
- Connection pooling with limits
- Per-host connection limits
- Proper timeout handling
- Status code validation (not just 200)

---

## 📁 Output Files

### domains.json
Same format, but now:
- ✅ Updated in real-time as domains are found
- ✅ Easier to work with while crawler is running
- ✅ Safe atomic writes

### log.json
**NEW**: Updated every 10 URLs with:
- Current crawl status
- URLs crawled so far
- Unique domains found
- Memory and CPU info
- Crawl rate statistics
- Top servers and domains
- Error count

---

## 🎓 Best Practices

### For LLM Training (Recommended)
```bash
python main.py https://example.com --mode async
# Then monitor progress:
watch -n 2 cat log.json | python -m json.tool
```

### For Deep Exploration
```bash
python main.py https://example.com --mode async --unlimited
# Good for comprehensive domain mapping
```

### For Restricted Systems
```bash
python main.py https://example.com
# Stable sync mode, good error messages
```

---

**This project is not finished yet so it will be updated soon this week for even better performance**

