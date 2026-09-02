# Getting Started with Patchtroy

## 📦 Installation

Install Patchtroy using pip or uv:

```bash
pip install patchtroy

# Install undetected Chromium browser binaries
patchright install chromium
```

### Optional Extras

- **REST API Microservice**: `pip install "patchtroy[server]"`
- **Documentation Build**: `pip install "patchtroy[docs]"`
- **All dependencies**: `pip install "patchtroy[all]"`

---

## 🐍 Python Usage

### 1. Synchronous One-Liner

```python
from patchtroy import Patchtroy

result = Patchtroy.crawl("https://en.wikipedia.org/wiki/Web_scraping")

if result.success:
    print(f"# {result.title}\n")
    print(result.markdown)
```

### 2. Asynchronous API with Context Manager (Recommended)

```python
import asyncio
from patchtroy import AsyncPatchtroy, PatchtroyConfig

async def main():
    config = PatchtroyConfig(
        headless=True,
        browser_timeout_s=15.0,
        wait_for="article.main",
    )

    async with AsyncPatchtroy(config) as crawler:
        result = await crawler.scrape("https://news.ycombinator.com")
        print("Markdown size:", len(result.markdown))
        print("Links extracted:", len(result.links))

asyncio.run(main())
```

---

## 💻 CLI Quickstart

Patchtroy installs a standalone terminal command `patchtroy`:

```bash
# Print clean Markdown to stdout
patchtroy https://news.ycombinator.com

# Save to Markdown file
patchtroy https://example.com -o page.md

# Save complete JSON record with metadata & links
patchtroy https://example.com -f json -o page.json
```
