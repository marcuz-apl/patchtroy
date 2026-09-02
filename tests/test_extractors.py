import json
from patchtroy.extractors import (
    extract_markdown_and_metadata,
    extract_structured_data,
    extract_links,
)

def test_extract_markdown():
    html = """
    <html>
      <head><title>Test Article Title</title></head>
      <body>
        <nav><a href="/">Home</a></nav>
        <article>
          <h1>Deep Dive into Patchtroy</h1>
          <p>Patchtroy pairs Patchright with Trafilatura for undetected crawling.</p>
        </article>
        <footer>Copyright 2026</footer>
      </body>
    </html>
    """
    md, title, meta = extract_markdown_and_metadata(html, "https://example.com/article")
    assert "Deep Dive into Patchtroy" in md or "Patchtroy" in md
    assert title == "Test Article Title" or "Deep Dive" in title

def test_extract_json_ld():
    html = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "Product",
          "name": "Stealth Keyboard",
          "price": "99.99"
        }
        </script>
      </head>
      <body><h1>Product Page</h1></body>
    </html>
    """
    data = extract_structured_data(html, "https://shop.example/product")
    assert len(data) == 1
    assert data[0]["name"] == "Stealth Keyboard"
    assert data[0]["@type"] == "Product"

def test_extract_next_data():
    html = """
    <html>
      <body>
        <script id="__NEXT_DATA__" type="application/json">
        {
          "props": {
            "pageProps": {
              "products": [
                {"id": 1, "title": "Wireless Mouse"},
                {"id": 2, "title": "Mechanical Keyboard"}
              ]
            }
          }
        }
        </script>
      </body>
    </html>
    """
    data = extract_structured_data(html, "https://nextjs.example/store")
    assert len(data) == 2
    assert data[0]["title"] == "Wireless Mouse"
    assert data[1]["title"] == "Mechanical Keyboard"

def test_extract_custom_schema():
    html = """
    <div class="listing">
      <h2 class="title">First Car</h2>
      <span class="price">5,000</span>
    </div>
    <div class="listing">
      <h2 class="title">Second Car</h2>
      <span class="price">2,000</span>
    </div>
    """
    schema = {
        "item_selector": ".listing",
        "fields": {"car_name": ".title", "cost": ".price"}
    }
    data = extract_structured_data(html, "https://cars.example/", custom_schema=schema)
    assert len(data) == 2
    assert data[0]["car_name"] == "First Car"
    assert data[0]["cost"] == "5,000"
    assert data[1]["car_name"] == "Second Car"
