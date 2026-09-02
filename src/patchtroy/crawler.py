"""Core crawler implementations for Patchtroy."""

from __future__ import annotations

import asyncio
import logging
import sys
import time
from typing import Any

import httpx

from patchtroy.extractors import (
    extract_links,
    extract_markdown_and_metadata,
    extract_structured_data,
)
from patchtroy.models import LinkItem, PatchtroyConfig, ScrapeResult
from patchtroy.utils import STEALTH_INJECTION_SCRIPT, get_random_user_agent, is_valid_url

logger = logging.getLogger("patchtroy.crawler")


class AsyncPatchtroy:
    """Asynchronous stealth web crawler powered by Patchright and Trafilatura."""

    def __init__(self, config: PatchtroyConfig | dict[str, Any] | None = None) -> None:
        if isinstance(config, dict):
            self.config = PatchtroyConfig(**config)
        elif isinstance(config, PatchtroyConfig):
            self.config = config
        else:
            self.config = PatchtroyConfig()

        self._playwright: Any = None
        self._browser: Any = None

    async def __aenter__(self) -> AsyncPatchtroy:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def start(self) -> None:
        """Launch underlying stealth Patchright Chromium browser process."""
        if self._browser is not None:
            return

        try:
            try:
                from patchright.async_api import async_playwright
            except ImportError:
                from playwright.async_api import async_playwright

            self._playwright = await async_playwright().start()
            launch_args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
            self._browser = await self._playwright.chromium.launch(
                headless=self.config.headless,
                args=launch_args,
            )
        except Exception as exc:
            logger.warning("Patchright/Playwright launch failed: %s", exc)
            self._browser = None

    async def close(self) -> None:
        """Gracefully terminate browser instance and playwright context."""
        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass
            self._browser = None

        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

    async def scrape(
        self,
        url: str,
        wait_for: str | None = None,
        custom_schema: dict[str, Any] | None = None,
    ) -> ScrapeResult:
        """Scrape a target URL using stealth browser automation, with optional HTTP fallback."""
        if not is_valid_url(url):
            return ScrapeResult(
                url=url,
                status_code=400,
                success=False,
                error=f"Invalid HTTP/HTTPS URL: {url}",
            )

        start_time = time.perf_counter()
        wait_for_selector = wait_for or self.config.wait_for
        ua = self.config.user_agent or get_random_user_agent()

        # 1. Attempt stealth browser navigation
        try:
            return await self._scrape_with_browser(url, ua, wait_for_selector, custom_schema, start_time)
        except Exception as exc:
            logger.info("Browser scrape encountered issue: %s", exc)
            if self.config.http_fallback:
                logger.info("Engaging HTTP fallback for %s", url)
                return await self._scrape_with_http(url, ua, custom_schema, start_time, str(exc))
            else:
                elapsed = time.perf_counter() - start_time
                return ScrapeResult(
                    url=url,
                    status_code=500,
                    success=False,
                    error=str(exc),
                    elapsed_s=round(elapsed, 3),
                )

    async def _scrape_with_browser(
        self,
        url: str,
        user_agent: str,
        wait_for_selector: str | None,
        custom_schema: dict[str, Any] | None,
        start_time: float,
    ) -> ScrapeResult:
        """Execute in-browser rendering with stealth injection."""
        if self._browser is None:
            await self.start()
        if self._browser is None:
            raise RuntimeError("No stealth browser instance available.")

        timeout_ms = int(self.config.browser_timeout_s * 1000)

        context_kwargs: dict[str, Any] = {
            "user_agent": user_agent,
            "viewport": {"width": self.config.viewport_width, "height": self.config.viewport_height},
            "ignore_https_errors": True,
            "locale": "en-US",
        }
        if self.config.proxy:
            context_kwargs["proxy"] = {"server": self.config.proxy}

        context = await self._browser.new_context(**context_kwargs)
        page = await context.new_page()

        try:
            # Inject stealth evasions
            await page.add_init_script(STEALTH_INJECTION_SCRIPT)

            resp = await page.goto(
                url,
                timeout=timeout_ms,
                wait_until=self.config.wait_until,
            )

            status_code = resp.status if resp else 200

            if wait_for_selector:
                try:
                    await page.wait_for_selector(wait_for_selector, timeout=7000)
                except Exception as wait_exc:
                    logger.debug("wait_for selector '%s' timeout: %s", wait_for_selector, wait_exc)

            html = await page.content()
            final_url = page.url or url

            # Content extractions
            markdown, title, metadata = extract_markdown_and_metadata(html, base_url=final_url)
            structured_data = []
            if self.config.extract_schema:
                schema_to_use = custom_schema or self.config.custom_schema
                structured_data = extract_structured_data(html, source_url=final_url, custom_schema=schema_to_use)

            links = []
            if self.config.extract_links:
                raw_links = extract_links(html, base_url=final_url)
                links = [LinkItem(**l) for l in raw_links]

            elapsed = time.perf_counter() - start_time
            return ScrapeResult(
                url=final_url,
                status_code=status_code,
                title=title,
                markdown=markdown,
                html=html,
                structured_data=structured_data,
                links=links,
                metadata=metadata,
                success=True,
                engine_used="patchright",
                elapsed_s=round(elapsed, 3),
            )
        finally:
            await page.close()
            await context.close()

    async def _scrape_with_http(
        self,
        url: str,
        user_agent: str,
        custom_schema: dict[str, Any] | None,
        start_time: float,
        browser_error: str,
    ) -> ScrapeResult:
        """Fast direct HTTP fallback when browser engine is unavailable or timed out."""
        headers = {"User-Agent": user_agent, "Accept-Language": "en-US,en;q=0.9"}
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=self.config.browser_timeout_s,
                verify=False,
            ) as client:
                resp = await client.get(url, headers=headers)
                html = resp.text
                final_url = str(resp.url)
                status_code = resp.status_code

            markdown, title, metadata = extract_markdown_and_metadata(html, base_url=final_url)
            structured_data = []
            if self.config.extract_schema:
                schema_to_use = custom_schema or self.config.custom_schema
                structured_data = extract_structured_data(html, source_url=final_url, custom_schema=schema_to_use)

            links = []
            if self.config.extract_links:
                raw_links = extract_links(html, base_url=final_url)
                links = [LinkItem(**l) for l in raw_links]

            elapsed = time.perf_counter() - start_time
            return ScrapeResult(
                url=final_url,
                status_code=status_code,
                title=title,
                markdown=markdown,
                html=html,
                structured_data=structured_data,
                links=links,
                metadata=metadata,
                success=resp.is_success,
                error=f"HTTP fallback (browser failed: {browser_error})",
                engine_used="http_fallback",
                elapsed_s=round(elapsed, 3),
            )
        except Exception as http_exc:
            elapsed = time.perf_counter() - start_time
            return ScrapeResult(
                url=url,
                status_code=500,
                success=False,
                error=f"Both browser and HTTP fallback failed. Browser: {browser_error} | HTTP: {http_exc}",
                engine_used="failed",
                elapsed_s=round(elapsed, 3),
            )

    @classmethod
    async def crawl(
        cls,
        url: str,
        headless: bool = True,
        wait_for: str | None = None,
        custom_schema: dict[str, Any] | None = None,
    ) -> ScrapeResult:
        """One-shot convenience coroutine for instant scraping."""
        async with cls(PatchtroyConfig(headless=headless, wait_for=wait_for)) as client:
            return await client.scrape(url, wait_for=wait_for, custom_schema=custom_schema)


class Patchtroy:
    """Synchronous wrapper for Patchtroy crawler execution."""

    def __init__(self, config: PatchtroyConfig | dict[str, Any] | None = None) -> None:
        self._async_crawler = AsyncPatchtroy(config)

    def scrape(
        self,
        url: str,
        wait_for: str | None = None,
        custom_schema: dict[str, Any] | None = None,
    ) -> ScrapeResult:
        """Execute scrape synchronously in an event loop."""
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        return asyncio.run(self._async_crawler.scrape(url, wait_for=wait_for, custom_schema=custom_schema))

    @classmethod
    def crawl(
        cls,
        url: str,
        headless: bool = True,
        wait_for: str | None = None,
        custom_schema: dict[str, Any] | None = None,
    ) -> ScrapeResult:
        """Synchronous one-shot convenience function for scraping."""
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        return asyncio.run(AsyncPatchtroy.crawl(url, headless=headless, wait_for=wait_for, custom_schema=custom_schema))
