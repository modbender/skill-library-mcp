# Security

This skill is a small Node.js CLI + SDK for Voice.ai text-to-speech.

## Credentials

- The only credential used is `VOICE_AI_API_KEY`.
- The CLI reads it from the `VOICE_AI_API_KEY` environment variable.

## Network Access

- Outbound HTTPS requests are made only to `https://dev.voice.ai` (Voice.ai's production API domain).
- The SDK rejects non-HTTPS base URLs.

## Local File Access

The skill reads/writes local files only for its documented behavior:

- Reads `voices.json` to map friendly voice names to voice IDs.
- Writes the generated audio to `--output` (default `output.mp3`).

## What This Skill Does Not Do

- Does not execute shell commands (`child_process` is not used).
- Does not download or install other software.
- Does not modify system configuration files.
- Does not run persistently in the background.

## Reporting

If you find a security issue, please open an issue in the GitHub repository with a minimal reproduction and impact summary.
