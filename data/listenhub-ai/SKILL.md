---
name: listenhub
description: |
  Turn ideas into podcasts, explainer videos, voice narration, and AI images via ListenHub.
  Use when the user wants to "make a podcast", "create an explainer video", "read this aloud",
  "generate an image", or share knowledge in audio/visual form.
  Supports: topic descriptions, YouTube links, article URLs, plain text, and image prompts.
  Requires LISTENHUB_API_KEY environment variable (get from https://listenhub.ai/settings/api-keys).
---

# ListenHub

Generate podcasts, explainer videos, TTS audio, and AI images through shell scripts that wrap the ListenHub API.

## Setup

Set `LISTENHUB_API_KEY` before first use. Two options:

**Option A** — OpenClaw env config (recommended):
Add to `~/.openclaw/openclaw.json` under `env`:
```json
{ "env": { "LISTENHUB_API_KEY": "lh_sk_..." } }
```

**Option B** — Shell export:
```bash
export LISTENHUB_API_KEY="lh_sk_..."
```

Get your key: https://listenhub.ai/settings/api-keys

For image generation, also set `LISTENHUB_OUTPUT_DIR` (defaults to `~/Downloads`).

## Script Location

All scripts live at `scripts/` relative to this SKILL.md. Resolve the path:

```bash
SCRIPTS="$(cd "$(dirname "<path-to-this-SKILL.md>")" && pwd)/scripts"
```

Dependencies: `curl`, `jq` (install if missing).

## Modes

| Mode | Script | Use Case |
|------|--------|----------|
| Podcast | `create-podcast.sh` | 1-2 speaker discussion |
| Explainer | `create-explainer.sh` + `generate-video.sh` | Narration + AI visuals |
| TTS | `create-tts.sh` | Pure voice reading |
| Speech | `create-speech.sh` | Multi-speaker scripted audio |
| Image | `generate-image.sh` | AI image generation |

Helper scripts: `get-speakers.sh` (list voices), `check-status.sh` (poll progress).

## Hard Constraints

- Execute ONLY through provided scripts. Direct API calls are forbidden.
- Never hardcode speakerIds — call `get-speakers.sh` to discover them.
- The API is proprietary; endpoints and parameters are internal to scripts.

## Mode Detection

Auto-detect from user input:

- **Podcast**: "podcast", "chat about", "discuss", "debate" → `create-podcast.sh`
- **Explainer**: "explain", "introduce", "video", "tutorial" → `create-explainer.sh`
- **TTS**: "read aloud", "convert to speech", "tts" → `create-tts.sh`
- **Image**: "generate image", "draw", "create picture" → `generate-image.sh`

If ambiguous, ask user.

## Quick Reference

### Get Speakers
```bash
$SCRIPTS/get-speakers.sh --language zh   # or en
```
Returns JSON with `data.items[].speakerId`. If user doesn't specify a voice, pick the first match for the language.

### Podcast (One-Stage, default)
```bash
$SCRIPTS/create-podcast.sh --query "topic" --language zh|en --mode quick|deep|debate --speakers <id1[,id2]> [--source-url URL] [--source-text TEXT]
```
- `quick` is default mode. `debate` requires 2 speakers.
- Multiple `--source-url` / `--source-text` allowed.

### Podcast (Two-Stage: text → review → audio)
Use only when user wants to review/edit the script before audio generation.

**Stage 1**: `$SCRIPTS/create-podcast-text.sh` (same args as one-stage)
**Review**: Poll with `check-status.sh --wait`, save draft, STOP and wait for user approval.
**Stage 2**: `$SCRIPTS/create-podcast-audio.sh --episode <id> [--scripts modified.json]`

### Explainer Video
```bash
$SCRIPTS/create-explainer.sh --content "text" --language zh|en --mode info|story --speakers <id>
$SCRIPTS/generate-video.sh --episode <id>
```

### TTS (FlowSpeech)
```bash
$SCRIPTS/create-tts.sh --type text|url --content "text or URL" --language zh|en --mode smart|direct --speakers <id>
```
- Default mode: `direct` (no content modification). `smart` fixes grammar/punctuation.
- Text limit: 10,000 characters; use URL for longer content.

### Multi-Speaker Speech
```bash
$SCRIPTS/create-speech.sh --scripts scripts.json
```
JSON format: `{"scripts": [{"content": "...", "speakerId": "..."}]}`

### Image Generation
```bash
$SCRIPTS/generate-image.sh --prompt "description" [--size 1K|2K|4K] [--ratio 16:9|1:1|9:16|...] [--reference-images "url1,url2"]
```
- Default: 2K, 16:9. Max 14 reference images.
- Output saved to `$LISTENHUB_OUTPUT_DIR` (default `~/Downloads`).

### Check Status
```bash
$SCRIPTS/check-status.sh --episode <id> --type podcast|flow-speech|explainer [--wait] [--timeout 300]
```
Exit codes: 0=done, 1=failed, 2=timeout (retry safe).

Use `--wait` for automated polling. Run generation in background for long tasks.

## Interaction Pattern

1. Detect mode from user input
2. If no speaker specified, call `get-speakers.sh`, pick first match
3. Run the appropriate script (background for long tasks)
4. Report submission, give estimated time (podcast 2-3min, explainer 3-5min, TTS 1-2min)
5. On "done yet?" → run `check-status.sh --wait`
6. Show result link. Offer download only when asked.

## Language

Match response language to user input language. Chinese input → Chinese responses. English → English.

## Links

- Podcast library: https://listenhub.ai/app/podcast
- Explainer library: https://listenhub.ai/app/explainer
- TTS library: https://listenhub.ai/app/text-to-speech
- API keys: https://listenhub.ai/settings/api-keys
