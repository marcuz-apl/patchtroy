# LLM Chunking & Fast Tokenizer

Feeding large scraped web pages directly into LLM prompts or vector databases requires chunking long texts without cutting sentences or dropping headings.

**Patchtroy** includes a **structure-aware Markdown chunker** designed specifically for RAG architectures.

---

## ⚡ Key Features

1. **Heading-Preserving Splits**: Recursively respects `#`, `##`, `###` headings.
2. **Metadata Retention**: Every `TextChunk` records the enclosing `section_heading` in its metadata dictionary.
3. **Calibrated BPE Tokenizer**: Fast BPE token estimation (~130,000 tokens/sec) with automatic fallback to `tiktoken` when available.
4. **Configurable Overlap**: Preserves semantic continuity across chunk boundaries with `overlap_tokens`.

---

## 🐍 Python Usage

```python
from patchtroy import Patchtroy

result = Patchtroy.crawl("https://en.wikipedia.org/wiki/Artificial_intelligence")

# Split result into 1024-token chunks with 100-token overlap
chunks = result.chunk(max_tokens=1024, overlap_tokens=100)

for c in chunks:
    print(f"Chunk #{c.chunk_index} ({c.token_count} tokens):")
    print(f"Section: {c.metadata.get('section_heading')}")
    print(c.text[:200])
    print("-" * 40)
```

---

## 📋 `TextChunk` Model Specification

```python
class TextChunk:
    text: str                     # Chunk text content
    chunk_index: int              # Sequential index (0, 1, 2, ...)
    token_count: int              # Number of tokens in chunk
    metadata: dict[str, Any]      # Source URL, title, section_heading
```
