---
name: daily-ai-news
description: Use when users need comprehensive daily news about AI, large models, and related fields.
---

# Daily AI News Skill

This skill helps AI agents fetch and present daily curated AI news from the 60s API, which provides the latest updates on AI, large models, and related technologies.

## When to Use This Skill

Use this skill when users:
- Ask for today's AI news or updates on large language models
- Want a quick daily briefing on artificial intelligence
- Request AI news summaries
- Need historical AI news from a specific date
- Want AI news in different formats (text, JSON, markdown)

## How to Use

Execute the associated `scripts/news.sh` script to fetch the AI news.

```bash
./scripts/news.sh [options] [date]
```

### Options

- `--encoding, -e <format>`: Optional. Specifies the output response format. Valid options are `text`, `json`, and `markdown`. The API defaults to `json` if not specified.
- `--date, -d <YYYY-MM-DD>`: Optional. Fetch historical AI news for a specific date. If omitted, fetches today's news. Note: If this is the only argument provided, you can omit the `--date` flag entirely.

### Return Values

The script securely calls the 60s AI news API and outputs the response to `stdout`. Depending on the `encoding` parameter, the response could be a JSON string, plain text, or markdown.

### Usage Examples

```bash
# Get today's AI news using default API encoding (json)
./scripts/news.sh

# Get today's AI news in plain text format
./scripts/news.sh --encoding text

# Get AI news for a specific date using flags
./scripts/news.sh --date 2024-03-01

# Get AI news for a specific date (simplified usage without flags)
./scripts/news.sh 2024-03-01

# Get AI news for a specific date in markdown format
./scripts/news.sh -e markdown -d 2024-03-01
```

## Response Format

To balance information depth with token consumption, you **MUST** use the following rules for the `encoding` parameter:

1. **Default Strategy (`--encoding markdown`)**
   - **When to use:** By default for standard AI news inquiries.
   - **Why:** Provides well-structured, easy-to-read information with moderate token usage.

2. **Brief Information (`--encoding text`)**
   - **When to use:** When the user explicitly requests brief or summarized AI news.
   - **Why:** Returns only essential details in plain text, saving maximum tokens.

3. **Complete Information (`--encoding json`)**
   - **When to use:** Only when the user explicitly asks for raw data, detailed fields, or comprehensive data.
   - **Why:** Returns the complete API payload, which is highly token-heavy.
