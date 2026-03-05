---
name: resemble-stt
description: Transcribe audio into text using Resemble AI speech-to-text.
metadata:
  clawdbot:
    emoji: "🎤"
    requires:
      bins: ["curl", "jq", "base64"]
      env: ["RESEMBLE_API_KEY"]
    primaryEnv: "RESEMBLE_API_KEY"
---

# Resemble STT

Convert speech audio into text.
