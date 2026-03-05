# Platform Specifications

## YouTube

| Type | Aspect | Resolution | Max Duration | Max Size |
|------|--------|------------|--------------|----------|
| Standard | 16:9 | 1920x1080 (or 4K) | 12 hours | 256GB |
| Shorts | 9:16 | 1080x1920 | 60 seconds | 256GB |

**Recommended:** H.264, AAC, 30/60fps, `-movflags +faststart`

---

## TikTok

| Aspect | Resolution | Duration | Max Size |
|--------|------------|----------|----------|
| 9:16 | 1080x1920 | 3 min (web), 10 min (some) | 287MB (iOS), 500MB (web) |

**Recommended:** H.264, AAC, 30fps, bitrate 2-5 Mbps

---

## Instagram

| Type | Aspect | Resolution | Duration | Max Size |
|------|--------|------------|----------|----------|
| Reels | 9:16 | 1080x1920 | 90 seconds | 250MB |
| Feed | 1:1 or 4:5 | 1080x1080/1350 | 60 seconds | 250MB |
| Stories | 9:16 | 1080x1920 | 15 sec each | 250MB |

**Recommended:** H.264, AAC, 30fps

---

## LinkedIn

| Type | Aspect | Resolution | Duration | Max Size |
|------|--------|------------|----------|----------|
| Feed | 16:9, 1:1, 4:5 | 1080p | 10 minutes | 5GB |

**Recommended:** H.264, AAC, keep under 200MB for reliability

---

## Twitter/X

| Aspect | Resolution | Duration | Max Size |
|--------|------------|----------|----------|
| 16:9, 1:1 | 1280x720 min | 2:20 | 512MB |

**Recommended:** H.264, AAC, 40fps max

---

## WhatsApp

| Max Size | Notes |
|----------|-------|
| 64MB | Compress aggressively, H.264 baseline profile |

**Compression target:** CRF 28-32, 720p, AAC 128kbps

---

## Facebook

| Type | Aspect | Resolution | Duration | Max Size |
|------|--------|------------|----------|----------|
| Feed | 16:9, 1:1, 4:5, 9:16 | 1080p | 240 min | 10GB |
| Reels | 9:16 | 1080x1920 | 90 seconds | 4GB |

---

## Discord

| Max Size | Notes |
|----------|-------|
| 25MB free, 100MB Nitro | Compress heavily for free tier |

---

## Quick Platform Flags

```bash
# YouTube optimized
-c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k -movflags +faststart

# TikTok/Reels (9:16, compressed)
-vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -crf 23 -c:a aac -b:a 128k

# WhatsApp (max compression)
-vf "scale=720:-2" -c:v libx264 -crf 28 -preset fast -c:a aac -b:a 96k
```
