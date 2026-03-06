---
name: video-news-downloader
description: "Automated daily news video downloader with AI subtitle proofreading. Downloads CBS Evening News and BBC News at Ten from YouTube, extracts and proofreads subtitles using DeepSeek, serves videos via HTTP with embedded players. Use when: (1) Setting up automated daily news video downloads, (2) Downloading CBS/BBC news with subtitles, (3) Proofreading subtitle files with AI, (4) Creating local video streaming servers with web players, (5) Managing cron jobs for scheduled video updates."
---

# Video News Downloader with AI Subtitle Proofreading

Complete workflow for downloading daily news videos, processing subtitles, and serving them via HTTP with web players.

## Overview

This skill automates:
1. **Video Download**: CBS Evening News + BBC News at Ten from YouTube
2. **Subtitle Processing**: Extract auto-captions and convert to VTT format
3. **AI Proofreading**: Use DeepSeek to fix speech recognition errors
4. **HTTP Streaming**: Serve videos with embedded web players
5. **Scheduled Updates**: Daily cron jobs at configurable times

## Quick Start

### 1. Download Latest News

```bash
python3 scripts/video_download.py --cbs --bbc
```

### 2. Proofread Subtitles

```bash
python3 scripts/subtitle_proofreader.py /path/to/subtitle.vtt
```

Or use DeepSeek directly:
> "校对字幕文件 /path/to/subtitle.vtt"

### 3. Start HTTP Servers

```bash
bash scripts/setup_server.sh
```

### 4. Setup Daily Cron Jobs

```bash
bash scripts/setup_cron.sh
```

## Commands

### Video Download Script

**Download CBS only:**
```bash
python3 scripts/video_download.py --cbs
```

**Download BBC only:**
```bash
python3 scripts/video_download.py --bbc
```

**Download both:**
```bash
python3 scripts/video_download.py --cbs --bbc
```

**With subtitle proofreading:**
```bash
python3 scripts/video_download.py --cbs --bbc --proofread
```

### Subtitle Proofreading

**Proofread single file:**
```bash
python3 scripts/subtitle_proofreader.py <vtt_file_path>
```

**Auto-proofread all news subtitles:**
```bash
python3 scripts/subtitle_proofreader.py --all
```

### Server Management

**Start servers:**
```bash
bash scripts/setup_server.sh start
```

**Check status:**
```bash
bash scripts/setup_server.sh status
```

**Stop servers:**
```bash
bash scripts/setup_server.sh stop
```

## File Structure

```
/workspace/
├── cbs-live-local/
│   ├── cbs_latest.mp4
│   ├── cbs_latest.en.vtt          # Original subtitle
│   ├── cbs_latest.en.vtt-backup   # Backup
│   ├── cbs_latest-corrected.txt   # DeepSeek corrected text
│   └── cbs_latest-corrections.md  # Error list
│
├── bbc-news-live/
│   ├── bbc_news_latest.mp4
│   ├── bbc_news_latest.en.vtt
│   ├── bbc_news_latest.en.vtt-backup
│   ├── bbc_news_latest-corrected.txt
│   └── bbc_news_latest-corrections.md
│
└── temp/                           # Temporary download files
```

## HTTP Endpoints

| Endpoint | Description |
|----------|-------------|
| http://IP:8093/ | CBS Evening News player |
| http://IP:8093/cbs_latest.mp4 | CBS video direct |
| http://IP:8095/ | BBC News at Ten player |
| http://IP:8095/bbc_news_latest.mp4 | BBC video direct |

## Cron Jobs

### Default Schedule (Beijing Time)

| Time | Task |
|------|------|
| 20:00 | Download latest CBS + BBC videos |
| 20:30 | DeepSeek proofread subtitles |

### Manual Cron Setup

See [references/cron-setup.md](references/cron-setup.md) for detailed cron configuration.

## DeepSeek Proofreading

### What Gets Fixed

- Speech recognition errors (e.g., "noraster" → "nor'easter")
- Name errors (e.g., "trunk" → "Trump")
- Location name errors
- Professional terminology errors
- Obvious spelling mistakes

### Output Files

For each subtitle file, generates:
1. `-backup.vtt` - Original subtitle (never modified)
2. `-corrected.txt` - AI-corrected plain text
3. `-corrections.md` - List of corrections made

## Troubleshooting

### Video Download Fails

- Check yt-dlp is installed: `yt-dlp --version`
- Check YouTube URL is accessible
- Try manual download first

### Subtitle Extraction Fails

- Some videos don't have auto-captions
- Check if `--list-subs` shows available languages

### Server Won't Start

- Check ports 8093/8095 are free: `lsof -i :8093`
- Check Python http.server is available

### Proofreading Issues

- Ensure DeepSeek model is available
- Check subtitle file exists and is valid VTT format

## See Also

- [references/workflow.md](references/workflow.md) - Detailed workflow documentation
- [references/cron-setup.md](references/cron-setup.md) - Cron job configuration guide
