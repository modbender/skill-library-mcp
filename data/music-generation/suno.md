# Suno

**Best for:** Full songs with AI vocals, lyrics, complete productions

**Web:** https://suno.ai/

## Overview

Suno generates complete songs with vocals, lyrics, and instrumentation from text prompts. Currently the most popular AI music generator for full song creation.

## Models

- **V5** — Latest, best quality vocals and music
- **V4.5** — Good quality, faster
- **V4** — Stable, reliable

## Web Interface

1. Go to https://suno.ai/
2. Enter prompt describing song style
3. Optionally provide custom lyrics
4. Generate and download

## API Access

**Note:** No official public API. Third-party wrappers available:

### Unofficial APIs

**SunoAPI.org:**
```python
import requests

response = requests.post(
    "https://api.sunoapi.org/v1/generate",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "prompt": "upbeat pop song about summer",
        "model": "v5",
        "lyrics": "Optional custom lyrics here"
    }
)
```

**PiAPI (suno-v5):**
```python
response = requests.post(
    "https://api.piapi.ai/api/v1/suno/generate",
    headers={"X-API-Key": API_KEY},
    json={
        "prompt": "epic orchestral trailer music",
        "make_instrumental": True
    }
)
```

## Prompt Structure

```
[Genre] [Mood] [Instruments] [Additional details]
```

**Examples:**
- "Upbeat indie pop song with acoustic guitar and female vocals"
- "Dark ambient electronic with deep bass and atmospheric pads"
- "90s hip-hop beat with vinyl crackle and boom bap drums"

## Custom Lyrics

```
[Verse 1]
Your lyrics here
Line by line

[Chorus]
Catchy hook goes here

[Verse 2]
More lyrics
```

**Tags supported:**
- `[Verse]`, `[Chorus]`, `[Bridge]`
- `[Intro]`, `[Outro]`
- `[Instrumental]`

## Pricing

- **Free:** 50 credits/day (~10 songs)
- **Pro ($10/mo):** 2,500 credits/month
- **Premier ($30/mo):** 10,000 credits/month

**Pro/Premier includes:**
- Commercial license
- No watermarks
- Priority generation

## Tips

- Detailed prompts get better results
- Regenerate multiple times — quality varies
- Use custom lyrics for specific content
- Instrumental mode avoids vocal generation issues
- Extend songs by using "Continue" feature
