"""Tests for Patchtroy FastAPI REST API microservice."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from patchtroy.models import ScrapeResult
from patchtroy.server import create_app


@pytest.mark.asyncio
async def test_health_check_endpoint():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.3.0"
        assert data["engine"] == "patchright"


@pytest.mark.asyncio
async def test_scrape_endpoint_mocked():
    app = create_app()
    fake_res = ScrapeResult(
        url="https://example.com",
        title="Mocked Page",
        markdown="# Mocked Content",
        success=True,
    )

    with patch("patchtroy.server.AsyncPatchtroy") as mock_crawler_cls:
        mock_crawler = AsyncMock()
        mock_crawler.start = AsyncMock()
        mock_crawler.close = AsyncMock()
        mock_crawler.scrape = AsyncMock(return_value=fake_res)
        mock_crawler._pool = AsyncMock()
        mock_crawler._pool.is_running = True
        mock_crawler_cls.return_value = mock_crawler

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/scrape", json={"url": "https://example.com"})
            assert resp.status_code == 200
            data = resp.json()
            assert data["url"] == "https://example.com"
            assert data["title"] == "Mocked Page"
            assert data["markdown"] == "# Mocked Content"


@pytest.mark.asyncio
async def test_scrape_batch_endpoint_mocked():
    app = create_app()
    fake_res1 = ScrapeResult(url="https://example.com/1", title="Page 1", success=True)
    fake_res2 = ScrapeResult(url="https://example.com/2", title="Page 2", success=True)

    with patch("patchtroy.server.AsyncPatchtroy") as mock_crawler_cls:
        mock_crawler = AsyncMock()
        mock_crawler.start = AsyncMock()
        mock_crawler.close = AsyncMock()
        mock_crawler.scrape_many = AsyncMock(return_value=[fake_res1, fake_res2])
        mock_crawler._pool = AsyncMock()
        mock_crawler._pool.is_running = True
        mock_crawler_cls.return_value = mock_crawler

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/scrape/batch",
                json={"urls": ["https://example.com/1", "https://example.com/2"], "concurrency": 3},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert len(data) == 2
            assert data[0]["url"] == "https://example.com/1"
            assert data[1]["url"] == "https://example.com/2"
