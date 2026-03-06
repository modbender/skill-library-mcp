---
name: ressemble
displayName: Ressemble - Adriano
version: 1.0.0
description: Text-to-Speech and Speech-to-Text integration using Resemble AI HTTP API.
author: Adriano Vargas
tags: [tts, stt, audio, ai, voice]
---

# Ressemble – Text & Voice AI Integration

This skill integrates OpenClaw with the Resemble AI HTTP API, enabling:

- 🎙 Speech-to-Text (audio transcription)
- 🔊 Text-to-Speech (voice synthesis)

It uses direct HTTP calls to Resemble's production endpoints and supports asynchronous transcription polling.

---

## Features

### resemble-tts
Generate high-quality speech audio from text input.

Supports:
- Custom `voice_uuid`
- MP3 output format
- Base64 audio return

### resemble-stt
Transcribe audio files to text using Resemble AI.

Supports:
- Multipart audio upload
- Automatic polling until transcription is complete
- Returns clean transcript text

---

## Requirements

You must define the environment variable:

```bash
export RESEMBLE_API_KEY="your_api_key_here"
