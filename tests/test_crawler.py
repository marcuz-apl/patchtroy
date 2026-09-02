import pytest
from patchtroy.crawler import AsyncPatchtroy, Patchtroy
from patchtroy.models import PatchtroyConfig

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
