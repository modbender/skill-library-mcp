---
name: video-download-faas
description: Download videos in MP4 format using yt-dlp with FaaS (Firecracker/Container) isolation. Start downloads, check status, and kill processes. Videos are automatically converted to MP4 format.
---

# Video Download FaaS

Download videos asynchronously using yt-dlp in isolated background processes. **All downloads are saved as MP4 files.**

## Overview

This skill manages video downloads as background tasks that:
- Start immediately and return control to the user
- Continue running even if the session disconnects
- Can be monitored for progress
- Can be terminated when needed

## When to Use

Use this skill when:
- Downloading large videos that take time
- Processing multiple videos concurrently
- Running downloads on remote/headless systems
- Need to continue working while downloading

## Quick Start

### Start a Download

```bash
scripts/download.sh "https://youtube.com/watch?v=..."
```

Returns immediately with:
- Session ID
- Process ID (PID)
- Log file location

### Check Status

```bash
# List all active downloads
scripts/check-status.sh

# Check specific download
scripts/check-status.sh video_dl_1234567890_12345
```

### Kill Download

```bash
# Graceful stop
scripts/kill-download.sh video_dl_1234567890_12345

# Force kill
scripts/kill-download.sh video_dl_1234567890_12345 --force
```

## Commands

### download.sh

Start a video download in background with **MP4 output format**.

**Usage:**
```bash
download.sh <URL> [output_directory]
```

**Parameters:**
- `URL` - Video URL to download (required)
- `output_directory` - Where to save video (optional, default: ~/Downloads)

**Output Format:**
- Downloads are automatically converted to **MP4** format
- Uses best available MP4 video + M4A audio, merged into MP4
- If source isn't MP4, it will be re-encoded to MP4

**Returns:**
- Session ID for tracking
- PID for process management
- Paths to log and session files

**Example:**
```bash
scripts/download.sh "https://www.youtube.com/watch?v=dQw4w9WgXcQ" /tmp/videos
```

### check-status.sh

Check download progress and status.

**Usage:**
```bash
# List all sessions
check-status.sh

# Check specific session
check-status.sh <session_id>
```

**Returns:**
- Process status (running/completed)
- Download progress (if running)
- Downloaded files (if completed)
- Error information (if failed)

### kill-download.sh

Terminate a running download.

**Usage:**
```bash
kill-download.sh <session_id> [--force]
```

**Parameters:**
- `session_id` - The session ID from download.sh
- `--force` - Use SIGKILL instead of SIGTERM

## Session Management

Session files are stored in `/tmp/` with format:
- `video_dl_{timestamp}_{pid}.session` - Session metadata
- `video_dl_{timestamp}_{pid}.pid` - Process ID
- `video_dl_{timestamp}_{pid}.log` - Download log

Sessions are automatically cleaned up when:
- Download completes successfully
- Process is killed via kill-download.sh

## FaaS Integration

For containerized/Firecracker execution:

```bash
# Run download in isolated container
./run-in-container.sh scripts/download.sh "URL"

# Check from host
scripts/check-status.sh
```

## Troubleshooting

**Download not starting:**
- Check yt-dlp is installed: `yt-dlp --version`
- Verify URL is accessible: `curl -I "URL"`

**Process not found:**
- Session may have completed and auto-cleaned
- Check ~/Downloads for finished files

**Permission denied:**
- Ensure scripts are executable: `chmod +x scripts/*.sh`

## Requirements

- yt-dlp installed and in PATH
- Bash 4.0+
- Write access to /tmp and output directory
