---
name: podcast-chaptering-highlights
description: Create chapters, highlights, and show notes from podcast audio or transcripts. Use when a user wants chapter markers, highlight clips, or show-note drafts without publishing or distribution actions.
---

# Podcast Chaptering and Highlights

## Goal
Produce podcast chapter markers and highlight suggestions with concise show notes.

## Best fit
- Use when the user provides audio files or transcripts.
- Use when the user wants chapter timestamps and titles.
- Use when the user needs highlight clip ideas and show notes.

## Not fit
- Avoid when the user asks to publish or upload to hosting platforms.
- Avoid when rights or consent are unclear.
- Avoid when audio quality is too poor to segment.

## Quick orientation
- `references/overview.md` for workflow and quality bar.
- `references/auth.md` for access and token handling.
- `references/endpoints.md` for optional integrations and templates.
- `references/webhooks.md` for async event handling.
- `references/ux.md` for intake questions and output formats.
- `references/troubleshooting.md` for common issues.
- `references/safety.md` for safety and privacy guardrails.

## Required inputs
- Audio file path or transcript.
- Target chapter format (MM:SS or HH:MM:SS).
- Preferred chapter length range.
- Show description and guest details if available.

## Expected output
- Chapter markers with timestamps and titles.
- Highlight clip suggestions with timestamps.
- Show notes draft with key links or topics.
- Optional social post drafts.

## Operational notes
- Keep chapters aligned to topic shifts.
- Ensure titles are concise and descriptive.
- Provide drafts only; do not publish or upload.

## Security notes
- Treat audio content as private unless told otherwise.
- Avoid sharing raw audio beyond the workspace.

## Safe mode
- Analyze and draft chapters, highlights, and notes only.
- No publishing or distribution actions.

## Sensitive ops
- Uploading or publishing audio is out of scope.
