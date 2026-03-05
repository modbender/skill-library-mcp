# Media Handling — Telegram Bot API

## File Size Limits

| Type | Max Size | Notes |
|------|----------|-------|
| Photo upload | 10 MB | Compressed to JPEG |
| Photo URL | 5 MB | Must be direct link |
| Document upload | 50 MB | Any file type |
| Document URL | 20 MB | Telegram downloads it |
| Video upload | 50 MB | Max 10 min recommended |
| Audio upload | 50 MB | MP3/M4A supported |
| Voice upload | — | OGG with OPUS only |
| Video note | 50 MB | Circular video, ≤1 min |
| Sticker | 512 KB | WebP format |
| Animation | 50 MB | GIF or MPEG4 |

---

## Sending Methods

### By Upload (multipart/form-data)

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendPhoto" \
  -F "chat_id=123456789" \
  -F "photo=@/path/to/image.jpg" \
  -F "caption=Photo caption"
```

### By URL

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendPhoto" \
  -d "chat_id=123456789" \
  -d "photo=https://example.com/image.jpg" \
  -d "caption=Photo caption"
```

**URL requirements:**
- Must be direct link (no redirects)
- HTTPS recommended
- Telegram caches the file

### By file_id (Reuse)

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendPhoto" \
  -d "chat_id=123456789" \
  -d "photo=AgACAgIAAxkBAAI..."
```

**Advantages of file_id:**
- Instant delivery (already on Telegram servers)
- No upload needed
- Works across chats

**file_id is unique per bot** — Can't use another bot's file_id.

---

## Getting file_id

When you receive or send media, Telegram returns file info:

```json
{
  "message_id": 100,
  "photo": [
    {"file_id": "AgAC..._small", "width": 90, "height": 90},
    {"file_id": "AgAC..._medium", "width": 320, "height": 320},
    {"file_id": "AgAC..._large", "width": 800, "height": 800}
  ]
}
```

**For photos:** Array of sizes, use largest (`[-1]`) for best quality.

---

## Downloading Files

### Step 1: Get File Path

```bash
curl "https://api.telegram.org/bot${TOKEN}/getFile?file_id=AgACAgIAAxkBAAI..."
```

Response:
```json
{
  "ok": true,
  "result": {
    "file_id": "AgACAgIAAxkBAAI...",
    "file_unique_id": "AQADAgATqH...",
    "file_size": 12345,
    "file_path": "photos/file_0.jpg"
  }
}
```

### Step 2: Download File

```bash
curl -O "https://api.telegram.org/file/bot${TOKEN}/photos/file_0.jpg"
```

**Note:** Files are available for 1 hour after getFile.

---

## Media Types

### Photos

```bash
# Send photo with caption
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendPhoto" \
  -F "chat_id=123456789" \
  -F "photo=@photo.jpg" \
  -F "caption=<b>Bold caption</b>" \
  -F "parse_mode=HTML" \
  -F "has_spoiler=true"
```

| Parameter | Description |
|-----------|-------------|
| photo | File, URL, or file_id |
| caption | 0-1024 characters |
| parse_mode | HTML or MarkdownV2 |
| has_spoiler | Blur until tapped |

### Documents

```bash
# Send any file type
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendDocument" \
  -F "chat_id=123456789" \
  -F "document=@file.pdf" \
  -F "caption=PDF document" \
  -F "thumbnail=@thumb.jpg"
```

| Parameter | Description |
|-----------|-------------|
| document | File, URL, or file_id |
| thumbnail | Custom thumbnail (JPEG, ≤200KB) |
| disable_content_type_detection | Send as generic file |

### Videos

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendVideo" \
  -F "chat_id=123456789" \
  -F "video=@video.mp4" \
  -F "duration=60" \
  -F "width=1280" \
  -F "height=720" \
  -F "supports_streaming=true"
```

| Parameter | Description |
|-----------|-------------|
| duration | Duration in seconds |
| width, height | Dimensions |
| thumbnail | Custom thumbnail |
| supports_streaming | Enable streaming |

### Audio

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendAudio" \
  -F "chat_id=123456789" \
  -F "audio=@song.mp3" \
  -F "title=Song Title" \
  -F "performer=Artist Name" \
  -F "duration=180"
```

Displayed with album art and audio player controls.

### Voice Messages

```bash
# Must be OGG with OPUS codec
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendVoice" \
  -F "chat_id=123456789" \
  -F "voice=@voice.ogg" \
  -F "duration=10"
```

**Convert to OGG/OPUS:**
```bash
ffmpeg -i input.mp3 -c:a libopus output.ogg
```

### Video Notes (Circles)

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendVideoNote" \
  -F "chat_id=123456789" \
  -F "video_note=@circle.mp4" \
  -F "length=240"
```

Circular video, max 1 minute. `length` is the diameter.

### Animations (GIFs)

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendAnimation" \
  -F "chat_id=123456789" \
  -F "animation=@animation.gif" \
  -F "caption=Funny GIF"
```

---

## Media Groups (Albums)

Send 2-10 photos/videos as album:

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendMediaGroup" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "media": [
      {
        "type": "photo",
        "media": "https://example.com/photo1.jpg",
        "caption": "First photo"
      },
      {
        "type": "photo",
        "media": "https://example.com/photo2.jpg"
      },
      {
        "type": "video",
        "media": "https://example.com/video.mp4",
        "caption": "A video"
      }
    ]
  }'
```

**Rules:**
- 2-10 items
- Only first item's caption shown (can be on any item)
- Can mix photos and videos
- Can't mix documents with photos/videos

### Upload Files in Media Group

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendMediaGroup" \
  -F 'media=[{"type":"photo","media":"attach://photo1"},{"type":"photo","media":"attach://photo2"}]' \
  -F "photo1=@/path/to/photo1.jpg" \
  -F "photo2=@/path/to/photo2.jpg" \
  -F "chat_id=123456789"
```

---

## Tips

1. **Use file_id when possible** — Faster, no re-upload
2. **Store file_ids** — Save them for reuse
3. **Compress before upload** — Reduce transfer time
4. **Use thumbnails** — Better UX for documents/videos
5. **Check file size first** — Avoid upload failures
6. **Handle download timeouts** — Files expire after 1 hour
