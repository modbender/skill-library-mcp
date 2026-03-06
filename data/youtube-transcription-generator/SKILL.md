---
name: youtube-transcription-generator
description: "Use VLM Run (vlmrun) to generate transcriptions from YouTube videos. Download a video with yt-dlp, then run vlmrun to transcribe with optional timestamps. VLMRUN_API_KEY must be in .env; follow vlmrun-cli-skill for CLI setup and options."
---

## YouTube Transcription Generator (VLM Run)

Generate transcriptions from YouTube videos using **vlmrun** for speech-to-text and optional timestamps. This skill:

1. **Downloads** the YouTube video (or audio) with **yt-dlp**.
2. **Transcribes** the video with **vlmrun** (Orion visual AI).
3. **Saves** the transcript to a file (plain text or with timestamps).

Refer to **vlmrun-cli-skill** for vlmrun CLI setup, environment variables, and all `vlmrun chat` options.

---

## How the assistant should use this skill

- **Check `.env` for API key**
  - Ensure `.env` (or `.env.local`) contains `VLMRUN_API_KEY`.
  - If missing, instruct the user to set it before running any `vlmrun` commands.

- **Use vlmrun for transcription only**
  - For **transcription** (and optional timestamps), use the **vlmrun** CLI with a **video file** as input (`-i <video>`).
  - vlmrun accepts video files (e.g. `.mp4`). For YouTube, the skill first downloads the video with **yt-dlp**, then passes the file to vlmrun.

- **Workflow**
  - User provides a **YouTube URL** (and optionally output path).
  - Download the video (or audio-only for faster/smaller) with **yt-dlp**.
  - Run: `vlmrun chat "Transcribe this video with timestamps for each section. Output the full transcript in a clear, readable format." -i <downloaded_file> -o <output_dir>`.
  - Capture vlmrun’s response and save it as the transcript file (e.g. `transcript.txt`).

---

## Prerequisites

- **Python 3.10+**
- **VLMRUN_API_KEY** (required for vlmrun)
- **vlmrun CLI** (`vlmrun[cli]`)
- **yt-dlp** (for downloading YouTube videos)

> See **vlmrun-cli-skill** for detailed vlmrun usage and examples (including video transcription).

---

## Installation & Setup

From the `youtube-transcription-generator` directory:

**Windows (PowerShell):**

```powershell
cd path\to\youtube-transcription-generator
uv venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

**macOS/Linux:**

```bash
cd path/to/youtube-transcription-generator
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Copy `.env_template` to `.env` and set `VLMRUN_API_KEY`.

---

## Quick Start: Transcribe a YouTube Video

### Option A: Run the script (recommended)

```bash
# From youtube-transcription-generator directory, with venv activated
python scripts/run_transcription.py "https://www.youtube.com/watch?v=VIDEO_ID" -o ./output
```

This will:

1. Download the video with yt-dlp into the output directory.
2. Run vlmrun to transcribe the video.
3. Save the transcript as `output/transcript.txt` (and keep artifacts in `output/`).

### Option B: Manual vlmrun (after downloading the video yourself)

```bash
# 1) Download with yt-dlp
yt-dlp -f "bv*[ext=mp4]+ba/best[ext=mp4]/best" -o video.mp4 "https://www.youtube.com/watch?v=VIDEO_ID"

# 2) Transcribe with vlmrun (see vlmrun-cli-skill for options)
vlmrun chat "Transcribe this video with timestamps for each section. Output the full transcript in a clear, readable format." -i video.mp4 -o ./output
```

Capture the vlmrun stdout and save it as your transcript, or use `--json` if you need structured output.

---

## Prompt variants for vlmrun

- **With timestamps:**  
  `"Transcribe this video with timestamps for each section. Output the full transcript in a clear, readable format."`

- **Plain transcript only:**  
  `"Transcribe everything said in this video. Output only the spoken text, no timestamps."`

- **Structured (e.g. JSON):**  
  Use `--json` and ask for a structured format in the prompt (e.g. list of `{ "time": "...", "text": "..." }`).

---

## Workflow checklist

- [ ] Confirm `vlmrun` is installed and `VLMRUN_API_KEY` is set (see vlmrun-cli-skill).
- [ ] Install dependencies: `uv pip install -r requirements.txt` (includes `vlmrun[cli]` and `yt-dlp`).
- [ ] Run `python scripts/run_transcription.py <youtube_url> -o ./output` or download + vlmrun manually.
- [ ] Find transcript in the output directory (e.g. `output/transcript.txt`).

---

## Troubleshooting

- **vlmrun not found**  
  Activate the venv and run: `uv pip install "vlmrun[cli]"`. See vlmrun-cli-skill.

- **Authentication errors**  
  Verify `VLMRUN_API_KEY` in `.env` or the current shell.

- **yt-dlp fails**  
  Update yt-dlp: `uv pip install -U yt-dlp`. Check the URL is a valid public YouTube video.

- **Large or long videos**  
  Use audio-only download in the script (e.g. `-f bestaudio`) to reduce size and speed up transcription.
