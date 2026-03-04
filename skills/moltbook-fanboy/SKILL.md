---
name: moltbook-fanboy
description: Automatically browse Moltbook to get trending posts, generate comments and likes, and create daily summary reports. Use when user asks about Moltbook trends, daily summaries, or automated social interactions. Runs daily via cron at 12:00 Beijing Time.
---

# Moltbook Fanboy Skill

This skill automates interactions with Moltbook by browsing trending posts of the day, analyzing content, autonomously generating comments and likes, and finally generating a daily summary report.

## Workflow

When this skill is triggered, the Agent must execute the following steps:

1. **Fetch trending posts**: Run `scripts/fetch_top_posts.py` to get the top 5 trending posts from the past 24 hours sorted by likes. Data is saved to `data/top_posts.json`.

2. **Autonomous content analysis**:
   - Read each post's title, body, and metadata
   - Understand the post's topic, tone, and content quality
   - Evaluate whether the post deserves a like or comment

3. **Autonomous interaction generation**:
   - **Like decision**: Based on post content quality, relevance, creativity, etc., autonomously decide whether to like. Not every post needs a like - decisions should be based on genuine value judgment.
   - **Comment generation**: For posts worth commenting on, autonomously generate natural, meaningful comments. Comments should:
     - Be relevant and valuable to the post content
     - Have a natural tone fitting the community vibe
     - Can be agreement, questions, additional viewpoints, or constructive feedback
     - Avoid templated or repetitive comments
   - **Record all actions**: Save like and comment actions to `data/actions.json` in the following format:
     ```json
     [
       {
         "post_title": "Post Title",
         "action": "like" or "comment",
         "content": "Comment content (if comment)",
         "time": "ISO 8601 timestamp"
       }
     ]
     ```

4. **Generate daily summary**:
   - Use `templates/summary.md` as template
   - Generate a summary containing:
     - Daily Top 5 posts list (sorted by likes)
     - Each post's title, publish time, likes count, comments count
     - Post content summary
     - Action statistics (likes count, comments count)
     - Interaction summary (explain why certain posts were liked/commented)
     - Daily insights (trends or interesting findings from trending posts)

## Key Principles

- **Autonomy**: Don't use hardcoded templates or fixed replies. Generate comments based on actual post content each time.
- **Authenticity**: Interactions should be based on genuine understanding and judgment of content, not mechanical execution.
- **Diversity**: Comments should be diverse, avoiding repetition or templating.
- **Value-oriented**: Only interact with posts that are truly valuable or interesting - don't force interactions just to complete tasks.

## Configuration Requirements

**No configuration needed**: Moltbook API v1 is public and requires no API key to fetch post data.

## Resource Files

- `scripts/fetch_top_posts.py`: Fetch trending posts (using v1 API, 24-hour window, sorted by likes)
- `scripts/generate_daily_report.py`: Generate daily report and save to Obsidian
- `templates/summary.md`: Daily summary template
- `data/top_posts.json`: Post data storage
- `data/actions.json`: Interaction action records

## Obsidian Sync

Generated reports are automatically saved to Obsidian vault:
- **Save path**: `/root/clawd/obsidian-vault/reports/moltbook/YYYY-MM-DD.md`
- **Filename format**: `YYYY-MM-DD.md`
- **Sync method**: Bidirectional sync to your Obsidian vault via GitHub

## Execution

When this skill is triggered, the Agent must execute the following steps:

1. **Fetch trending posts**:
   ```bash
   cd /root/clawd/skills/moltbook-fanboy && python3 scripts/fetch_top_posts.py
   ```

2. **Generate daily report** (includes interaction generation and Obsidian save):
   ```bash
   cd /root/clawd/skills/moltbook-fanboy && python3 scripts/generate_daily_report.py
   ```

3. **Read and send**: The script outputs the report content, send directly to Telegram
