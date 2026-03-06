---
name: OpenClaw Voice Skill
description: "Voice conversation with AI via Whisper STT + ElevenLabs TTS.
  Records audio, transcribes, generates spoken responses, stores transcripts.
  For v1: CLI-based commands only (no real-time conversation m..."
---

# OpenClaw Voice Skill

## Overview
Voice conversation with AI via Whisper STT + ElevenLabs TTS. Records audio, transcribes, generates spoken responses, stores transcripts. For v1: CLI-based commands only (no real-time conversation mode — that's v1.1). Focus on transcript storage/search + TTS/STT wrappers.

## Tech Stack
- Node.js ESM
- better-sqlite3 (WAL mode always)
- commander for CLI
- uuid for IDs
- @openclaw/interchange (import from ../interchange/src/index.js)
- NO external audio packages — use child_process to call sox/rec and ffplay

## Database
See migrations/001_initial.sql for schema.

## CLI
See src/cli.js for commands.

## Tests
Run with npm test.