# Screenshots & PDF Export

Playtrafi supports full visual and document capture alongside clean text and Markdown extraction.

---

## 📸 Media Capture Options

| Option | Type | Description |
| :--- | :--- | :--- |
| `screenshot` | `bool` | Captures viewport screenshot (PNG bytes). |
| `full_page_screenshot` | `bool` | Scrolls and captures entire full-length page. |
| `pdf` | `bool` | Generates a formatted PDF document. |

---

## 🐍 Python Usage

```python
from playtrafi import Playtrafi, PlaytrafiConfig

config = PlaytrafiConfig(
    screenshot=True,
    full_page_screenshot=True,
    pdf=True,
)

crawler = Playtrafi(config)
with crawler:
    result = crawler.scrape("https://example.com")

    # Save captured media directly to disk
    if result.screenshot_bytes:
        result.save_screenshot("page_screenshot.png")

    if result.pdf_bytes:
        result.save_pdf("page_document.pdf")
```

---

## 💻 CLI Usage

```bash
# Standard viewport screenshot
playtrafi https://example.com --screenshot page.png

# Full-page screenshot and PDF
playtrafi https://example.com --screenshot full.png --full-page --pdf doc.pdf
```
