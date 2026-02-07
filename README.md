# DEEPWEBER - Test Domain Crawler [![Status](https://img.shields.io/badge/Status-Ongoing-brightgreen)](#status)


[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)

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
The current version is condenced from +2000 lines to just ~500 lines with better performance and verifies as you go no need for verify.py and can be lunched by directly: `python main.py`

Features in Progress:
  - Remote multi‑server IP rotation using multiple servers with variable intervals
  - Currently supported OS for remote nodes: Ubuntu only

Next steps:
  - PDF & Text data gathering system
  - Fine tuning 1
  - Basic next word prediction based on data gathered
  - Fine tuning 2
The docs are incomplete and will soon be changed.

![Demo](demo.gif)
---
**Version:** 1.0.2 | **Python:** 3.8+ | **Updated:** 31 JAN 2026
