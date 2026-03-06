---
name: hetu-lyrics-blessing
description: |
  A daily lyrics blessing skill that sends a random Hetu (河图) song lyric to a designated 
  recipient every day at 23:00. Lyrics are fetched from Baidu Baike using agent-browser.
  IMPORTANT: Uses browser automation to fetch exact lyrics from baike.baidu.com
  Use when: (1) Daily medicine reminder (2) Sending warm messages with verified lyrics
---

# Hetu Lyrics Blessing (河图歌词祝福)

Daily send a random Hetu (河图) song lyric with blessing message.

## Features

- 🎵 Lyrics fetched from Baidu Baike (baike.baidu.com) via agent-browser
- ⚠️ NEVER modify lyrics - always fetch exact text
- 💌 Personalized blessing message
- 📧 Email delivery via SMTP
- ⏰ Scheduled daily at 23:00

## Directory Structure

```
hetu-lyrics-blessing/
├── SKILL.md
└── scripts/
    └── send_lyrics.py   # Main script with browser automation
```

## How It Works

1. Randomly select a song from predefined list
2. Use `agent-browser` to open Baidu Baike page
3. Extract exact lyrics from the page
4. Send email with lyrics + blessing

## Quick Start

### 1. Install Dependencies

```bash
npm install -g agent-browser
agent-browser install --with-deps
```

### 2. Configure SMTP

Edit `send_lyrics.py`:

```python
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SMTP_EMAIL = "your_email@qq.com"
SMTP_PASSWORD = "your_auth_code"
TO_EMAIL = "recipient@email.com"
```

### 3. Set up Cron

```bash
# Run daily at 23:00
crontab -l | { cat; echo "0 23 * * * /path/to/send_lyrics.py >> /path/to/log.txt 2>&1"; } | crontab -
```

## Important Rules

- ⚠️ ALWAYS fetch from https://baike.baidu.com
- ⚠️ NEVER guess or modify lyrics
- ⚠️ If lyrics not found, use predefined backup
- Include source URL in every message
