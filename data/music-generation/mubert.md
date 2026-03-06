# Mubert

**Best for:** Background music, streaming, real-time generation

**API:** https://mubert.com/api

## Overview

Mubert generates royalty-free music for commercial use. Specializes in background music, ambient tracks, and continuous streaming audio. Used by apps like Canva and streaming platforms.

## API Versions

- **API 3.0** — Latest, includes pre-generated library
- **API 2.0** — Real-time generation

## Features

- Real-time music generation
- Pre-generated curated library (12,000+ tracks)
- Genre, mood, activity filtering
- BPM control
- Like/dislike personalization
- Continuous streaming

## API Setup

1. Contact Mubert for API access
2. Receive API key and documentation
3. Integrate via REST API

## Basic Generation

```python
import requests

response = requests.post(
    "https://api.mubert.com/v2/generate",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "prompt": "energetic workout music",
        "duration": 60,
        "format": "mp3"
    }
)

track_url = response.json()["track_url"]
```

## Text-to-Music

```python
# Using Mubert's text-to-music
response = requests.post(
    "https://api.mubert.com/v2/ttm",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "prompt": "relaxing ambient music for meditation",
        "duration": 180,
        "tags": ["ambient", "calm", "meditation"]
    }
)
```

## Tag-Based Generation

```python
response = requests.post(
    "https://api.mubert.com/v2/generate",
    json={
        "tags": ["electronic", "upbeat", "happy"],
        "bpm": 120,
        "duration": 90
    }
)
```

## Available Tags

**Genres:**
- Electronic, Hip-Hop, Rock, Jazz, Classical
- Ambient, Chill, Lo-fi, Cinematic

**Moods:**
- Happy, Sad, Energetic, Calm
- Epic, Mysterious, Romantic

**Activities:**
- Workout, Study, Sleep, Focus
- Gaming, Meditation, Party

## Streaming Mode

For continuous background music:

```python
# Initialize stream
stream = requests.post(
    "https://api.mubert.com/v2/stream/start",
    json={"tags": ["lo-fi", "chill"]}
)

stream_url = stream.json()["stream_url"]
# Use stream_url in audio player
```

## Pricing

- **Contact for pricing** — B2B focused
- Per-track or streaming license
- Enterprise plans available

## Use Cases

- Video background music
- App/game soundtracks
- Podcast intros/outros
- Streaming platforms
- Fitness apps
- Meditation apps

## Tips

- Combine multiple tags for specific results
- Use BPM control for video sync
- Pre-generated library for instant access
- Real-time generation for unique tracks
- Good for non-vocal commercial content
