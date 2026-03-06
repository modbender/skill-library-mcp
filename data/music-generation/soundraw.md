# Soundraw

**Best for:** Royalty-free music for content creators, video production

**Web:** https://soundraw.io/
**API:** https://discover.soundraw.io/api

## Overview

Soundraw generates customizable royalty-free music. Designed for content creators needing background music for videos, podcasts, and apps. Integrated with platforms like Canva and Filmora.

## Features

- Royalty-free for commercial use
- Customizable track sections
- Genre and mood selection
- Adjustable length and energy
- Download stems (Pro)
- API for integration

## Web Interface

1. Select genre, mood, length
2. Generate tracks
3. Customize sections (intro, buildup, climax, etc.)
4. Adjust energy levels per section
5. Download MP3 or WAV

## API Access

Contact Soundraw for API integration:

```python
import requests

# Example API call (actual endpoints may vary)
response = requests.post(
    "https://api.soundraw.io/v1/generate",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "genre": "corporate",
        "mood": "uplifting",
        "length": 90,
        "energy": "medium"
    }
)

track_data = response.json()
```

## Genres

- **Corporate** — Business, presentations
- **Cinematic** — Film, trailers
- **Electronic** — EDM, techno
- **Hip-Hop** — Beats, urban
- **Pop** — Mainstream, catchy
- **Rock** — Guitar-driven
- **Acoustic** — Organic, natural
- **Classical** — Orchestral

## Moods

- Uplifting, Happy, Energetic
- Calm, Peaceful, Dreamy
- Dark, Tense, Mysterious
- Romantic, Sentimental
- Epic, Powerful

## Customization

**Track Structure:**
1. Intro — Set the tone
2. Build — Rising energy
3. Climax — Peak energy
4. Drop — Release
5. Outro — Wind down

**Per-Section Controls:**
- Energy level (1-5)
- Instrument emphasis
- Length

## Pricing

- **Creator ($16.99/mo):** Unlimited downloads, personal use
- **Artist ($19.99/mo):** Commercial use, monetization
- **Enterprise:** API access, custom pricing

## Integrations

- Canva
- Wondershare Filmora
- Custom apps via API

## Use Cases

- YouTube videos
- Podcasts
- Corporate presentations
- Advertisements
- Social media content
- Games

## Tips

- Use mood + genre combo for best results
- Customize sections to match video cuts
- Download stems for mixing flexibility
- Generate multiple tracks for options
- Check license terms for your use case
