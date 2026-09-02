# 🛡️ Patchtroy

**The undetected stealth web scraper & clean Markdown extractor for LLMs, RAG pipelines, and AI agents.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Engine: Patchright](https://img.shields.io/badge/Stealth%20Engine-Patchright-orange)](https://github.com/kaliiiiiiiiii/patchright)
[![Extractor: Trafilatura](https://img.shields.io/badge/Extraction-Trafilatura-green)](https://github.com/adbar/trafilatura)

---

## ⚡ What is Patchtroy?

**Patchtroy** is a lightweight, high-performance web crawling and content extraction engine designed specifically for LLMs and AI pipelines.

It bridges the gap between low-level drivers and high-level scrapers by coupling **Patchright** (the C++ patched Chromium engine that eliminates automated telemetry leakages) with **Trafilatura** (the gold standard for algorithmic boilerplate removal and pristine Markdown conversion).

### 🎯 Why Patchtroy?

| Feature | Crawl4AI | Firecrawl (Self-hosted) | **Patchtroy** |
| :--- | :---: | :---: | :---: |
| **Stealth Engine** | ❌ Standard Playwright (CDP leaked) | ❌ Blocked without paid SaaS proxy | **✅ Native Patchright Stealth** |
| **Boilerplate Stripping** | ⚠️ Heuristic regex / CSS | ✅ Full DOM clean | **✅ Trafilatura Gold Standard** |
| **Framework Data** | ⚠️ Partial regex | ✅ | **✅ Native Next.js (`__NEXT_DATA__`) & Schema.org JSON-LD** |
| **Dependencies** | ❌ Heavy (PyTorch, Transformers, ML) | ❌ Complex (Node, Redis, BullMQ) | **✅ Ultra-lean (< 15MB pure Python)** |
| **Throughput** | ⚠️ Process-level restart | ⚠️ Queue bottleneck | **✅ Browser Context Pool (>5x throughput)** |
| **Failure Tolerance** | ❌ Crashes on timeout | ❌ | **✅ Automatic fast HTTP fallback** |
| **Deployment** | Heavy multi-GB image | Multi-container stack | **✅ Single lightweight Docker container** |

---

## 🚀 Quick Example

```python
from patchtroy import Patchtroy

# 1-line instant stealth crawl to pristine Markdown
result = Patchtroy.crawl("https://news.ycombinator.com")

print("Title:", result.title)
print(result.markdown[:300])

# Structure-aware LLM chunking
chunks = result.chunk(max_tokens=500)
print(f"Generated {len(chunks)} LLM chunks.")
```
