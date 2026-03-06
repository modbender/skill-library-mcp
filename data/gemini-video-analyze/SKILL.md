---
name: google-video-url-analysis
description: Send a public video URL directly to a Google Gemini model for analysis. Use when Codex must summarize a video, answer questions about video content, or extract key points from a URL without local download or file upload steps.
---

# Google Video Url Analysis

Use `scripts/gemini_video_url_analyzer.py` for deterministic Gemini calls instead of ad-hoc API snippets.

## Workflow

1. Set an API key:
   - `GEMINI_API_KEY` (preferred), or
   - `GOOGLE_API_KEY`
2. Run the analyzer with a public video URL supported by Gemini as direct URI input.
3. Provide a task-specific prompt (summary, timeline extraction, Q&A, moderation, etc.).
4. Inspect the text output.

## Command Guide

- Basic analysis:
  - `python scripts/gemini_video_url_analyzer.py --video-url "https://www.youtube.com/watch?v=..." --prompt "Summarize in 5 bullets and list important timestamps."`
- Override model:
  - `python scripts/gemini_video_url_analyzer.py --video-url "<url>" --model "gemini-2.5-pro" --prompt "Produce a scene-by-scene report."`

## Operational Rules

- Require a publicly accessible URL.
- Prefer concise, explicit prompts with concrete output constraints.
