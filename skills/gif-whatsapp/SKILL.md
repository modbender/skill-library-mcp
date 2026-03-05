---
name: gif-whatsapp
version: 1.1.0
description: Search and send GIFs on WhatsApp. Handles the Tenor→MP4 conversion required for WhatsApp.
author: Leo 🦁
homepage: https://clawhub.com/skills/gif-whatsapp
metadata: {"clawdbot":{"emoji":"🎬","requires":{"bins":["gifgrep","ffmpeg","curl"]},"requiresTools":["message"],"notes":"Uses the platform message tool (already configured) for WhatsApp delivery. gifgrep searches Tenor/Giphy only. Downloads are saved to /tmp and cleaned up after sending."}}
allowed-tools: [exec, message]
---

# GIF Sender

Send GIFs naturally in WhatsApp conversations.

## CRITICAL: WhatsApp GIF Workflow

WhatsApp doesn't support direct Tenor/Giphy URLs. You MUST:
1. Download the GIF
2. Convert to MP4
3. Send with `gifPlayback: true`

## Complete Workflow

### Step 1: Search for GIF
```bash
gifgrep "SEARCH QUERY" --max 5 --format url
```
Search in English for best results.

**Always get 5 results and pick the best one** based on the filename/description - don't just take the first result.

### Step 2: Download the GIF
```bash
curl -sL "GIF_URL" -o /tmp/gif.gif
```

### Step 3: Convert to MP4
```bash
ffmpeg -i /tmp/gif.gif -movflags faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" /tmp/gif.mp4 -y
```

### Step 4: Send via message tool
```
message action=send to=NUMBER message="‎" filePath=/tmp/gif.mp4 gifPlayback=true
```

Note: Use invisible character `‎` (left-to-right mark, U+200E) as message to send GIF without visible caption.

## One-liner Example

```bash
# Search
gifgrep "thumbs up" --max 3 --format url

# Pick best URL, then:
curl -sL "https://media.tenor.com/xxx.gif" -o /tmp/g.gif && \
ffmpeg -i /tmp/g.gif -movflags faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" /tmp/g.mp4 -y 2>/dev/null

# Then send with message tool, gifPlayback=true
```

## When to Send GIFs

✅ Good times:
- User asks for a GIF
- Celebrating good news
- Funny reactions
- Expressing emotions (excitement, facepalm, etc.)

❌ Don't overuse:
- One GIF per context is enough
- Not every message needs a GIF

## Popular Search Terms

| Emotion | Search Terms |
|---------|--------------|
| Happy | celebration, party, dancing, excited |
| Approval | thumbs up, nice, good job, applause |
| Funny | laugh, lol, haha, funny |
| Shocked | mind blown, shocked, surprised, wow |
| Sad | crying, sad, disappointed |
| Frustrated | facepalm, ugh, annoyed |
| Love | heart, love, hug |
| Cool | sunglasses, cool, awesome |

## Security & Safety Notes

- **Source domains**: gifgrep only searches trusted GIF providers (Tenor, Giphy)
- **File handling**: All downloads go to `/tmp` and are overwritten each time (`-y` flag)
- **Empty caption**: The `‎` character (U+200E, Left-to-Right Mark) is used as an invisible caption so WhatsApp sends the GIF without visible text. This is a standard Unicode control character, not an injection technique
- **WhatsApp integration**: Uses the platform's built-in `message` tool — no separate WhatsApp credentials needed
- **ffmpeg safety**: Processes only GIF files from trusted providers; no arbitrary file execution

## Why This Works

- WhatsApp converts all GIFs to MP4 internally
- Direct Tenor/Giphy URLs often fail
- MP4 with `gifPlayback=true` displays as looping GIF
- Small file size = fast delivery
