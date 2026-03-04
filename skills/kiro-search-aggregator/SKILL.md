---
name: kiro-search-aggregator
description: Multi-source search skill for Kiro on OpenClaw. Aggregate and rank results from Google, Google Scholar, YouTube, and X, then output a concise brief.
homepage: https://openclaw.ai
metadata:
  {
    "openclaw":
      {
        "emoji": "🔎",
        "primaryEnv": "SERPER_API_KEY",
        "requires":
          {
            "bins": ["python3"],
            "env": ["SERPER_API_KEY", "SERPAPI_API_KEY", "X_BEARER_TOKEN"],
          },
      },
  }
---

# Kiro Search Aggregator

Plugin producer: `kiroai.io`

Aggregate search results across multiple providers and return one ranked list with a short summary.

## Supported Sources

- `google` (Serper API)
- `scholar` (SerpAPI, `google_scholar` engine)
- `youtube` (Serper videos API)
- `x` (X recent search API)

## API keys

Optional, per source:

- `SERPER_API_KEY` for `google`, `youtube`
- `SERPAPI_API_KEY` for `scholar`
- `X_BEARER_TOKEN` for `x`

## Quick start

```bash
python3 skills/kiro-search-aggregator/scripts/search_aggregator.py \
  --query "AI agents workflow" \
  --sources "google,scholar,youtube,x" \
  --per-source 5
```

## Output

Default folder: `outputs/search-aggregator/`

- `latest.json`: full machine-readable result
- `latest.md`: readable summary + top results
