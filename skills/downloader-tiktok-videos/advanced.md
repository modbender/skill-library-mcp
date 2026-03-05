# Advanced Techniques — Downloader TikTok Videos

## Watermark Removal

yt-dlp offers a specific format that may be watermark-free depending on the creator's settings:

```bash
yt-dlp \
  --format "download_addr-0/bestvideo[ext=mp4]+bestaudio/best" \
  --merge-output-format mp4 \
  --output "./%(uploader_id)s_%(id)s.%(ext)s" \
  "{url}"
```

List all available formats to check:
```bash
yt-dlp -F "https://www.tiktok.com/@user/video/ID"
```

> ⚠️ Watermark-free format availability depends on the video creator's settings.

---

## Cookies & Authentication

### From the browser (easiest method)
```bash
# Chrome
yt-dlp --cookies-from-browser chrome URL

# Firefox
yt-dlp --cookies-from-browser firefox URL

# Edge
yt-dlp --cookies-from-browser edge URL
```

### From a cookies file (Netscape format)
```bash
yt-dlp --cookies /path/to/cookies.txt URL
```

**How to export cookies (manual methods only):**

Option A — Chrome DevTools (no extension needed):
1. Open Chrome, log in to TikTok
2. Open DevTools (F12) → Application tab → Cookies → https://www.tiktok.com
3. Manually copy the values you need into a Netscape-format cookies.txt

Option B — Firefox (built-in export):
1. Open Firefox, log in to TikTok
2. Use the built-in `--cookies-from-browser firefox` flag directly (no file needed)

> ⚠️ Avoid third-party browser extensions for cookie export — they request broad
> permissions and may themselves collect your session data. Use built-in browser
> tools or the `--cookies-from-browser` flag whenever possible.

---

## Rate Limiting Bypass

```bash
yt-dlp \
  --sleep-interval 2 \
  --max-sleep-interval 5 \
  --sleep-requests 1 \
  --retries 5 \
  --fragment-retries 5 \
  --retry-sleep 5 \
  "https://www.tiktok.com/@{username}"
```

---

## Custom Headers

```bash
yt-dlp \
  --add-header "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  --add-header "Referer: https://www.tiktok.com/" \
  --add-header "Accept-Language: en-US,en;q=0.9" \
  "{url}"
```

---

## Proxy

```bash
# SOCKS5
yt-dlp --proxy "socks5://127.0.0.1:1080" URL

# HTTP with authentication
yt-dlp --proxy "http://user:pass@proxy.example.com:8080" URL

# Geo-restriction bypass without proxy
yt-dlp --geo-bypass URL
```

---

## Video Format Selection

```bash
# Best available quality (may include VP9/H.265)
--format "bestvideo+bestaudio/best"

# Force H.264 + AAC (maximum compatibility)
--format "bestvideo[vcodec^=avc]+bestaudio[acodec^=mp4a]/best[ext=mp4]"

# Max 720p (save storage space)
--format "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]"

# Audio only (MP3)
--extract-audio --audio-format mp3 --audio-quality 0
```

---

## Archive — Avoid Duplicates

For repeated runs on the same account:
```bash
yt-dlp \
  --playlist-items 1-20 \
  --download-archive ./tiktok_archive.txt \
  --output "./%(uploader_id)s/%(upload_date)s_%(id)s.%(ext)s" \
  "https://www.tiktok.com/@{username}"
```

The `tiktok_archive.txt` file keeps track of already downloaded video IDs.
On the next run, only new videos will be downloaded.

---

## TikTok URL Structure

```
Profile:       https://www.tiktok.com/@{username}
Video:         https://www.tiktok.com/@{username}/video/{video_id}
Short URL:     https://vm.tiktok.com/{short_id}
Short URL:     https://vt.tiktok.com/{short_id}
```

All these formats are handled automatically by yt-dlp.

---

## ffmpeg — Required for Audio/Video Merge

If missing, install it yourself using the appropriate command for your OS.

> ⚠️ **These commands modify your host environment.** Run them only if you
> understand what they do and are comfortable making this change.

```bash
# Ubuntu/Debian
apt-get install ffmpeg -y

# macOS
brew install ffmpeg

# Verify
ffmpeg -version
```

---

## Verbose Debugging

```bash
yt-dlp --verbose URL 2>&1 | head -50
```
