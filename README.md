# DEEPWEBER - Global Domain Crawler [![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](#status)

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Memory](https://img.shields.io/badge/Memory-8GB-blue)](#system-requirements)
[![Threads](https://img.shields.io/badge/Threads-64-blue)](#features)

> **Discover real-world domains at scale.** High-performance web crawler for collecting live domain data and training machine learning models with authentic web infrastructure information.

---

## ✅ Minimum Requirements (MUST HAVE)

| Component | Minimum | Why |
|-----------|---------|-----|
| **Python** | **3.8+** | Core requirement, 3.13+ compatible |
| **RAM** | **2GB** | Sync mode works fine, async needs 4GB+ |
| **Disk Space** | **500MB free** | For cache, output files, temporary storage |
| **Internet** | **Stable connection** | Required for crawling |
| **OS** | **Windows/macOS/Linux** | Cross-platform support |

⚠️ **Can't proceed without these!** Everything else is optional/configurable.

---

## 🚀 FASTEST START (60 Seconds)

```bash
# 1. Install dependencies (30 seconds)
pip install -r requirements.txt

# 2. Run crawl (30 seconds)
python main.py https://example.com

# 3. Check results
type log.json    # Windows
cat log.json     # macOS/Linux
```

**Result:**
- ✅ `domains.json` - Discovered domains list
- ✅ `log.json` - Statistics and progress
- ✅ `errors.json` - Any errors encountered

**Run again to resume automatically!**

---

## 📦 Installation (3 Steps)

### Step 1: Install Python 3.8+
```bash
python --version
# Should show: Python 3.8.0 or higher
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Verify Setup
```bash
python main.py --help
```

**Done!** You're ready to crawl.

---

## 📚 Documentation Index

| Section | Purpose |
|---------|---------|
| [💡 What is DEEPWEBER?](#-what-is-deepweber) | Understand the tool |
| [⚡ Key Features](#-key-features) | All capabilities |
| [📖 Usage Guide](#-usage-guide) | How to use commands |
| [📊 Output Files](#-output-files) | What files are created |
| [⚙️ Configuration](#-configuration) | Customize behavior |
| [📈 Performance](#-performance-tuning) | Speed & optimization |
| [🛡️ Safety](#-safety--security) | Ethics & limits |
| [🔧 Troubleshooting](#-troubleshooting) | Fix issues |
| [🌍 Examples](#-real-world-examples) | Use cases |
| [❓ FAQ](#-faq) | Q&A |

---

## 💡 What is DEEPWEBER?

DEEPWEBER is a **web crawler** that:
- 🔍 **Discovers domains** by following links automatically
- 📊 **Collects metadata** (server info, URL structure)
- 💾 **Saves results** to easy-to-parse JSON files
- ⚡ **Works at scale** with smart memory management
- 🔄 **Auto-resumes** from previous crawls

### Perfect For:
| Task | Why DEEPWEBER |
|------|---------------|
| 🤖 LLM Training | Real domain datasets |
| 📊 Domain Research | Infrastructure analysis |
| 🏗️ Build Catalogs | Systematic discovery |
| 🔬 Study Hosting | Server distribution |

---

## ⚡ Key Features

### 🔄 Two Processing Modes
| Mode | Speed | Stability | Use When |
|------|-------|-----------|----------|
| **Sync** | Medium | ⭐⭐⭐⭐⭐ | Testing, learning |
| **Async** | 2-3x faster | ⭐⭐⭐⭐ | Production, large scale |

### 📝 Real-Time Updates
- ✅ Progress every 10 URLs
- ✅ Memory tracking
- ✅ Speed metrics (URLs/sec)
- ✅ Top servers found
- ✅ Top domains found
- ✅ Error counting

### 🔍 Smart Link Extraction
Extracts from: href, src, meta tags, forms, JSON-LD, event handlers, data attributes

### 🚫 Prevents Duplicates
- URL deduplication
- Domain deduplication
- Subdomain loop prevention
- Depth limits (5-30 levels)

### 💾 Memory Smart
- 8GB RAM limit (configurable)
- 10GB SSD cache
- 500 links per batch
- Automatic garbage collection

### 📊 Server Detection
Identifies 20+ server types: Nginx, Apache, CloudFlare, IIS, LiteSpeed, etc.

### ⚙️ Auto-Resume
- Saves progress automatically
- Resumes from exact stopping point
- No data loss if stopped mid-crawl

---

## 📖 Usage Guide

### Basic Syntax
```bash
python main.py <URL> [OPTIONS]
```

### Command Examples

#### 1️⃣ Start Simple (Recommended)
```bash
python main.py https://example.com
```
- Sync mode (stable)
- 500 domain limit
- Max 5 depth
- ~10-20 URLs/sec

#### 2️⃣ Faster Crawl
```bash
python main.py https://example.com --mode async
```
- Async mode
- 500 domain limit
- ~25-50 URLs/sec

#### 3️⃣ Deep Research
```bash
python main.py https://example.com --mode async --unlimited
```
- No domain limit
- Max 30 depth
- ⚠️ May take hours

#### 4️⃣ Stable Large Scale
```bash
python main.py https://example.com --unlimited
```
- Sync mode (more stable)
- No domain limit
- Best for stability

### Real Examples
```bash
python main.py https://github.com --mode async

python main.py https://wikipedia.org --mode async

python main.py https://google.com --mode async --unlimited
```

---

## 📊 Output Files

### 1. `domains.json` - List of Found Domains
```json
[
  {"id": 1, "domain": "google.com", "server": "gws"},
  {"id": 2, "domain": "example.com", "server": "nginx"},
  {"id": 3, "domain": "wikipedia.org", "server": "Apache"}
]
```

### 2. `log.json` - Statistics & Progress
```json
{
  "timestamp_start": "2026-01-24T14:30:00Z",
  "timestamp_end": "2026-01-24T14:45:30Z",
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
    "top_servers": {"nginx": 45, "Apache": 32, "gws": 15},
    "top_domains": ["google.com", "example.com"]
  }
}
```

### 3. `errors.json` - Error Log
```json
[
  {
    "timestamp": "2026-01-24T14:31:15Z",
    "url": "https://example.com",
    "error_type": "timeout",
    "error_message": "Connection timeout after 15s"
  }
]
```

---

## ⚙️ Configuration

### Auto-Resume (Automatic)
```bash
# First run
python main.py https://example.com
# Stops at 500 domains, saves to domains.json

# Second run - continues automatically!
python main.py https://example.com --unlimited
# Resumes from 501, skips already-found domains
```

### Start Fresh
```bash
# Windows
del domains.json log.json errors.json

# macOS/Linux
rm domains.json log.json errors.json

# Then run again
python main.py https://example.com
```

### Customize in main.py

```python
# Memory limits
MEMORY_LIMIT_MB = 8000           # 8GB (adjust to your system)
THREADS = 64                     # Parallel workers

# Batch processing
BATCH_SIZE = 500                 # Links per batch
TIMEOUT = 15                     # Seconds per domain

# Crawler limits
MAX_DEPTH = 15                   # Standard depth
MAX_DEPTH_UNLIMITED = 30         # Unlimited mode depth
```

### Custom Blacklist (Skip Domains)
```python
DOMAIN_BLACKLIST = {
    "facebook.com",
    "instagram.com",
    "tiktok.com",
    # Add your own:
    "unwanted.com",
}
```

---

## 📈 Performance Tuning

### For Speed
```bash
# 2-3x faster than sync
python main.py https://example.com --mode async

# Edit main.py: THREADS = 128 (if CPU available)
```

### For Stability
```bash
# Use sync mode
python main.py https://example.com

# Edit main.py: BATCH_SIZE = 50 (fewer concurrent)
```

### Monitor
```bash
# Watch log.json during crawl
# Metrics: urls_crawled, memory_mb, avg_crawl_rate_urls_per_sec
```

### Speed Benchmarks
| Mode | Expected |
|------|----------|
| Sync (default) | 10-20 URLs/sec |
| Sync (unlimited) | 8-15 URLs/sec |
| Async (default) | 25-50 URLs/sec |
| Async (unlimited) | 20-40 URLs/sec |

*Varies by internet, target sites, hardware.*

---

## 🛡️ Safety & Security

### Built-In Protections
- URL/domain deduplication
- Memory limits (8GB)
- HTML size limits (2MB/page)
- Connection timeout (15s)
- Automatic retries (3x)
- Depth limits (5-30)

### Ethical Use
✅ **DO:**
- Check `robots.txt`
- Read terms of service
- Use for legitimate purposes
- Run off-peak hours

❌ **DON'T:**
- Crawl sites that prohibit it
- Extract personal data
- Bypass authentication
- Overwhelm servers

### Privacy
- Only processes HTTP headers
- Respects robots.txt
- No form data captured
- No JavaScript execution

---

## 🔧 Troubleshooting

### Problem: Exit Code 1

```bash
# Solution: Verify URL and internet
python main.py https://google.com
ping google.com
```

### Problem: Out of Memory

```bash
# Use sync mode (less memory)
python main.py https://example.com --mode sync

# Or reduce batch size in main.py: BATCH_SIZE = 50
```

### Problem: Not Resuming

```bash
# Check if domains.json exists
dir domains.json  # Windows
ls domains.json   # macOS/Linux

# If missing, start fresh
python main.py https://example.com
```

### Problem: Slow Crawling

```bash
# Try async mode (2-3x faster)
python main.py https://example.com --mode async

# Or increase threads in main.py: THREADS = 128
```

### Problem: Few Domains Found

```bash
# Try different seed URL
python main.py https://github.com --mode async

# Or remove domain limit
python main.py https://example.com --unlimited
```

---

## 🌍 Real-World Examples

### Build LLM Training Data
```bash
python main.py https://github.com --mode async --unlimited
# Import domains.json into ML pipeline
```

### Analyze Infrastructure
```bash
python main.py https://github.com --mode async
# Check log.json for top_servers, patterns
```

### Competitive Research
```bash
python main.py https://competitor1.com --unlimited
python main.py https://competitor2.com --unlimited
# Compare domains.json files
```

### Find Subdomains
```bash
python main.py https://company.com --mode async --unlimited
# Results show: api.company.com, blog.company.com, etc.
```

---

## ❓ FAQ

**Q: Is crawling legal?**
A: Legal if done ethically - check ToS, respect robots.txt, use for legitimate purposes.

**Q: What's the difference between domains and unique domains?**
A: Domains = total, Unique = distinct only, Base = root only (example.com), Subdomains = sub-level.

**Q: Can I run multiple crawls?**
A: Yes sequentially, but not recommended simultaneously (resource intensive).

**Q: What if I stop mid-crawl?**
A: Progress saved. Next run resumes automatically. No data lost.

**Q: How much disk space?**
A: 500 domains ≈ 50KB, 10K ≈ 500KB, 100K+ ≈ 5MB.

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

### Contribute Code
```bash
git clone https://github.com/Site123456/deepweber.git
cd deepweber
git checkout -b feature/my-feature
# Make changes, test
git commit -m "Add feature: description"
git push origin feature/my-feature
```

---

## 📄 License
 - Use freely for research and training

---

## 🚀 Quick Reference

```bash
# Start here
python main.py https://example.com

# Faster
python main.py https://example.com --mode async

# Deep crawl
python main.py https://example.com --mode async --unlimited

# Start fresh
del domains.json log.json errors.json  # Windows
rm domains.json log.json errors.json   # macOS/Linux

# Help
python main.py --help
```

---

**Built with ❤️ for AI research and domain intelligence**

**Version:** 1.0.1 | **Python:** 3.8+ | **Updated:** 24/01/2026

