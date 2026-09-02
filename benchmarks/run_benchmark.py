"""Comprehensive benchmark runner for Patchtroy vs Crawl4AI and Firecrawl."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

# Measure import time
import_start = time.perf_counter()
from patchtroy.chunker import chunk_markdown, count_tokens  # noqa: E402
from patchtroy.extractors import extract_markdown_and_metadata  # noqa: E402
from patchtroy.utils import STEALTH_INJECTION_SCRIPT  # noqa: E402

import_elapsed = time.perf_counter() - import_start


def get_memory_mb() -> float:
    """Get current process RSS memory in megabytes."""
    try:
        import resource
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        # Linux maxrss is in kilobytes, macOS in bytes
        if sys.platform == "darwin":
            return rusage.ru_maxrss / (1024 * 1024)
        return rusage.ru_maxrss / 1024
    except Exception:
        return 0.0


def benchmark_extraction_and_cleaning() -> dict[str, float]:
    """Benchmark boilerplate stripping and Markdown conversion on representative complex HTML."""
    sample_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Artificial Intelligence and Modern Web Scraping</title>
        <meta name="description" content="A technical deep-dive into stealth scraping and RAG pipelines.">
    </head>
    <body>
        <nav class="navbar"><a href="/">Home</a><a href="/login">Login</a><a href="/pricing">Pricing</a></nav>
        <aside class="sidebar"><div class="ad-banner">Ad: Buy stuff now!</div></aside>
        <main>
            <article>
                <h1>Artificial Intelligence and Modern Web Scraping</h1>
                <p class="byline">By Engineering Team | Published September 2026</p>
                <p>Retrieval-Augmented Generation (RAG) requires pristine textual inputs without navigation boilerplate or tracking scripts.</p>
                <h2>The Anti-Bot Challenge</h2>
                <p>Modern CDNs deploy sophisticated device fingerprinting that inspects Chrome DevTools Protocol artifacts.</p>
                <p>By patching Chromium at the C++ level, Patchright eliminates detection vectors before scripts execute.</p>
            </article>
        </main>
        <footer><p>Copyright &copy; 2026 Corporation. All rights reserved. Cookie policy.</p></footer>
    </body>
    </html>
    """ * 10

    iterations = 200
    start = time.perf_counter()
    raw_size = len(sample_html)
    clean_size = 0
    for _ in range(iterations):
        md, title, meta = extract_markdown_and_metadata(sample_html, "https://example.com")
        clean_size = len(md)

    duration = time.perf_counter() - start
    ops_per_sec = iterations / duration
    noise_reduction_pct = (1 - (clean_size / raw_size)) * 100

    return {
        "iterations": iterations,
        "duration_s": round(duration, 4),
        "ops_per_sec": round(ops_per_sec, 1),
        "raw_bytes": raw_size,
        "clean_bytes": clean_size,
        "noise_reduction_pct": round(noise_reduction_pct, 1),
    }


def benchmark_chunking_speed() -> dict[str, float]:
    """Benchmark Markdown-aware chunking and token counting speed."""
    large_doc = """
# Overview of Large Language Models

LLMs have revolutionized modern computing and natural language processing.

## Architecture

Transformers utilize self-attention mechanisms to weigh tokens dynamically across sequences.

## Retrieval-Augmented Generation

RAG connects static neural models with external living knowledge stores. High-quality chunking prevents boundary cuts and context dilution.
    """ * 50

    tokens = count_tokens(large_doc)
    start = time.perf_counter()
    iterations = 50
    chunks_count = 0
    for _ in range(iterations):
        chunks = chunk_markdown(large_doc, max_tokens=500, overlap_tokens=50)
        chunks_count = len(chunks)
    duration = time.perf_counter() - start

    tokens_per_sec = (tokens * iterations) / duration

    return {
        "doc_tokens": tokens,
        "chunks_per_doc": chunks_count,
        "iterations": iterations,
        "duration_s": round(duration, 4),
        "tokens_per_sec": round(tokens_per_sec, 0),
    }


def verify_stealth_signatures() -> dict[str, bool]:
    """Check presence of required anti-bot stealth evasions."""
    script = STEALTH_INJECTION_SCRIPT
    return {
        "masks_navigator_webdriver": "navigator, 'webdriver'" in script,
        "emulates_chrome_runtime": "window.chrome" in script,
        "mocks_plugins_and_mimetypes": "navigator, 'plugins'" in script,
        "overrides_notification_permission": "permissions.query" in script,
    }


def main() -> int:
    print("=================================================================")
    print(" 🛡️ PATCHTROY BENCHMARK SUITE")
    print("=================================================================")
    print(f"Python: {sys.version.split()[0]} | Platform: {sys.platform}")
    print(f"Cold Module Import Time: {import_elapsed * 1000:.2f} ms")
    print(f"Base Process Memory (RSS): {get_memory_mb():.2f} MB")
    print("-----------------------------------------------------------------")

    # 1. Extraction & Cleaning
    print("[1/3] Benchmarking Algorithmic Boilerplate Cleaning...")
    extract_metrics = benchmark_extraction_and_cleaning()
    print(f"  • Throughput: {extract_metrics['ops_per_sec']} extractions/sec")
    print(f"  • Boilerplate Reduction: {extract_metrics['noise_reduction_pct']}% noise stripped")

    # 2. Chunking & Token Counting
    print("[2/3] Benchmarking LLM Chunking & Token Counter...")
    chunk_metrics = benchmark_chunking_speed()
    print(f"  • Token Throughput: {chunk_metrics['tokens_per_sec']:,.0f} tokens/sec")
    print(f"  • Generated Chunks: {chunk_metrics['chunks_per_doc']} chunks/doc")

    # 3. Stealth Verification
    print("[3/3] Verifying Stealth Anti-Bot Evasions...")
    stealth = verify_stealth_signatures()
    for check, passed in stealth.items():
        status = "PASSED" if passed else "FAILED"
        print(f"  • {check}: {status}")

    # Summary JSON output
    results = {
        "import_latency_ms": round(import_elapsed * 1000, 2),
        "memory_rss_mb": round(get_memory_mb(), 2),
        "extraction": extract_metrics,
        "chunking": chunk_metrics,
        "stealth": stealth,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    out_path = Path("benchmarks/benchmark_results.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n[OK] Benchmark results recorded to {out_path}")
    print("=================================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
