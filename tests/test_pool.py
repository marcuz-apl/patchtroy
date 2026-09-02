"""Unit tests for BrowserContextPool in patchtroy."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from patchtroy.models import PatchtroyConfig
from patchtroy.pool import BrowserContextPool
from patchtroy.proxy import ProxyManager


@pytest.mark.asyncio
async def test_pool_context_acquisition():
    config = PatchtroyConfig(max_concurrency=2)
    pool = BrowserContextPool(config)

    # Mock browser and playwright objects
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_context.close = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()

    pool._browser = mock_browser

    async with pool.acquire_context(user_agent="TestAgent") as (ctx, proxy):
        assert ctx == mock_context
        assert proxy is None
        assert pool._active_contexts == 1

    assert pool._active_contexts == 0
    mock_context.close.assert_awaited_once()

    await pool.close()
    mock_browser.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_pool_with_proxy_manager():
    config = PatchtroyConfig(max_concurrency=2)
    pm = ProxyManager(proxies=["http://proxy1:8080", "http://proxy2:8080"])
    pool = BrowserContextPool(config, proxy_manager=pm)

    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_context.close = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    pool._browser = mock_browser

    async with pool.acquire_context(user_agent="TestAgent") as (ctx, proxy):
        assert proxy == "http://proxy1:8080"
        mock_browser.new_context.assert_awaited_with(
            user_agent="TestAgent",
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True,
            locale="en-US",
            proxy={"server": "http://proxy1:8080"},
        )
