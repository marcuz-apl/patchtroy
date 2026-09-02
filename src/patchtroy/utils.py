"""Utility functions, stealth injection scripts, and platform helpers."""

from __future__ import annotations

import random
import sys
from typing import Any
from urllib.parse import urlparse

DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]

STEALTH_INJECTION_SCRIPT = """
// Configure natural browser environment signatures
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
// Emulate permissions query
if (window.navigator && window.navigator.permissions) {
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: 'default' }) :
            originalQuery(parameters)
    );
}
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


def silence_windows_proactor_bug() -> None:
    """Silence known Python Windows asyncio proactor pipe transport bug.

    On Windows, when an asyncio subprocess transport is garbage collected after
    loop shutdown, _ProactorBasePipeTransport.__del__ and BaseSubprocessTransport.__del__
    call __repr__, which calls fileno() on a closed pipe handle and raises
    ValueError: I/O operation on closed pipe. This wraps both destructors to cleanly
    catch and ignore closed pipe errors during interpreter teardown.
    """
    if sys.platform != "win32":
        return

    try:
        from asyncio.proactor_events import _ProactorBasePipeTransport

        orig_pipe_del = getattr(_ProactorBasePipeTransport, "__del__", None)
        if orig_pipe_del and not getattr(_ProactorBasePipeTransport, "_patchtroy_safe", False):

            def _safe_pipe_del(self: Any, *args: Any, **kwargs: Any) -> None:
                try:
                    orig_pipe_del(self, *args, **kwargs)
                except (ValueError, OSError):
                    pass

            _ProactorBasePipeTransport.__del__ = _safe_pipe_del  # type: ignore[method-assign]
            _ProactorBasePipeTransport._patchtroy_safe = True  # type: ignore[attr-defined]
    except Exception:
        pass

    try:
        from asyncio.base_subprocess import BaseSubprocessTransport

        orig_sub_del = getattr(BaseSubprocessTransport, "__del__", None)
        if orig_sub_del and not getattr(BaseSubprocessTransport, "_patchtroy_safe", False):

            def _safe_sub_del(self: Any, *args: Any, **kwargs: Any) -> None:
                try:
                    orig_sub_del(self, *args, **kwargs)
                except (ValueError, OSError):
                    pass

            BaseSubprocessTransport.__del__ = _safe_sub_del  # type: ignore[method-assign]
            BaseSubprocessTransport._patchtroy_safe = True  # type: ignore[attr-defined]
    except Exception:
        pass
