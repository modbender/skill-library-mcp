---
name: trackyard
description: Search and download licensed music from Trackyard's AI-powered catalog. Use for finding background music for videos, social content, podcasts, or any project needing royalty-free tracks. Supports natural language search ("upbeat electronic for tech video"), smart audio trimming to exact durations with hit-point alignment, and filtering by genre, mood, BPM, vocals, energy, and instruments.
homepage: https://trackyard.com
metadata: {"openclaw":{"emoji":"🎵","requires":{"bins":["curl","jq"],"env":["TRACKYARD_API_KEY"]},"primaryEnv":"TRACKYARD_API_KEY"}}
---

# Trackyard Music API

Trackyard gives you instant access to tens of thousands of curated tracks — every song 100% legally cleared for social media, YouTube, podcasts, and online content (non-film/TV). Three things make it stand out:

1. **Massive cleared catalog** — tens of thousands of hand-curated songs ready to use on any social platform, no licensing headaches.
2. **AI-powered search** — describe what you need in plain English ("moody lo-fi for a coffee shop vlog") and the API finds the right track, even inferring genre, mood, BPM, and instrumentation from your description.
3. **Smart clip downloader** — trim any track to an exact duration and the algorithm automatically finds the best-sounding segment. Optionally specify a hit point so the biggest moment in the song lands exactly where you need it in your video.

## Use Cases

- **Social media content farms** — automate music selection at scale for TikTok, Reels, and Shorts pipelines; search once per video brief and clip to the exact platform duration (15s, 30s, 60s)
- **Social media ads** — find brand-safe tracks that match your ad's energy, trimmed to exact ad lengths with the hook or drop landing right at the key visual moment
- **AI video generation** — pair AI-generated video with AI-selected music; feed the video description into search and clip the result to match the video length exactly
- **YouTube & podcast backgrounds** — find instrumental, low-energy tracks to sit under voiceover without competing with it
- **Product demo & unboxing videos** — match music energy to product vibe; minimal synth for a productivity app, high-energy for a fitness brand
- **Real estate & property walkthroughs** — calm, spacious ambient tracks that complement visuals without distraction
- **Corporate & training videos** — professional, neutral background music that keeps viewers engaged without distracting from content
- **App & game trailers** — build tension or excitement with the hit point placed exactly on the key reveal moment

## Setup

Requires `TRACKYARD_API_KEY` environment variable. Users get an API key at [trackyard.com](https://trackyard.com).

```bash
export TRACKYARD_API_KEY="trackyard_live_..."
```

Or add to OpenClaw config: `env.vars.TRACKYARD_API_KEY`

## Quick Reference

### Search for music

```bash
scripts/trackyard.sh search "upbeat electronic for tech startup video"
```

With filters:

```bash
scripts/trackyard.sh search "chill background music" --limit 5 --no-vocals --energy medium
```

### Download a track

Full track:

```bash
scripts/trackyard.sh download TRACK_ID
```

Trimmed to 22 seconds:

```bash
scripts/trackyard.sh download TRACK_ID --duration 22
```

With hit-point alignment (drop lands at 12s mark):

```bash
scripts/trackyard.sh download TRACK_ID --duration 22 --hit-point 12
```

### Check credits

```bash
scripts/trackyard.sh me
```

## Workflow

1. **Search** with natural language → get track IDs and metadata
2. **Download** the chosen track (1 credit), optionally trimmed

## Filter Options

| Filter | Values |
|--------|--------|
| `--genres` | electronicDance, pop, rock, hiphop, ambient, classical, jazz, etc. |
| `--moods` | happy, energetic, sad, calm, dramatic, mysterious, romantic |
| `--energy` | low, medium, high |
| `--min-bpm` / `--max-bpm` | 60-200 |
| `--no-vocals` | Instrumental only |
| `--instruments` | synthesizer, guitar, piano, drums, strings, etc. |

## Trimming

When downloading with `--duration`:
- Algorithm finds the most energetic segment with smooth cut points
- `--hit-point N` places the peak/drop at N seconds into the clip
- Perfect for syncing music hits to video moments

## Credits

- Search: 1 credit
- Download: 1 credit
- Account info: Free

## Output

- Search returns JSON with track metadata
- Downloads save as `.mp3` to current directory (filename from track title)
