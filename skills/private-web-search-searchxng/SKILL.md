---
name: private-web-search-searchxng
description: Self-hosted private web search using SearXNG. Use when privacy is important, external APIs are blocked, you need search without tracking, or want to avoid paid search APIs.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["docker", "curl", "jq"] },
        "install":
          [
            {
              "id": "docker",
              "kind": "bin",
              "command": "docker --version",
              "label": "Docker required",
            },
          ],
      },
  }
---

# Private Web Search (SearXNG)

Privacy-respecting, self-hosted metasearch engine for AI agents.

## Quick Setup

```bash
# 1. Start container
docker run -d --name searxng -p 8080:8080 -e BASE_URL=http://localhost:8080/ searxng/searxng

# 2. Enable JSON API
docker exec searxng sed -i 's/  formats:/  formats:\n    - json/' /etc/searxng/settings.yml
docker restart searxng

# 3. Verify
curl -sL "http://localhost:8080/search?q=test&format=json" | jq '.results[0]'
```

## Usage

### Basic Search

```bash
curl -sL "http://localhost:8080/search?q=YOUR_QUERY&format=json" | jq '.results[:10]'
```

### Using the Helper Script

```bash
./scripts/search.sh "openclaw ai" 5
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| SEARXNG_PORT | 8080 | Container port |
| SEARXNG_HOST | localhost | Server host |
| BASE_URL | http://localhost:8080 | Public URL |

## Available Engines

Google, Bing, DuckDuckGo, Brave, Startpage, Wikipedia, and more.

## Management

```bash
docker start searxng   # Start
docker stop searxng    # Stop
docker logs searxng    # View logs
docker rm searxng -f   # Remove
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No results | Check `docker logs searxng` |
| 403 Forbidden | Enable JSON format (step 2) |
| Connection refused | Run `docker start searxng` |
