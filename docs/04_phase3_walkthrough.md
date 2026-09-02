# Walkthrough: Phase 3 (v0.3.0) Implementation

Phase 3 transitions **Patchtroy** from a Python-only crawler into a complete, language-agnostic LLM data engineering microservice and RAG-ready pipeline.

---

## Key Features Delivered

### 1. Structure-Aware LLM Chunking & Token Counter
- **Module**: [chunker.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/src/patchtroy/chunker.py)
- **Classes & Functions**: `TextChunk`, `chunk_markdown()`, `count_tokens()`
- **Method**: `ScrapeResult.chunk(max_tokens=2048, overlap_tokens=100) -> list[TextChunk]`
- **Zero-ML Design**: Uses a calibrated high-speed BPE tokenizer with an automatic hook for `tiktoken` when available.
- **Heading-Preserving Splitting**: Recursively splits across Markdown headings (`#`, `##`, `###`), preserving document hierarchy and section metadata (`section_heading`).

### 2. REST API Microservice (FastAPI)
- **Module**: [server.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/src/patchtroy/server.py)
- **Endpoints**:
  - `GET /health`: Returns health status, engine status, and version (`0.3.0`).
  - `POST /scrape`: Scrapes single target URL with options for screenshots, PDFs, selectors, custom schemas, and proxies.
  - `POST /scrape/batch`: Concurrent multi-URL scraping sharing the browser pool.
- **CLI Integration**:
  - `patchtroy serve --host 0.0.0.0 --port 4013`

### 3. Production Docker Deployment
- **[Dockerfile](file:///mnt/ubt24-vdisk1/projects/patchtroy/Dockerfile)**: Minimal Debian Python 3.11 image pre-configured with Patchright Chromium headless binaries, running as unprivileged user `patchtroy`.
- **[docker-compose.yml](file:///mnt/ubt24-vdisk1/projects/patchtroy/docker-compose.yml)**: Single-command deployment (`docker compose up -d`).
- **[.dockerignore](file:///mnt/ubt24-vdisk1/projects/patchtroy/.dockerignore)**: Excludes caches and local environments.

---

## Verification Results

### Automated Test Suite
Ran complete suite with `uv run --extra dev --extra server pytest -v`:
```
collected 32 items

tests/test_chunker.py::test_count_tokens PASSED                                                         [  3%]
tests/test_chunker.py::test_chunk_markdown_small_doc PASSED                                             [  6%]
tests/test_chunker.py::test_chunk_markdown_multi_section PASSED                                         [  9%]
tests/test_chunker.py::test_scrape_result_chunk_method PASSED                                           [ 12%]
tests/test_cli.py::test_cli_help PASSED                                                                 [ 15%]
tests/test_cli.py::test_cli_single_url PASSED                                                           [ 18%]
tests/test_cli.py::test_cli_batch_urls PASSED                                                           [ 21%]
tests/test_cli.py::test_cli_serve PASSED                                                                [ 25%]
tests/test_crawler.py::test_invalid_url_handling PASSED                                                 [ 28%]
tests/test_crawler.py::test_sync_invalid_url PASSED                                                     [ 31%]
tests/test_crawler.py::test_async_scrape_many PASSED                                                    [ 34%]
tests/test_crawler.py::test_sync_scrape_many PASSED                                                     [ 37%]
tests/test_extractors.py::test_extract_markdown PASSED                                                  [ 40%]
tests/test_extractors.py::test_extract_json_ld PASSED                                                   [ 43%]
tests/test_extractors.py::test_extract_next_data PASSED                                                 [ 46%]
tests/test_extractors.py::test_extract_custom_schema PASSED                                             [ 50%]
tests/test_media_capture.py::test_scrape_with_media_capture PASSED                                      [ 53%]
tests/test_models.py::test_default_config PASSED                                                        [ 56%]
tests/test_models.py::test_custom_config PASSED                                                         [ 59%]
tests/test_models.py::test_scrape_result PASSED                                                         [ 62%]
tests/test_models.py::test_scrape_result_save_media PASSED                                              [ 65%]
tests/test_models.py::test_scrape_result_save_media_missing PASSED                                      [ 68%]
tests/test_pool.py::test_pool_context_acquisition PASSED                                                [ 71%]
tests/test_pool.py::test_pool_with_proxy_manager PASSED                                                 [ 75%]
tests/test_proxy.py::test_proxy_item_quarantine PASSED                                                  [ 78%]
tests/test_proxy.py::test_proxy_manager_round_robin PASSED                                              [ 81%]
tests/test_proxy.py::test_proxy_manager_random PASSED                                                   [ 84%]
tests/test_proxy.py::test_proxy_manager_from_file PASSED                                                [ 87%]
tests/test_proxy.py::test_proxy_manager_quarantine_fallback PASSED                                      [ 90%]
tests/test_server.py::test_health_check_endpoint PASSED                                                 [ 93%]
tests/test_server.py::test_scrape_endpoint_mocked PASSED                                                [ 96%]
tests/test_server.py::test_scrape_batch_endpoint_mocked PASSED                                          [100%]

============================================= 32 passed in 1.93s ==============================================
```

### Code Style & Linting
Ran `uv run --extra dev --extra server ruff check src tests`:
```
All checks passed!
```

### Version & CLI Output
```bash
$ uv run patchtroy --version
patchtroy 0.3.0
```
