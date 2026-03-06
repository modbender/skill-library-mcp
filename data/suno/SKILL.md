---
name: Suno
slug: suno
version: 1.0.0
homepage: https://clawic.com/skills/suno
description: Generate AI music with Suno via API or browser, with prompt engineering and song extensions.
metadata: {"clawdbot":{"emoji":"🎵","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines.

## When to Use

User wants to generate music with Suno. Agent can use hosted APIs for programmatic generation, browser automation for direct platform interaction, or guide prompt engineering for manual use.

## Architecture

Memory at `~/suno/`. See `memory-template.md` for structure.

```
~/suno/
├── [memory.md]       # Created on first use: preferences, successful prompts
├── [projects/]       # Per-project song tracking
└── [songs/]          # Downloaded audio files
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup | `setup.md` |
| Memory | `memory-template.md` |
| API usage | `api.md` |
| Browser automation | `browser.md` |
| Prompt crafting | `prompts.md` |
| Style tags | `styles.md` |
| Lyrics guide | `lyrics.md` |

## Core Rules

### 1. Choose the Right Approach
| Situation | Method |
|-----------|--------|
| Programmatic generation | Hosted API (aimusicapi.ai, EvoLink) |
| Visual interaction | Browser at suno.com |
| Just need prompts | Prompt engineering only |

### 2. Structure Prompts in Layers
```
[genre] [subgenre] [mood] [instruments] [voice] [era/influence]
```
Example: "indie folk melancholic acoustic guitar soft female vocals 90s"

### 3. Custom Lyrics Format
```
[Verse]
Your lyrics here

[Chorus]
Hook section

[Bridge]
Contrast

[Outro]
Ending
```

### 4. Extend Songs Strategically
Suno generates clips. Build full songs:
1. Create initial clip with strong hook
2. Extend with consistent style
3. Add outro with ending indicators
4. Target 2-4 minutes total

### 5. API Usage Pattern
All APIs follow: generate → poll for completion → retrieve audio URL.
Generation takes 30-90 seconds. See `api.md` for code examples.

## API Integration

### Hosted APIs (Recommended)
Two main options for programmatic generation:

**aimusicapi.ai** — Get API key at aimusicapi.ai
**EvoLink** — Get API key at evolink.ai

Both provide REST APIs for generation, custom lyrics, and extensions.
See `api.md` for detailed code examples and endpoint documentation.

### API Flow
```python
# Conceptual flow (see api.md for real code)
1. POST /generate with prompt
2. Receive task_id
3. Poll /task/{id} every 5 seconds
4. Get audio_url when status="completed"
```

## Browser Automation

When API isn't available or user prefers visual interaction:

### Generate at suno.com
1. Navigate to suno.com/create
2. Choose Simple (description) or Custom (lyrics + style)
3. Enter prompt or lyrics
4. Click Create, wait 30-60 seconds
5. Download the audio

See `browser.md` for detailed automation steps.

## Prompt Patterns

### By Genre
| Genre | Pattern |
|-------|---------|
| Electronic | `electronic [subgenre] [mood] synth [texture]` |
| Rock | `[sub]rock [energy] [guitars] [vocals] [decade]` |
| Pop | `pop [mood] [tempo] [vocals] [production]` |
| Hip Hop | `hip hop [subgenre] [beat] [flow] [era]` |

### Voice Control
```
soft female vocals, ethereal, breathy
deep male vocals, baritone, raspy
instrumental, no vocals
```

See `prompts.md` and `styles.md` for comprehensive guides.

## Common Traps

| Trap | Problem | Solution |
|------|---------|----------|
| Vague prompts | Random output | Be specific with genre, mood |
| Contradictions | Confuses model | Consistent descriptors |
| Too many keywords | Dilutes focus | 8-12 key terms max |
| No structure tags | Awkward lyrics | Use [Verse], [Chorus] |

## Data Storage

This skill creates `~/suno/` on first use:
- **memory file** — Preferences, successful prompts
- **projects folder** — Per-project tracking
- **songs folder** — Downloaded audio (optional)

All data stays local. API keys should be stored as environment variables.

## Scope

**This skill does:**
- Generate music via hosted APIs (requires API key from provider)
- Navigate suno.com with browser automation
- Craft optimized prompts for Suno's model
- Write lyrics with proper structure tags
- Track projects and successful patterns locally

**This skill does NOT:**
- Store API keys in plain text files
- Access files outside `~/suno/`
- Make requests without user direction

## External Endpoints

When using hosted APIs, requests go to:

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| api.aimusicapi.ai | Prompts, lyrics | Music generation |
| api.evolink.ai | Prompts, lyrics | Music generation |
| suno.com | Browser session | Direct platform access |

API keys authenticate requests. Prompts and lyrics are sent for processing.

## Trust

By using this skill with APIs, prompts and lyrics are sent to third-party services for music generation. Only use services you trust with your creative content.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `audio` — Audio processing and editing
- `video` — Combine music with video content
- `ffmpeg` — Audio format conversion

## Feedback

- If useful: `clawhub star suno`
- Stay updated: `clawhub sync`
