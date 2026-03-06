---
name: mediaproc
description: Process media files (video, audio, images) via a locked-down SSH container with ffmpeg, sox, and imagemagick. Use when the user wants to transcode video, process audio, manipulate images, or work with media files.
compatibility: Requires ssh and a running mediaproc instance. MEDIAPROC_HOST and MEDIAPROC_PORT env vars must be set.
metadata:
  author: psyb0t
  homepage: https://github.com/psyb0t/docker-mediaproc
---

# mediaproc

Locked-down media processing over SSH. Built on [lockbox](https://github.com/psyb0t/docker-lockbox) — no shell access, no injection, no bullshit.

For installation and deployment, see [references/setup.md](references/setup.md).

## SSH Wrapper

Use `scripts/mediaproc.sh` for all commands. It handles host, port, and host key acceptance via `MEDIAPROC_HOST` and `MEDIAPROC_PORT` env vars.

```bash
scripts/mediaproc.sh <command> [args]
scripts/mediaproc.sh <command> < input_file
scripts/mediaproc.sh <command> > output_file
```

## Media Tools

| Command    | Description                                  |
| ---------- | -------------------------------------------- |
| `ffmpeg`   | Video/audio encoding, transcoding, filtering |
| `ffprobe`  | Media file analysis                          |
| `sox`      | Audio processing                             |
| `soxi`     | Audio file info                              |
| `convert`  | Image conversion/manipulation (ImageMagick)  |
| `identify` | Image file info (ImageMagick)                |
| `magick`   | ImageMagick CLI                              |

## Upload, Process, Download

```bash
# Upload
scripts/mediaproc.sh "put input.mp4" < input.mp4

# Transcode
scripts/mediaproc.sh "ffmpeg -i /work/input.mp4 -c:v libx264 /work/output.mp4"

# Download result
scripts/mediaproc.sh "get output.mp4" > output.mp4

# Clean up
scripts/mediaproc.sh "remove-file input.mp4"
scripts/mediaproc.sh "remove-file output.mp4"
```

## Video Operations

```bash
# Get video info as JSON
scripts/mediaproc.sh "ffprobe -v quiet -print_format json -show_format -show_streams /work/video.mp4"

# Apply frei0r glow effect
scripts/mediaproc.sh "ffmpeg -i /work/in.mp4 -vf frei0r=glow:0.5 /work/out.mp4"

# Extract audio from video
scripts/mediaproc.sh "ffmpeg -i /work/video.mp4 -vn -acodec libmp3lame /work/audio.mp3"

# Create thumbnail from video
scripts/mediaproc.sh "ffmpeg -i /work/video.mp4 -ss 00:00:05 -vframes 1 /work/thumb.jpg"
```

## Audio Operations

```bash
# Convert audio format
scripts/mediaproc.sh "sox /work/input.wav /work/output.mp3"

# Get audio info
scripts/mediaproc.sh "soxi /work/audio.wav"

# Normalize audio
scripts/mediaproc.sh "sox /work/input.wav /work/output.wav norm"
```

## Image Operations

```bash
# Resize image
scripts/mediaproc.sh "convert /work/input.png -resize 50% /work/output.png"

# Create thumbnail
scripts/mediaproc.sh "convert /work/input.jpg -thumbnail 200x200 /work/thumb.jpg"

# Get image info
scripts/mediaproc.sh "identify /work/image.png"
```

## File Operations

All paths relative to the work directory. Traversal blocked.

| Command                | Description                        |
| ---------------------- | ---------------------------------- |
| `put <path>`           | Upload file from stdin             |
| `get <path>`           | Download file to stdout            |
| `list-files [--json]`  | List directory                     |
| `remove-file <path>`   | Delete a file                      |
| `create-dir <path>`    | Create directory                   |
| `remove-dir <path>`    | Remove empty directory             |
| `remove-dir-recursive <path>` | Remove directory recursively |
| `move-file <src> <dst>`| Move or rename                     |
| `copy-file <src> <dst>`| Copy a file                        |
| `file-info <path>`     | Get file metadata as JSON          |
| `file-exists <path>`   | Check if file exists (true/false)  |
| `file-hash <path>`     | Get SHA256 hash                    |
| `disk-usage [path]`    | Get bytes used                     |
| `search-files <glob>`  | Glob search                        |
| `append-file <path>`   | Append stdin to a file             |

```bash
# List files
scripts/mediaproc.sh "list-files"

# List as JSON (size, modified, isDir, permissions)
scripts/mediaproc.sh "list-files --json"

# List subdirectory
scripts/mediaproc.sh "list-files project1"

# File operations
scripts/mediaproc.sh "create-dir project1"
scripts/mediaproc.sh "move-file old.mp4 new.mp4"
scripts/mediaproc.sh "copy-file input.mp4 backup.mp4"
scripts/mediaproc.sh "file-info video.mp4"
scripts/mediaproc.sh "file-exists video.mp4"
scripts/mediaproc.sh "file-hash video.mp4"
scripts/mediaproc.sh "search-files '*.mp4'"
scripts/mediaproc.sh "disk-usage"
scripts/mediaproc.sh "remove-dir-recursive project1"
```

## Plugins

- **frei0r** — Video effect plugins (used via `-vf frei0r=...`)
- **LADSPA** — Audio effect plugins: SWH, TAP, CMT (used via `-af ladspa=...`)
- **LV2** — Audio plugins (used via `-af lv2=...`)

## Fonts

2200+ fonts included covering emoji, CJK, Arabic, Thai, Indic, monospace, and more. Custom fonts can be mounted to `/usr/share/fonts/custom`.
