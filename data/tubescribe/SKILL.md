---
name: TubeScribe
description: "YouTube video summarizer with speaker detection, formatted documents, and audio output. Works out of the box with macOS built-in TTS. Optional recommended tools (pandoc, ffmpeg, mlx-audio) enhance quality. Requires internet for YouTube access. No paid APIs or subscriptions. Use when user sends a YouTube URL or asks to summarize/transcribe a YouTube video."
metadata:
  {
    "openclaw":
      {
        "emoji": "🎬",
        "requires": { "bins": ["summarize"] }
      }
  }
---

# TubeScribe 🎬

**Turn any YouTube video into a polished document + audio summary.**

Drop a YouTube link → get a beautiful transcript with speaker labels, key quotes, timestamps that link back to the video, and an audio summary you can listen to on the go.

### 💸 Free & No Paid APIs

- **No subscriptions or API keys** — works out of the box
- **Local processing** — transcription, speaker detection, and TTS run on your machine
- **Network access** — fetching from YouTube (captions, metadata, comments) requires internet
- **No data uploaded** — nothing is sent to external services; all processing stays on your machine
- **Safe sub-agent** — spawned sub-agent has strict instructions: no software installation, no network calls beyond YouTube

### ✨ Features

- **📄 Transcript with summary and key quotes** — Export as DOCX, HTML, or Markdown
- **🎯 Smart Speaker Detection** — Automatically identifies participants
- **🔊 Audio Summaries** — Listen to key points (MP3/WAV)
- **📝 Clickable Timestamps** — Every quote links directly to that moment in the video
- **💬 YouTube Comments** — Viewer sentiment analysis and best comments
- **📋 Queue Support** — Send multiple links, they get processed in order
- **🚀 Non-Blocking Workflow** — Conversation continues while video processes in background

### 🎬 Works With Any Video

- Interviews & podcasts (multi-speaker detection)
- Lectures & tutorials (single speaker)
- Music videos (lyrics extraction)
- News & documentaries
- Any YouTube content with captions

## Quick Start

