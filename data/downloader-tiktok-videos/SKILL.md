---
name: Downloader Tiktok Videos
description: >
  Automatically downloads the latest video (or the N most recent) from a public TikTok account
  using yt-dlp. Use this skill whenever the user mentions TikTok, a @username, "download a TikTok
  video", "get the latest TikTok post", "scrape TikTok", or any request to download/extract content
  from TikTok. Also applies when the user wants to retrieve metadata only (title, hashtags, date,
  stats) without downloading, archive TikTok videos, or automate TikTok content retrieval.
---

# Downloader TikTok Videos

## Overview

Downloader TikTok Videos downloads the latest video (or multiple videos) from a public TikTok
account using **yt-dlp**. Read this documentation fully before writing any code or running commands.

## Prerequisites

This skill requires **yt-dlp** (and optionally **ffmpeg** for audio/video merging).

> ⚠️ The commands below modify your host environment (install packages system-wide).
> Run them only if yt-dlp is not already installed and you are comfortable doing so.

```bash
pip install -U yt-dlp --break-system-packages   # Linux system Python
# or
pip install -U yt-dlp                           # virtualenv / macOS
yt-dlp --version                                # verify install
```

## Operation Types

This skill supports four operation types. Determine which one(s) the user needs:

1. **Quick Download** — Download the latest video from an account
2. **Bulk Download** — Download the N most recent videos
3. **Metadata Only** — Retrieve info/stats without downloading the video
4. **Direct Video URL** — Download from a specific video URL

## Workflows

### 1. Quick Download — Latest Video from an Account

**When to use:** User provides a @username or profile URL

**Steps:**
1. Normalize the username (strip `@` if present)
2. Build the profile URL: `https://www.tiktok.com/@{username}`
3. Fetch metadata for the latest video (`--playlist-items 1 --no-download`)
4. Show the user the video info (title, date, duration)
5. Download with the optimal command
6. Confirm success and provide the file path

**Command:**
```bash
yt-dlp \
  --playlist-items 1 \
  --format "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  --merge-output-format mp4 \
  --output "./%(uploader_id)s_%(upload_date)s_%(id)s.%(ext)s" \
  "https://www.tiktok.com/@{username}"
```

**Verify the result:**
```bash
ls -lh ./*.mp4
```

### 2. Bulk Download — N Most Recent Videos

**When to use:** User wants multiple videos

**Steps:**
1. Ask how many videos (if not specified, default = 5)
2. Build the command with `--playlist-items 1-N`
3. Add `--download-archive` to avoid duplicates
4. Download with progress output
5. List downloaded files

**Command:**
```bash
yt-dlp \
  --playlist-items 1-{N} \
  --format "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  --merge-output-format mp4 \
  --download-archive ./tiktok_archive.txt \
  --output "./%(uploader_id)s/%(upload_date)s_%(id)s.%(ext)s" \
  "https://www.tiktok.com/@{username}"
```

### 3. Metadata Only

**When to use:** User wants video info without downloading

**Read:** `references/metadata.md` for all available fields and the full command

**Quick command:**
```bash
yt-dlp \
  --playlist-items 1 \
  --skip-download \
  --write-info-json \
  --print "%(uploader_id)s | %(upload_date)s | %(duration)ss | %(view_count)s views | %(title)s" \
  "https://www.tiktok.com/@{username}"
```

### 4. Direct Video URL

**When to use:** User provides a direct video URL

**Command:**
```bash
yt-dlp \
  --format "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  --merge-output-format mp4 \
  --output "./%(uploader_id)s_%(id)s.%(ext)s" \
  "{video_url}"
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `HTTP Error 403` | TikTok rate limiting | Add `--sleep-interval 3 --max-sleep-interval 6` |
| `Unable to extract` | Outdated yt-dlp | `pip install -U yt-dlp --break-system-packages` |
| `Private account` | Private account | Use `--cookies-from-browser chrome` if logged in ⚠️ exports session cookies — keep them private |
| `No video formats` | Geo-restriction | Add `--geo-bypass` |
| `Sign in required` | Restricted content | Provide cookies via `--cookies cookies.txt` ⚠️ treat this file like a password |
| `Merge requires ffmpeg` | ffmpeg missing | `apt-get install ffmpeg -y` |

> ⚠️ **Cookie security note:** Browser cookies exported via `--cookies-from-browser` or `cookies.txt`
> contain active session tokens. Never share these files, commit them to version control, or pass
> them to untrusted scripts. Delete them after use if no longer needed.

## Username Normalization

```python
# Accepts all these formats:
# @myaccount  →  myaccount
# myaccount   →  myaccount
# https://www.tiktok.com/@myaccount  →  myaccount

def normalize(input_str):
    if "tiktok.com/@" in input_str:
        return input_str.split("tiktok.com/@")[-1].split("/")[0]
    return input_str.lstrip("@").strip()
```

## Reference Files

Load these references as needed:

**references/metadata.md**
- When: Fetching metadata, working with JSON fields
- Contains: All available yt-dlp fields, print format examples, JSON export

**references/advanced.md**
- When: Watermark removal, cookies, proxy, custom headers
- Contains: Advanced techniques, restriction bypass, full yt-dlp options

**KBLICENSE.txt**
- When: Questions about usage rights or Terms of Service
- Contains: Usage conditions, permitted and prohibited uses

## Output Guidelines

- Always display metadata before downloading (title, date, duration)
- Confirm the downloaded file path
- Show the final file size
- On error, propose the fix directly

## Example Queries

**Quick download:**
- "Download the latest video from @someaccount"
- "Get the latest TikTok post from myaccount"
- "Download the last video from https://www.tiktok.com/@user"

**Bulk download:**
- "Download the 5 latest videos from @user"
- "Get the last 10 videos from @account"

**Metadata:**
- "Give me the info on the latest video from @user"
- "What is the title and date of the last post from @account"

**Direct URL:**
- "Download this TikTok video: https://www.tiktok.com/@user/video/123456"
