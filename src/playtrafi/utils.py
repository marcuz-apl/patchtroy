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
        if orig_sub_del and not getattr(BaseSubprocessTransport, "_playtrafi_safe", False):

            def _safe_sub_del(self: Any, *args: Any, **kwargs: Any) -> None:
                try:
                    orig_sub_del(self, *args, **kwargs)
                except (RuntimeError, ValueError, OSError):
                    pass

            BaseSubprocessTransport.__del__ = _safe_sub_del  # type: ignore[method-assign]
            BaseSubprocessTransport._playtrafi_safe = True  # type: ignore[attr-defined]
    except Exception:
        pass

    try:
        from asyncio.proactor_events import _ProactorBasePipeTransport

        orig_pipe_del = getattr(_ProactorBasePipeTransport, "__del__", None)
        if orig_pipe_del and not getattr(_ProactorBasePipeTransport, "_playtrafi_safe", False):

            def _safe_pipe_del(self: Any, *args: Any, **kwargs: Any) -> None:
                try:
                    orig_pipe_del(self, *args, **kwargs)
                except (RuntimeError, ValueError, OSError):
                    pass

            _ProactorBasePipeTransport.__del__ = _safe_pipe_del  # type: ignore[method-assign]
            _ProactorBasePipeTransport._playtrafi_safe = True  # type: ignore[attr-defined]
    except Exception:
        pass


# Backwards-compatible alias
silence_windows_proactor_bug = silence_subprocess_transport_bug


def results_to_csv(results: Any) -> str:
    """Convert one or multiple ScrapeResult instances into standard RFC 4180 CSV text.

    Args:
        results: A single ScrapeResult or an iterable/list of ScrapeResult instances.

    Returns:
        A valid CSV string containing header and data rows.
    """
    import csv
    import io

    if not isinstance(results, (list, tuple)):
        items = [results]
    else:
        items = list(results)

    fieldnames = [
        "url",
        "success",
        "status_code",
        "title",
        "author",
        "date",
        "token_count",
        "elapsed_s",
        "engine_used",
        "markdown",
        "error",
    ]

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        quoting=csv.QUOTE_MINIMAL,
        lineterminator="\n",
    )
    writer.writeheader()

    for r in items:
        meta = getattr(r, "metadata", {}) or {}
        author = meta.get("author") or meta.get("byline") or ""
        date = meta.get("date") or meta.get("published_time") or ""
        token_count = meta.get("token_count", 0)
        markdown_str = getattr(r, "markdown", "") or ""
        if not token_count and markdown_str:
            try:
                from playtrafi.chunker import count_tokens
                token_count = count_tokens(markdown_str)
            except Exception:
                token_count = len(markdown_str) // 4

        writer.writerow({
            "url": getattr(r, "url", ""),
            "success": getattr(r, "success", True),
            "status_code": getattr(r, "status_code", 200),
            "title": getattr(r, "title", "") or "",
            "author": author,
            "date": date,
            "token_count": token_count,
            "elapsed_s": round(float(getattr(r, "elapsed_s", 0.0) or 0.0), 3),
            "engine_used": getattr(r, "engine_used", "patchright"),
            "markdown": markdown_str,
            "error": getattr(r, "error", "") or "",
        })

    return output.getvalue()

