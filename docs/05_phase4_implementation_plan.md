# Implementation Plan - Phase 4 (v0.4.0): Public Launch, Benchmark Suite & Documentation Portal

Phase 4 establishes the public release readiness of **Patchtroy** at version **`0.4.0`**, delivering:
1. **PyPI Public Release & CI/CD Automation**: Multi-OS matrix testing across Python 3.10–3.12 (Linux, macOS, Windows) and automated PyPI Trusted Publishing.
2. **Benchmark Suite vs Crawl4AI & Firecrawl**: Reproducible benchmarking suite measuring cold start, memory footprint, boilerplate stripping ratio, and throughput.
3. **Official Documentation Portal**: Complete MkDocs Material documentation site deployable to GitHub Pages.

---

## User Review Required

> [!IMPORTANT]
> - **Calibrated Versioning**: Following user alignment, version is set to **`0.4.0`** (Public Release / Community Preview) rather than premature `1.0.0`, leaving room for community feedback and API iteration.
> - **PyPI Trusted Publishing**: Release workflow utilizes modern OIDC GitHub Actions Trusted Publishing.

---

## Key Features & Architecture

### 1. PyPI Release & CI/CD Pipelines
- **Cross-Platform CI Matrix (`.github/workflows/ci.yml`)**:
  - Matrix across `ubuntu-latest`, `macos-latest`, `windows-latest`.
  - Python versions: `3.10`, `3.11`, `3.12`.
  - Automated steps: syntax linting (`ruff`), unit test execution (`pytest`), and wheel build verification (`uv build`).
- **PyPI Release Pipeline (`.github/workflows/release.yml`)**:
  - Triggers on tag pushes matching `v*`.
  - Builds sdist and binary wheel.
  - Deploys to PyPI with `pypa/gh-action-pypi-publish`.
- **Package Metadata**:
  - Version set to `0.4.0`.

### 2. Comprehensive Benchmark Suite (`benchmarks/`)
- **`benchmarks/run_benchmark.py`**:
  - **Cold Start Latency**: Evaluates import and engine startup time (< 1.5s per NFR-02).
  - **Footprint Analysis**: Compares install disk footprint and runtime memory consumption (Patchtroy < 15MB vs Crawl4AI > 1.2GB with PyTorch/Transformers).
  - **Boilerplate Stripping Cleanliness**: Quantitative noise ratio test comparing Trafilatura's algorithmic extraction against naive text/regex extractors.
  - **Throughput & Concurrency**: Benchmarks single-worker vs pooled context throughput.
- **`benchmarks/BENCHMARKS.md`**:
  - Full publishable report with comparison tables, charts, and methodology.

### 3. Official Documentation Portal
- **`mkdocs.yml`**: Configured with Material for MkDocs theme, dark mode toggle, code syntax highlighting, and navigation tabs.
- **Documentation Structure**:
  - `docs/index.md`: Overview, feature comparison, and architecture blueprint.
  - `docs/getting-started.md`: Installation, CLI usage, and Python quickstart.
  - `docs/stealth-architecture.md`: C++ patched CDP masking and anti-bot evasion deep dive.
  - `docs/context-pool.md`: High-throughput context pooling and batch scraping.
  - `docs/media-capture.md`: Screenshots and PDF export capabilities.
  - `docs/proxy-rotation.md`: Proxy pooling, strategies, and fault quarantine.
  - `docs/llm-chunking.md`: Structure-aware Markdown chunking and token counting.
  - `docs/rest-api.md`: FastAPI microservice endpoints, schemas, and Docker deployment.
  - `docs/benchmarks.md`: Benchmark results vs Crawl4AI and Firecrawl.
- **GitHub Pages Workflow (`.github/workflows/docs.yml`)**:
  - Automated build and deploy to GitHub Pages on pushes to `main`.

---

## Proposed Changes

### Packaging & Metadata
#### [MODIFY] [pyproject.toml](file:///mnt/ubt24-vdisk1/projects/patchtroy/pyproject.toml)
- Bump version to `0.4.0`.
- Add `docs` optional dependencies group (`mkdocs-material>=9.5.0`).

#### [MODIFY] [__init__.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/src/patchtroy/__init__.py)
- Bump `__version__` to `0.4.0`.

#### [MODIFY] [cli.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/src/patchtroy/cli.py)
- Bump `__version__` to `0.4.0`.

#### [MODIFY] [server.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/src/patchtroy/server.py)
- Bump version to `0.4.0`.

#### [MODIFY] [Dockerfile](file:///mnt/ubt24-vdisk1/projects/patchtroy/Dockerfile)
- Bump image version label to `0.4.0`.

### CI/CD Workflows
#### [NEW] [.github/workflows/ci.yml](file:///mnt/ubt24-vdisk1/projects/patchtroy/.github/workflows/ci.yml)
- Multi-OS matrix CI pipeline.

#### [NEW] [.github/workflows/release.yml](file:///mnt/ubt24-vdisk1/projects/patchtroy/.github/workflows/release.yml)
- PyPI automated release pipeline.

#### [NEW] [.github/workflows/docs.yml](file:///mnt/ubt24-vdisk1/projects/patchtroy/.github/workflows/docs.yml)
- Documentation portal build and GitHub Pages deployment.

### Benchmarks
#### [NEW] [benchmarks/run_benchmark.py](file:///mnt/ubt24-vdisk1/projects/patchtroy/benchmarks/run_benchmark.py)
- Automated benchmarking script.

#### [NEW] [benchmarks/BENCHMARKS.md](file:///mnt/ubt24-vdisk1/projects/patchtroy/benchmarks/BENCHMARKS.md)
- Complete published benchmark results vs Crawl4AI and Firecrawl.

### Documentation Portal
#### [NEW] [mkdocs.yml](file:///mnt/ubt24-vdisk1/projects/patchtroy/mkdocs.yml)
- Material for MkDocs configuration.

#### [NEW] Documentation guides in `docs/`
- Full documentation pages covering API, CLI, Docker, Proxy, Pool, and Chunking.

#### [MODIFY] [PRD.md](file:///mnt/ubt24-vdisk1/projects/patchtroy/PRD.md)
- Mark Phase 4 completed.

#### [NEW] [docs/05_phase4_implementation_plan.md](file:///mnt/ubt24-vdisk1/projects/patchtroy/docs/05_phase4_implementation_plan.md)
- Record plan in documentation folder.

---

## Verification Plan

### Automated Tests
- Run complete test suite: `uv run --extra dev --extra server pytest -v`.
- Run linter: `uv run --extra dev --extra server ruff check src tests benchmarks`.
- Run benchmark runner to verify latency and metrics: `uv run python benchmarks/run_benchmark.py`.
- Verify packaging build: `uv build`.
