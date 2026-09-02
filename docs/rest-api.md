# REST API Microservice & Docker Deployment

Deploy Patchtroy as a standalone microservice for non-Python applications (Node.js, Go, Rust, Ruby, C#).

---

## 🚀 Launching the Microservice

### Via CLI

```bash
patchtroy serve --host 0.0.0.0 --port 4013
```

### Via Docker

```bash
docker run -d -p 4013:4013 --name patchtroy marcuszou/patchtroy:latest
```

### Via Docker Compose

```yaml
version: "3.8"

services:
  patchtroy:
    image: marcuszou/patchtroy:latest
    container_name: patchtroy-api
    restart: unless-stopped
    ports:
      - "4013:4013"
    environment:
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4013/health"]
      interval: 30s
      timeout: 5s
      retries: 3
```

---

## 📡 API Endpoints

### 1. Health Check (`GET /health`)

```bash
curl http://localhost:4013/health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "0.4.0",
  "engine": "patchright",
  "active": true
}
```

### 2. Scrape Single URL (`POST /scrape`)

```bash
curl -X POST http://localhost:4013/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://news.ycombinator.com",
    "screenshot": true,
    "wait_for": ".athing"
  }'
```

### 3. Batch Scrape (`POST /scrape/batch`)

```bash
curl -X POST http://localhost:4013/scrape/batch \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://site1.com",
      "https://site2.com"
    ],
    "concurrency": 4
  }'
```
