---
name: resemble-tts
description: Generate speech audio from text using Resemble AI.
metadata:
  clawdbot:
    emoji: "🔊"
    requires:
      bins: ["curl", "jq", "base64"]
      env: ["RESEMBLE_API_KEY"]
    primaryEnv: "RESEMBLE_API_KEY"
---

# Resemble TTS

Convert text into speech audio using Resemble AI.
