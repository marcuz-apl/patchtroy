# Implementation Plan - Phase 3 (v0.3.0): Microservice, LLM Chunking & Docker Deployment

Phase 3 expands Patchtroy into a language-agnostic microservice and a complete RAG-ready pipeline for LLMs, featuring:
1. **REST API Microservice**: FastAPI server with `/health`, `/scrape`, and `/scrape/batch` endpoints.
2. **Token Counter & Markdown Chunking Utility**: Structure-aware LLM chunking (`result.chunk(max_tokens=2048)`).
3. **Lightweight Production Docker Container**: Containerized image (`marcuszou/patchtroy:latest`) with headless Patchright Chromium and REST API.

---

## User Review Required

> [!IMPORTANT]
> - **Zero-ML Dependency Policy**: Consistent with Non-Functional Requirement NFR-01, the chunker and token counter will remain strictly zero-ML (no PyTorch, no transformers). Token counting will use a fast algorithmic BPE approximation with optional `tiktoken` hook if available in the environment.
> - **Modular Server Dependency**: FastAPI and Uvicorn will be configured under an optional dependency extra `[project.optional-dependencies] server = ["fastapi>=0.110.0", "uvicorn>=0.29.0"]` so users installing standard `patchtroy` for script/CLI usage keep a minimal <15MB install footprint.

---

## Key Features & Architecture

### 1. REST API Microservice (`src/patchtroy/server.py`)
- **FastAPI Application**:
  - `GET /health`: Health check, uptime, version, engine status.
  - `POST /scrape`: Scrapes single URL. Accepts `ScrapeRequest` JSON payload (`url`, `wait_for`, `screenshot`, `full_page`, `pdf`, `custom_schema`, `timeout`, `proxy`). Returns `ScrapeResult`.
  - `POST /scrape/batch`: Batch scraping endpoint accepting `urls: list[str]` and `concurrency: int`.
- **CLI Subcommand**:
  - `patchtroy serve --host 0.0.0.0 --port 8000 --workers 1`
  - Integrated into existing `cli.py` arguments.

### 2. Token Counting & Markdown Chunking (`src/patchtroy/chunker.py`)
- **`TextChunk` Schema**:
  - `text: str`: chunk Markdown text.
  - `chunk_index: int`: sequential order.
  - `token_count: int`: estimated/calculated tokens.
  - `metadata: dict[str, Any]`: document title, source URL, heading path.
- **Structure-Aware Splitting**:
  - Respects Markdown syntax: splits hierarchically at Headings (`#`, `##`, `###`), then Paragraphs (`\n\n`), then line breaks.
  - Prevents mid-sentence and mid-table truncation.
  - Supports configurable `overlap_tokens` (default: 100).
- **API Integration**:
  - `ScrapeResult.chunk(max_tokens: int = 2048, overlap: int = 100) -> list[TextChunk]`.

### 3. Lightweight Docker Container
- **`Dockerfile`**:
  - Debian-based minimal Python environment.
  - Installs Patchright and Chromium runtime system dependencies.
  - Installs `patchtroy[server]`.
  - Runs as non-root user `patchtroy`.
  - Configures `HEALTHCHECK` against `http://localhost:8000/health`.
  - Default command: starts FastAPI server on port 8000.
- **`docker-compose.yml`**:
  - Convenience setup for local orchestration.
- **`.dockerignore`**:
  - Excludes local virtual environments, test caches, Git history.

---

## Proposed Changes

### Core Library

#### [MODIFY] [pyproject.toml](file:///mnt/ubt24-vdisk1/projects/patchtroy/pyproject.toml)
- Bump version to `0.3.0`.
- Add `server` and `all` optional dependency groups (`fastapi`, `uvicorn`).

#### [NEW] [chunker.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/src/patchtroy/chunker.py)
- Implements `TextChunk`, token counting helper, and Markdown-aware semantic chunker.

#### [NEW] [server.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/src/patchtroy/server.py)
- Implements FastAPI server application, request/response models, and lifespan management with `AsyncPatchtroy`.

#### [MODIFY] [models.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/src/patchtroy/models.py)
- Import `TextChunk` and bind `chunk()` method on `ScrapeResult`.

#### [MODIFY] [cli.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/src/patchtroy/cli.py)
- Add `serve` subcommand: `patchtroy serve [--host] [--port]`.

#### [MODIFY] [__init__.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/src/patchtroy/__init__.py)
- Export `TextChunk` and `create_app` / `server`.

### Deployment Artifacts

#### [NEW] [Dockerfile](file:///mnt/ubt24-vdisk1/projects/patchtroy/Dockerfile)
- Multi-platform container specification for Patchtroy microservice.

#### [NEW] [docker-compose.yml](file:///mnt/ubt24-vdisk1/projects/patchtroy/docker-compose.yml)
- Docker Compose configuration for instant launch.

#### [NEW] [.dockerignore](file:///mnt/ubt24-vdisk1/projects/patchtroy/.dockerignore)
- Ignore rules for Docker build context.

### Documentation & Tracking

#### [MODIFY] [PRD.md](file:///mnt/ubt24-vdisk1/projects/patchtroy/PRD.md)
- Mark Phase 3 roadmap items as completed.

#### [MODIFY] [README.md](file:///mnt/ubt24-vdisk1/projects/patchtroy/README.md)
- Document REST API endpoints, Docker execution, and LLM chunking examples.

#### [NEW] [03_phase3_implementation_plan.md](file:///mnt/ubt24-vdisk1/projects/patchtroy/docs/03_phase3_implementation_plan.md)
- Record implementation plan in `docs/`.

---

## Verification Plan

### Automated Tests
- `tests/test_chunker.py`: Test heading preservation, token threshold adherence, overlap behavior, and `result.chunk()`.
- `tests/test_server.py`: Test FastAPI endpoints (`/health`, `/scrape`, `/scrape/batch`) with `TestClient`.
- Full suite execution: `uv run --extra dev --extra server pytest -v`.
- Linting: `uv run --extra dev --extra server ruff check src tests`.

### Manual & CLI Verification
- Test `patchtroy serve --help` and spin up local server test.
- Test `curl -X POST http://localhost:8000/scrape` with test payload.
