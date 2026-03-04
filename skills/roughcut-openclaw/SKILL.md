---
name: roughcut
description: "Run RoughCut headlessly on macOS to generate Final Cut Pro (FCPXML) rough-cut timeline variants from a talking-head video — local-first, no media upload."
metadata:
  {
    "openclaw":
      {
        "os": ["darwin"],
        "requires":
          {
            "bins": ["bash", "python3", "curl", "ffmpeg", "node", "npm"],
            "config": [
              "skills.entries.roughcut.config.repo_root",
              "skills.entries.roughcut.config.output_root"
            ]
          },
        "primaryEnv": "GEMINI_API_KEY"
      }
  }
---

# RoughCut (macOS)

This skill lets an OpenClaw agent run RoughCut locally on a user's Mac to produce `RoughCut.xml_variants.zip` from a raw video file, without uploading media.

## Preconditions

1. Confirm the video is present on local disk and get an absolute file path (example: `/Users/alice/Movies/raw.mp4`).
   If the file is on Google Drive/iCloud/Dropbox, ensure it is fully downloaded and accessible as a local file path.
   Tip: on macOS, you can drag the video file into Terminal to paste its absolute path.
   If the user is on a different machine than the OpenClaw Mac, agree on a delivery method:
   - Synced folder: a folder that syncs onto the OpenClaw Mac (iCloud Drive, Dropbox, Google Drive Desktop, etc.).
   - Direct download URL: ask the user for a direct HTTPS download link (for example an S3/R2/GCS pre-signed URL), then run RoughCut with `--video-url` (it downloads into `output_root/RoughCut.inputs/` automatically).

2. Confirm RoughCut repo is present on the same Mac.
   - Repo: https://github.com/samerGMTM22/OpenClaw-RoughCut

3. If the user enables fluff removal, ensure `GEMINI_API_KEY` is set in the environment that will run RoughCut.
   If it is not set, ask the user to provide it and explain it is used only for fluff removal.

## Questions To Ask The User

1. Do you want to remove bad takes? (default: yes)
2. Do you want to remove fluff/off-topic content? (default: no)
3. If fluff removal is enabled: what is the video topic/goal? (required)

## How To Run

Use `repo_root` and `output_root` from OpenClaw config:

```bash
bash "$REPO_ROOT/scripts/openclaw/roughcut.sh" \
  --video "$VIDEO_ABS_PATH" \
  --out "$OUTPUT_ROOT" \
  --remove-bad-takes true \
  --remove-fluff false
```

If the user provides a direct download URL, you can pass it directly (the runner downloads to `$OUTPUT_ROOT/RoughCut.inputs/` first):

```bash
bash "$REPO_ROOT/scripts/openclaw/roughcut.sh" \
  --video-url "$VIDEO_URL" \
  --out "$OUTPUT_ROOT" \
  --remove-bad-takes true \
  --remove-fluff false
```

If the URL has no filename (common for pre-signed URLs), include `--video-name`, and optionally `--video-sha256`:

```bash
bash "$REPO_ROOT/scripts/openclaw/roughcut.sh" \
  --video-url "$VIDEO_URL" \
  --video-name "my_video.mov" \
  --video-sha256 "0123456789abcdef..." \
  --out "$OUTPUT_ROOT" \
  --remove-bad-takes true \
  --remove-fluff false
```

If fluff removal is enabled:

```bash
bash "$REPO_ROOT/scripts/openclaw/roughcut.sh" \
  --video "$VIDEO_ABS_PATH" \
  --out "$OUTPUT_ROOT" \
  --remove-bad-takes true \
  --remove-fluff true \
  --topic "$TOPIC"
```

The runner prints a single-line JSON result to stdout. On success it includes:
- `xml_variants_zip`: absolute path to `RoughCut.xml_variants.zip`
- `video_path`: absolute path to the input video used for processing
- `downloaded_video_path`: present only when `--video-url` was used (where the video was saved)

On failure it will include:
- `error`
- optionally `debug_zip` (a bundle of intermediate outputs)

## What To Return To The User

1. The output zip path(s) from the JSON.
2. How to import into Final Cut Pro:
   - Unzip `RoughCut.xml_variants.zip`.
   - In Final Cut Pro: `File -> Import -> XML...`
   - Choose the desired `.fcpxml` variant.
