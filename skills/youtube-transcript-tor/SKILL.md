---
name: youtube-transcript
description: Download YouTube video transcripts with Tor proxy. Automatically detects manual subtitles first, falls back to auto-generated if unavailable.
---

# YouTube Transcript Downloader (with Tor Proxy)

This skill downloads YouTube video transcripts using Tor proxy to bypass IP blocking. It automatically prioritizes manual subtitles over auto-generated ones.

## Prerequisites

1. **Tor** - Install on Ubuntu/Debian:
   ```bash
   sudo apt-get update && sudo apt-get install -y tor
   sudo systemctl start tor
   sudo systemctl enable tor
   ```

2. **yt-dlp** - Install:
   ```bash
   sudo wget -q https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O /usr/local/bin/yt-dlp
   sudo chmod a+rx /usr/local/bin/yt-dlp
   ```

3. **Python** - For transcript cleanup (usually pre-installed)

## Quick Start

```bash
# Run the script
./scripts/youtube-transcript.sh <video_url_or_id> [language]
```

**Examples:**
```bash
./scripts/youtube-transcript.sh dQw4w9WgXcQ
./scripts/youtube-transcript.sh "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
./scripts/youtube-transcript.sh cMx139eTxoc en
```

## How It Works

### 1. Tor Proxy
- YouTube blocks cloud VPS IPs (AWS, GCP, Hetzner, etc.)
- Tor provides rotating IPs to bypass this blocking
- Connects via SOCKS5 proxy at `127.0.0.1:9050`

### 2. yt-dlp Usage
- `yt-dlp --proxy "socks5://127.0.0.1:9050"` - Routes through Tor
- `--write-subs` - Downloads manually uploaded subtitles
- `--write-auto-subs` - Downloads auto-generated subtitles
- `--sub-format vtt` - Downloads in VTT format

### 3. Automatic Detection Logic
```
1. Check if manual subtitles exist (--write-subs)
2. If found, download manual subtitles (preferred)
3. If not found, fallback to auto-generated (--write-auto-subs)
4. Clean up VTT file (remove timestamps, HTML tags)
5. Save as {video_title}_clean.txt
```

### 4. Transcript Cleanup
The cleanup script:
- Removes VTT timestamps (`00:00:00.000 --> 00:00:03.030`)
- Removes HTML-like tags (`<c>`, `<00:00:00.160>`, etc.)
- Removes duplicate lines
- Saves clean text file

## Output Files

Two files are created in `/home/ubuntu/.openclaw/workspace/tmp/`:

1. `{title}.vtt` - Original VTT file with timestamps
2. `{title}_clean.txt` - Clean transcript (recommended)

## Troubleshooting

| Error | Solution |
|-------|----------|
| "Sign in to confirm you're not a bot" | Tor is running but IP might be flagged. Wait and retry. |
| "No supported JavaScript runtime" | Install yt-dlp properly - this is just a warning |
| "Connection refused" | Start Tor: `sudo systemctl start tor` |
| "No subtitles available" | Video might not have any subtitles |

## API Reference

### Main Script: `youtube-transcript.sh`

**Parameters:**
- `$1` - Video URL or Video ID (required)
- `$2` - Language code (optional, default: `en`)

**Environment:**
- `OUTPUT_DIR` - Default: `/home/ubuntu/.openclaw/agents/<agent-id>/yt-transcripts`
- `AGENT_ID` - Agent ID (default: main)
- `PROXY` - Default: `socks5://127.0.0.1:9050`

### Cleanup Script: `clean_transcript.py`

**Usage:**
```bash
python3 scripts/clean_transcript.py <input.vtt> [output.txt]
```

## Alternative Methods

If Tor doesn't work:
1. **Residential Proxy** - Paid services like Bright Data (~$10/month)
2. **VPN with residential exit** - Connect to home network via WireGuard
3. **Browser with cookies** - Export YouTube cookies and pass to yt-dlp:
   ```bash
   yt-dlp --cookies /path/to/cookies.txt ...
   ```

## Notes

- Tor might be slow - be patient
- Each request gets a different IP (rotating)
- Some videos have no subtitles at all
- Auto-generated subtitles may contain errors
- Manual subtitles are always preferred when available
