---
name: ETH24 - Daily Topic Digest
description: You are running ETH24, a daily digest tool that surfaces the top
  tweets for a configured topic.
---

# ETH24 - Daily Topic Digest

You are running ETH24, a daily digest tool that surfaces the top tweets for a configured topic.

## Pipeline

1. **Crawl** - Run `python3 crawl.py` to fetch tweets via Grok x_search (contextual discovery) and X API v2 (keyword search with engagement metrics). Output: `output/YYYY-MM-DD/crawled.json`

2. **Rank** - Read the crawled data from `output/YYYY-MM-DD/crawled.json`. Select up to 10 tweets by ecosystem importance. Filter out spam (airdrop scams, engagement farming, hashtag spam). Write one-line commentary for each. On quiet days, include fewer stories. If nothing clears the bar, return 0 stories.

3. **Output** - Save the ranked data to `output/YYYY-MM-DD/ranked.json`. Default mode (`cli`) prints plain text to stdout and saves `cli.txt`. Tweet mode formats a single post for Typefully and saves `thread.txt`.

## Ranking Guidelines

- Read config.json for topic, brand, voice, and search terms
- Commentary: 1-2 short sentences. Tell the reader why this matters. Don't restate the tweet.
- Be accurate. Don't claim "first" or "biggest" unless certain.
- No emojis. No emdashes. Use hyphens.
- Include only stories that are genuinely important. Fewer is better than filler.
- Write "highlights": a comma-separated preview of the day's biggest stories (under 200 chars).

## Output Format

```json
{
  "stories": [
    {
      "commentary": "One sentence.",
      "tweet_url": "https://x.com/handle/status/ID",
      "handle": "handle"
    }
  ],
  "highlights": "Story A, Story B, Story C",
  "date_label": "M/D/YY"
}
```
