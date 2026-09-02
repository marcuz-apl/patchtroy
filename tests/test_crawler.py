from unittest.mock import AsyncMock, patch

import pytest

from patchtroy.crawler import AsyncPatchtroy, Patchtroy
from patchtroy.models import PatchtroyConfig, ScrapeResult


@pytest.mark.asyncio
async def test_invalid_url_handling():
    crawler = AsyncPatchtroy()
    res = await crawler.scrape("not-a-valid-url")
    assert res.success is False
    assert "Invalid HTTP/HTTPS URL" in res.error


def test_sync_invalid_url():
    crawler = Patchtroy()
    res = crawler.scrape("ftp://invalid-scheme.com")
    assert res.success is False
    assert "Invalid HTTP/HTTPS URL" in res.error


@pytest.mark.asyncio
async def test_async_scrape_many():
    crawler = AsyncPatchtroy(PatchtroyConfig(max_concurrency=3))
    mock_res = ScrapeResult(url="https://example.com", title="Example", success=True)

    with patch.object(crawler, "scrape", new_callable=AsyncMock, return_value=mock_res) as mock_scrape:
        urls = ["https://example.com/1", "https://example.com/2", "https://example.com/3"]
        results = await crawler.scrape_many(urls)
        assert len(results) == 3
        assert mock_scrape.call_count == 3
        assert all(r.success for r in results)


def test_sync_scrape_many():
    crawler = Patchtroy(PatchtroyConfig(max_concurrency=2))
    urls = ["ftp://bad-url-1", "ftp://bad-url-2"]
    results = crawler.scrape_many(urls)
    assert len(results) == 2
    assert all(not r.success for r in results)
