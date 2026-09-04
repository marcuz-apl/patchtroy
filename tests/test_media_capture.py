"""Unit tests for media capture (Screenshots & PDFs) in playtrafi."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from playtrafi.crawler import AsyncPlaytrafi
from playtrafi.models import PlaytrafiConfig


@pytest.mark.asyncio
async def test_scrape_with_media_capture(tmp_path: Path):
    shot_path = tmp_path / "page.png"
    pdf_path = tmp_path / "page.pdf"

    config = PlaytrafiConfig(
        screenshot=True,
        full_page_screenshot=True,
        screenshot_path=str(shot_path),
        pdf=True,
        pdf_path=str(pdf_path),
    )

    crawler = AsyncPlaytrafi(config)

    # Mock page and context
    mock_page = MagicMock()
    mock_page.add_init_script = AsyncMock()
    mock_page.goto = AsyncMock(return_value=MagicMock(status=200))
    mock_page.screenshot = AsyncMock(return_value=b"fake-png-data")
    mock_page.pdf = AsyncMock(return_value=b"fake-pdf-data")
    mock_page.content = AsyncMock(return_value="<html><body><h1>Test</h1><p>Content</p></body></html>")
    mock_page.url = "https://example.com"
    mock_page.close = AsyncMock()

    mock_context = MagicMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()

    crawler._pool._browser = MagicMock()
    crawler._pool._browser.new_context = AsyncMock(return_value=mock_context)

    result = await crawler.scrape("https://example.com")

    assert result.success is True
    assert result.screenshot_bytes == b"fake-png-data"
    assert result.pdf_bytes == b"fake-pdf-data"
    mock_page.screenshot.assert_awaited_once_with(full_page=True)
    mock_page.pdf.assert_awaited_once()

    # Files should have been written to disk
    assert shot_path.is_file()
    assert shot_path.read_bytes() == b"fake-png-data"
    assert pdf_path.is_file()
    assert pdf_path.read_bytes() == b"fake-pdf-data"
