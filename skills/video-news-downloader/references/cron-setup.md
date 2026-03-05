# Cron Job Setup Guide

## Default Schedule

| Beijing Time | UTC Time | Task |
|--------------|----------|------|
| 20:00 | 12:00 | Download CBS + BBC videos |
| 20:30 | 12:30 | DeepSeek proofread subtitles |

## Installation

### Using setup_cron.sh Script

```bash
bash scripts/setup_cron.sh install
```

### Manual Cron Setup

```bash
# Edit crontab
crontab -e

# Add these lines:
# Video download at 20:00 Beijing Time (12:00 UTC)
0 12 * * * cd /root/.openclaw/workspace/skills/video-news-downloader && python3 scripts/video_download.py --cbs --bbc --proofread >> /root/.openclaw/workspace/logs/video-download.log 2>&1

# Subtitle proofreading at 20:30 Beijing Time (12:30 UTC)
30 12 * * * cd /root/.openclaw/workspace/skills/video-news-downloader && python3 scripts/subtitle_proofreader.py --all >> /root/.openclaw/workspace/logs/proofread.log 2>&1
```

## OpenClaw Cron Integration

For OpenClaw-managed cron jobs:

```json
{
  "name": "Daily Video Download",
  "schedule": {
    "kind": "cron",
    "expr": "0 12 * * *",
    "tz": "UTC"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "Download latest CBS and BBC news videos",
    "timeoutSeconds": 300
  }
}
```

## Time Zone Conversion

| Beijing | UTC | US Eastern | US Pacific |
|---------|-----|------------|------------|
| 08:00 | 00:00 | 20:00 (prev) | 17:00 (prev) |
| 12:00 | 04:00 | 00:00 | 21:00 (prev) |
| 20:00 | 12:00 | 08:00 | 05:00 |
| 22:00 | 14:00 | 10:00 | 07:00 |

## Managing Cron Jobs

### List Current Jobs

```bash
crontab -l
```

### Remove All Video Jobs

```bash
bash scripts/setup_cron.sh remove
```

### Check Job Status

```bash
bash scripts/setup_cron.sh status
```

### View Execution Logs

```bash
# Video download logs
tail -f /root/.openclaw/workspace/logs/video-download.log

# Proofreading logs
tail -f /root/.openclaw/workspace/logs/proofread.log
```

## Troubleshooting

### Jobs Not Running

1. Check cron service: `systemctl status cron`
2. Check syntax: `crontab -l | crontab -`
3. Check logs: `grep CRON /var/log/syslog`

### Permission Issues

Ensure scripts are executable:
```bash
chmod +x scripts/*.py scripts/*.sh
```

### Path Issues

Always use full paths in cron:
```bash
# Good
/usr/bin/python3 /full/path/to/script.py

# Bad (may fail)
python3 script.py
```
