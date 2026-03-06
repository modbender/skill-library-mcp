---
name: voiceai-creator-voiceover-pipeline
description: "Turn scripts into publishable voiceovers with Voice.ai TTS, including segments, chapters, captions, and video muxing."
version: 0.2.1
env:
  - VOICE_AI_API_KEY
required_env:
  - VOICE_AI_API_KEY
credentials:
  - VOICE_AI_API_KEY
setup: "none — single file, runs directly with Node.js"
runtime: "node>=20"
optional_deps: "ffmpeg"
---

# Voice.ai Creator Voiceover Pipeline

> This skill follows the [Agent Skills specification](https://agentskills.io/specification).

Turn any script into a **publish-ready voiceover** — complete with numbered segments, a stitched master, YouTube chapters, SRT captions, and a beautiful review page. Optionally, replace the audio track on an existing video.

Built for creators who want studio-quality voiceovers without the studio. Powered by [Voice.ai](https://voice.ai).

---

## When to use this skill

| Scenario | Why it fits |
|---|---|
| **YouTube long-form** | Full narration with chapter markers and captions |
| **YouTube Shorts** | Quick hooks with the `shortform` template |
| **Podcasts** | Consistent host voice, intro/outro templates |
| **Course content** | Professional narration for educational videos |
| **Quick iteration** | Smart caching — edit one section, only that segment re-renders |
| **Video audio replacement** | Drop AI voiceover onto screen recordings or B-roll |

---

## The one-command workflow

Have a script and a video? Turn them into a finished video with AI voiceover in one shot:

```bash
node voiceai-vo.cjs build \
  --input my-script.md \
  --voice oliver \
  --title "My Video" \
  --video ./my-recording.mp4 \
  --mux
```

This renders the voiceover, stitches the master audio, and drops it onto your video — all in one command. Output:

- `out/my-video/muxed.mp4` — your video with the new voiceover
- `out/my-video/master.wav` — the standalone audio
- `out/my-video/review.html` — listen and review each segment
- `out/my-video/chapters.txt` — YouTube-ready chapter timestamps
- `out/my-video/captions.srt` — SRT captions

Use `--sync pad` if the audio is shorter than the video, or `--sync trim` to cut it to match.

---

## Requirements

- **Node.js 20+** — runtime (no npm install needed — the CLI is a single bundled file)
- **VOICE_AI_API_KEY** — set as environment variable or in a `.env` file in the skill root. Get a key at [voice.ai/dashboard](https://voice.ai/dashboard).
- **ffmpeg** (optional) — needed for master stitching, MP3 encoding, loudness normalization, and video muxing. The pipeline still produces individual segments, the review page, chapters, and captions without it.

---

## Configuration

The skill reads `VOICE_AI_API_KEY` from (in order):

1. Environment variable `VOICE_AI_API_KEY`
2. Environment variable `VOICEAI_API_KEY` (alternate)
3. `.env` file in the skill root

```bash
echo 'VOICE_AI_API_KEY=your-key-here' > .env
```

Use `--mock` on any command to run the full pipeline without an API key (produces placeholder audio).

---

## Commands

### `build` — Generate a voiceover from a script

```bash
node voiceai-vo.cjs build \
  --input <script.md or script.txt> \
  --voice <voice-alias-or-uuid> \
  --title "My Project" \
  [--template youtube|podcast|shortform] \
  [--language en] \
  [--video input.mp4 --mux --sync shortest] \
  [--force] [--mock]
```

**What it does:**

1. Reads the script and splits it into segments (by `##` headings for `.md`, or by sentence boundaries for `.txt`)
2. Optionally prepends/appends template intro/outro segments
3. Renders each segment via Voice.ai TTS as a numbered WAV file
4. Stitches a master audio file (if ffmpeg is available)
5. Generates chapters, captions, a review page, and metadata files
6. Optionally muxes the voiceover into an existing video

**Full options:**

| Option | Description |
|---|---|
| `-i, --input <path>` | Script file (.txt or .md) — **required** |
| `-v, --voice <id>` | Voice alias or UUID — **required** |
| `-t, --title <title>` | Project title (defaults to filename) |
| `--template <name>` | `youtube`, `podcast`, or `shortform` |
| `--mode <mode>` | `headings` or `auto` (default: headings for .md) |
| `--max-chars <n>` | Max characters per auto-chunk (default: 1500) |
| `--language <code>` | Language code (default: en) |
| `--video <path>` | Input video for muxing |
| `--mux` | Enable video muxing (requires --video) |
| `--sync <policy>` | `shortest`, `pad`, or `trim` (default: shortest) |
| `--force` | Re-render all segments (ignore cache) |
| `--mock` | Mock mode — no API calls, placeholder audio |
| `-o, --out <dir>` | Custom output directory |

### `replace-audio` — Swap the audio track on a video

```bash
node voiceai-vo.cjs replace-audio \
  --video ./input.mp4 \
  --audio ./out/my-project/master.wav \
  [--out ./out/my-project/muxed.mp4] \
  [--sync shortest|pad|trim]
```

Requires ffmpeg. If not installed, generates helper shell/PowerShell scripts instead.

| Sync policy | Behavior |
|---|---|
| `shortest` (default) | Output ends when the shorter track ends |
| `pad` | Pad audio with silence to match video duration |
| `trim` | Trim audio to match video duration |

Video stream is copied without re-encoding (`-c:v copy`). Audio is encoded as AAC. A mux report is saved alongside the output.

**Privacy:** Video processing is entirely local. Only script text is sent to Voice.ai for TTS.

### `voices` — List available voices

```bash
node voiceai-vo.cjs voices [--limit 20] [--query "deep"] [--mock]
```

---

## Available voices

Use short aliases or full UUIDs with `--voice`:

| Alias    | Voice                | Gender | Style                    |
|----------|----------------------|--------|--------------------------|
| `ellie`  | Ellie                | F      | Youthful, vibrant vlogger|
| `oliver` | Oliver               | M      | Friendly British         |
| `lilith` | Lilith               | F      | Soft, feminine           |
| `smooth` | Smooth Calm Voice    | M      | Deep, smooth narrator    |
| `corpse` | Corpse Husband       | M      | Deep, distinctive        |
| `skadi`  | Skadi                | F      | Anime character          |
| `zhongli`| Zhongli              | M      | Deep, authoritative      |
| `flora`  | Flora                | F      | Cheerful, high pitch     |
| `chief`  | Master Chief         | M      | Heroic, commanding       |

The `voices` command also returns any additional voices available on the API. Voice list is cached for 10 minutes.

---

## Build outputs

After a build, the output directory contains:

```
out/<title-slug>/
  segments/           # Numbered WAV files (001-intro.wav, 002-section.wav, …)
  master.wav          # Stitched audio (requires ffmpeg)
  master.mp3          # MP3 encode (requires ffmpeg)
  manifest.json       # Build metadata: voice, template, segment list, hashes
  timeline.json       # Segment durations and start times
  review.html         # Interactive review page with audio players
  chapters.txt        # YouTube-friendly chapter timestamps
  captions.srt        # SRT captions using segment boundaries
  description.txt     # YouTube description with chapters + Voice.ai credit
```

### review.html

A standalone HTML page with:
- Master audio player (if stitched)
- Individual segment players with titles and durations
- Collapsible script text for each segment
- Regeneration command hints

---

## Templates

Templates auto-inject intro/outro segments around the script content:

| Template | Prepends | Appends |
|---|---|---|
| `youtube` | `templates/youtube_intro.txt` | `templates/youtube_outro.txt` |
| `podcast` | `templates/podcast_intro.txt` | — |
| `shortform` | `templates/shortform_hook.txt` | — |

Edit the files in `templates/` to customize the intro/outro text.

---

## Caching

Segments are cached by a hash of: `text content + voice ID + language`.

- Unchanged segments are **skipped** on rebuild — fast iteration
- Modified segments are **re-rendered** automatically
- Use `--force` to re-render everything
- Cache manifest is stored in `segments/.cache.json`

---

## Multilingual support

Voice.ai supports 11 languages. Use `--language <code>` to switch:

`en`, `es`, `fr`, `de`, `it`, `pt`, `pl`, `ru`, `nl`, `sv`, `ca`

The pipeline auto-selects the multilingual TTS model for non-English languages.

---

## Troubleshooting

| Issue | Solution |
|---|---|
| **ffmpeg missing** | Pipeline still works — you get segments, review page, chapters, captions. Install ffmpeg for master stitching and video muxing. |
| **Rate limits (429)** | Segments render sequentially, which stays under most limits. Wait and retry. |
| **Insufficient credits (402)** | Top up at [voice.ai/dashboard](https://voice.ai/dashboard). Cached segments won't re-use credits on retry. |
| **Long scripts** | Caching makes rebuilds fast. Text over 490 chars per segment is automatically split across API calls. |
| **Windows paths** | Wrap paths with spaces in quotes: `--input "C:\My Scripts\script.md"` |

See [`references/TROUBLESHOOTING.md`](references/TROUBLESHOOTING.md) for more.

---

## References

- [Agent Skills Specification](https://agentskills.io/specification)
- [Voice.ai](https://voice.ai)
- [`references/VOICEAI_API.md`](references/VOICEAI_API.md) — API endpoints, audio formats, models
- [`references/TROUBLESHOOTING.md`](references/TROUBLESHOOTING.md) — Common issues and fixes
