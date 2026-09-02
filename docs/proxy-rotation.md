# Proxy Rotation & Fault Quarantine

When scraping at scale, target servers may rate-limit or IP-ban requests. **Patchtroy** includes a production-grade `ProxyManager` supporting automatic rotation, format normalization, and unhealthy proxy quarantine.

---

## 🔄 Supported Proxy Strategies

- **`round-robin`** (default): Cycles sequentially through all available proxies.
- **`random`**: Randomly picks an active proxy for each leased browser context.

---

## 🐍 Python Usage

```python
from patchtroy import AsyncPatchtroy, PatchtroyConfig

config = PatchtroyConfig(
    proxies=[
        "http://user:pass@proxy1.example.com:8080",
        "socks5://proxy2.example.com:1080",
    ],
    proxy_strategy="round-robin",
    max_proxy_failures=3,      # Quarantines after 3 consecutive failures
    proxy_quarantine_s=300.0,   # Quarantined for 5 minutes
)

async with AsyncPatchtroy(config) as client:
    result = await client.scrape("https://example.com")
```

---

## 💻 CLI Usage

Provide proxies either inline or via a text file:

```bash
# Inline proxies
patchtroy https://example.com --proxy "http://user:pass@p1:8080"

# Proxy file (one proxy per line, supporting comments and credentials)
patchtroy https://site1.com https://site2.com \
  --proxy-file proxies.txt \
  --proxy-strategy random \
  -c 5
```
