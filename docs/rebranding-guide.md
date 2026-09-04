# Rebranding Guide: Patchtroy to Playtrafi

This document details the complete end-to-end process for rebranding the project from **Patchtroy** (`patchtroy`) to **Playtrafi** (`playtrafi`), covering repository refactoring, PyPI package migration, GitHub releases, Docker configurations, and backwards compatibility.

---

## 1. Naming & Identity Mapping

| Component | Legacy Identifier | New Identifier | Notes |
| :--- | :--- | :--- | :--- |
| **Project Title** | Patchtroy | Playtrafi | Used in documentation, headers, branding |
| **PyPI Package** | `patchtroy` | `playtrafi` | Lowercase canonical PEP 508 package name |
| **Python Import Module** | `src/patchtroy` | `src/playtrafi` | `import playtrafi` |
| **CLI Command** | `patchtroy` | `playtrafi` | Provide `patchtroy` entrypoint alias during deprecation window |
| **GitHub Repository** | `marcuz-apl/patchtroy` | `marcuz-apl/playtrafi` | GitHub preserves redirects after rename |
| **PyPI Environment URL** | `https://pypi.org/p/patchtroy` | `https://pypi.org/p/playtrafi` | Updated in GitHub Actions workflow |
| **Docker Container** | `patchtroy:latest` | `playtrafi:latest` | Image tag and compose service naming |

---

## 2. Status & Phase Tracker

- [x] **Phase 1: Pre-flight Verification & Registry Availability** *(Completed)*
- [x] **Phase 2: In-Repository Codebase & Packaging Refactoring** *(Completed)*
- [x] **Phase 3: Docker & Documentation Updates** *(Completed)*
- [x] **Phase 4: GitHub Repository & Git Remote Rename** *(Completed — remotes & repo active)*
- [x] **Phase 5: PyPI Package Registration & Publishing** *(Completed — playtrafi 0.6.0 live on PyPI)*
- [x] **Phase 6: Verification & Test Suite Validation** *(Completed — 38 tests passing, ruff clean)*
- [x] **Phase 7: Transitional Deprecation Package for `patchtroy`** *(Completed — patchtroy 0.6.0 bridge published to PyPI)*
- [x] **Phase 8: Initial Release of `playtrafi` (`v0.6.0`)** *(Completed — v0.6.0 tagged & released)*

---

## 3. Phase 1: Pre-flight Verification & Registry Availability

### 1.1 PyPI Package Name Check
Verification performed via PyPI JSON API and index search:
- Endpoint: `https://pypi.org/pypi/playtrafi/json` &rarr; **HTTP 404 (Available)**
- Pip Index query: `pip index versions playtrafi` &rarr; **No matching distribution found (Available)**
- **Result:** The `playtrafi` package name is unregistered and ready to be claimed on PyPI.

### 1.2 GitHub Repository Namespace Check
Verification performed via GitHub API:
- Endpoint: `https://api.github.com/repos/marcuz-apl/playtrafi` &rarr; **HTTP 404 (Available)**
- **Result:** No namespace collision exists under `marcuz-apl`.

---

## 4. Phase 2: In-Repository Refactoring Plan

### 2.1 Directory Structure
Move the primary Python package:
```bash
git mv src/patchtroy src/playtrafi
```

### 2.2 `pyproject.toml` Updates
```toml
[project]
name = "playtrafi"
description = "Stealth web scraper & markdown extractor for LLMs, pairing Patchright with Trafilatura."
# ...
[project.scripts]
playtrafi = "playtrafi.cli:main"
patchtroy = "playtrafi.cli:main"  # Deprecation alias for CLI backwards compatibility

[project.urls]
Homepage = "https://github.com/marcuz-apl/playtrafi"
Repository = "https://github.com/marcuz-apl/playtrafi"
Issues = "https://github.com/marcuz-apl/playtrafi/issues"

[tool.hatch.build.targets.wheel]
packages = ["src/playtrafi"]
```

### 2.3 Source Code & Internal Import Updates
Replace all internal package imports across:
- `src/playtrafi/**/*.py` (`from patchtroy...` &rarr; `from playtrafi...`)
- `tests/**/*.py`
- `benchmarks/run_benchmark.py`

Regenerate lockfile:
```bash
uv lock
```

---

## 5. Phase 3: Docker & Documentation Updates

### 5.1 Docker Configuration
- **`Dockerfile`**: Update package installation references and entrypoint to `playtrafi`.
- **`docker-compose.yml`**: Update service name from `patchtroy-api` to `playtrafi-api` and image tags.

### 5.2 Documentation & MkDocs
- **`mkdocs.yml`**: Update `site_name: Playtrafi`, `repo_url`, and page navigation.
- **`README.md` & `PRD.md`**: Update install instructions (`pip install playtrafi`), code examples, and command line guides.

---

## 6. Phase 4: GitHub Repository & Remote Settings

### 6.1 GitHub Repository Rename
1. Go to repository settings on GitHub: `https://github.com/marcuz-apl/patchtroy/settings`.
2. In the **General** tab under **Repository name**, update to `playtrafi` and click **Rename**.
3. Update local git remote:
   ```bash
   git remote set-url origin https://github.com/marcuz-apl/playtrafi.git
   ```

---

## 7. Phase 5: PyPI Trusted Publishing (OIDC) Setup

Because publishing uses PyPI Trusted Publishing (`id-token: write`):
1. Navigate to **PyPI Account Settings &rarr; Publishing**: `https://pypi.org/manage/account/publishing/`.
2. Add a new **Pending Publisher**:
   - **PyPI Project Name:** `playtrafi`
   - **Owner:** `marcuz-apl`
   - **Repository Name:** `playtrafi`
   - **Workflow Name:** `release.yml`
   - **Environment Name:** `pypi`
3. Update `.github/workflows/release.yml`:
   ```yaml
   environment:
     name: pypi
     url: https://pypi.org/p/playtrafi
   ```

---

## 8. Phase 6: Deprecation Bridge for `patchtroy` (Optional but Recommended)

To ensure existing installations and scripts don't fail immediately:
1. Release a transitional version of `patchtroy` (e.g. `v0.6.0`) with dependency on `playtrafi>=0.6.0`.
2. Emit a `DeprecationWarning` when imported:
   ```python
   # In patchtroy/__init__.py of the transitional package
   import warnings
   from playtrafi import *  # noqa: F403

   warnings.warn(
       "'patchtroy' has been renamed to 'playtrafi'. "
       "Please update your requirements to use 'playtrafi'.",
       DeprecationWarning,
       stacklevel=2,
   )
   ```

---

## 9. Phase 7: Release Execution

1. Run verification test suite locally:
   ```bash
   uv run pytest -v
   uv run ruff check .
   uv build
   ```
2. Commit and push:
   ```bash
   git add .
   git commit -m "feat!: rebrand project from patchtroy to Playtrafi"
   git push origin main
   ```
3. Tag and push version to trigger GitHub Actions release:
   ```bash
   git tag v0.6.0
   git push origin v0.6.0
   ```
