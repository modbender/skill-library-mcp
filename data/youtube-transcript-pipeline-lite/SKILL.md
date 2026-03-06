---
name: youtube-transcript-pipeline-lite
description: "Run a lightweight YouTube transcript workflow: transcribe, attribution cleanup, translation, and packaging with minimal tooling. Use for repeatable transcript handoff tasks when you need a concise, auditable process over custom automation."
---

# YouTube Transcript Pipeline (Lite)

## Quick Start

Use this when a user asks for:
- YouTube transcript generation and cleanup
- speaker correction around interview/interjector vs main speaker
- translated transcript output while preserving timestamps/speakers
- ready-to-share folder packaging

## Minimal Workflow

1. **Transcribe**
   - Run your existing transcript flow for the target video (word-level preferred for reliable speaker calibration).
   - Keep all raw outputs.

2. **Speaker cleanup (small-impact)**
   - Preserve the default/primary speaker mapping.
   - Only flip clearly short-interjection/question lines when they are obviously misattributed.
   - Keep line count and timestamps unchanged.

3. **Translate (optional)**
   - Translate content line-by-line.
   - Keep format exactly: `[HH:MM:SS] Speaker: text`.
   - Keep technical terms unless explicitly asked to simplify.

4. **Package for handoff**
   - Create concise structure: `transcripts/`, `artifacts/`, `MANIFEST.txt`.
   - Include one reviewed transcript + one translated version when asked.

## What not to do in this skill

- Do not introduce heavy automation assumptions.
- Do not change line/timestamp structure unless user explicitly asks.
- Do not aggressively relabel all speaker turns; prefer conservative flips.

## Quality checks

- Validate final line counts against source.
- Confirm active final files are present and clearly named.
- Keep every major handoff stage discoverable in manifest.

## Reference

See `references/limits.md` for quick trade-offs and rollback guidance.