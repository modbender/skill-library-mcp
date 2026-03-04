# Content Watcher Skill

AI-powered content monitoring and summarization toolkit.

## Features

- Monitor RSS feeds, blogs, and news sources
- Auto-fetch and extract article content
- AI summarization with key insights
- Daily/weekly digest generation
- Multi-channel delivery (Feishu, Email, etc.)

## Install

```bash
clawhub install content-watcher
```

## Usage

```bash
# Add sources to monitor
content-watcher add https://example.com/feed.xml --name "Tech News"

# Run once (manual)
content-watcher run

# Setup daily cron
content-watcher cron --schedule "0 9 * * *" --delivery feishu
```

## Config

Edit `~/.config/content-watcher/config.json`:
```json
{
  "sources": [],
  "delivery": "feishu",
  "summaryStyle": "bullet",
  "maxItemsPerSource": 5
}
```
