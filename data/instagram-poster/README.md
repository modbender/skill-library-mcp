# 📸 instagram-poster — OpenClaw Skill

> Post to Instagram from your AI agent. One command. Real residential IP. No blocks.

[![ClawHub](https://img.shields.io/badge/ClawHub-instagram--poster-orange)](https://clawhub.ai/skills/instagram-poster)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## What it does

Tell your AI agent (in Telegram, Signal, wherever) to post an image to Instagram.
It generates or downloads the image, logs in with a stealth browser, and posts — all automatically.

```
You:   "Generate a sunset over mountains and post it to Instagram"

Agent: → WaveSpeed generates image
       → Human Browser logs into Instagram (Romanian IP, iPhone fingerprint)
       → Posts with your caption
       → Done ✅
```

---

## Install

```bash
clawhub install instagram-poster
```

Or clone:

```bash
git clone https://github.com/YOUR_USERNAME/instagram-poster
```

---

## Usage

**Post a local image:**
```bash
node scripts/post.js \
  --image ./photo.jpg \
  --caption "Good morning ☀️ #photography" \
  --user your_instagram \
  --pass your_password
```

**Post from URL:**
```bash
node scripts/post.js \
  --image https://example.com/image.jpg \
  --caption "Look at this 👀"
```

**Generate + post (WaveSpeed → Instagram):**
```bash
# Generate
node .agents/skills/wavespeed/scripts/wavespeed.js generate \
  --model flux-schnell \
  --prompt "cinematic sunset over mountains, golden hour" \
  --output /tmp/post.png

# Post
node scripts/post.js \
  --image /tmp/post.png \
  --caption "Golden hour 🏔️ #nature #ai"
```

---

## How it works

Instagram blocks 99% of automation tools because they run on **datacenter IPs**.
This skill uses [Human Browser](https://humanbrowser.dev) to browse from a **real Romanian residential IP** with an **iPhone 15 Pro fingerprint** — indistinguishable from a real user.

```
Your VPS IP  →  Cloudflare/Meta ban  ❌
Romanian residential IP  →  Passes all checks  ✅
```

**Flow:**
1. Downloads/resolves image (URL or local file)
2. Launches stealth browser (residential proxy + iPhone fingerprint)
3. Logs in to Instagram (or restores saved session)
4. Clicks "New Post" → uploads image → adds caption → shares
5. Saves session cookies (no re-login next time)

---

## Configuration

Set credentials via env vars or config:

**Environment variables:**
```bash
export IG_USERNAME="your_username"
export IG_PASSWORD="your_password"
```

**OpenClaw config (`~/.openclaw/openclaw.json`):**
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

**Session caching:**
First run logs in and saves cookies to `~/.openclaw/ig-session.json`.
Next runs reuse the session automatically.

---

## Requirements

| Requirement | Details |
|-------------|---------|
| [human-browser](https://clawhub.ai/skills/human-browser) | Stealth browser skill (free) |
| Residential proxy | Required for bypassing Instagram's IP checks → [humanbrowser.dev](https://humanbrowser.dev) from $13.99/mo |
| Instagram account | Your own account credentials |

> **Why do you need a residential proxy?**  
> Instagram (Meta) instantly blocks datacenter IPs (AWS, Hetzner, DigitalOcean, etc.).  
> A residential IP from a real home ISP passes all their checks. No proxy = instant block.

---

## Agent prompt examples

```
Post my photo.jpg to Instagram with caption "Weekend vibes 🌊"
Generate a photo of a Tokyo street at night and post it to Instagram
Post to Instagram: [image] with caption "Morning run done ✅"
```

---

## License

MIT — free to use, modify, distribute.

Part of the [OpenClaw](https://github.com/openclaw/openclaw) ecosystem.
