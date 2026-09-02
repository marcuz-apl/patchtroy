"""Proxy rotation manager for Patchtroy."""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

logger = logging.getLogger("patchtroy.proxy")

ProxyStrategy = Literal["round-robin", "random"]


@dataclass
class ProxyItem:
    """Represents a single proxy with health and failure tracking."""

    server: str
    failures: int = 0
    quarantined_until: float = 0.0

    @property
    def is_healthy(self) -> bool:
        """Return True if proxy is not quarantined."""
        return time.monotonic() >= self.quarantined_until

    def mark_failure(self, max_failures: int = 3, quarantine_seconds: float = 60.0) -> None:
        """Increment failure counter and quarantine if threshold is reached."""
        self.failures += 1
        if self.failures >= max_failures:
            self.quarantined_until = time.monotonic() + quarantine_seconds
            logger.warning(
                "Proxy %s quarantined for %.1fs after %d failures",
                self.server,
                quarantine_seconds,
                self.failures,
            )

    def mark_success(self) -> None:
        """Reset failures counter upon a successful request."""
        self.failures = 0
        self.quarantined_until = 0.0


class ProxyManager:
    """Manages a pool of proxies with rotation strategies and fault recovery."""

    def __init__(
        self,
        proxies: list[str] | str | Path | None = None,
        strategy: ProxyStrategy = "round-robin",
        max_failures: int = 3,
        quarantine_seconds: float = 60.0,
    ) -> None:
        self.strategy: ProxyStrategy = strategy
        self.max_failures = max_failures
        self.quarantine_seconds = quarantine_seconds
        self._index: int = 0
        self._items: list[ProxyItem] = []

        if proxies:
            self.load_proxies(proxies)

    def load_proxies(self, proxies: list[str] | str | Path) -> None:
        """Load proxies from a list of URLs, a comma-separated string, or a file path."""
        proxy_list: list[str] = []

        if isinstance(proxies, (str, Path)):
            path = Path(proxies)
            if path.is_file():
                content = path.read_text(encoding="utf-8")
                proxy_list = [
                    line.strip()
                    for line in content.splitlines()
                    if line.strip() and not line.strip().startswith("#")
                ]
            elif isinstance(proxies, str):
                proxy_list = [p.strip() for p in proxies.split(",") if p.strip()]
        elif isinstance(proxies, list):
            proxy_list = [p.strip() for p in proxies if p and p.strip()]

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for p in proxy_list:
            # Ensure protocol prefix exists if not provided
            normalized = p if "://" in p else f"http://{p}"
            if normalized not in seen:
                seen.add(normalized)
                unique.append(normalized)

        self._items = [ProxyItem(server=p) for p in unique]
        self._index = 0
        logger.info("Loaded %d proxies into ProxyManager", len(self._items))

    def __len__(self) -> int:
        return len(self._items)

    @property
    def has_proxies(self) -> bool:
        """Return True if at least one proxy is loaded."""
        return len(self._items) > 0

    def get_proxy(self) -> str | None:
        """Select next healthy proxy based on configured strategy."""
        if not self._items:
            return None

        healthy = [item for item in self._items if item.is_healthy]
        # If all proxies are currently quarantined, use least-recently quarantined as fallback
        pool = healthy if healthy else self._items

        if self.strategy == "random":
            chosen = random.choice(pool)
            return chosen.server

        # Round-robin selection
        chosen = pool[self._index % len(pool)]
        self._index = (self._index + 1) % len(pool)
        return chosen.server

    def report_failure(self, proxy_server: str) -> None:
        """Record a failure for the specified proxy server."""
        for item in self._items:
            if item.server == proxy_server:
                item.mark_failure(
                    max_failures=self.max_failures,
                    quarantine_seconds=self.quarantine_seconds,
                )
                break

    def report_success(self, proxy_server: str) -> None:
        """Record a success for the specified proxy server."""
        for item in self._items:
            if item.server == proxy_server:
                item.mark_success()
                break
