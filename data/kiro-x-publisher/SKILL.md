---
name: kiro-x-hot-publisher
version: 1.1.0
description: Discover hot topics on X, enrich tweets one-by-one, score and summarize signals, generate one tweet draft, and optionally publish on schedule.
homepage: https://x.com
metadata:
  {
    "openclaw":
      {
        "emoji": "🐦",
        "primaryEnv": "X_BEARER_TOKEN",
        "requires":
          {
            "bins": ["python3"],
            "env":
              [
                "X_BEARER_TOKEN",
                "X_API_KEY",
                "X_API_SECRET",
                "X_ACCESS_TOKEN",
                "X_ACCESS_TOKEN_SECRET",
              ],
          },
      },
  }
---

# Kiro X Hot Publisher

Plugin producer: `kiroai.io`

End-to-end X workflow for Kiro:

1. Discover trending tweets from X API
2. Enrich each candidate via FxTwitter (full text/article support)
3. Score and rank (engagement + freshness)
4. Summarize key signals
5. Generate exactly one tweet draft
6. Optionally publish via X API (OAuth 1.0a)

## Files

- `scripts/x_hot_pipeline.py`
- `examples/cron_command.txt`

## Required env vars

Search:

- `X_BEARER_TOKEN` (recommended)

Publish (optional, only when `--post`):

- `X_API_KEY`
- `X_API_SECRET`
- `X_ACCESS_TOKEN`
- `X_ACCESS_TOKEN_SECRET`

## Quick start

```bash
python3 skills/kiro-x-hot-publisher/scripts/install_and_init.py

python3 skills/kiro-x-hot-publisher/scripts/x_hot_pipeline.py \
  --queries "AI,OpenAI,DeepSeek,Claude,Gemini" \
  --batch-size 10
```

Post directly:

```bash
python3 skills/kiro-x-hot-publisher/scripts/x_hot_pipeline.py \
  --queries "AI,OpenAI,DeepSeek" \
  --batch-size 10 \
  --post
```

## Output

Default output folder: `./outputs/x-hot/`

Generated files:

- `latest.json`: full structured result
- `latest.txt`: plain-text briefing + final tweet draft

## Notes

- This workflow is designed for public tweets only.
- FxTwitter is a third-party dependency for enrichment; if unavailable, base X data is still used.
- Keep `--batch-size` small initially (recommended `10`).


## Changelog

- 1.1.0: Security hardening for `scripts/setup_cron.sh` (input validation and command construction safeguards).
