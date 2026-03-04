# Signal intelligence pipeline for content creation.

## What's Included

1 Pipeline

Marketing. **RSS feeds** → rss_db.py
2. **X/Twitter** → x_monitor.py
3. **Telegram** → telegram_monitor.py
4. **Gmail newsletters** → newsletter_monitor.py
5. **Daily/Weekly/Monthly reports** → daily_signals.py

## Setup

```bash
# Clone or copy to your skills folder
cd skills/signal-pipeline

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Activate environment
source venv/bin/activate

# Daily signals (runs every day)
python daily_signals.py

# Weekly summary
python daily_signals.py --weekly

# Monthly deep-dive
python daily_signals.py --monthly
```

## Adding Sources

### RSS Feeds (edit rss_db.py)

```python
new_feeds = [
    ('Your Feed Name', 'https://example.com/feed.xml'),
]
```

### Telegram Channels (edit telegram_monitor.py)

```python
CHANNELS = ['channel_name_1', 'channel_name_2']
```

### X Accounts (edit x_monitor.py)

```python
MONITOR_URLS = [
    'https://x.com/username/status/123456789',
]
```

### Gmail Newsletters

The newsletter monitor requires `gog` CLI to be configured with Gmail access.

## Output

- Daily signals saved to: `memory/daily_signals/YYYY-MM-DD.json`
- Weekly/Monthly reports printed to stdout

## Databases Created

- `rss_db.db` - RSS articles
- `x_monitor.db` - X/Twitter data
- `telegram_db.db` - Telegram posts

## Customize

Edit the individual module files to:
- Change output format
- Add/remove keywords
- Customize post templates
- Add more RSS feeds, X accounts, Telegram channels
