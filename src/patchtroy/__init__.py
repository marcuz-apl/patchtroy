"""Patchtroy — Undetected stealth web scraper & markdown extractor for LLMs."""

from patchtroy.crawler import AsyncPatchtroy, Patchtroy
from patchtroy.models import LinkItem, PatchtroyConfig, ScrapeResult

__version__ = "0.1.0"
__author__ = "Marcus Zou"
__license__ = "MIT"

__all__ = [
    "AsyncPatchtroy",
    "LinkItem",
    "Patchtroy",
    "PatchtroyConfig",
    "ScrapeResult",
]
