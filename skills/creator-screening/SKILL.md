---
name: creator-screening
description: Screen and evaluate social media creators/influencers using configurable quality frameworks. Analyzes Instagram, TikTok, YouTube creators using Memories.ai V2 Video Understanding API — fetches profile metadata, runs MAI visual+audio AI analysis on videos, and scores against production quality, audio, delivery, and positioning criteria. Use when asked to vet creators, screen influencers, evaluate content quality, or generate creator reports.
metadata:
  openclaw:
    emoji: "🎯"
---

# Creator Screening Skill

Automated creator/influencer screening powered by **Memories.ai V2 Video Understanding API**.

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `videos_per_creator` | 5 | Number of top videos to analyze per creator |
| `video_seconds` | 30 | First N seconds of each video to analyze |
| `platforms` | instagram | Supported: instagram, tiktok, youtube |
| `analysis_mode` | `mai` | `mai` (visual+audio AI analysis) or `transcript` (audio-only fallback) |
| `framework` | default | Screening framework to apply. See `references/frameworks/` |
| `output_format` | discord | `discord`, `pdf` (Google Doc→PDF), or `json` |
| `batch_size` | 10 | Max creators per batch run |

## Quick Start

```
Screen these creators: @anshmehra.in, @nishkarshsharmaa
Parameters: videos_per_creator=3, framework=cac-crusher
```

## Workflow

### Step 1: Parse Input
Accept creator URLs in any format:
- Profile: `https://www.instagram.com/username/`
- Individual reel: `https://www.instagram.com/reel/SHORTCODE/`
- YouTube: `https://www.youtube.com/@channel` or `/shorts/ID`

### Step 2: Get Profile & Video Metadata

**Memories.ai V2**: `POST /instagram/video/metadata`

```bash
python3 scripts/scrape_profiles.py --urls "reel_url1,reel_url2" --channel rapid
```

Returns per video ($0.01/video):
- **Owner profile**: username, full_name, followers, verified, profile_pic
- **Video stats**: views, play_count, duration, caption, comments, dimensions, audio info

### Step 3: Video Understanding (MAI)

**Memories.ai V2 MAI**: `POST /instagram/video/mai/transcript`

This is the core analysis step. MAI provides:
- **Visual scene descriptions**: lighting quality, framing, environment, clothing, production value
- **Audio transcription**: speech-to-text with timestamps
- **Content understanding**: topic classification, delivery style, structure

```bash
python3 scripts/analyze_videos.py --mode mai --videos_per_creator 5 --urls "url1,url2"
```

Each video returns visual + audio AI analysis. Use this to evaluate:
- Section 2.1: Look & Feel (lighting, environment, framing) — from **visual scenes**
- Section 2.2: Audio Quality (clarity, echo, consistency) — from **audio analysis**
- Section 3.x: Delivery & Content (structure, fluency, maturity) — from **transcript text**
- Section 4: Positioning (tone, energy, brand safety) — from **combined analysis**

**Fallback**: If MAI is unavailable, use `--mode transcript` for audio-only analysis:
```bash
python3 scripts/analyze_videos.py --mode transcript --videos_per_creator 5 --urls "url1,url2"
```

### Step 4: Apply Framework

Score against the selected screening framework:

```bash
python3 scripts/score_creator.py --framework cac-crusher --profile profile.json --transcripts transcripts.json
```

Frameworks live in `references/frameworks/`:
- `cac-crusher.md` — CAC Crusher Creator Screening Framework (Talking Head + Skit categories)
- `default.md` — Generic quality screening (5 dimensions, weighted scoring)
- `template.md` — Template for creating custom frameworks

### Step 5: Generate Report

Output per-creator screening cards with:
- Profile stats (followers, verified, engagement)
- Per-section scores (PASS/FAIL/FLAG)
- Transcript excerpts as evidence
- Visual quality notes from MAI
- Final verdict (APPROVED / REJECTED / CONDITIONAL)

## Memories.ai V2 API Reference

All endpoints use: `Authorization: <API_KEY>` header (no Bearer prefix).
Base URL: `https://mavi-backend.memories.ai/serve/api/v2`

| Endpoint | Method | Use | Cost |
|----------|--------|-----|------|
| `/{platform}/video/metadata` | POST | Profile + video stats | $0.01/video |
| `/{platform}/video/mai/transcript` | POST | Visual + audio AI analysis | ~$0.11/video |
| `/{platform}/video/transcript` | POST | Audio transcription only | ~$0.01/video |

Platforms: `instagram`, `tiktok`, `youtube`, `twitter`

**Request body**: `{"video_url": "...", "channel": "rapid"}`
**MAI response**: `{"data": {"task_id": "..."}}` (async, results via webhook)

**URL format**: Instagram must use `/reel/SHORTCODE/` (not `/p/` or `/reels/`)

## Error Handling

- Add 0.5s delay between API calls
- Retry failed requests once, then skip
- If MAI webhook not received, fall back to transcript mode
- Always normalize Instagram URLs: `/p/` → `/reel/`, `/reels/` → `/reel/`
