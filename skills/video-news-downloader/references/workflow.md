# Video News Downloader - Detailed Workflow

## Complete Workflow Diagram

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Cron Job      │────▶│  Video Download  │────▶│  HTTP Server    │
│  (Daily 20:00)  │     │  (yt-dlp)        │     │  (Python)       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │ Subtitle Extract │
                        │ (VTT format)     │
                        └──────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │ AI Proofreading  │────▶┌─────────────────┐
                        │ (DeepSeek)       │     │ Corrected Files │
                        └──────────────────┘     └─────────────────┘
```

## Step-by-Step Process

### 1. Video Download (20:00 Beijing Time)

**CBS Evening News:**
- Source: YouTube Playlist
- URL: https://www.youtube.com/playlist?list=PLotzEBRQdc0cMXjf4FKw6_1Pu8in6rzBQ
- Quality: 360p MP4 (format 18)
- Output: `cbs-live-local/cbs_latest.mp4`

**BBC News at Ten:**
- Source: YouTube Search
- Query: "BBC News at Ten"
- Quality: 360p MP4
- Output: `bbc-news-live/bbc_news_latest.mp4`

### 2. Subtitle Extraction

**Automatic Captions:**
- Language: English (en)
- Format: WebVTT (.vtt)
- Source: YouTube auto-generated
- Backup: Original saved as `-backup.vtt`

**Common Issues:**
- Some videos lack auto-captions
- Live streams may have delayed captions
- Music/background noise affects accuracy

### 3. HTTP Server (Always Running)

**Ports:**
- 8093: CBS Evening News
- 8095: BBC News at Ten

**Features:**
- Embedded HTML5 video player
- Subtitle track support (VTT)
- Direct MP4 download links
- CORS enabled for cross-origin

**Player Features:**
- Auto-play disabled
- Subtitle toggle (CC button)
- Full-screen support
- Responsive design

### 4. AI Proofreading (20:30 Beijing Time)

**Process:**
1. Extract plain text from VTT
2. Send to DeepSeek with proofreading prompt
3. Receive corrections list
4. Generate corrected text file

**Error Types Detected:**

| Type | Example | Correction |
|------|---------|------------|
| Speech Recognition | noraster | nor'easter |
| Name Errors | trunk | Trump |
| Location | bucking ham | Buckingham |
| Terminology | AI words | proper terms |
| Spelling | obviosly | obviously |

**Output Files:**

For each subtitle:
- `-backup.vtt`: Original (never modified)
- `-corrected.txt`: AI-corrected plain text
- `-corrections.md`: List of changes made

## Directory Structure

```
/workspace/
├── cbs-live-local/              # CBS content
│   ├── cbs_latest.mp4          # Video file
│   ├── cbs_latest.en.vtt       # Current subtitle
│   ├── cbs_latest.en.vtt-backup
│   ├── cbs_latest-corrected.txt
│   ├── cbs_latest-corrections.md
│   └── index.html              # Web player
│
├── bbc-news-live/               # BBC content
│   ├── bbc_news_latest.mp4
│   ├── bbc_news_latest.en.vtt
│   ├── bbc_news_latest.en.vtt-backup
│   ├── bbc_news_latest-corrected.txt
│   ├── bbc_news_latest-corrections.md
│   └── index.html
│
├── temp/                        # Temporary downloads
│   └── (auto-cleaned daily)
│
└── logs/                        # Download logs
    ├── video-download.log
    └── proofread.log
```

## Manual Operations

### Force Download Now

```bash
cd /root/.openclaw/workspace/skills/video-news-downloader
python3 scripts/video_download.py --cbs --bbc
```

### Force Proofread Now

```bash
python3 scripts/subtitle_proofreader.py --all
```

### Check Server Status

```bash
bash scripts/setup_server.sh status
```

### Restart Servers

```bash
bash scripts/setup_server.sh restart
```

### View Logs

```bash
tail -f /root/.openclaw/workspace/logs/video-download.log
tail -f /root/.openclaw/workspace/logs/proofread.log
```

## Troubleshooting

### Video Download Fails

**Symptom:** yt-dlp returns error

**Solutions:**
1. Check YouTube URL is accessible
2. Try manual download: `yt-dlp -f 18 "URL"`
3. Check disk space: `df -h`
4. Update yt-dlp: `pip install -U yt-dlp`

### Subtitle Not Found

**Symptom:** No .vtt file generated

**Solutions:**
1. Check if video has auto-captions: `yt-dlp --list-subs URL`
2. Some videos don't have English captions
3. Try different video source

### Server Won't Start

**Symptom:** Port already in use

**Solutions:**
1. Find process: `lsof -i :8093`
2. Kill process: `kill $(lsof -t -i :8093)`
3. Use different port

### Proofreading Takes Too Long

**Symptom:** DeepSeek times out

**Solutions:**
1. Subtitle may be too long (limit to 6000 chars)
2. Split into chunks
3. Use lighter model

## Customization

### Change Download Quality

Edit `scripts/video_download.py`:
```python
"-f", "22"  # 720p instead of 360p
```

### Change Schedule

Edit cron jobs:
```bash
# Beijing Time 22:00
0 14 * * * python3 video_download.py --cbs --bbc
```

### Add More News Sources

1. Add new directory in workspace
2. Create download function in video_download.py
3. Add to cron job
4. Create index.html player

## API Reference

### Video Download Script

```python
python3 video_download.py [options]

Options:
  --cbs          Download CBS Evening News
  --bbc          Download BBC News at Ten
  --proofread    Auto-proofread after download
  --cleanup N    Keep files for N days (default: 2)
```

### Subtitle Proofreader

```python
python3 subtitle_proofreader.py [file|--all]

Arguments:
  file           Single VTT file to proofread
  --all          Proofread all news subtitles
```

### Server Control

```bash
bash setup_server.sh [command]

Commands:
  start    Start both servers
  stop     Stop both servers
  restart  Restart both servers
  status   Check server status
```
