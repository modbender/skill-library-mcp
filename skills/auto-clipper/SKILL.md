---
name: auto-clipper
displayName: AutoClipper
description: Automatically create clips and videos from media files in a specified folder. Uses Agent Swarm for intelligent task delegation and supports cron-based scheduling.
version: 1.0.0
---

# AutoClipper

## Description

Automatically create clips and videos from media files in a specified folder. Uses Agent Swarm for intelligent task delegation and supports cron-based scheduling.

# AutoClipper

**Automatic Video Clip & Highlight Generator for OpenClaw.**

**v1.0.0 — Design draft.** Automatically scan a folder for media files, create clips/highlights using ffmpeg, and organize output. Cron-ready for scheduled automation.


## Installation

```bash
# Add to crontab (crontab -e)
# Run every hour at minute 0
0 * * * * /Users/ghost/.openclaw/workspace/skills/auto-clipper/scripts/run.sh

# Or run daily at 9 AM
0 9 * * * /Users/ghost/.openclaw/workspace/skills/auto-clipper/scripts/run.sh --output daily
```


## Usage

- **Screen recording highlights**: Auto-clip moments from Loom/obsidian recordings
- **Meeting recaps**: Extract key segments from meeting recordings
- **Content creation**: Batch-process raw footage into short clips
- **Security camera clips**: Pull motion-triggered segments from camera feeds
- **Gaming highlights**: Auto-clip "best of" moments from recordings

```bash
# Run once (scan and process)
python3 scripts/auto_clipper.py run

# Dry run (show what would be processed)
python3 scripts/auto_clipper.py run --dry-run

# Force reprocess all files
python3 scripts/auto_clipper.py run --force

# Start continuous watcher (not cron-based)
python3 scripts/auto_clipper.py watch

# Show status
python3 scripts/auto_clipper.py status
```


## Purpose

AutoClipper enables OpenClaw agents to automatically:
- **Monitor a watch folder** for new media files (videos, screen recordings, camera clips)
- **Analyze media** to understand what's worth clipping (via Agent Swarm delegation)
- **Generate clips** using ffmpeg (highlights, segments, trimmed videos)
- **Produce compilations** by stitching multiple clips together
- **Schedule runs** via cron for fully automated workflows


## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      AutoClipper Skill                       │
├─────────────────────────────────────────────────────────────┤
│  1. Watch Folder (configurable input path)                  │
│         ↓                                                   │
│  2. Media Scanner (find new files, filter by extension)    │
│         ↓                                                   │
│  3. Agent Swarm delegation (analyze → clip strategy)             │
│         ↓                                                   │
│  4. Clip Engine (ffmpeg operations)                         │
│         ↓                                                   │
│  5. Output Organizer (save to output folder, optional SNS)  │
└─────────────────────────────────────────────────────────────┘
```


## Components

### 1. Watch Folder Scanner
- Monitors a configured input directory
- Filters by file extensions: `.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`
- Tracks processed files (to avoid re-processing)
- Configurable: `watchFolder`, `fileExtensions`, `processedLog`

### 2. Media Analyzer (via Agent Swarm)
- Delegates analysis to appropriate model (MiniMax for code/technical, Kimi for creative)
- Determines:
  - Which segments to clip (timestamp ranges)
  - Clip duration targets
  - Output format preferences
- Returns structured clip plan: `[{start, end, label, priority}]`

### 3. Clip Engine (ffmpeg)
- **Trim**: Extract segments without re-encoding (fast)
- **Transcode**: Convert to target format/codec
- **Highlight**: Auto-detect "interesting" segments (via scene detection)
- **Compile**: Stitch multiple clips into single video
- **Overlay**: Add watermarks, timestamps, captions

### 4. Output Manager
- Organized output folder structure: `output/YYYY-MM-DD/`
- Configurable naming: `{original}-{timestamp}-{index}.mp4`
- Optional: Notify via OpenClaw message (Discord, WhatsApp, etc.)

### 5. Cron Scheduler
- Standalone script for cron integration
- Configurable schedule: `0 * * * *` (hourly), `0 9 * * *` (daily at 9am)
- Dry-run mode for testing
- Lock file to prevent overlapping runs


## Configuration (config.json)

```json
{
  "watchFolder": "~/Downloads/Recordings",
  "outputFolder": "~/Videos/Clips",
  "fileExtensions": [".mp4", ".mov", ".mkv"],
  "processedLog": "logs/processed.json",
  "clipSettings": {
    "defaultDuration": 60,
    "minClipDuration": 10,
    "maxClipDuration": 300,
    "outputCodec": "h264",
    "outputFormat": "mp4"
  },
  "intentRouter": {
    "enabled": true,
    "model": "openrouter/minimax/minimax-m2.5"
  },
  "cron": {
    "schedule": "0 * * * *",
    "enabled": false
  },
  "notifications": {
    "enabled": false,
    "channel": "discord"
  }
}
```


## Tools Needed

| Tool | Purpose | Required |
|------|---------|----------|
| **ffmpeg** | Video transcoding, trimming, clipping | Yes |
| **ffprobe** | Media metadata extraction (duration, codec) | Yes |
| **Agent Swarm** | Analyze media and determine clip strategy | Yes |
| **OpenClaw message** | Send notifications when clips are ready | Optional |
| **OpenClaw nodes** | Screen recording capture (live input) | Optional |
| **file system** | Watch folder, output management | Yes |


## Agent Swarm integration

When AutoClipper finds new media, it delegates analysis:

```
User task: "Analyze video and suggest clip timestamps for meeting highlights"
→ router.spawn() → sessions_spawn(task, model)
← Returns: [{start: "00:05:30", end: "00:07:45", label: "action item discussion"}, ...]
```

**Prompt template for media analysis:**
```
Analyze this video file: {filename}
Duration: {duration_seconds} seconds
Extract: Key moments worth clipping as short highlights (30-90 seconds each)
Output: JSON array of {start_timestamp, end_timestamp, description}
```


## Directory Structure

```
auto-clipper/
├── SKILL.md              # This file
├── _meta.json            # Skill metadata
├── config.json           # Configuration
├── README.md             # Setup instructions
├── scripts/
│   ├── auto_clipper.py   # Main entry point
│   ├── scanner.py        # Watch folder scanner
│   ├── clipper.py        # ffmpeg wrapper
│   ├── analyzer.py       # Agent Swarm integration
│   └── run.sh            # Cron launcher
└── logs/
    └── processed.json    # Track processed files
```


## Keywords

- **video**, **clip**, **clips**, **highlight**, **highlights**
- **trim**, **cut**, **extract**, **segment**
- **ffmpeg**, **transcode**, **encode**, **convert**
- **folder**, **watch**, **monitor**, **automation**
- **cron**, **schedule**, **batch**, **process**
- **screen recording**, **meeting**, **recording**


## Skill Name Ideas

1. **AutoClipper** ✓ (chosen)
2. **ClipForge**
3. **MediaMason**
4. **VideoHarvest**
5. **HighlightHub**
6. **ClipStream**
7. **MediaSnip**
8. **AutoTrim**


## Implementation Phases

### Phase 1: Core (MVP)
- [ ] Folder scanner with extension filtering
- [ ] Basic ffmpeg trim operation
- [ ] Simple processed file tracking
- [ ] CLI entry point

### Phase 2: Intelligence
- [ ] Agent Swarm integration for clip planning
- [ ] Scene detection for auto-highlighting
- [ ] Metadata extraction with ffprobe

### Phase 3: Automation
- [ ] Cron launcher script
- [ ] Continuous watcher mode
- [ ] Notification system
- [ ] Output organization

### Phase 4: Advanced
- [ ] Multi-clip compilation
- [ ] Overlay/watermark support
- [ ] Custom clip templates
- [ ] Node camera integration


## Notes

- **Performance**: Use `-c copy` for fast trimming (no re-encode)
- **Storage**: Auto-cleanup processed files or move to archive
- **Error handling**: Skip corrupted files gracefully, log failures
- **Idempotency**: Same input file should not produce duplicate output
