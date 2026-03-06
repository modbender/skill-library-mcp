---
name: instagram-poster
description: >
  Post images to Instagram automatically via Telegram. Generates images with WaveSpeed or uses
  your own. Bypasses Instagram bot detection using residential proxy. Use when: user wants to
  post to Instagram, auto-post image, share photo on Instagram, instagram autoposter, schedule
  instagram post, publish to instagram, post reel image. Requires IG_USERNAME + IG_PASSWORD env vars
  or a saved session. Needs human-browser skill for residential proxy.
metadata:
  openclaw:
    emoji: 📸
    os: [linux, darwin, win32]
    requires:
      skills: [human-browser]
      env: [IG_USERNAME, IG_PASSWORD]
---

# instagram-poster

Post images to Instagram directly from your AI agent — bypasses bot detection with a real residential IP.

## Quick start

```bash
node {baseDir}/scripts/post.js \
  --image ./photo.jpg \
  --caption "Good morning 🌅 #photography" \
  --user YOUR_USERNAME \
  --pass YOUR_PASSWORD
```

Post a WaveSpeed-generated image:

```bash
# 1. Generate image
node /workspace/.agents/skills/wavespeed/scripts/wavespeed.js generate \
  --model flux-schnell --prompt "sunset over mountains" --output /tmp/post.png

# 2. Post to Instagram
node {baseDir}/scripts/post.js \
  --image /tmp/post.png \
  --caption "Golden hour 🏔️ #nature #photography"
```

## Options

| Flag | Env | Description |
|------|-----|-------------|
| `--image` | `IG_IMAGE` | Local file path or HTTPS URL |
| `--caption` | `IG_CAPTION` | Post caption (optional) |
| `--user` | `IG_USERNAME` | Instagram username |
| `--pass` | `IG_PASSWORD` | Instagram password |
| `--session` | `IG_SESSION_PATH` | Cookie session file (default: `~/.openclaw/ig-session.json`) |

## Session caching

On first run, logs in and saves cookies to `~/.openclaw/ig-session.json`.
Subsequent runs reuse the session — no re-login needed.

## Config in openclaw.json

```json5
{
  skills: {
    entries: {
      "instagram-poster": {
        env: {
          IG_USERNAME: "your_username",
          IG_PASSWORD: "your_password"
        }
      }
    }
  }
}
```

## How it works

1. Launches a stealth browser with a **Romanian residential IP** (via human-browser)
2. Logs into Instagram as a real iPhone user — passes all bot checks
3. Uploads your image and submits the caption
4. Saves session cookies so you stay logged in

## Requirements

- [human-browser](https://clawhub.ai/skills/human-browser) skill installed
- Human Browser subscription (residential proxy) → [humanbrowser.dev](https://humanbrowser.dev)
- Instagram account credentials

## Agent usage example

```
User: Post this sunset photo to Instagram with caption "Golden hour 🌅"
Agent: node {baseDir}/scripts/post.js --image /tmp/sunset.jpg --caption "Golden hour 🌅"
```
