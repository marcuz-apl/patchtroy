from patchtroy.models import PatchtroyConfig, ScrapeResult, LinkItem

def test_default_config():
    cfg = PatchtroyConfig()
    assert cfg.headless is True
    assert cfg.browser_timeout_s == 25.0
    assert cfg.http_fallback is True
    assert cfg.extract_schema is True

def test_custom_config():
    cfg = PatchtroyConfig(headless=False, browser_timeout_s=10.0, wait_for="article")
    assert cfg.headless is False
    assert cfg.browser_timeout_s == 10.0
    assert cfg.wait_for == "article"

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
