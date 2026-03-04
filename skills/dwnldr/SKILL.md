---
name: dwnldr
description: "Yarr! Plunder videos from the seven seas of the internet — YouTube, TikTok, Instagram, X, Reddit & 1000+ ports o' call. Drop a link, get full quality loot with metadata scrubbed clean. No traces, no evidence, just pure content booty delivered straight to yer Telegram. Supports MP4, MP3, playlists, and more."
metadata:
  openclaw:
    emoji: "🏴‍☠️"
    trigger: "/dl"
    requires:
      bins:
        - yt-dlp
        - ffmpeg
---

# Video Downloader

Download videos from **YouTube, TikTok, Instagram, Twitter/X**, and 1000+ sites. Just paste a link — the video gets downloaded at full quality and sent back to you.

## URL Detection (AUTO-TRIGGER)

**CRITICAL:** When the user sends a message that contains a URL from any of these domains, AUTOMATICALLY treat it as a download request. Do NOT ask "what do you want me to do with this?" — just download it.

**Auto-detect domains:**
- `youtube.com`, `youtu.be`, `m.youtube.com`
- `tiktok.com`, `vm.tiktok.com`
- `instagram.com` (reels, posts, stories)
- `x.com`, `twitter.com`
- `reddit.com` (video posts)
- `twitch.tv` (clips)
- `vimeo.com`
- `facebook.com` (videos, reels)

**Pattern:** If user message contains a URL matching these domains → skip questions, download immediately.

## Download Flow

### Step 1 — Download

```bash
yt-dlp --js-runtimes nodejs \
  -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  --merge-output-format mp4 \
  --no-playlist \
  --output "/home/rami/.openclaw/workspace/_incoming/%(title).50s.%(ext)s" \
  "<URL>"
```

**Fallback for stubborn sites (TikTok, Instagram):**
```bash
yt-dlp --js-runtimes nodejs \
  -f "best" \
  --no-playlist \
  --output "/home/rami/.openclaw/workspace/_incoming/%(title).50s.%(ext)s" \
  "<URL>"
```

### Step 2 — Strip metadata

Remove ALL metadata (title, author, GPS, comments, timestamps, source URL) for clean clips:

```bash
ffmpeg -i "/home/rami/.openclaw/workspace/_incoming/<filename>" \
  -map_metadata -1 \
  -fflags +bitexact \
  -flags:v +bitexact \
  -flags:a +bitexact \
  -c copy \
  "/home/rami/.openclaw/workspace/_incoming/<filename>_clean.mp4" \
  && mv "/home/rami/.openclaw/workspace/_incoming/<filename>_clean.mp4" \
        "/home/rami/.openclaw/workspace/_incoming/<filename>"
```

This strips: title, artist, comment, description, source URL, creation date, encoder info, GPS coordinates — everything.

### Step 3 — Get file info

```bash
ls -lh /home/rami/.openclaw/workspace/_incoming/<filename>
```

### Step 3 — Send to user

**If file is under 50MB** — send directly via Telegram:
```bash
openclaw message send \
  --channel telegram \
  --target <user_id> \
  --message "🎬 Downloaded: <title>" \
  --media /home/rami/.openclaw/workspace/_incoming/<filename>
```

**If file is over 50MB** — use LocalSend:
1. Notify user: "Video is <size> — too big for Telegram. Sending via LocalSend."
2. Start LocalSend send flow:
   ```bash
   localsend-cli send --to "<user_device>" /home/rami/.openclaw/workspace/_incoming/<filename>
   ```

**Buttons after send:**
```json
buttons: [
  [
    { "text": "🎬 Download Another", "callback_data": "dl:another" },
    { "text": "📱 Send via LocalSend", "callback_data": "dl:localsend" }
  ],
  [
    { "text": "🗑️ Delete File", "callback_data": "dl:delete" }
  ]
]
```

### Step 4 — Cleanup

After confirmed delivery, offer to delete the file to save disk space.

## Quality Options

Default is **best quality MP4**. If user asks for specific quality:

| Request | Flag |
|---------|------|
| "1080p" | `-f "bestvideo[height<=1080]+bestaudio/best[height<=1080]"` |
| "720p" | `-f "bestvideo[height<=720]+bestaudio/best[height<=720]"` |
| "audio only" / "mp3" | `-x --audio-format mp3` |
| "thumbnail" | `--write-thumbnail --skip-download` |

## Audio-Only Downloads

If user says "mp3", "audio only", "just the audio":

```bash
yt-dlp --js-runtimes nodejs \
  -x --audio-format mp3 \
  --output "/home/rami/.openclaw/workspace/_incoming/%(title).50s.%(ext)s" \
  "<URL>"
```

## Batch Downloads (Playlists)

If user sends a playlist URL and says "download all":

```bash
yt-dlp --js-runtimes nodejs \
  -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  --merge-output-format mp4 \
  --output "/home/rami/.openclaw/workspace/_incoming/%(title).50s.%(ext)s" \
  "<URL>"
```

Remove `--no-playlist` flag for playlists.

## Error Handling

| Error | Fix |
|-------|-----|
| "Video unavailable" | Private/deleted video — notify user |
| "Sign in to confirm" | Age-restricted — try with `--cookies-from-browser chrome` |
| Geographic restriction | Try with `--geo-bypass` |
| Rate limited | Wait 30s and retry once |
| Merge failed | Fallback to `-f best` (single stream) |

## Callback Reference

| callback_data | Action |
|---------------|--------|
| `dl:another` | Prompt for another URL |
| `dl:localsend` | Send last downloaded file via LocalSend |
| `dl:delete` | Delete the downloaded file |
| `dl:audio` | Re-download as MP3 |

## CLI Reference

| Command | Usage |
|---------|-------|
| Best quality | `yt-dlp -f "bestvideo+bestaudio/best" --merge-output-format mp4 URL` |
| Audio only | `yt-dlp -x --audio-format mp3 URL` |
| List formats | `yt-dlp -F URL` |
| Thumbnail | `yt-dlp --write-thumbnail --skip-download URL` |
