"""Utility functions, stealth injection scripts, and headers."""

from __future__ import annotations

import random
from urllib.parse import urlparse

DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]

STEALTH_INJECTION_SCRIPT = """
// Evade common automated browser detection signatures
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {}
};
// Emulate realistic plugins
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5],
});
// Emulate standard languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en'],
});
"""


def get_random_user_agent() -> str:
    """Return a realistic modern desktop browser User-Agent."""
    return random.choice(DEFAULT_USER_AGENTS)


def is_valid_url(url: str) -> bool:
    """Validate URL scheme is http or https."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False
