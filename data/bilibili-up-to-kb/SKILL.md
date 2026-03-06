---
name: bilibili-up-to-kb
description: "Convert Bilibili (B站) videos into a searchable text knowledge base. Supports single videos and batch processing of entire UP主 channels. Uses local whisper.cpp for transcription (no API key needed). Includes automated transcript cleaning to fix ASR errors with full paragraph-level coverage. Use when: (1) user wants to transcribe a Bilibili video, (2) user wants to build a knowledge base from a channel, (3) user sends a bilibili.com or b23.tv link and asks for text/transcript/summary, (4) user says 转写, 知识库, 文字版, or transcribe bilibili."
---

# Bilibili UP to KB

Convert B站 videos (single or entire channels) into cleaned, structured text knowledge bases.

## Design Principle

**Agent orchestrates, scripts execute.** The agent's job is to decide WHAT to do and kick off
the right script. All mechanical, repetitive work (downloading, transcribing, cleaning) is
handled by shell scripts with built-in parallelism. The agent NEVER loops through videos
one by one — it runs ONE command and the script handles concurrency internally.

## Output Structure

```
kb/UP主名_UID/
├── BV号_视频标题.txt          # Cleaned transcript (user-facing)
├── BV号_视频标题.meta.json    # Video metadata
├── index.md                   # Summary index
└── .raw/                      # Hidden: whisper transcripts (if any)
    └── BV号_视频标题.txt
```

**Key decisions:**
- File names include title for readability (`BV1xxx_标题.txt`)
- Folder includes UP主 name (`UP主名_UID/`)
- Raw transcripts hidden in `.raw/`
- No `_clean` suffix — clean files are the main files
- Per-video `.meta.json` with title, uploader, duration, etc.

## Full Pipeline

### Step 1: Download AI subtitles (fast, high concurrency OK)
```bash
# 30-50 concurrent is fine — B站 CDN handles it
scripts/batch_channel.sh "https://space.bilibili.com/UID/" ./kb/output zh 0 30
```

### Step 2: For videos without AI subtitles, run whisper (LOW concurrency!)
```bash
# Metal GPU can only handle 1-4 parallel whisper instances
# More = slower total (GPU saturation)
scripts/batch_channel.sh "https://space.bilibili.com/UID/" ./kb/output zh 0 2 --whisper-only
```

### Step 3: Clean + Index
```bash
# Clean whisper transcripts (AI subtitles skip automatically)
scripts/batch_clean.sh ./kb/UP主名_UID/
scripts/generate_index.sh ./kb/UP主名_UID/
```

## Concurrency Guide

**Critical: Different stages need different concurrency!**

| Stage | Bottleneck | Recommended | Why |
|-------|-----------|-------------|-----|
| AI subtitle download | Network | **30-50** | B站 CDN handles high parallel |
| Whisper transcribe | Metal GPU | **1-4** | GPU饱和，多了反而慢 |
| Transcript cleaning | API rate limit | **ALL (0)** | Network I/O only |

## Quick Start — Single Video

```bash
scripts/transcribe.sh "https://www.bilibili.com/video/BV..." ./output zh
```

## Transcript Cleaning

**AI subtitles are clean enough — skipped by default.**

| Source | Cleaning needed? |
|--------|-----------------|
| B站 AI subtitles | **No** — directly usable |
| whisper fallback | Yes — goes through cleaning |

Cleaning uses `opencode/minimax-m2.5-free`:
1. Fix homophones and garbled words
2. Add punctuation
3. Output MUST be Simplified Chinese
4. Keep uncertain proper nouns unchanged
5. Never substitute one real term for another

Chunk size: 80 lines. Retry: 3 attempts with 3s delay.

## ⚠️ Long-running tasks

Use nohup to avoid session compaction killing processes:
```bash
nohup bash scripts/batch_clean.sh ./kb/UP主名_UID/ 0 80 > /tmp/clean.log 2>&1 &
```
batch_clean.sh is resumable — safe to re-run after interruption.

## ⚠️ Large Channel Handling (1000+ videos)

Script auto-detects large channels (>800 videos) and fetches in chunks to avoid timeout.

```bash
# Auto-chunked, just re-run to resume
nohup bash scripts/batch_channel.sh "https://space.bilibili.com/UID/" ./kb/output > /tmp/batch.log 2>&1 &
```

If still fails, manually fetch URL list:
```bash
for i in $(seq 1 500 2000); do
  yt-dlp --flat-playlist --playlist-start $i --playlist-end $((i+499)) \
    --print url "https://space.bilibili.com/UID/" >> /tmp/urls.txt
done
cat /tmp/urls.txt | xargs -P 20 -I {} bash scripts/transcribe.sh {} ./kb/OUTPUT zh
```

## ⚠️ Thermal & Fan Warning

**Keep system cool — avoid fan spin!**

| Stage | Risk | Mitigation |
|-------|------|------------|
| Whisper (GPU) | **HIGH** | Keep concurrency ≤2, monitor temps |
| AI subtitle download | Low | Can run 30-50 concurrent |
| Cleaning (API) | None | Pure network I/O, no local load |

**If fans start spinning:**
- Stop whisper processes immediately
- Wait for cooldown
- Resume with lower concurrency (1-2)

```bash
# Check GPU temp (if using CUDA)
nvidia-smi

# Check Mac CPU/GPU temp
sudo powermetrics --sample-rate 1000 -i 1 -n 1 | grep -E "CPU|GPU"
```

## Dependencies

**Required**: yt-dlp, ffmpeg, whisper.cpp (+ model), opencode CLI
**Optional**: Browser cookies for member-only content (`--cookies-from-browser chrome`)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_CLI` | `whisper-cli` | Path to whisper.cpp |
| `WHISPER_MODEL` | `~/.whisper-cpp/ggml-small.bin` | Whisper model |
| `OPENCODE_BIN` | `~/.opencode/bin/opencode` | opencode CLI |
| `CLEAN_MODEL` | `opencode/minimax-m2.5-free` | Cleaning model |

## Tips

- **China users**: Use `hf-mirror.com` for whisper model
- **Long videos (1h+)**: Auto-segmented into 10-min chunks
- **Resumable**: All batch scripts skip already-processed files
