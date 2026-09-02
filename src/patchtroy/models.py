"""Data schemas and models for Patchtroy."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class PatchtroyConfig(BaseModel):
    """Configuration options for Patchtroy crawler execution."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    headless: bool = Field(
        default=True,
        description="Run Chromium in headless mode."
    )
    browser_timeout_s: float = Field(
        default=25.0,
        ge=2.0,
        le=120.0,
        description="Maximum seconds to wait for page load before fallback or error."
    )
    wait_for: str | None = Field(
        default=None,
        description="Optional CSS selector to wait for before extracting page content."
    )
    wait_until: str = Field(
        default="domcontentloaded",
        description="Navigation lifecycle event: 'domcontentloaded', 'load', or 'networkidle'."
    )
    user_agent: str | None = Field(
        default=None,
        description="Custom User-Agent string. If omitted, uses realistic browser UA."
    )
    http_fallback: bool = Field(
        default=True,
        description="Automatically fall back to direct HTTP request if browser crashes or times out."
    )
    extract_schema: bool = Field(
        default=True,
        description="Extract JSON-LD and Next.js __NEXT_DATA__ structured items."
    )
    extract_links: bool = Field(
        default=True,
        description="Extract all valid hyperlinks from the page."
    )
    viewport_width: int = Field(default=1280, ge=320, le=3840)
    viewport_height: int = Field(default=800, ge=240, le=2160)
    proxy: str | None = Field(
        default=None,
        description="Proxy URL (e.g. 'http://user:pass@host:port')."
    )
    custom_schema: dict[str, Any] | None = Field(
        default=None,
        description="Optional declarative custom CSS selector schema for structured item harvesting."
    )


class LinkItem(BaseModel):
    """Hyperlink extracted from rendered page."""
    href: str
    text: str = ""


class ScrapeResult(BaseModel):
    """Result emitted from a Patchtroy scrape operation."""

    url: str
    status_code: int = 200
    title: str = ""
    markdown: str = ""
    html: str = ""
    structured_data: list[dict[str, Any]] = Field(default_factory=list)
    links: list[LinkItem] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error: str | None = None
    engine_used: str = "patchright"
    elapsed_s: float = 0.0

    @property
    def has_content(self) -> bool:
        return bool(self.markdown.strip() or self.structured_data)
