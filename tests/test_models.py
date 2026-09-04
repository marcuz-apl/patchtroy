from pathlib import Path

import pytest

from playtrafi.models import LinkItem, PatchtroyConfig, PlaytrafiConfig, ScrapeResult


def test_default_config():
    cfg = PlaytrafiConfig()
    assert cfg.headless is True
    assert cfg.browser_timeout_s == 25.0
    assert cfg.http_fallback is True
    assert cfg.extract_schema is True
    assert cfg.max_concurrency == 5
    assert cfg.screenshot is False
    assert cfg.pdf is False
    # Test backwards compatibility alias
    assert PatchtroyConfig is PlaytrafiConfig


def test_custom_config():
    cfg = PlaytrafiConfig(
        headless=False,
        browser_timeout_s=10.0,
        wait_for="article",
        max_concurrency=10,
        screenshot=True,
        pdf=True,
        proxies=["http://proxy1:8080", "http://proxy2:8080"],
    )
    assert cfg.headless is False
    assert cfg.browser_timeout_s == 10.0
    assert cfg.wait_for == "article"
    assert cfg.max_concurrency == 10
    assert cfg.screenshot is True
    assert cfg.pdf is True
    assert len(cfg.proxies) == 2


def test_scrape_result():
    res = ScrapeResult(
        url="https://example.com",
        title="Example",
        markdown="# Example\nContent",
        links=[LinkItem(href="https://example.com/about", text="About")],
    )
    assert res.success is True
    assert res.has_content is True
    assert len(res.links) == 1
    assert res.links[0].href == "https://example.com/about"


def test_scrape_result_save_media(tmp_path: Path):
    res = ScrapeResult(
        url="https://example.com",
        screenshot_bytes=b"fake-png-bytes",
        pdf_bytes=b"fake-pdf-bytes",
    )

    png_path = tmp_path / "shot.png"
    pdf_path = tmp_path / "doc.pdf"

    saved_png = res.save_screenshot(png_path)
    assert saved_png.is_file()
    assert saved_png.read_bytes() == b"fake-png-bytes"

    saved_pdf = res.save_pdf(pdf_path)
    assert saved_pdf.is_file()
    assert saved_pdf.read_bytes() == b"fake-pdf-bytes"


def test_scrape_result_save_media_missing():
    res = ScrapeResult(url="https://example.com")
    with pytest.raises(ValueError, match="No screenshot bytes available"):
        res.save_screenshot("/tmp/shot.png")

    with pytest.raises(ValueError, match="No PDF bytes available"):
        res.save_pdf("/tmp/doc.pdf")
