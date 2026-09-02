"""Utility functions, stealth injection scripts, and platform helpers."""

from __future__ import annotations

import random
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


def silence_subprocess_transport_bug() -> None:
    """Silence Python asyncio BaseSubprocessTransport and pipe transport destructor errors.

    When an event loop finishes and closes (via asyncio.run), underlying child process
    transports may remain in the garbage collector until interpreter exit. During GC,
    their __del__ destructors attempt post-loop cleanup:
      - On Unix/Linux: calls self.close() -> loop.call_soon() -> RuntimeError('Event loop is closed')
      - On Windows: calls _warn() -> __repr__() -> fileno() -> ValueError('I/O operation on closed pipe')
    Wrapping both destructors safely catches and suppresses these post-loop cleanup errors across
    all platforms (Linux, macOS, Windows).
    """
    try:
        from asyncio.base_subprocess import BaseSubprocessTransport

        orig_sub_del = getattr(BaseSubprocessTransport, "__del__", None)
        if orig_sub_del and not getattr(BaseSubprocessTransport, "_patchtroy_safe", False):

            def _safe_sub_del(self: Any, *args: Any, **kwargs: Any) -> None:
                try:
                    orig_sub_del(self, *args, **kwargs)
                except (RuntimeError, ValueError, OSError):
                    pass

            BaseSubprocessTransport.__del__ = _safe_sub_del  # type: ignore[method-assign]
            BaseSubprocessTransport._patchtroy_safe = True  # type: ignore[attr-defined]
    except Exception:
        pass

    try:
        from asyncio.proactor_events import _ProactorBasePipeTransport

        orig_pipe_del = getattr(_ProactorBasePipeTransport, "__del__", None)
        if orig_pipe_del and not getattr(_ProactorBasePipeTransport, "_patchtroy_safe", False):

            def _safe_pipe_del(self: Any, *args: Any, **kwargs: Any) -> None:
                try:
                    orig_pipe_del(self, *args, **kwargs)
                except (RuntimeError, ValueError, OSError):
                    pass

            _ProactorBasePipeTransport.__del__ = _safe_pipe_del  # type: ignore[method-assign]
            _ProactorBasePipeTransport._patchtroy_safe = True  # type: ignore[attr-defined]
    except Exception:
        pass


# Backwards-compatible alias
silence_windows_proactor_bug = silence_subprocess_transport_bug
