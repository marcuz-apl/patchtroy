# 🛡️ Playtrafi

**The undetected stealth web scraper & clean Markdown extractor for LLMs and AI pipelines.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Engine: Patchright](https://img.shields.io/badge/Stealth%20Engine-Patchright-orange)](https://github.com/kaliiiiiiiiii/patchright)
[![Extractor: Trafilatura](https://img.shields.io/badge/Extraction-Trafilatura-green)](https://github.com/adbar/trafilatura)
[![Documentation](https://img.shields.io/badge/docs-Material_for_MkDocs-teal.svg)](https://marcuz-apl.github.io/playtrafi)

---

## ⚡ What is Playtrafi?

**Playtrafi** (formerly *Patchtroy*) is a lightweight, high-performance web crawling and content extraction engine designed specifically for LLMs, RAG pipelines, and AI agents.

It bridges the gap between low-level drivers and high-level scrapers by pairing **Patchright** (the C++ patched Chromium engine that eliminates automated telemetry leakages) with **Trafilatura** (the gold standard for algorithmic boilerplate removal and pristine Markdown conversion).

### 🎯 Why Playtrafi vs Crawl4AI & Firecrawl?

| Feature | Crawl4AI | Firecrawl (Self-hosted) | **Playtrafi** |
| :--- | :---: | :---: | :---: |
| **Stealth Engine** | ❌ Standard Playwright (telemetry leaked) | ❌ Blocked unless using paid SaaS | **✅ Native Patchright Stealth** |
| **Boilerplate Stripping** | ⚠️ Heuristic regex | ✅ Full DOM clean | **✅ Trafilatura Gold Standard** |
| **Framework Data** | ⚠️ Partial regex | ✅ | **✅ Native Next.js (`__NEXT_DATA__`) & Schema.org JSON-LD** |
| **Dependencies** | ❌ Heavy (PyTorch, Transformers, ML) | ❌ Complex (Node, Redis, BullMQ) | **✅ Ultra-lean (< 15MB pure Python)** |
| **Throughput** | ⚠️ Process-level restart | ⚠️ Queue bottleneck | **✅ Browser Context Pool (>5x throughput)** |
| **Failure Tolerance** | ❌ Crashes on timeout | ❌ | **✅ Automatic fast HTTP fallback** |

---

## 📦 Installation

```bash
pip install playtrafi

# Install stealth Chromium driver
patchright install chromium
```

> **Note on Backwards Compatibility:** `patchtroy` remains available as an import and CLI alias during the migration deprecation window.

---

## 🚀 Quickstart

### Python (Async API)

```python
import asyncio
from playtrafi import AsyncPlaytrafi

async def main():
    async with AsyncPlaytrafi() as client:
        result = await client.scrape("https://news.ycombinator.com")
        print("Title:", result.title)
        print("Markdown:\n", result.markdown[:300])

async def_run():
    asyncio.run(main())
```

### Python (Sync 1-Liner)

```python
from playtrafi import Playtrafi

result = Playtrafi.crawl("https://en.wikipedia.org/wiki/Web_scraping")
print(result.markdown[:300])
```

### CLI

```bash
# Scrape clean Markdown directly to stdout
playtrafi https://news.ycombinator.com

# Save to Markdown, CSV, or JSON (auto-detected from file extension)
playtrafi https://example.com -o output.md
playtrafi https://example.com -o output.csv
playtrafi https://example.com -f json -o output.json
```

---

## 🧩 Core Architecture Highlights

- **🛡️ Native Stealth Engine**: Runs on Patchright's patched C++ Chromium binary, eliminating internal debugging flags and CDP telemetry before page scripts execute.
- **🧹 Algorithmic Content Cleaning**: Trafilatura strips 96%+ of navigation menus, advertisements, and tracking noise while preserving tables, code snippets, and Markdown formatting.
- **⚡ Browser Context Pool**: Reuses a single background browser process across requests, leasing isolated browser contexts for >5x higher throughput and lower RAM usage.
- **🧠 Structure-Aware LLM Chunking**: Recursively splits Markdown documents along heading hierarchy (`#`, `##`, `###`) with token estimation and metadata tracking.
- **🐳 Standalone REST Microservice**: Single lightweight Docker container exposing `/scrape`, `/scrape/batch`, and `/health` on port 4013 for any programming language.

---

## 📖 Documentation

Full documentation, API references, architecture guides, and benchmarks are available at the **[Playtrafi Documentation Portal](https://marcuz-apl.github.io/playtrafi)**:

- [Getting Started Guide](https://marcuz-apl.github.io/playtrafi/getting-started/)
- [Stealth Architecture Deep Dive](https://marcuz-apl.github.io/playtrafi/stealth-architecture/)
- [Context Pooling & Concurrency](https://marcuz-apl.github.io/playtrafi/context-pool/)
- [Media Capture (Screenshots & PDFs)](https://marcuz-apl.github.io/playtrafi/media-capture/)
- [Proxy Rotation & Fault Quarantine](https://marcuz-apl.github.io/playtrafi/proxy-rotation/)
- [LLM Chunking & Tokenizer](https://marcuz-apl.github.io/playtrafi/llm-chunking/)
- [REST API Microservice & Docker](https://marcuz-apl.github.io/playtrafi/rest-api/)
- [Benchmark Results vs Crawl4AI & Firecrawl](https://marcuz-apl.github.io/playtrafi/benchmarks/)
- [Rebranding Guide](https://marcuz-apl.github.io/playtrafi/rebranding-guide/)

---

## 📄 License

Playtrafi is open-source software created by [@marcuz-apl](https://github.com/marcuz-apl) and maintained by **Alfazen Inc.**, released under the **[Apache 2.0 License](LICENSE)**.