When user sends a YouTube URL:
1. Spawn sub-agent with the full pipeline task **immediately**
2. Reply: "🎬 TubeScribe is processing — I'll let you know when it's ready!"
3. Continue conversation (don't wait!)
4. Sub-agent notification will announce completion with title and details

**DO NOT BLOCK** — spawn and move on instantly.

## First-Time Setup

Run setup to check dependencies and configure defaults:

```bash
python skills/tubescribe/scripts/setup.py
```

This checks: `summarize` CLI, `pandoc`, `ffmpeg`, `Kokoro TTS`

## Full Workflow (Single Sub-Agent)

Spawn ONE sub-agent that does the entire pipeline:

```python
sessions_spawn(
    task=f"""
## TubeScribe: Process {youtube_url}

⚠️ CRITICAL: Do NOT install any software.
No pip, brew, curl, venv, or binary downloads.
If a tool is missing, STOP and report what's needed.

Run the COMPLETE pipeline — do not stop until all steps are done.

### Step 1: Extract
```bash
python3 skills/tubescribe/scripts/tubescribe.py "{youtube_url}"
```
Note the **Source** and **Output** paths printed by the script. Use those exact paths in subsequent steps.

### Step 2: Read source JSON
Read the Source path from Step 1 output and note:
- metadata.title (for filename)
- metadata.video_id
- metadata.channel, upload_date, duration_string

### Step 3: Create formatted markdown
Write to the Output path from Step 1:

1. `# **<title>**`
---
2. Video info block — Channel, Date, Duration, URL (clickable). Empty line between each field.
---
3. `## **Participants**` — table with bold headers:
   ```
   | **Name** | **Role** | **Description** |
   |----------|----------|-----------------|
   ```
---
4. `## **Summary**` — 3-5 paragraphs of prose
---
5. `## **Key Quotes**` — 5 best with clickable YouTube timestamps. Format each as:
   ```
   "Quote text here." - [12:34](https://www.youtube.com/watch?v=ID&t=754s)

   "Another quote." - [25:10](https://www.youtube.com/watch?v=ID&t=1510s)
   ```
   Use regular dash `-`, NOT em dash `—`. Do NOT use blockquotes `>`. Plain paragraphs only.
---
6. `## **Viewer Sentiment**` (if comments exist)
---
7. `## **Best Comments**` (if comments exist) — Top 5, NO lines between them:
   ```
   Comment text here.

   *- ▲ 123 @AuthorName*

   Next comment text here.

   *- ▲ 45 @AnotherAuthor*
   ```
   Attribution line: dash + italic. Just blank line between comments, NO `---` separators.

---
8. `## **Full Transcript**` — merge segments, speaker labels, clickable timestamps

### Step 4: Create DOCX
Clean the title for filename (remove special chars), then:
```bash
pandoc <output_path> -o ~/Documents/TubeScribe/<safe_title>.docx
```

### Step 5: Generate audio
Write the summary text to a temp file, then use TubeScribe's built-in audio generation:
```bash
# Write summary to temp file (use python3 to write, avoids shell escaping issues)
python3 -c "
text = '''YOUR SUMMARY TEXT HERE'''
with open('<temp_dir>/tubescribe_<video_id>_summary.txt', 'w') as f:
    f.write(text)
"

# Generate audio (auto-detects engine, voice, format from config)
python3 skills/tubescribe/scripts/tubescribe.py \
  --generate-audio <temp_dir>/tubescribe_<video_id>_summary.txt \
  --audio-output ~/Documents/TubeScribe/<safe_title>_summary
```
This reads `~/.tubescribe/config.json` and uses the configured TTS engine (mlx/kokoro/builtin), voice blend, and speed automatically. Output format (mp3/wav) comes from config.

### Step 6: Cleanup
```bash
python3 skills/tubescribe/scripts/tubescribe.py --cleanup <video_id>
```

### Step 7: Open folder
```bash
open ~/Documents/TubeScribe/
```

### Report
Tell what was created: DOCX name, MP3 name + duration, video stats.
""",
    label="tubescribe",
    runTimeoutSeconds=900,
    cleanup="delete"
)
```

**After spawning, reply immediately:**
> 🎬 TubeScribe is processing - I'll let you know when it's ready!
Then continue the conversation. The sub-agent notification announces completion.

## Configuration

Config file: `~/.tubescribe/config.json`

```json
{
  "output": {
    "folder": "~/Documents/TubeScribe",
    "open_folder_after": true,
    "open_document_after": false,
    "open_audio_after": false
  },
  "document": {
    "format": "docx",
    "engine": "pandoc"
  },
  "audio": {
    "enabled": true,
    "format": "mp3",
    "tts_engine": "mlx"
  },
  "mlx_audio": {
    "path": "~/.openclaw/tools/mlx-audio",
    "model": "mlx-community/Kokoro-82M-bf16",
    "voice": "af_heart",
    "lang_code": "a",
    "speed": 1.05
  },
  "kokoro": {
    "path": "~/.openclaw/tools/kokoro",
    "voice_blend": { "af_heart": 0.6, "af_sky": 0.4 },
    "speed": 1.05
  },
  "processing": {
    "subagent_timeout": 600,
    "cleanup_temp_files": true
  }
}
```

### Output Options
| Option | Default | Description |
|--------|---------|-------------|
| `output.folder` | `~/Documents/TubeScribe` | Where to save files |
| `output.open_folder_after` | `true` | Open output folder when done |
| `output.open_document_after` | `false` | Auto-open generated document |
| `output.open_audio_after` | `false` | Auto-open generated audio summary |

### Document Options
| Option | Default | Values | Description |
|--------|---------|--------|-------------|
| `document.format` | `docx` | `docx`, `html`, `md` | Output format |
| `document.engine` | `pandoc` | `pandoc` | Converter for DOCX (falls back to HTML) |

### Audio Options
| Option | Default | Values | Description |
|--------|---------|--------|-------------|
| `audio.enabled` | `true` | `true`, `false` | Generate audio summary |
| `audio.format` | `mp3` | `mp3`, `wav` | Audio format (mp3 needs ffmpeg) |
| `audio.tts_engine` | `mlx` | `mlx`, `kokoro`, `builtin` | TTS engine (mlx = fastest on Apple Silicon) |

### MLX-Audio Options (preferred on Apple Silicon)
| Option | Default | Description |
|--------|---------|-------------|
| `mlx_audio.path` | `~/.openclaw/tools/mlx-audio` | mlx-audio venv location |
| `mlx_audio.model` | `mlx-community/Kokoro-82M-bf16` | MLX model to use |
| `mlx_audio.voice` | `af_heart` | Voice preset (used if no voice_blend) |
| `mlx_audio.voice_blend` | `{af_heart: 0.6, af_sky: 0.4}` | Custom voice mix (weighted blend) |
| `mlx_audio.lang_code` | `a` | Language code (a=US English) |
| `mlx_audio.speed` | `1.05` | Playback speed (1.0 = normal, 1.05 = 5% faster) |

### Kokoro PyTorch Options (fallback)
| Option | Default | Description |
|--------|---------|-------------|
| `kokoro.path` | `~/.openclaw/tools/kokoro` | Kokoro repo location |
| `kokoro.voice_blend` | `{af_heart: 0.6, af_sky: 0.4}` | Custom voice mix |
| `kokoro.speed` | `1.05` | Playback speed (1.0 = normal, 1.05 = 5% faster) |

### Processing Options
| Option | Default | Description |
|--------|---------|-------------|
| `processing.subagent_timeout` | `600` | Seconds for sub-agent (increase for long videos) |
| `processing.cleanup_temp_files` | `true` | Remove /tmp files after completion |

### Comment Options
| Option | Default | Description |
|--------|---------|-------------|
| `comments.max_count` | `50` | Number of comments to fetch |
| `comments.timeout` | `90` | Timeout for comment fetching (seconds) |

### Queue Options
| Option | Default | Description |
|--------|---------|-------------|
| `queue.stale_minutes` | `30` | Consider a processing job stale after this many minutes |

## Output Structure

```
~/Documents/TubeScribe/
├── {Video Title}.html         # Formatted document (or .docx / .md)
└── {Video Title}_summary.mp3  # Audio summary (or .wav)
```

After generation, opens the folder (not individual files) so you can access everything.

## Dependencies

**Required:**
- `summarize` CLI — `brew install steipete/tap/summarize`
- Python 3.8+

**Optional (better quality):**
- `pandoc` — DOCX output: `brew install pandoc`
- `ffmpeg` — MP3 audio: `brew install ffmpeg`
- `yt-dlp` — YouTube comments: `brew install yt-dlp`
- mlx-audio — Fastest TTS on Apple Silicon: `pip install mlx-audio` (uses MLX backend for Kokoro)
- Kokoro TTS — PyTorch fallback: see https://github.com/hexgrad/kokoro

### yt-dlp Search Paths

TubeScribe checks these locations (in order):

| Priority | Path | Source |
|----------|------|--------|
| 1 | `which yt-dlp` | System PATH |
| 2 | `/opt/homebrew/bin/yt-dlp` | Homebrew (Apple Silicon) |
| 3 | `/usr/local/bin/yt-dlp` | Homebrew (Intel) / Linux |
| 4 | `~/.local/bin/yt-dlp` | pip install --user |
| 5 | `~/.local/pipx/venvs/yt-dlp/bin/yt-dlp` | pipx |
| 6 | `~/.openclaw/tools/yt-dlp/yt-dlp` | TubeScribe auto-install |

If not found, setup downloads a standalone binary to the tools directory.
The tools directory version doesn't conflict with system installations.

## Queue Handling

When user sends multiple YouTube URLs while one is processing:

### Check Before Starting
```bash
python skills/tubescribe/scripts/tubescribe.py --queue-status
```

### If Already Processing
```bash
# Add to queue instead of starting parallel processing
python skills/tubescribe/scripts/tubescribe.py --queue-add "NEW_URL"
# → Replies: "📋 Added to queue (position 2)"
```

### After Completion
```bash
# Check if more in queue
python skills/tubescribe/scripts/tubescribe.py --queue-next
# → Automatically pops and processes next URL
```

### Queue Commands
| Command | Description |
|---------|-------------|
| `--queue-status` | Show what's processing + queued items |
| `--queue-add URL` | Add URL to queue |
| `--queue-next` | Process next item from queue |
| `--queue-clear` | Clear entire queue |

### Batch Processing (multiple URLs at once)
```bash
python skills/tubescribe/scripts/tubescribe.py url1 url2 url3
```
Processes all URLs sequentially with a summary at the end.

## Error Handling

The script detects and reports these errors with clear messages:

| Error | Message |
|-------|---------|
| Invalid URL | ❌ Not a valid YouTube URL |
| Private video | ❌ Video is private — can't access |
| Video removed | ❌ Video not found or removed |
| No captions | ❌ No captions available for this video |
| Age-restricted | ❌ Age-restricted video — can't access without login |
| Region-blocked | ❌ Video blocked in your region |
| Live stream | ❌ Live streams not supported — wait until it ends |
| Network error | ❌ Network error — check your connection |
| Timeout | ❌ Request timed out — try again later |

When an error occurs, report it to the user and don't proceed with that video.

## Tips

- For long videos (>30 min), increase sub-agent timeout to 900s
- Speaker detection works best with clear interview/podcast formats
- Single-speaker videos (tutorials, lectures) skip speaker labels automatically
- Timestamps link directly to YouTube at that moment
- Use batch mode for multiple videos: `tubescribe url1 url2 url3`
