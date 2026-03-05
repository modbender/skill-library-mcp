---
name: gettr-transcribe
description: Download audio from a GETTR post or streaming page and transcribe it locally with MLX Whisper on Apple Silicon (with timestamps via VTT). Use when given a GETTR URL and asked to produce a transcript. Summarization is handled by the caller.
homepage: https://gettr.com
metadata:
  {
    "clawdbot":
      {
        "emoji": "📺",
        "requires": { "bins": ["mlx_whisper", "ffmpeg"] },
        "install":
          [
            {
              "id": "mlx-whisper",
              "kind": "pip",
              "package": "mlx-whisper",
              "bins": ["mlx_whisper"],
              "label": "Install mlx-whisper (pip)",
            },
            {
              "id": "ffmpeg",
              "kind": "brew",
              "formula": "ffmpeg",
              "bins": ["ffmpeg"],
              "label": "Install ffmpeg (brew)",
            },
          ],
      },
  }
---

# Gettr Transcribe (MLX Whisper)

## Quick start

```bash
# 1. Parse the slug from the URL (just read it — no script needed)
#    https://gettr.com/post/p1abc2def  → slug = p1abc2def
#    https://gettr.com/streaming/p3xyz → slug = p3xyz

# 2. Get the audio/video URL via browser automation (see Step 1 below)
#    For /streaming/ URLs: extract the .m4a audio URL
#    For /post/ URLs: extract the og:video .m3u8 URL

# 3. Run download + transcription pipeline
bash scripts/run_pipeline.sh "<AUDIO_OR_VIDEO_URL>" "<SLUG>"
```

To explicitly set the transcription language (recommended for non-English content):

```bash
bash scripts/run_pipeline.sh --language zh "<AUDIO_OR_VIDEO_URL>" "<SLUG>"
```

Common language codes: `zh` (Chinese), `en` (English), `ja` (Japanese), `ko` (Korean), `es` (Spanish), `fr` (French), `de` (German), `ru` (Russian).

This outputs:

- `./out/gettr-transcribe/<slug>/audio.wav`
- `./out/gettr-transcribe/<slug>/audio.vtt`

Summarization is handled separately by the caller (see your prompt for summarization instructions).

---

## Workflow (GETTR URL → transcript)

### Inputs to confirm

Ask for:

- GETTR post URL
- Language (optional): if the video is non-English and auto-detection fails, ask for the language code (e.g., `zh` for Chinese)

Notes:

- This skill does **not** handle authentication-gated GETTR posts.
- This skill does **not** translate; outputs stay in the video's original language.
- If transcription quality is poor or mixed with English, re-run with explicit `--language` flag.

### Prereqs (local)

- `mlx_whisper` installed and on PATH
- `ffmpeg` installed (recommended: `brew install ffmpeg`)

### Step 0 — Parse the slug and pick an output directory

Parse the slug directly from the GETTR URL — just read the last path segment, no script needed:

- `https://gettr.com/post/p1abc2def` → slug = `p1abc2def`
- `https://gettr.com/streaming/p3xyz789` → slug = `p3xyz789`

Output directory: `./out/gettr-transcribe/<slug>/`

Directory structure:

- `./out/gettr-transcribe/<slug>/audio.wav`
- `./out/gettr-transcribe/<slug>/audio.vtt`

### Step 1 — Get the audio/video URL via browser automation

Use browser automation to navigate to the GETTR URL and extract the media URL from the rendered DOM.

#### For `/streaming/` URLs (primary path)

Streaming pages provide a direct `.m4a` audio download. Extract it by deriving from the `og:video` meta tag:

1. Navigate to the GETTR streaming URL and wait for the page to fully load (JavaScript must execute)
2. Extract the audio URL via JavaScript:
   ```javascript
   const ogVideo = document.querySelector('meta[property="og:video"]')?.getAttribute("content");
   // Replace .m3u8 with /audio.m4a to get the direct audio download URL
   const audioUrl = ogVideo.replace(".m3u8", "/audio.m4a");
   ```
3. Use the `.m4a` URL for the pipeline in Step 2

The `.m4a` URL is a direct file download (no HLS), so it downloads faster and more reliably than the `.m3u8` stream.

#### For `/post/` URLs (fallback path)

Post pages do not have a "Download Audio" button. Extract the `og:video` URL from the rendered DOM:

1. Navigate to the GETTR post URL and wait for the page to fully load
2. Extract the video URL via JavaScript:
   ```javascript
   document.querySelector('meta[property="og:video"]')?.getAttribute("content");
   ```
3. Use the `.m3u8` URL directly for the pipeline in Step 2

If browser automation is not available or fails, see `references/troubleshooting.md` for how to guide the user to manually extract the URL from their browser.

### Step 2 — Run the pipeline (download + transcribe)

Feed the extracted URL and slug into the pipeline:

```bash
bash scripts/run_pipeline.sh "<AUDIO_OR_VIDEO_URL>" "<SLUG>"
```

To explicitly set the language (recommended when auto-detection fails):

```bash
bash scripts/run_pipeline.sh --language zh "<AUDIO_OR_VIDEO_URL>" "<SLUG>"
```

The pipeline does two things:

1. Downloads audio as 16kHz mono WAV via ffmpeg (handles both `.m4a` and `.m3u8` inputs)
2. Transcribes with MLX Whisper, outputting VTT with timestamps

#### If the pipeline fails with HTTP 412 (stale signed URL)

This error occurs with `/streaming/` URLs when the signed URL has expired. Re-run browser automation to get a fresh URL, then retry the pipeline.

If browser automation is not available or fails, see `references/troubleshooting.md` for how to guide the user to manually extract the fresh URL from their browser.

Notes:

- By default, language is auto-detected. For non-English content where detection fails, use `--language`.
- If too slow or memory-heavy, try smaller models: `mlx-community/whisper-medium` or `mlx-community/whisper-small`.
- If quality is poor, try the full model: `mlx-community/whisper-large-v3` (slower but more accurate).
- If `--word-timestamps` causes issues, the pipeline retries automatically without it.

## Bundled scripts

- `scripts/run_pipeline.sh`: download + transcription pipeline (takes an audio/video URL and slug)
- `scripts/download_audio.sh`: download/extract audio from HLS (.m3u8) or direct (.m4a) URL to 16kHz mono WAV

### Error handling

- **No audio track**: The download script validates output and reports if the source has no audio.
- **HTTP 412 errors**: Occurs with `/streaming/` URLs when the signed URL has expired. Re-run browser automation to get a fresh URL (see Step 1); if that fails, see `references/troubleshooting.md`.

## Troubleshooting

See `references/troubleshooting.md` for detailed solutions to common issues including:

- HTTP 412 errors (stale signed URLs)
- Download errors
- Transcription quality issues
