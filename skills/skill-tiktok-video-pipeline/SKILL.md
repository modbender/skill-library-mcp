---
name: skill-tiktok-video-pipeline
version: 2.0.0
# Updated: pipeline.py wired to overlay v3 engine with --audio and --slowmo support
description: End-to-end TikTok ad video pipeline. Product script → Veo base video → animated caption overlay → audio mix → final MP4. One command, full automation.
metadata:
  openclaw:
    requires: { bins: ["uv", "ffmpeg", "node"] }
---

# skill-tiktok-video-pipeline v2

Full end-to-end pipeline for TikTok product ads. Takes a `product_id` + `script_text` and outputs a publish-ready vertical short-form video with captions, optional logo watermark, and background music.

## Architecture

```
script_text + product_id
       │
       ▼
Step 1: Veo 3 base video generation (9:16, ~8s)
       │
       ▼
Step 2: Caption overlay + logo watermark
        └── tiktok_overlay_engine_v3.py (ffmpeg drawtext)
       │
       ▼
Step 3: Background audio mix (20% volume, ffmpeg amix)
       │
       ▼
output/tiktok/<product_id>_<lang>_final.mp4
```

## Requirements

- `GEMINI_API_KEY` env var (for Veo generation)
- `ffmpeg` on PATH
- `uv` on PATH (for Python scripts)
- `veo3-video-gen` skill installed at `skills/veo3-video-gen/`

## Usage

```bash
node scripts/generate.js \
  --product-id rain_cloud \
  --script-text "Stop dry air!|Ultrasonic mist|Whisper-quiet|Get yours today" \
  --lang EN
```

### With logo and custom audio

```bash
node scripts/generate.js \
  --product-id hydro_bottle \
  --script-text "Hydrogen water|Boosts energy|Pure & clean|Shop now" \
  --lang EN \
  --logo /path/to/brand_logo.png \
  --audio /path/to/bgm.mp3
```

### Arabic (AR) captions

```bash
node scripts/generate.js \
  --product-id mini_cam \
  --script-text "صوّر كل لحظة|دقة عالية|خفيف وصغير|اطلب الآن" \
  --lang AR
```

### Dry-run (no API calls, generates dummy video for testing overlay)

```bash
node scripts/generate.js \
  --product-id test \
  --script-text "Line 1|Line 2|Line 3" \
  --dry-run
```

## Inputs

| Argument | Required | Default | Description |
|---|---|---|---|
| `--product-id` | ✅ | — | Product identifier (used in output filename) |
| `--script-text` | ✅ | — | Caption lines separated by `\|` |
| `--lang` | ❌ | `EN` | Language: `EN` or `AR` |
| `--logo` | ❌ | none | Path to logo PNG for watermark (top-right) |
| `--audio` | ❌ | `assets/bgm_default.mp3` | Background music path |
| `--veo-model` | ❌ | `veo-3.1-generate-preview` | Veo model to use |
| `--prompt` | ❌ | auto | Custom Veo generation prompt |
| `--segments` | ❌ | `1` | Number of Veo segments to generate & stitch |
| `--dry-run` | ❌ | false | Skip Veo API call; use dummy black video |

## Outputs

| File | Description |
|---|---|
| `output/tiktok/<product_id>_<lang>_final.mp4` | Final publish-ready TikTok video |

## Scripts

| Script | Description |
|---|---|
| `scripts/generate.js` | Main Node.js orchestrator |
| `scripts/tiktok_overlay_engine_v3.py` | Python/ffmpeg caption overlay engine |

## Caption Format

Captions are split by `|` and timed evenly across the video duration.

**Example:** `"Hook line!|Feature 1|Feature 2|CTA here"` → 4 pills, each shown for ~2s on an 8s video.

Pill style: dark semi-transparent box, white text, centered at 75% height.

## Default Audio

Place a royalty-free BGM file at `assets/bgm_default.mp3` in this skill folder to auto-mix audio in all runs. If no audio is found, the video is output without BGM.

## Pipeline Steps Detail

```
Step 1  Veo 3 generates a 9:16 base MP4           ~60–120s
Step 2  Python overlays timed caption pills         ~5s
Step 3  ffmpeg mixes BGM at 20% volume              ~5s
─────────────────────────────────────────────────────────
Output  Final branded MP4 ready to post
```

## pipeline.py (v2.0.0 — Python orchestrator)

Direct Python pipeline wired to overlay engine via subprocess.

```bash
uv run scripts/pipeline.py \
  --product rain_cloud \
  --image product.jpg \
  --output final.mp4 \
  --audio /path/to/music.mp3 \
  --slowmo
```

### New flags (v2.0.0)

| Flag | Default | Description |
|---|---|---|
| `--audio` | `$DEFAULT_AUDIO` env or bundled Hyperfun.mp3 | Audio file passed to overlay step |
| `--slowmo` | false | Apply 0.83x speed → fills ~12s. Overrides `--extend-to` auto-stretch |

### Environment Variables

| Var | Default | Description |
|---|---|---|
| `DEFAULT_AUDIO` | workspace root `audio_Hyperfun.mp3` | Default audio if `--audio` not set |
