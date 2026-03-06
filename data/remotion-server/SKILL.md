---
name: remotion-server
description: Headless video rendering with Remotion. Works on any Linux server - no Mac or GUI needed. Templates for chat demos, promos, and more.
homepage: https://remotion.dev
user-invocable: true
disable-model-invocation: true
metadata:
  clawdbot:
    emoji: "🎬"
    requires:
      bins: [node, npx]
    os: [linux]
---

# Remotion Server

Render videos headlessly on any Linux server using Remotion. No Mac or GUI required.

## Setup (one-time)

Install browser dependencies:
```bash
bash {baseDir}/scripts/setup.sh
```

## Quick Start

### Create a project:
```bash
bash {baseDir}/scripts/create.sh my-video
cd my-video
```

### Render a video:
```bash
npx remotion render MyComp out/video.mp4
```

## Templates

### Chat Demo (Telegram-style)
Creates a phone mockup with animated chat messages.

```bash
bash {baseDir}/scripts/create.sh my-promo --template chat
```

Edit `src/messages.json`:
```json
[
  {"text": "What's the weather?", "isUser": true},
  {"text": "☀️ 72°F and sunny!", "isUser": false}
]
```

### Title Card
Simple animated title/intro card.

```bash
bash {baseDir}/scripts/create.sh my-intro --template title
```

## Example Chat Usage

- "Make a video showing a chat about [topic]"
- "Create a promo video for [feature]"
- "Render a title card saying [text]"

## Linux Dependencies

The setup script installs:
- libnss3, libatk, libcups2, libgbm, etc.
- Required for Chrome Headless Shell

For Ubuntu/Debian:
```bash
sudo apt install -y libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libgbm1 libpango-1.0-0 libcairo2 libxcomposite1 libxdamage1 libxfixes3 libxrandr2
```

**Note:** Remotion 4.0.418+ uses custom Chrome binaries with proprietary codecs for both Linux x64 and ARM64, improving compatibility.

## Output Formats

- MP4 (h264) - default
- WebM (vp8/vp9)
- GIF
- PNG sequence

```bash
npx remotion render MyComp out/video.webm --codec=vp8
npx remotion render MyComp out/video.gif --codec=gif
```

## Privacy Note

All templates use FAKE demo data only:
- Fake GPS coords (San Francisco: 37.7749, -122.4194)
- Placeholder names and values
- Never includes real user data

Always review generated content before publishing.

## Security & Permissions

**What this skill does:**
- Installs Chromium dependencies for headless rendering (via `scripts/setup.sh`)
- Creates Remotion project scaffolding locally (via `scripts/create.sh`)
- Renders video files to local disk using `npx remotion render`

**What this skill does NOT do:**
- Does not require any API keys or credentials
- Does not upload videos or data to external services
- Does not access network resources beyond npm package downloads during setup
- Does not access personal data — all templates use placeholder content
- Cannot be invoked autonomously by the agent (`disable-model-invocation: true`)

**Bundled scripts:** `scripts/setup.sh` (install dependencies), `scripts/create.sh` (scaffold projects)

Review scripts before first use. The setup script runs `apt install` for browser dependencies on Linux.
