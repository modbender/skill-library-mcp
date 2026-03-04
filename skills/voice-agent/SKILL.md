---
name: voice-agent
display-name: AI Voice Agent Backend
version: 1.1.0
description: Local Voice Input/Output for Agents using the AI Voice Agent API.
author: trevisanricardo
homepage: https://github.com/ricardotrevisan/ai-conversational-skill
user-invocable: true
disable-model-invocation: false
---

# Voice Agent

This skill allows you to speak and listen to the user using a local Voice Agent API.
It is client-only and does not start containers or services.
It uses **local Whisper** for Speech-to-Text transcription and **AWS Polly** for Text-to-Speech generation.

## Prerequisite
Requires a running backend API at `http://localhost:8000`.
Backend setup instructions are in this repository:
- `README.md`
- `walkthrough.md`
- `DOCKER_README.md`

## Behavior Guidelines
-   **Audio First**: When the user communicates via audio (files), your PRIMARY mode of response is **Audio File**.
-   **Silent Delivery**: When sending an audio response, **DO NOT** send a text explanation like "I sent an audio". Just send the audio file.
-   **Workflow**:
    1.  User sends audio.
    2.  Use `transcribe` to read it.
    3.  You think of a response.
    4.  Use `synthesize` to generate the audio file.
    5.  You send the file.
    6.  **STOP**. Do not add text commentary.
-   **Failure Handling**: If `health` fails or connection errors occur, do not attempt service management from this skill. Ask the user to start or fix the backend using the repository docs.

## Tools

### Transcribe File
To transcribe an audio file with **local Whisper STT**, run the client script with the `transcribe` command.

```bash
python3 {baseDir}/scripts/client.py transcribe "/path/to/audio/file.ogg"
```

### Synthesize to File
To generate audio from text with **AWS Polly TTS** and save it to a file, run the client script with the `synthesize` command.

```bash
python3 {baseDir}/scripts/client.py synthesize "Text to speak" --output "/path/to/output.mp3"
```

### Health Check
To check if the voice agent API is running and healthy:

```bash
python3 {baseDir}/scripts/client.py health
```
