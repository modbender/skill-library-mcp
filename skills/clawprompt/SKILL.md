---
name: clawprompt
description: >-
  Launch a smart teleprompter with mobile remote control for video recording.
  Use when the user wants to read scripts while recording video, use a teleprompter,
  or needs a prompter with phone remote control.
  Triggers on phrases like "open teleprompter", "start prompter", "提词器", "打开提词器",
  "录视频提词", "teleprompter", "提词", "I need a prompter", "read script while recording",
  "手机遥控提词", "ClawPrompt", "念稿子", "录视频看词", "对镜头念词".
  Features: dual-screen sync (computer + phone show same text), QR code phone pairing,
  mobile remote control (another person controls page turns), text upload from either device,
  fullscreen black-background white-text display, auto sentence segmentation,
  adjustable font size, countdown before start.
  Works with ClawCut — import AI-generated 9-scene scripts directly.
  提词器, 智能提词器, teleprompter, 手机遥控, 视频录制辅助工具, prompter, autocue,
  录制提词, 双屏同步, 远程翻页.
tags:
  - teleprompter
  - video
  - recording
  - remote-control
  - productivity
---

# ClawPrompt 🦞📝 — Smart Teleprompter with Mobile Remote

## What It Does
A browser-based teleprompter that runs on your Mac. A second person can use their phone as a remote control to turn pages while the speaker focuses on the camera.

## Quick Start

```bash
cd {SKILL_DIR}/scripts
npm install --silent
node server.js
```

Then open `http://localhost:7870` on the computer.

## How It Works
1. **Computer**: Open the teleprompter page → paste or type your script → click "开始提词"
2. **Phone**: Scan the QR code shown on the computer → phone becomes a remote controller
3. **Recording**: Speaker looks at camera, peripheral vision reads text at top of screen. Another person holds the phone and taps "下一句" to advance.

## Controls
- **Computer keyboard**: Space/↓ = next, ↑ = prev, +/- = font size, ESC = exit
- **Phone**: Tap "下一句" / "上一句" buttons
- **Text upload**: From either computer or phone

## Integration with ClawCut
If using ClawCut to generate video scripts, the 9-scene script can be pasted directly into ClawPrompt.

## Requirements
- Node.js (for WebSocket server)
- Computer and phone on the same WiFi network
- Port 7870 (configurable via PORT env var)
