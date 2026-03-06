# Media — WhatsApp Business API

## Supported Media Types

| Type | Formats | Max Size |
|------|---------|----------|
| Image | JPEG, PNG | 5 MB |
| Video | MP4, 3GPP | 16 MB |
| Audio | AAC, MP3, OGG, AMR | 16 MB |
| Document | PDF, DOC, XLS, PPT, TXT | 100 MB |
| Sticker | WEBP | 500 KB (static), 1 MB (animated) |

---

## Upload Media

```bash
curl -X POST "https://graph.facebook.com/v21.0/$WHATSAPP_PHONE_NUMBER_ID/media" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN" \
  -F "file=@/path/to/image.jpg" \
  -F "type=image/jpeg" \
  -F "messaging_product=whatsapp"
```

Response:

```json
{
  "id": "1234567890"
}
```

Use this `id` in message requests.

---

## Get Media URL

Media IDs from webhooks need to be converted to URLs:

```bash
curl "https://graph.facebook.com/v21.0/{media_id}" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN"
```

Response:

```json
{
  "messaging_product": "whatsapp",
  "url": "https://lookaside.fbsbx.com/whatsapp_business/...",
  "mime_type": "image/jpeg",
  "sha256": "abc123...",
  "file_size": 1234567,
  "id": "1234567890"
}
```

---

## Download Media

The URL from `Get Media URL` requires authentication:

```bash
curl -L "https://lookaside.fbsbx.com/whatsapp_business/..." \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN" \
  -o downloaded_file.jpg
```

**Note:** URLs expire after a few days. Download promptly.

---

## Delete Media

```bash
curl -X DELETE "https://graph.facebook.com/v21.0/{media_id}" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN"
```

---

## Using Media in Messages

### With Media ID (uploaded)

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "image",
  "image": {
    "id": "1234567890",
    "caption": "Your receipt"
  }
}
```

### With URL (external)

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "image",
  "image": {
    "link": "https://example.com/image.jpg",
    "caption": "Your receipt"
  }
}
```

---

## Media Requirements

### Images
- Recommended: 1024x1024 or smaller
- Aspect ratio: Any, but square displays best
- Formats: JPEG, PNG

### Videos
- Codec: H.264
- Audio: AAC
- Max duration: Unlimited (but keep <1 min for engagement)
- Recommended resolution: 720p

### Audio
- Voice notes: OGG with Opus codec
- Music/podcasts: MP3, AAC
- Max duration: Unlimited

### Documents
- All common office formats supported
- PDF renders preview in chat
- Other formats show icon + filename

### Stickers
- Static: 512x512 WEBP
- Animated: 512x512 WEBP, <500 KB
- Must have transparent background

---

## Common Traps

- **URL not accessible** — Media URLs must be publicly accessible (no auth required)
- **Wrong MIME type** — Match file extension to type parameter
- **File too large** — Compress before upload
- **Expired URL** — Download media from webhooks immediately
- **Missing caption** — Always include caption for context
