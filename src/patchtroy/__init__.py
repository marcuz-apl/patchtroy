"""Patchtroy — Undetected stealth web scraper & markdown extractor for LLMs."""

from patchtroy.chunker import TextChunk, chunk_markdown, count_tokens
from patchtroy.crawler import AsyncPatchtroy, Patchtroy
from patchtroy.models import LinkItem, PatchtroyConfig, ScrapeResult
from patchtroy.pool import BrowserContextPool
from patchtroy.proxy import ProxyItem, ProxyManager

__version__ = "0.3.0"
__author__ = "Marcus Zou"
__license__ = "MIT"

__all__ = [
    "AsyncPatchtroy",
    "BrowserContextPool",
    "LinkItem",
    "Patchtroy",
    "PatchtroyConfig",
    "ProxyItem",
    "ProxyManager",
    "ScrapeResult",
    "TextChunk",
    "chunk_markdown",
    "count_tokens",
]
