# Browser Context Pool & High-Concurrency Batching

Starting and stopping a full browser process for every single URL is slow, consuming 200–500MB of RAM and 1.5–3 seconds of startup overhead per request.

**Patchtroy** introduces the **Browser Context Pool (`BrowserContextPool`)**, achieving over **5x higher throughput** while drastically lowering system memory consumption.

---

## ⚡ How It Works

Instead of launching a new browser process for each scraping task:
1. Patchtroy launches a single shared browser instance in the background.
2. For each request, an isolated **browser context** is leased from the pool.
3. Each context has its own cookies, cache, proxy configuration, and storage.
4. An `asyncio.Semaphore` bounds concurrent active contexts (default: 5), preventing CPU thrashing and memory exhaustion.
5. Once scraping finishes, the context is cleanly closed, releasing resources while keeping the main browser process alive.

---

## 🚀 Usage Examples

### 1. Python Batch Scraping (`scrape_many`)

```python
import asyncio
from patchtroy import AsyncPatchtroy, PatchtroyConfig

async def main():
    urls = [
        "https://news.ycombinator.com",
        "https://lobste.rs",
        "https://en.wikipedia.org/wiki/Web_crawler",
    ]

    config = PatchtroyConfig(concurrency=5)

    async with AsyncPatchtroy(config) as client:
        results = await client.scrape_many(urls)
        for r in results:
            print(f"{r.url}: {r.status_code} ({len(r.markdown)} chars)")

asyncio.run(main())
```

### 2. Synchronous Batch Scraping

```python
from patchtroy import Patchtroy

results = Patchtroy.crawl_many(
    urls=["https://site1.com", "https://site2.com"],
    concurrency=4,
)
```

### 3. CLI Batch Crawling

```bash
patchtroy https://site1.com https://site2.com https://site3.com -c 4 -o batch_output.md
```
