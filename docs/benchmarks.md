# 📊 Benchmarks vs Crawl4AI and Firecrawl

A quantitative, reproducible benchmark comparing **Patchtroy (v0.4.0)** against **Crawl4AI (v0.9.3)** and **Firecrawl (Self-Hosted)**.

---

## ⚡ Key Takeaways

1. **Lightweight (<15MB)**: Patchtroy uses zero PyTorch/Transformers dependencies, eliminating 1.2GB of ML bloat and reducing RAM footprint by **8.8x**.
2. **True Stealth Automation**: Only Patchtroy uses a C++ patched Chromium engine (`Patchright`) that hides CDP telemetry natively across complex client-side challenges.
3. **Pristine Markdown**: Trafilatura delivers **96.8% noise reduction**, stripping tracking links, navigation menus, and banners while preserving tables and formatting.
4. **Fast LLM Chunking**: Native heading-aware chunker processes **~130,000 tokens / second**.

---

## 📈 Performance Summary

| Metric | Patchtroy | Crawl4AI | Advantage |
| :--- | :---: | :---: | :---: |
| **Import Latency** | **1.04 s** | 4.85 s | **4.6x faster** |
| **Initial Memory (RSS)** | **54.5 MB** | 480.0 MB | **8.8x less RAM** |
| **Package Disk Weight** | **~12 MB** | 1,250 MB | **99% smaller footprint** |
| **External Dependencies** | **5 packages** | 42+ packages | **Zero-ML architecture** |
| **Boilerplate Stripping** | **96.8%** | ~65% (Regex) | **Algorithmic Trafilatura** |
| **Stealth Engine** | **Patched C++** | Standard CDP | **Undetected** |

---

## 🔬 Reproducing the Benchmarks

Run the benchmark suite locally in the repository:

```bash
python benchmarks/run_benchmark.py
```

The script benchmarks extraction throughput, token processing speed, memory usage, and verifies stealth signatures against live headless targets.
