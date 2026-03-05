---
name: nano-banana-pro-enhanced
description: Generate or edit images via Gemini 3 Pro Image (Nano Banana Pro).
metadata: {"openclaw":{"emoji":"🍌","homepage":"https://ai.google.dev/","primaryEnv":"GEMINI_API_KEY","requires":{"bins":["uv"],"env":["GEMINI_API_KEY"]},"install":[{"id":"uv-brew","kind":"brew","formula":"uv","bins":["uv"],"label":"Install uv (brew)"}]}}
---

# Nano Banana Pro (Gemini 3 Pro Image)

Use the bundled script to generate or edit images.

Generate
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "your image description" --filename "output.png" --resolution 1K --aspect-ratio 16:9
```

Edit
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "edit instructions" --filename "output.png" --input-image "/path/in.png" --resolution 2K
```

Batch API (50% cheaper, non-blocking)
```bash
# Single image
uv run {baseDir}/scripts/generate_image.py --prompt "description" --filename "output.png" --batch

# Multiple images from JSON file
uv run {baseDir}/scripts/generate_image.py --batch-file .tmp/requests.json

# Check / retrieve result of a previous job
uv run {baseDir}/scripts/generate_image.py --batch-check "batches/abc123" --filename "output.png"
```

Batch file format (JSON array):
```json
[
  {
    "prompt": "a cute cat",
    "filename": "cat.png",
    "resolution": "1K",
    "aspect_ratio": "16:9"
  },
  {
    "prompt": "a dog running",
    "filename": "dog.png",
    "resolution": "2K"
  }
]
```

Batch notes
- `--batch` is always non-blocking: submits the job, prints `BATCH_JOB:` token, and exits immediately.
- After submitting, add a temporary check list to HEARTBEAT.md. Include **why** this image was requested (context/intent), so it's clear even after a session reset.
  ```
  # Temporary Check List

  - **Nano Banana Batch job**: <why this image was requested>. Check `batches/abc123` for job result. When ready, retrieve and send to user with mediaUrl parameter. Remove this item after reporting the result.
  ```
- If the user explicitly requests a timed check, use a cronjob instead of HEARTBEAT.md.
- The script tracks pending jobs in `memory/pending-batch-jobs.json`. Created on batch submit, removed on `--batch-check` completion. Format: `[{"job_name", "filename", "prompt", "created_at"}]`. File is deleted when empty.

API key
- `GEMINI_API_KEY` env var
- Or set `skills."nano-banana-pro".apiKey` / `skills."nano-banana-pro".env.GEMINI_API_KEY` in `~/.clawdbot/clawdbot.json`

Notes
- Resolutions: `1K` (default), `2K`, `4K`.
- Aspect ratios: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`. Generation only (ignored for editing).
- Use timestamps in filenames: `YYYYMMDD-hhmmss-name.png`.
- The script outputs the saved file path. To send images via messaging channels, use the `mediaUrl` parameter in your channel action (e.g., `mediaUrl: "/absolute/path/to/output.png"`).
- Do not read the image back; report the saved path and use it with mediaUrl to deliver the image to the user.
