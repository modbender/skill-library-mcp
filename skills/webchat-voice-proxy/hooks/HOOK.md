---
name: voice-input-inject
description: "Injects voice-input.js into Control UI on gateway startup (survives updates)"
metadata:
  openclaw:
    emoji: "🎤"
    events: ["gateway:startup"]
    requires:
      bins: ["bash"]
---

# Voice Input Inject Hook

Re-injects the voice-input microphone button into the OpenClaw Control UI
every time the gateway starts. This ensures the modification survives
`openclaw update` or `npm update`.

## Install

The `deploy.sh` script copies this hook into `~/.openclaw/hooks/voice-input-inject/` automatically.
