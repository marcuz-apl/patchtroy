# Implementation Plan - Phase 2 (v0.2.0): High-Throughput Context Pool, Media Capture & Proxy Rotation

Phase 2 transitions Patchtroy from a single-session scraper into a production-grade scraping pipeline capable of high-concurrency batch execution, multi-modal capture (Screenshots & PDFs), and enterprise anti-blocking through resilient proxy rotation.

## User Review Required

> [!IMPORTANT]
> - **PDF Export Limitation**: Chromium headless supports PDF generation natively; however, headful Chromium does not support `page.pdf()`. When `--headful` is selected with PDF capture, we will log an informative warning or fallback cleanly.
> - **Proxy Protocol Support**: The `ProxyManager` will support `http://`, `https://`, and `socks5://` proxy URL formats compatible with Chromium/Playwright.

---

## Key Features & Architecture

### 1. Browser Context Pool & Batch Scraping (`src/patchtroy/pool.py`)
- **`BrowserContextPool`**:
  - Manages a pool of browser contexts under a unified browser process to achieve >5x throughput without repeatedly spawning Chromium processes.
  - Concurrency management via `asyncio.Semaphore` with configurable `max_concurrency` (default 5).
  - Context recycling policy: cleans cache/cookies or creates fresh contexts after a configurable number of requests (`max_requests_per_context`) to eliminate memory leaks.
- **Batch API**:
  - `AsyncPatchtroy.scrape_many(urls: list[str], max_concurrency: int = 5, ...)` -> returns `list[ScrapeResult]`.
  - `Patchtroy.crawl_many(urls: list[str], ...)` -> synchronous wrapper.

### 2. Multi-Modal Media Capture (Screenshots & PDFs)
- **`PatchtroyConfig` updates**:
  - `screenshot: bool = False`
  - `full_page_screenshot: bool = False`
  - `screenshot_path: str | None = None`
  - `pdf: bool = False`
  - `pdf_path: str | None = None`
- **`ScrapeResult` updates**:
  - `screenshot_bytes: bytes | None = None`
  - `pdf_bytes: bytes | None = None`
  - Convenience methods: `save_screenshot(path: str)` and `save_pdf(path: str)`.
- **CLI updates (`src/patchtroy/cli.py`)**:
  - `--screenshot <path>`: captures and saves screenshot to target path.
  - `--full-page`: toggles full-page screenshot instead of viewport.
  - `--pdf <path>`: generates and saves PDF document.

### 3. Proxy Rotation Manager (`src/patchtroy/proxy.py`)
- **`ProxyManager` / `ProxyPool`**:
  - Supports multiple proxy strings or proxy files (`proxies.txt`).
  - Rotation strategies: `"round-robin"` (default), `"random"`.
  - Fault tolerance & health tracking:
    - Automatically detects failed requests and temporarily quarantines degraded proxies (cooldown period).
    - Thread-safe / asyncio-safe rotation.
- **Integration**:
  - `PatchtroyConfig` accepts `proxies: list[str] | str | None` and `proxy_strategy: str = "round-robin"`.
  - Crawler assigns proxy per context automatically.
  - CLI flag: `--proxy <url>` and `--proxy-file <file>`.

---

## Proposed Changes

### Core Library

#### [NEW] [proxy.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/src/patchtroy/proxy.py)
- Implements `ProxyManager`, `ProxyItem`, and rotation strategies (`round_robin`, `random`).
- Failure counter and quarantine/cooldown mechanism.

#### [NEW] [pool.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/src/patchtroy/pool.py)
- Implements `BrowserContextPool` for shared browser reuse and semaphore-bounded concurrent scraping.

#### [MODIFY] [models.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/src/patchtroy/models.py)
- Extend `PatchtroyConfig` with:
  - `screenshot`, `full_page_screenshot`, `screenshot_path`
  - `pdf`, `pdf_path`
  - `proxies`, `proxy_strategy`, `max_concurrency`
- Extend `ScrapeResult` with:
  - `screenshot_bytes: bytes | None`
  - `pdf_bytes: bytes | None`
  - `save_screenshot(filepath: str | Path)` and `save_pdf(filepath: str | Path)`.

#### [MODIFY] [crawler.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/src/patchtroy/crawler.py)
- Integrate `ProxyManager` into `AsyncPatchtroy` to supply dynamic proxy configuration.
- Implement screenshot and PDF capture during page rendering lifecycle in `_scrape_with_browser`.
- Implement `scrape_many` in `AsyncPatchtroy` and `crawl_many` in `Patchtroy`.
- Support `BrowserContextPool` lifecycle.

#### [MODIFY] [cli.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/src/patchtroy/cli.py)
- Add CLI arguments: `--screenshot`, `--full-page`, `--pdf`, `--proxy-file`, `--concurrency`.
- Save media files directly when output paths are provided.

#### [MODIFY] [pyproject.toml](file:///mnt/ubt24-vdisk1/projects/patchtroy/pyproject.toml)
- Bump version from `0.1.0` to `0.2.0`.

#### [MODIFY] [PRD.md](file:///mnt/ubt24-vdisk1/projects/patchtroy/PRD.md)
- Update Phase 2 tasks to completed status.

#### [MODIFY] [README.md](file:///mnt/ubt24-vdisk1/projects/patchtroy/README.md)
- Add documentation and usage examples for Context Pool, Proxy Rotation, and Screenshot/PDF capture.

---

## Tests

#### [NEW] [test_proxy.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/tests/test_proxy.py)
- Unit tests for `ProxyManager`: rotation strategies, error tracking, quarantine & recovery.

#### [NEW] [test_pool.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/tests/test_pool.py)
- Unit and concurrent batch execution tests for `BrowserContextPool` and `scrape_many`.

#### [NEW] [test_media_capture.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/tests/test_media_capture.py)
- Tests for screenshot & PDF generation, file saving helpers, and fallback handling.

#### [MODIFY] [test_crawler.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/tests/test_crawler.py)
- Add tests for `crawl_many`, proxy options, and batch error resilience.

---

## Verification Plan

### Automated Tests
- Run complete test suite with `uv run --extra dev pytest -v`.
- Verify 100% test pass rate across new and existing tests.
- Run ruff linter: `uv run ruff check src tests`.

### Integration Verification
- Execute CLI with screenshot & PDF flags against a real or local HTML page to verify file creation.
- Execute batch crawl of multiple URLs to verify throughput and context pool reuse.
