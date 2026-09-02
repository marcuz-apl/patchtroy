# ==============================================================================
# Patchtroy Production Dockerfile
# Undetected stealth web scraper & markdown extractor microservice for LLMs
# ==============================================================================

FROM python:3.11-slim

LABEL maintainer="Marcus Zou <marcus.zou@icloud.com>"
LABEL org.opencontainers.image.title="Patchtroy"
LABEL org.opencontainers.image.description="Undetected stealth web scraper & markdown extractor microservice"
LABEL org.opencontainers.image.version="0.4.6"

# Python and environment settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PATCHRIGHT_BROWSERS_PATH=/ms-playwright

# Install minimal OS dependencies for headless Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency definition and source code
COPY pyproject.toml README.md /app/
COPY src/ /app/src/

# Install patchtroy with REST microservice extras and download Chromium
RUN pip install --no-cache-dir ".[server]" \
    && patchright install chromium

# Create unprivileged user
RUN useradd -m -u 1000 patchtroy \
    && chown -R patchtroy:patchtroy /app /ms-playwright

USER patchtroy

EXPOSE 4013

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:4013/health || exit 1

ENTRYPOINT ["patchtroy"]
CMD ["serve", "--host", "0.0.0.0", "--port", "4013"]
