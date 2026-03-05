---
name: searxng
description: Search the web using a self-hosted SearXNG instance. Privacy-respecting metasearch that aggregates results from multiple engines.
metadata:
  clawdbot:
    config:
      optionalEnv:
        - SEARXNG_URL
tools:
  - name: search
    description: Search the web using the self-hosted SearXNG instance.
    args:
      - name: query
        type: string
        description: Search query
      - name: categories
        type: string
        description: Search categories (general, images, news, videos, it, science)
        default: general
    command:
      kind: http
      method: GET
      url: ${SEARXNG_URL:-http://localhost:8080}/search
      query:
        q: ${query}
        categories: ${categories}
        format: json
---

# SearXNG Search Skill

Search the web using your self-hosted SearXNG instance.  
Privacy-respecting metasearch that aggregates results from Google, DuckDuckGo, Brave, Startpage, and many other engines.

---

## Prerequisites

SearXNG running locally or on a server.

Quick Docker setup:

```bash
mkdir -p ~/Projects/searxng/searxng
cd ~/Projects/searxng

cat > docker-compose.yml << 'EOF'
services:
  searxng:
    image: searxng/searxng:latest
    container_name: searxng
    ports:
      - "8080:8080"
    volumes:
      - ./searxng:/etc/searxng:rw
    environment:
      - SEARXNG_BASE_URL=http://localhost:8080/
    restart: unless-stopped
EOF

cat > searxng/settings.yml << 'EOF'
use_default_settings: true
server:
  secret_key: "change-me-to-random-string"
  bind_address: "127.0.0.1"
  port: 8080
search:
  safe_search: 0
  autocomplete: "google"
  default_lang: "en"
  formats:
    - html
    - json
EOF

docker compose up -d
```

---

## Configuration

Set the SearXNG URL (optional, defaults to http://localhost:8080):

```bash
export SEARXNG_URL="http://localhost:8080"
```

---

## Response Format

Each result includes:
- `title` – Result title
- `url` – Link to the result  
- `content` – Snippet/description
- `engines` – Engines returning the result
- `score` – Relevance score
- `category` – Result category

---

## Security Notes

- Default binding is `127.0.0.1` to prevent public exposure.
- Replace the default `secret_key` with a strong random value.
- Do not expose SearXNG directly to the public internet without HTTPS and authentication.
- This skill uses HTTP requests only and does not execute shell commands.

---

## Why SearXNG?

- Privacy-first (no tracking, no ads)
- Aggregates 70+ engines
- Self-hosted control
- JSON API support
- No API keys or rate limits