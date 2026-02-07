# DEEPWEBER – Test Domain Crawler  
[![Status](https://img.shields.io/badge/Status-Ongoing-brightgreen)](#status)  [![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)  
![Demo](demo.gif)

**DEEPWEBER** is a lightweight, high-performance domain crawler designed to discover, verify, and analyze domains with minimal setup. It consolidates over 2000 lines of code into ~500 lines while maintaining modularity and reliability.

---

## 🚀 Quick Start

1. Install dependencies:  
```bash
pip install -r requirements.txt
```
2. Python main.py:  
```bash
python main.py
```
3. Open your browser at localhost 3000 or your IP:3000
   
### Progress of DEEPWEBER
| Category         | Capability                             | Status |
| ---------------- | -------------------------------------- | ------ |
| **Crawling**     | A–Z domain sweep                       | ⏳      |
|                  | Subdomain discovery                    | ⏳      |
|                  | Bruteforce (dictionary + permutations) | ⏳      |
|                  | Recursive link crawling (depth‑aware)  | ⏳      |
|                  | sitemap.xml & robots.txt parsing       | ⏳      |
|                  | URL normalization & canonicalization   | ✅      |
| **Verification** | Streaming domain verification          | ⏳      |
|                  | HTTP status detection                  | ✅      |
|                  | SSL/TLS validation                     | ⏳      |
|                  | Parked / expired domain detection      | ✅      |
|                  | Redirect chain analysis                | ⏳      |
|                  | MIME / content‑type detection          | ⏳      |
| **Safety**       | Adaptive rate limiting                 | ✅      |
|                  | Request timeout handling               | ✅      |
|                  | Exponential backoff retries            | ⏳      |
|                  | Robots.txt strict & permissive modes   | ⏳      |
|                  | Trap / honeypot detection              | ⏳      |
|                  | Blacklist / whitelist rules            | ✅      |
| **Networking**   | Proxy support                          | ⏳      |
|                  | TOR routing mode                       | ⏳      |
|                  | Header randomization                   | ⏳      |
|                  | IP randomization                       | ⏳      |
| **Performance**  | Multi‑threaded crawling                | ⏳      |
|                  | Async I/O pipeline                     | ✅      |
|                  | Queue‑based scheduler                  | ✅      |
|                  | Resume from checkpoints                | ✅      |
|                  | Distributed crawling                   | ⏳      |
| **Storage**      | JSON output                            | ⏳      |
|                  | Compressed output                      | ⏳      |
|                  | SQLite backend                         | ⏳      |
|                  | Append‑only logs                       | ⏳      |
| **Analysis**     | Content hashing                        | ⏳      |
|                  | Duplicate detection                    | ⏳      |
|                  | Keyword extraction                     | ⏳      |
|                  | Language detection                     | ⏳      |
|                  | Page classification                    | ⏳      |
|                  | Server fingerprinting                  | ⏳      |
| **DevX**         | CLI interface                          | ⏳      |
|                  | Modular documentation                  | ⬜      |

✅ Implemented   ⬜ Planned ⏳ Made but not published on current version
---
🔍 Features in Progress

Remote multi-server IP rotation with configurable intervals only local network works for now

Supported OS for remote nodes: Ubuntu only

🛠️ Next Steps

PDF & text data gathering

Fine-tuning phase 1

Basic next-word prediction from collected data

Fine-tuning phase 2
---
**Version:** 1.0.2 | **Python:** 3.8+ | **Updated:** 07 FEB 2026
