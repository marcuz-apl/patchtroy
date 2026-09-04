from unittest.mock import AsyncMock, patch

import pytest

from playtrafi.crawler import (
    AsyncPatchtroy,
    AsyncPlaytrafi,
    Patchtroy,
    Playtrafi,
)
from playtrafi.models import PatchtroyConfig, PlaytrafiConfig, ScrapeResult


@pytest.mark.asyncio
async def test_invalid_url_handling():
    crawler = AsyncPlaytrafi()
    res = await crawler.scrape("not-a-valid-url")
    assert res.success is False
    assert "Invalid HTTP/HTTPS URL" in res.error
    # Test backwards compatibility alias
    assert AsyncPatchtroy is AsyncPlaytrafi
    assert PatchtroyConfig is PlaytrafiConfig


def test_sync_invalid_url():
    crawler = Playtrafi()
    res = crawler.scrape("ftp://invalid-scheme.com")
    assert res.success is False
    assert "Invalid HTTP/HTTPS URL" in res.error
    # Test backwards compatibility alias
    assert Patchtroy is Playtrafi


@pytest.mark.asyncio
async def test_async_scrape_many():
    crawler = AsyncPlaytrafi(PlaytrafiConfig(max_concurrency=3))
    mock_res = ScrapeResult(url="https://example.com", title="Example", success=True)

    with patch.object(crawler, "scrape", new_callable=AsyncMock, return_value=mock_res) as mock_scrape:
        urls = ["https://example.com/1", "https://example.com/2", "https://example.com/3"]
        results = await crawler.scrape_many(urls)
        assert len(results) == 3
        assert mock_scrape.call_count == 3
        assert all(r.success for r in results)


def test_sync_scrape_many():
    crawler = Playtrafi(PlaytrafiConfig(max_concurrency=2))
    urls = ["ftp://bad-url-1", "ftp://bad-url-2"]
    results = crawler.scrape_many(urls)
    assert len(results) == 2
    assert all(not r.success for r in results)
    crawler.close()


def test_sync_context_manager():
    with Playtrafi() as crawler:
        res = crawler.scrape("ftp://bad-url")
        assert res.success is False


def test_silence_windows_proactor_bug():
    from playtrafi.utils import silence_windows_proactor_bug

    # Should execute cleanly across all platforms
    silence_windows_proactor_bug()

