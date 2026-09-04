"""Tests for Markdown chunking and token counting utility."""

from playtrafi.chunker import TextChunk, chunk_markdown, count_tokens
from playtrafi.models import ScrapeResult


def test_count_tokens():
    text = "Hello world! This is a simple token count test."
    tokens = count_tokens(text)
    assert tokens > 0
    assert count_tokens("") == 0


def test_chunk_markdown_small_doc():
    md = "# Title\n\nThis is a short markdown document with a paragraph."
    chunks = chunk_markdown(md, max_tokens=100)
    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].token_count > 0
    assert "Title" in chunks[0].text
    assert chunks[0].metadata.get("section_heading") == "# Title"


def test_chunk_markdown_multi_section():
    section1 = "# Section 1\n\n" + ("Content line for section 1. " * 30)
    section2 = "## Section 2\n\n" + ("Content line for section 2. " * 30)
    full_md = f"{section1}\n\n{section2}"

    chunks = chunk_markdown(full_md, max_tokens=50, overlap_tokens=10)
    assert len(chunks) >= 2
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i
        assert chunk.token_count <= 80  # bounded close to threshold


def test_scrape_result_chunk_method():
    res = ScrapeResult(
        url="https://example.com/test",
        title="Test Page",
        markdown="# Main Heading\n\nFirst paragraph.\n\n## Subheading\n\nSecond paragraph.",
        success=True,
    )
    chunks = res.chunk(max_tokens=2048)
    assert len(chunks) == 1
    assert chunks[0].metadata["url"] == "https://example.com/test"
    assert chunks[0].metadata["title"] == "Test Page"
    assert isinstance(chunks[0], TextChunk)
