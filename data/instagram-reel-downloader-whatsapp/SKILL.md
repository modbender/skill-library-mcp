---
name: instagram-reel-downloader-whatsapp
description: Download an Instagram Reel via sssinstagram.com and return it as a WhatsApp-ready video file. Use when a reel URL is provided and yt-dlp is blocked or not preferred.
---

# Instagram Reel via sssinstagram

## Requirements

- Node.js 18+.
- `playwright-core` installed in the runtime.
- Chromium-compatible browser binary available via:
  - `BROWSER_EXECUTABLE_PATH` (preferred), or
  - default `/usr/bin/brave-browser`.

## Environment variables

- `OPENCLAW_WORKSPACE` (optional): workspace root used for output path.
- `REEL_DOWNLOAD_DIR` (optional): explicit download directory override.
- `BROWSER_EXECUTABLE_PATH` (optional): browser binary path override.

1. Validate input URL.
   - Accept only `https://www.instagram.com/reel/...` (or `/reels/...`) links.

2. Run downloader automation script.
   - Execute:
     - `node scripts/download_via_sss.mjs "<instagram-url>"`
   - On success it prints:
     - `MEDIA_PATH=<absolute path>`

3. Send the file to user on WhatsApp.
   - Use `message` `action=send` with `media` set to `MEDIA_PATH`.
   - Add a small caption like `Done 🐾`.

4. If the site blocks automation.
   - Retry once after a short wait.
   - If it still fails, report failure cleanly and ask user for another link.

## Notes
- Uses `BROWSER_EXECUTABLE_PATH` if set, otherwise defaults to `/usr/bin/brave-browser`.
- Saves videos to `REEL_DOWNLOAD_DIR` when set, else `<workspace>/downloads` (`OPENCLAW_WORKSPACE` or current working directory).
- Uses Playwright (`playwright-core`) in headless mode.
- Optional cleanup script: `bash scripts/cleanup_reels.sh 30` (minutes to retain, default 30).
- For user privacy, do not store links longer than needed for the download run.