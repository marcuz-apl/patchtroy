# Getting Started with Playtrafi

A complete developer guide to installing, configuring, and deploying **Playtrafi** across Python applications, CLI pipelines, and microservices.

---

## 📦 Installation

Install Playtrafi from PyPI:

```bash
pip install playtrafi

# Install patched Chromium browser binaries
patchright install chromium
```

### Optional Dependency Groups

| Group | Install Command | Use Case |
| :--- | :--- | :--- |
| **Microservice** | `pip install "playtrafi[server]"` | FastAPI REST server and Uvicorn runner |
| **Documentation** | `pip install "playtrafi[docs]"` | Material for MkDocs documentation portal |
| **Development** | `pip install "playtrafi[dev]"` | Pytest, async test plugins, and Ruff linter |
| **All** | `pip install "playtrafi[all]"` | Full installation of all features |

---

## 🐍 Python Quickstart

### 1. Asynchronous API (Recommended)

```python
import asyncio
from playtrafi import AsyncPlaytrafi, PlaytrafiConfig

async def main():
    config = PlaytrafiConfig(
        headless=True,
        browser_timeout_s=15.0,
        wait_for="tr.athing",
    )

    async with AsyncPlaytrafi(config) as client:
        result = await client.scrape("https://news.ycombinator.com")
        print("Title:", result.title)
        print("Markdown Preview:\n", result.markdown[:400])
        print("Discovered Links:", len(result.links))

asyncio.run(main())
```

### 2. Synchronous One-Liner

```python
from playtrafi import Playtrafi

result = Playtrafi.crawl("https://en.wikipedia.org/wiki/Web_scraping")
if result.success:
    print(f"# {result.title}\n")
    print(result.markdown)
```

---

## 🎯 Advanced Extraction Workflows

### 3. Extract Next.js Data (`__NEXT_DATA__`) & Schema.org JSON-LD

Dynamic Single Page Applications often embed pristine JSON payloads in hydration tags. Playtrafi parses these automatically into structured records:

```python
from playtrafi import Playtrafi

result = Playtrafi.crawl("https://example.com/product/123")

for item in result.structured_data:
    print(item)
```

### 4. Custom Declarative CSS Extraction

Extract typed, structured fields alongside the article body:

```python
from playtrafi import Playtrafi

schema = {
    "item_selector": "article.card",
    "fields": {
        "headline": "h2.title",
        "author": "span.byline",
        "date": "time",
    }
}

result = Playtrafi.crawl("https://blog.example.com", custom_schema=schema)
for article in result.structured_data:
    print(article["headline"], "by", article["author"])
```

### 5. High-Throughput Batch Crawling (`crawl_many`)

Scrape dozens of URLs concurrently by leasing isolated browser contexts from a shared browser instance (>5x faster than spawning fresh processes):

```python
from playtrafi import Playtrafi

urls = [
    "https://news.ycombinator.com",
    "https://github.com/trending",
    "https://lobste.rs",
]

results = Playtrafi.crawl_many(urls, max_concurrency=5)
for res in results:
    print(f"{res.url} -> {res.status_code} ({len(res.markdown)} chars)")
```

### 6. Screenshots & PDF Generation

Capture full viewport screenshots and export high-resolution PDFs:

```python
from playtrafi import Playtrafi

result = Playtrafi.crawl(
    "https://example.com",
    screenshot=True,
    full_page_screenshot=True,
    pdf=True,
)

result.save_screenshot("screenshot.png")
result.save_pdf("document.pdf")
```

### 7. Residential Proxy Rotation

Cycle through proxy pools with automatic failure tracking and temporary quarantine:

```python
import asyncio
from playtrafi import AsyncPlaytrafi, PlaytrafiConfig

config = PlaytrafiConfig(
    proxies=["http://user:pass@proxy1:8080", "http://user:pass@proxy2:8080"],
    proxy_strategy="round-robin",
)

async def run():
    async with AsyncPlaytrafi(config) as client:
        result = await client.scrape("https://example.com")
        print(result.title)

asyncio.run(run())
```

### 8. LLM Token Counting & Markdown Chunking

Slice long extracted documents into coherent, structure-preserving Markdown chunks directly ready for RAG vector stores:

```python
from playtrafi import Playtrafi

result = Playtrafi.crawl("https://en.wikipedia.org/wiki/Artificial_intelligence")

# Split into 1024-token chunks with 100-token overlap
chunks = result.chunk(max_tokens=1024, overlap_tokens=100)

for chunk in chunks:
    print(f"Chunk #{chunk.chunk_index} ({chunk.token_count} tokens):")
    print("Section:", chunk.metadata.get("section_heading"))
    print(chunk.text[:200], "\n---\n")
```

---

## 💻 CLI Usage

Playtrafi installs a standalone command `playtrafi` (with `patchtroy` alias retained for compatibility):

```bash
# Scrape URL and output clean Markdown to stdout
playtrafi https://news.ycombinator.com

# Save to output file
playtrafi https://example.com -o output.md

# Save complete JSON payload (markdown, metadata, structured items, links)
playtrafi https://example.com -f json -o output.json

# Export to standard CSV (auto-detected from file extension)
playtrafi https://example.com -o output.csv

# Batch crawl multiple URLs directly to CSV for data pipelines
playtrafi https://site1.com https://site2.com -f csv -o dataset.csv

# Capture screenshot and PDF
playtrafi https://example.com --screenshot page.png --pdf document.pdf

# Full-page screenshot
playtrafi https://example.com --screenshot full.png --full-page

# Batch scraping multiple URLs with proxy rotation and concurrency
playtrafi https://site1.com https://site2.com --proxy-file proxies.txt -c 5 -o batch.md

# Launch REST API microservice on port 4013
playtrafi serve --host 0.0.0.0 --port 4013
```

---

## 📡 REST API & Docker Microservice

Start the microservice for non-Python applications (Node.js, Go, Rust, Ruby):

```bash
# Start microservice
playtrafi serve --port 4013

# Or launch with Docker
docker run -d -p 4013:4013 --name playtrafi marcuszou/playtrafi:latest
```

### Scrape Endpoint Example

```bash
curl -X POST http://localhost:4013/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://news.ycombinator.com", "screenshot": true}'
```
