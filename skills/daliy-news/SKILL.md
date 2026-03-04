---
name: daily-news
description: Use when users need daily news summaries, current events, or want to stay informed about world news in Chinese.
---

# Daily News Skill

This skill helps AI agents fetch and present daily curated news from the 60s API, which provides 15 selected news items plus a daily quote.

## When to Use This Skill

Use this skill when users:
- Ask for today's news or current events
- Want a quick daily briefing
- Request news summaries in Chinese
- Need historical news from a specific date
- Want news in different formats (text, markdown, image)

## How to Use

Execute the associated `scripts/news.sh` script to fetch the news.

```bash
./scripts/news.sh [options] [date]
```

### Options

- `--encoding, -e <format>`: Optional. Specifies the output response format. Valid options are `text`, `json`, `markdown`, `image`, and `image-proxy`. The API defaults to `json` if not specified.
- `--date, -d <YYYY-MM-DD>`: Optional. Fetch historical news for a specific date. If omitted, fetches today's news. Note: If this is the only argument provided, you can omit the `--date` flag entirely.

### Return Values

The script securely calls the 60s API and outputs the response to `stdout`. Depending on the `encoding` parameter, the response could be a JSON string, plain text, markdown, or image URLs.

### Usage Examples

```bash
# Get today's news using default API encoding (json)
./scripts/news.sh

# Get today's news in plain text format
./scripts/news.sh --encoding text

# Get news for a specific date using flags
./scripts/news.sh --date 2024-03-01

# Get news for a specific date (simplified usage without flags)
./scripts/news.sh 2024-03-01

# Get news for a specific date in markdown format
./scripts/news.sh -e markdown -d 2024-03-01
```

## Response Format

To balance information depth with token consumption when text-based output is needed, you **MUST** use the following rules for the `encoding` parameter. **Note: If image output is requested, you should still use `image` or `image-proxy`.**

1. **Default Strategy (`--encoding markdown`)**
   - **When to use:** By default for standard daily news inquiries.
   - **Why:** Provides well-structured, easy-to-read information with moderate token usage.

2. **Brief Information (`--encoding text`)**
   - **When to use:** When the user explicitly requests brief or summarized news.
   - **Why:** Returns only essential details in plain text, saving maximum tokens.

3. **Complete Information (`--encoding json`)**
   - **When to use:** Only when the user explicitly asks for raw data, detailed fields, or comprehensive data.
   - **Why:** Returns the complete API payload, which is highly token-heavy.

## Troubleshooting

### Issue: No data returned
- **Solution**: Try requesting previous dates (yesterday or the day before)
- The service tries latest 3 days automatically

### Issue: Image not loading
- **Solution**: Use `encoding=image-proxy` instead of `encoding=image`
- The proxy endpoint directly returns image binary data

### Issue: Old date requested
- **Solution**: Data is only available for recent dates
- Check the response status code
