---
name: signal-pipeline
description: Marketing intelligence pipeline - gather signals from RSS, X/Twitter, Telegram, and Gmail newsletters. Generate daily posts, weekly summaries, and monthly deep-dives for content creation. Use when you need to build a content intelligence system or track marketing/tech trends.
---

# Signal Pipeline

A marketing intelligence pipeline that aggregates signals from multiple sources, stores them in SQLite, and generates content for personal branding.

## What It Does

- **RSS feeds** → SQLite database (rss_db.py)
- **X/Twitter** → SQLite database (x_monitor.py)
- **Telegram channels** → SQLite database (telegram_monitor.py)
- **Gmail newsletters** → Signal extraction (newsletter_monitor.py)
- **Daily signals** → Draft posts
- **Weekly synthesis** → Theme analysis
- **Monthly deep-dive** → Essay/book chapter

## Files Included

```
signal-pipeline/
├── SKILL.md              # This file
├── README.md             # Setup instructions
├── requirements.txt      # Python dependencies
├── daily_signals.py      # Main script (daily/weekly/monthly)
├── rss_db.py           # RSS feed storage
├── x_monitor.py        # X/Twitter monitoring
├── telegram_monitor.py  # Telegram channel scraping
└── newsletter_monitor.py # Gmail newsletter extraction
```

## Quick Start

```bash
# Install dependencies
cd skills/signal-pipeline
pip install -r requirements.txt

# Run daily signals
python daily_signals.py

# Generate weekly summary
python daily_signals.py --weekly

# Generate monthly report
python daily_signals.py --monthly
```

## Configuration

### RSS Feeds
Edit `rss_db.py` to add your feed URLs:
```python
new_feeds = [
    ('Feed Name', 'https://example.com/feed.xml'),
]
```

### Telegram Channels
Edit `telegram_monitor.py`:
```python
CHANNELS = ['channel_name_1', 'channel_name_2']
```

### X Accounts
Edit `x_monitor.py`:
```python
MONITOR_URLS = [
    'https://x.com/username/status/123456789',
]
```

### Gmail Newsletters
The `newsletter_monitor.py` uses `gog` CLI. Ensure it's configured:
```bash
gog gmail search 'newer_than:30d label:newsletter'
```

## Requirements

- Python 3.8+
- feedparser>=6.0.0
- beautifulsoup4>=4.12.0
- requests>=2.31.0
- httpx>=0.25.0

## Database

Three SQLite databases are created:
- `rss_db.db` - RSS articles
- `x_monitor.db` - X/Twitter data  
- `telegram_db.db` - Telegram posts

## Use Cases

1. **Content Creation** - Daily signals for X/LinkedIn posts
2. **Market Research** - Track industry trends
3. **Competitive Intelligence** - Monitor competitors
4. **Personal Branding** - Build content streak
5. **Book Writing** - Compile monthly insights

## Author

Open source - free to use and modify.
