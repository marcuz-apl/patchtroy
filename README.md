# 🛡️ Patchtroy

**The undetected stealth web scraper & clean Markdown extractor for LLMs and AI pipelines.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Engine: Patchright](https://img.shields.io/badge/Stealth%20Engine-Patchright-orange)](https://github.com/kaliiiiiiiiii/patchright)
[![Extractor: Trafilatura](https://img.shields.io/badge/Extraction-Trafilatura-green)](https://github.com/adbar/trafilatura)

---

## ⚡ What is Patchtroy?

**Patchtroy** is a lightweight, high-performance web crawling and content extraction engine designed specifically for LLMs, RAG pipelines, and automated intelligence gathering.

It bridges the gap between low-level stealth drivers and high-level scrapers by pairing **Patchright** (the undetected Playwright fork that evades Cloudflare, DataDome, and PerimeterX CDP leaks) with **Trafilatura** (the gold standard for algorithmic boilerplate removal and pristine Markdown conversion).

### 🎯 Why Patchtroy vs Crawl4AI & Firecrawl?

| Feature | Crawl4AI | Firecrawl (Self-hosted) | **Patchtroy** |
| :--- | :---: | :---: | :---: |
| **Stealth Anti-Bot** | ❌ Standard Playwright (CDP leaked) | ❌ Blocked unless using paid SaaS | **✅ Native Patchright Stealth** |
| **Boilerplate Stripping** | ⚠️ Heuristic regex | ✅ Full DOM clean | **✅ Trafilatura Gold Standard** |
| **Framework Data** | ⚠️ Partial regex | ✅ | **✅ Native Next.js (`__NEXT_DATA__`) & Schema.org JSON-LD** |
| **Dependencies** | ❌ Heavy (PyTorch, Transformers, ML) | ❌ Complex (Node, Redis, BullMQ) | **✅ Ultra-lean (< 15MB pure Python)** |
| **Failure Tolerance** | ❌ Crashes on timeout | ❌ | **✅ Automatic fast HTTP fallback** |

---

## 📦 Installation

```bash
pip install patchtroy

# Install stealth Chromium driver
patchright install chromium
```

---

## 🚀 Quick Start

### 1. Asynchronous Python API (Recommended)

```python
import asyncio
from patchtroy import AsyncPatchtroy

async def main():
    async with AsyncPatchtroy() as client:
        result = await client.scrape(
            "https://news.ycombinator.com",
            wait_for="tr.athing",
        )
        print("Title:", result.title)
        print("Markdown Preview:
", result.markdown[:500])
        print("Links Found:", len(result.links))

asyncio.run(main())
```

### 2. Synchronous One-Liner

```python
from patchtroy import Patchtroy

# 1-line instant crawl
result = Patchtroy.crawl("https://en.wikipedia.org/wiki/Web_scraping")
print(result.markdown)
```

### 3. Extract Next.js embedded data & Schema.org JSON-LD

```python
from patchtroy import Patchtroy

result = Patchtroy.crawl("https://any-ecommerce-or-nextjs-site.com")

# Native structured data records
for item in result.structured_data:
    print(item)
```

### 4. Custom Declarative CSS Extraction

```python
from patchtroy import Patchtroy

schema = {
    "item_selector": "article.card",
    "fields": {
        "headline": "h2.title",
        "author": "span.byline",
        "date": "time",
    }
}

result = Patchtroy.crawl("https://blog.example.com", custom_schema=schema)
for article in result.structured_data:
    print(article["headline"], "by", article["author"])
```

### 5. High-Throughput Batch Crawling & Context Pool

```python
from patchtroy import Patchtroy

urls = [
    "https://news.ycombinator.com",
    "https://github.com/trending",
    "https://lobste.rs",
]

# Reuses a single browser process with isolated pooled contexts (>5x faster)
results = Patchtroy.crawl_many(urls, max_concurrency=5)
for res in results:
    print(res.url, "->", res.title, f"({len(res.markdown)} chars)")
```

### 6. Screenshots & PDF Generation

```python
from patchtroy import Patchtroy

# Capture screenshot & PDF in a single scrape
result = Patchtroy.crawl("https://example.com", screenshot=True, pdf=True)

# Save media files to disk
result.save_screenshot("screenshot.png")
result.save_pdf("document.pdf")
```

### 7. Proxy Rotation Manager

```python
from patchtroy import AsyncPatchtroy, PatchtroyConfig

# Automatic round-robin rotation with quarantine on failure
config = PatchtroyConfig(
    proxies=["http://user:pass@proxy1:8080", "http://user:pass@proxy2:8080"],
    proxy_strategy="round-robin",  # or "random"
)

async with AsyncPatchtroy(config) as client:
    result = await client.scrape("https://example.com")
```

### 8. LLM Token Counting & Markdown Chunking

Prepare crawled web content directly for RAG pipelines and vector stores:

```python
from patchtroy import Patchtroy

result = Patchtroy.crawl("https://en.wikipedia.org/wiki/Artificial_intelligence")

# Split into coherent, structure-preserving Markdown chunks (hierarchically splits by headings)
chunks = result.chunk(max_tokens=1024, overlap_tokens=100)

for chunk in chunks:
    print(f"Chunk #{chunk.chunk_index} ({chunk.token_count} tokens):")
    print("Section:", chunk.metadata.get("section_heading"))
    print(chunk.text[:200], "\n---\n")
```

### 9. REST API Microservice (FastAPI)

Launch Patchtroy as a standalone microservice for non-Python applications (Node.js, Go, Rust, Ruby):

```bash
# Start microservice on port 8000
patchtroy serve --port 8000
```

#### Scrape Endpoint
```bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://news.ycombinator.com", "screenshot": true}'
```

#### Batch Scrape Endpoint
```bash
curl -X POST http://localhost:8000/scrape/batch \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://site1.com", "https://site2.com"], "concurrency": 5}'
```

---

## 🐳 Docker Deployment

Run Patchtroy as a self-hosted microservice with zero local dependencies:

```bash
# Pull and run with Docker
docker run -d -p 8000:8000 --name patchtroy marcuszou/patchtroy:latest

# Or launch with Docker Compose
docker compose up -d
```

---

## 💻 CLI Usage

```bash
# Scrape to Markdown (prints to stdout)
patchtroy https://news.ycombinator.com

# Save to output file
patchtroy https://example.com -o output.md

# Save complete JSON payload (markdown + metadata + structured items)
patchtroy https://example.com -f json -o output.json

# Capture viewport screenshot and PDF export
patchtroy https://example.com --screenshot page.png --pdf document.pdf

# Full-page screenshot
patchtroy https://example.com --screenshot full.png --full-page

# Batch scraping multiple URLs with proxy rotation and concurrency
patchtroy https://site1.com https://site2.com --proxy-file proxies.txt -c 5 -o batch_out.md

# Start REST API microservice
patchtroy serve --host 0.0.0.0 --port 8000
```

---

## 🛡️ Anti-Bot Evasion Architecture

Most headless browsers get detected by modern anti-bot systems (Cloudflare Turnstile, DataDome, Akamai) due to **Chrome DevTools Protocol (CDP) leakages**:
- Standard Playwright injects `Runtime.enable` which triggers bot detection hooks.
- `navigator.webdriver` is set to `true`.
- Chrome runtime objects and plugins are missing or malformed.

Patchtroy eliminates these detection vectors by:
1. Running on **Patchright**, which patches the C++ Chromium binary to remove CDP telemetry.
2. Injecting custom stealth runtime mocks (`navigator.webdriver`, `window.chrome.runtime`, realistic plugin lists).
3. Utilizing randomized modern desktop User-Agents.
4. Supporting automatic HTTP fallback when headless browser rendering is unnecessary or rate-limited.

---

## 📄 License

MIT License © 2026 Marcus Zou / Patchtroy Authors.
