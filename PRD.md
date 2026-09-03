# Product Requirements Document (PRD) & Architecture Blueprint: Patchtroy

**Document Version**: 1.0.0  
**Status**: Active / Approved  
**Author**: Marcus Zou / Patchtroy Project  
**Target Category**: Developer Tools / AI & LLM Data Engineering  

---

## 1. Executive Summary

**Patchtroy** is a standalone open-source Python library, CLI, and microservice designed to convert any dynamic web page into clean, LLM-ready Markdown and structured data with resilient execution across modern web perimeters.

By coupling **Patchright** (the C++-patched undetected Playwright engine) with **Trafilatura** (the gold standard in algorithmic boilerplate removal and Markdown extraction), Patchtroy delivers superior stealth and content cleanliness with zero machine learning dependencies.

---

## 2. Problem Statement & Market Opportunity

### 2.1 The Current Problem
LLMs require high-quality, noise-free Markdown for RAG (Retrieval-Augmented Generation) and fine-tuning. However, developers face a painful dilemma:
1. **Low-level drivers (Patchright, Playwright)** render dynamic JS, but provide no content cleaning or Markdown extraction.
2. **Text extractors (Trafilatura, Readability)** produce pristine Markdown, but fail completely on JavaScript SPAs and dynamic client challenges.
3. **Existing all-in-one frameworks (Crawl4AI)** rely on standard Playwright (which triggers standard CDP detection) and are bloated with heavy PyTorch/Transformer dependencies.
4. **Commercial APIs (Firecrawl SaaS, Jina Reader)** introduce vendor lock-in, rate limits, and recurring subscription costs.

### 2.2 The Patchtroy Solution
Patchtroy occupies the unoccupied **"Lightweight Stealth Sweet Spot"**:
- Native Patchright C++ stealth architecture.
- Algorithmic Trafilatura extraction (zero ML overhead, <15MB install).
- Native extraction of embedded Next.js (`__NEXT_DATA__`) and Schema.org JSON-LD payloads.
- Automatic graceful HTTP fallback on browser timeout.

---

## 3. Architecture & System Design

```
                                  ┌───────────────────────────┐
                                  │      User Application     │
                                  │ (Python API / CLI / HTTP) │
                                  └─────────────┬─────────────┘
                                                │
                                  ┌─────────────▼─────────────┐
                                  │     Patchtroy Engine      │
                                  └──────┬─────────────┬──────┘
                                         │             │
                    ┌────────────────────┘             └────────────────────┐
                    ▼                                                       ▼
      ┌───────────────────────────┐                           ┌───────────────────────────┐
      │  Primary: Patchright      │                           │  Fallback: httpx Client   │
      │  Stealth Chromium Browser │                           │  Fast direct HTTP GET     │
      │  • CDP Masking            │                           │  (if browser times out)   │
      │  • JS Execution           │                           └─────────────┬─────────────┘
      │  • wait_for Selectors     │                                         │
      └─────────────┬─────────────┘                                         │
                    │                                                       │
                    └────────────────────┬──────────────────────────────────┘
                                         ▼
                         ┌───────────────────────────────┐
                         │   Extraction & Parser Hub     │
                         ├───────────────────────────────┤
                         │ • Trafilatura (Markdown)      │
                         │ • Metadata & Canonical URL    │
                         │ • __NEXT_DATA__ Props         │
                         │ • Schema.org JSON-LD          │
                         │ • Custom CSS Schema Selector  │
                         └───────────────┬───────────────┘
                                         ▼
                               ┌───────────────────┐
                               │   ScrapeResult    │
                               │  (Pydantic Model) │
                               └───────────────────┘
```

---

## 4. Requirements Specification

### 4.1 Functional Requirements (FR)

- **FR-01: Asynchronous & Synchronous Python API**
  - Provide `AsyncPatchtroy` with async context management (`async with`).
  - Provide synchronous `Patchtroy` convenience methods (`Patchtroy.crawl(url)`).

