---
name: vibeclip
description: Generate AI music videos from melody audio + photo + prompt. Local Ollama (llama3.2:1b/phi3:mini) for scene desc, FFmpeg for morph/zoompan + waveform sync. Node/Express webapp, VPS deploy ready (port 3000). Demo: cd video-app && node index.js. Revenue SaaS: credits/ETH payments.
metadata:
  openclaw:
    requires:
      bins: [node, ollama, ffmpeg]
    install:
      - id: ollama-models
        kind: exec
        command: ollama pull llama3.2:1b phi3:mini

# VibeClip Skill

## Usage
POST /generate {audio, photo, prompt} → video.mp4

## Revenue Ready
- 0$ API costs.
- Add ETH payments to wallet.