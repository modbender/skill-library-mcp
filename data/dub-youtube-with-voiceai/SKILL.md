---
name: dub-youtube-with-voiceai
description: "Dub YouTube videos with Voice.ai TTS. Turn scripts into publish-ready voiceovers with chapters, captions, and audio replacement for YouTube long-form and Shorts."
version: 0.1.2
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

# Dub YouTube with Voice.ai

> This skill follows the [Agent Skills specification](https://agentskills.io/specification).

Turn any script into a **YouTube-ready voiceover** — complete with numbered segments, a stitched master, chapter timestamps, SRT captions, and a review page. Drop the voiceover onto an existing video to dub it in one command.

Built for YouTube creators who want studio-quality narration without the studio. Powered by [Voice.ai](https://voice.ai).

---

## When to use this skill

| Scenario | Why it fits |
|---|---|
| **YouTube long-form** | Full narration with chapter markers and captions |
| **YouTube Shorts** | Quick hooks with punchy delivery |
| **Course content** | Professional narration for educational videos |
| **Screen recordings** | Dub a screencast with clean AI voiceover |
| **Quick iteration** | Smart caching — edit one section, only that segment re-renders |
| **Batch production** | Same voice, consistent quality across every video |

---

## The one-command workflow

Have a script and a video? Dub it in one shot:

```bash
node voiceai-vo.cjs build \
  --input my-script.md \
  --voice oliver \
  --title "My YouTube Video" \
  --video ./my-recording.mp4 \
  --mux \
  --template youtube
```

This renders the voiceover, stitches the master audio, and drops it onto your video — all in one command. Output:

- `out/my-youtube-video/muxed.mp4` — your video dubbed with the AI voiceover
- `out/my-youtube-video/master.wav` — the standalone audio
- `out/my-youtube-video/review.html` — listen and review each segment
- `out/my-youtube-video/chapters.txt` — paste directly into your YouTube description
- `out/my-youtube-video/captions.srt` — upload to YouTube as subtitles
- `out/my-youtube-video/description.txt` — ready-made YouTube description with chapters

Use `--sync pad` if the audio is shorter than the video, or `--sync trim` to cut it to match.

---

## Requirements

- **Node.js 20+** — runtime (no npm install needed — the CLI is a single bundled file)
- **VOICE_AI_API_KEY** — set as environment variable or in a `.env` file in the skill root. Get a key at [voice.ai/dashboard](https://voice.ai/dashboard).
- **ffmpeg** (optional) — needed for master stitching, MP3 encoding, loudness normalization, and video dubbing. The pipeline still produces individual segments, the review page, chapters, and captions without it.

---

## Configuration

Set `VOICE_AI_API_KEY` as an environment variable before running:

```bash
export VOICE_AI_API_KEY=your-key-here
```

The skill does not read `.env` files or access any files for credentials — only the environment variable.

Use `--mock` on any command to run the full pipeline without an API key (produces placeholder audio).

---

## Commands

### `build` — Generate a YouTube voiceover from a script

```bash
node voiceai-vo.cjs build \
  --input <script.md or script.txt> \
  --voice <voice-alias-or-uuid> \
  --title "My YouTube Video" \
  [--template youtube] \
  [--video input.mp4 --mux --sync shortest] \
  [--force] [--mock]
```

**What it does:**

1. Reads the script and splits it into segments (by `##` headings for `.md`, or by sentence boundaries for `.txt`)
2. Optionally prepends/appends YouTube intro/outro segments
3. Renders each segment via Voice.ai TTS
4. Stitches a master audio file (if ffmpeg is available)
5. Generates YouTube chapters, SRT captions, a review page, and a ready-made description
6. Optionally dubs your video with the voiceover

**Full options:**

| Option | Description |
|---|---|
| `-i, --input <path>` | Script file (.txt or .md) — **required** |
| `-v, --voice <id>` | Voice alias or UUID — **required** |
| `-t, --title <title>` | Video title (defaults to filename) |
| `--template youtube` | Auto-inject YouTube intro/outro |
| `--mode <mode>` | `headings` or `auto` (default: headings for .md) |
| `--max-chars <n>` | Max characters per auto-chunk (default: 1500) |
| `--language <code>` | Language code (default: en) |
| `--video <path>` | Input video to dub |
| `--mux` | Enable video dubbing (requires --video) |
| `--sync <policy>` | `shortest`, `pad`, or `trim` (default: shortest) |
| `--force` | Re-render all segments (ignore cache) |
| `--mock` | Mock mode — no API calls, placeholder audio |
| `-o, --out <dir>` | Custom output directory |

### `replace-audio` — Dub an existing video

```bash
node voiceai-vo.cjs replace-audio \
  --video ./my-video.mp4 \
  --audio ./out/my-video/master.wav \
  [--out ./out/my-video/dubbed.mp4] \
  [--sync shortest|pad|trim]
```

Requires ffmpeg. If not installed, generates helper shell/PowerShell scripts instead.

| Sync policy | Behavior |
|---|---|
| `shortest` (default) | Output ends when the shorter track ends |
| `pad` | Pad audio with silence to match video duration |
| `trim` | Trim audio to match video duration |

Video stream is copied without re-encoding (`-c:v copy`). Audio is encoded as AAC for YouTube compatibility.

**Privacy:** Video processing is entirely local. Only script text is sent to Voice.ai for TTS. Your video files never leave your machine.

### `voices` — List available voices

```bash
node voiceai-vo.cjs voices [--limit 20] [--query "deep"] [--mock]
```

---

## Available voices

Use short aliases or full UUIDs with `--voice`:

| Alias    | Voice                | Gender | Best for YouTube                  |
|----------|----------------------|--------|-----------------------------------|
| `ellie`  | Ellie                | F      | Vlogs, lifestyle, social content  |
| `oliver` | Oliver               | M      | Tutorials, narration, explainers  |
| `lilith` | Lilith               | F      | ASMR, calm walkthroughs           |
| `smooth` | Smooth Calm Voice    | M      | Documentaries, long-form essays   |
| `corpse` | Corpse Husband       | M      | Gaming, entertainment             |
| `skadi`  | Skadi                | F      | Anime, character content          |
| `zhongli`| Zhongli              | M      | Gaming, dramatic intros           |
| `flora`  | Flora                | F      | Kids content, upbeat videos       |
| `chief`  | Master Chief         | M      | Gaming, action trailers           |

The `voices` command also returns any additional voices available on the API. Voice list is cached for 10 minutes.

---

## Build outputs

After a build, the output directory contains everything you need to publish on YouTube:

```
out/<title-slug>/
  segments/           # Numbered WAV files (001-intro.wav, 002-section.wav, …)
  master.wav          # Stitched voiceover (requires ffmpeg)
  master.mp3          # MP3 for upload (requires ffmpeg)
  muxed.mp4           # Dubbed video (if --video --mux used)
  chapters.txt        # Paste into YouTube description
  captions.srt        # Upload as YouTube subtitles
  description.txt     # Ready-made YouTube description with chapters
  review.html         # Interactive review page with audio players
  manifest.json       # Build metadata: voice, template, segment list
  timeline.json       # Segment durations and start times
```

### YouTube workflow

1. Run the build command
2. Upload `muxed.mp4` (or your original video + `master.mp3` as audio)
3. Paste `chapters.txt` content into your YouTube description
4. Upload `captions.srt` as subtitles in YouTube Studio
5. Done — professional narration, chapters, and captions in minutes

---

## YouTube template

Use `--template youtube` to auto-inject a branded intro and outro:

| Segment | Source file |
|---|---|
| Intro (prepended) | `templates/youtube_intro.txt` |
| Outro (appended) | `templates/youtube_outro.txt` |

Edit the files in `templates/` to customize your channel's branding.

---

## Caching

Segments are cached by a hash of: `text content + voice ID + language`.

- Unchanged segments are **skipped** on rebuild — fast iteration
- Modified segments are **re-rendered** automatically
- Use `--force` to re-render everything
- Cache manifest is stored in `segments/.cache.json`

---

## Multilingual dubbing

Voice.ai supports 11 languages — dub your YouTube videos for global audiences:

`en`, `es`, `fr`, `de`, `it`, `pt`, `pl`, `ru`, `nl`, `sv`, `ca`

```bash
node voiceai-vo.cjs build \
  --input script-spanish.md \
  --voice ellie \
  --title "Mi Video" \
  --language es \
  --video ./my-video.mp4 \
  --mux
```

The pipeline auto-selects the multilingual TTS model for non-English languages.

---

## Troubleshooting

| Issue | Solution |
|---|---|
| **ffmpeg missing** | Pipeline still works — you get segments, review page, chapters, captions. Install ffmpeg for stitching and video dubbing. |
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