- **FR-02: Native Stealth Browser Automation**
  - Launch Patchright Chromium with `--disable-blink-features=AutomationControlled` and sandbox flags.
  - Automatically inject stealth configuration scripts masking `navigator.webdriver` and emulating `window.chrome.runtime`.

- **FR-03: Trafilatura Markdown & Metadata Extraction**
  - Transform rendered HTML into clean, formatted Markdown.
  - Automatically strip navigation bars, footer boilerplate, advertisements, and cookie modals.
  - Extract document metadata: title, author, description, date, and canonical URL.

- **FR-04: Dynamic Framework Data Extraction**
  - Detect and parse Next.js embedded `<script id="__NEXT_DATA__">` payloads.
  - Extract structured listings, product data, and page properties directly into dict records.

- **FR-05: Schema.org JSON-LD Extraction**
  - Extract and expand `<script type="application/ld+json">` graphs into structured dictionaries.

- **FR-06: Custom Declarative CSS Schema Extraction**
  - Accept a custom schema definition: `item_selector` and `fields` mapping to CSS selectors.
  - Extract tabular items from custom web architectures.

- **FR-07: Automatic HTTP Fallback**
  - If headless Chromium times out, encounters a system crash, or fails to launch, immediately fall back to a direct `httpx` HTTP GET request with realistic headers to ensure high fault tolerance.

- **FR-08: Command-Line Interface (CLI)**
  - Provide a standalone terminal executable `patchtroy <url>` supporting `-o/--output`, `--format [markdown|json|html]`, `--wait-for`, and `--headful`.

---

### 4.2 Non-Functional Requirements (NFR)

- **NFR-01: Minimal Footprint**
  - Package weight under 15MB (excluding browser binaries).
  - Absolutely zero heavy machine learning libraries (no torch, transformers, or sentence-transformers).

- **NFR-02: Fast Cold Starts**
  - Cold engine start time < 1.5 seconds.

- **NFR-03: Broad Python Support**
  - Compatible with Python 3.10, 3.11, and 3.12 across Linux, macOS, and Windows.

- **NFR-04: Type Safety**
  - 100% typed with Pydantic v2 schemas and complete type hints.

---

## 5. Release Roadmap

### Phase 1 (v0.1.0 — Current)
- [x] Standalone package structure (`pyproject.toml`, Hatchling).
- [x] `AsyncPatchtroy` and `Patchtroy` core drivers.
- [x] Trafilatura Markdown extraction.
- [x] Next.js `__NEXT_DATA__` & Schema.org JSON-LD extractors.
- [x] Automatic HTTP fallback.
- [x] CLI entry point.
- [x] Unit and contract test suite (9 tests passing).

### Phase 2 (v0.2.0)
- [x] Browser Context Pool (reusing browser instances across requests to achieve >5x throughput).
- [x] Screenshot & PDF capture modes.
- [x] Proxy rotation manager (residential proxy integration).
- [x] Concurrent batch crawling (`scrape_many` / `crawl_many`).
- [x] Full test suite (24 tests passing).

### Phase 3 (v0.3.0)
- [x] Lightweight Docker container (`marcuszou/patchtroy:latest`).
- [x] REST API microservice (FastAPI endpoint `/scrape` and `/scrape/batch`).
- [x] Token counter & LLM chunking utility (`result.chunk(max_tokens=2048)`).
- [x] Full test suite (32 tests passing).

### Phase 4 (v0.5.0 — Current)
- [x] PyPI public release workflows & multi-OS matrix CI (`.github/workflows/`).
- [x] Comprehensive benchmark publication vs Crawl4AI and Firecrawl (`benchmarks/BENCHMARKS.md`).
- [x] Official documentation portal (Material for MkDocs).
- [x] Full test suite (32 tests passing, 100% ruff clean, wheel package verified).

### Phase 5 (v1.0.0)
- [ ] Enterprise production stabilization and API freeze after community adoption.
- [ ] Distributed cluster crawling integration.
