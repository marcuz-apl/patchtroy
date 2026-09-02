"""FastAPI REST API microservice for Patchtroy."""

from __future__ import annotations

import base64
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from pydantic import BaseModel, Field

from patchtroy.crawler import AsyncPatchtroy
from patchtroy.models import PatchtroyConfig, ScrapeResult

logger = logging.getLogger("patchtroy.server")

try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
except ImportError as exc:
    raise ImportError(
        "FastAPI is required to run the Patchtroy REST microservice. "
        "Install it via: pip install 'patchtroy[server]'"
    ) from exc


class ScrapeRequestBody(BaseModel):
    """Payload for /scrape endpoint."""

    url: str = Field(description="Target URL to scrape")
    wait_for: str | None = Field(default=None, description="CSS selector to wait for")
    wait_until: str = Field(
        default="domcontentloaded",
        description="Navigation lifecycle: domcontentloaded, load, networkidle",
    )
    timeout: float = Field(default=25.0, description="Navigation timeout in seconds")
    screenshot: bool = Field(default=False, description="Whether to capture screenshot")
    full_page: bool = Field(default=False, description="Full-page screenshot mode")
    pdf: bool = Field(default=False, description="Whether to generate PDF (headless only)")
    proxy: str | None = Field(default=None, description="Optional proxy URL for request")
    custom_schema: dict[str, Any] | None = Field(
        default=None, description="Custom declarative CSS schema"
    )


class BatchScrapeRequestBody(BaseModel):
    """Payload for /scrape/batch endpoint."""

    urls: list[str] = Field(description="List of target URLs to scrape")
    wait_for: str | None = Field(default=None, description="CSS selector to wait for")
    timeout: float = Field(default=25.0, description="Navigation timeout in seconds")
    concurrency: int = Field(default=5, ge=1, le=50, description="Concurrent browser contexts")
    custom_schema: dict[str, Any] | None = Field(
        default=None, description="Custom declarative CSS schema"
    )


def _serialize_scrape_result(res: ScrapeResult) -> dict[str, Any]:
    """Serialize ScrapeResult into a JSON-friendly dict, encoding media bytes as base64."""
    data = res.model_dump(exclude={"screenshot_bytes", "pdf_bytes"})
    if res.screenshot_bytes:
        data["screenshot_base64"] = base64.b64encode(res.screenshot_bytes).decode("ascii")
    if res.pdf_bytes:
        data["pdf_base64"] = base64.b64encode(res.pdf_bytes).decode("ascii")
    return data


def create_app() -> FastAPI:
    """Factory creating configured FastAPI microservice instance."""
    crawler_instance: AsyncPatchtroy | None = None

    async def get_crawler() -> AsyncPatchtroy:
        nonlocal crawler_instance
        if crawler_instance is None:
            crawler_instance = AsyncPatchtroy()
            await crawler_instance.start()
        return crawler_instance

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        nonlocal crawler_instance
        logger.info("Initializing Patchtroy microservice browser engine...")
        await get_crawler()
        yield
        logger.info("Terminating Patchtroy microservice browser engine...")
        if crawler_instance:
            await crawler_instance.close()
            crawler_instance = None

    app = FastAPI(
        title="Patchtroy REST Microservice",
        description="Undetected stealth web scraper & clean Markdown extractor for LLMs.",
        version="0.3.0",
        lifespan=lifespan,
    )

    @app.get("/health")
    async def health_check() -> dict[str, Any]:
        """Microservice health and status check."""
        return {
            "status": "healthy",
            "version": "0.3.0",
            "engine": "patchright",
            "active": crawler_instance is not None and crawler_instance._pool.is_running,
        }

    @app.post("/scrape")
    async def scrape_single(body: ScrapeRequestBody) -> JSONResponse:
        """Scrape a single target web page into clean Markdown."""
        crawler = await get_crawler()

        config = PatchtroyConfig(
            browser_timeout_s=body.timeout,
            wait_for=body.wait_for,
            wait_until=body.wait_until,
            screenshot=body.screenshot,
            full_page_screenshot=body.full_page,
            pdf=body.pdf,
            proxy=body.proxy,
            custom_schema=body.custom_schema,
        )
        # Create lightweight client sharing the application's browser pool
        client = AsyncPatchtroy(config)
        client._pool = crawler._pool

        result = await client.scrape(
            body.url,
            wait_for=body.wait_for,
            custom_schema=body.custom_schema,
        )

        return JSONResponse(content=_serialize_scrape_result(result))

    @app.post("/scrape/batch")
    async def scrape_batch(body: BatchScrapeRequestBody) -> JSONResponse:
        """Scrape multiple target web pages concurrently."""
        crawler = await get_crawler()

        config = PatchtroyConfig(
            browser_timeout_s=body.timeout,
            wait_for=body.wait_for,
            max_concurrency=body.concurrency,
            custom_schema=body.custom_schema,
        )
        client = AsyncPatchtroy(config)
        client._pool = crawler._pool

        results = await client.scrape_many(
            body.urls,
            wait_for=body.wait_for,
            custom_schema=body.custom_schema,
        )

        serialized = [_serialize_scrape_result(r) for r in results]
        return JSONResponse(content=serialized)

    return app


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False) -> None:
    """Launch the Uvicorn ASGI server."""
    try:
        import uvicorn
    except ImportError as exc:
        raise ImportError(
            "Uvicorn is required to run the server. "
            "Install it via: pip install 'patchtroy[server]'"
        ) from exc

    uvicorn.run("patchtroy.server:create_app", host=host, port=port, reload=reload, factory=True)
