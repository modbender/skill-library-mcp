---
name: free-resource
description: "Search and retrieve royalty-free media from Pixabay (images/videos), Freesound (audio effects), and Jamendo (music/BGM). Use when the user needs to find stock photos, illustrations, vectors, videos, sound effects, or background music, download media, or query media libraries with filters."
---

# Free Resource

Search and download royalty-free images, videos, sound effects, and music from Pixabay, Freesound, and Jamendo.

## Quick Start

```bash
# 1. Copy config template and fill in your API keys
cp config.example.json config.json

# 2. Edit config.json with your API keys

# 3. Use without passing API keys
bun ./scripts/jamendo.ts search --query "background" --limit 5
bun ./scripts/freesound.ts search --query "piano"
bun ./scripts/pixabay.ts search-images --query "nature"
```

## Configuration

API keys are stored in `config.json`. Copy `config.example.json` and fill in your keys:

```json
{
  "pixabay": {
    "api_key": "YOUR_PIXABAY_API_KEY"
  },
  "freesound": {
    "api_token": "YOUR_FREESOUND_TOKEN"
  },
  "jamendo": {
    "client_id": "YOUR_JAMENDO_CLIENT_ID"
  }
}
```

### Get API Keys

| Platform | Type | Get API Key |
|----------|------|-------------|
| Pixabay | Images/Videos | https://pixabay.com/accounts/register/ |
| Freesound | Audio Effects | https://freesound.org/apiv2/apply |
| Jamendo | Music/BGM | https://devportal.jamendo.com/ |

### API Key Priority

1. **CLI flag**: `--key`, `--token`, or `--client-id`
2. **Environment variable**: `PIXABAY_API_KEY`, `FREESOUND_API_TOKEN`, `JAMENDO_CLIENT_ID`
3. **Config file**: `config.json`

---

## Pixabay (Images & Videos)

### Search Images

```bash
bun ./scripts/pixabay.ts search-images --query "yellow flowers" --image-type photo --orientation horizontal --per-page 5
```

Flags: `--query`, `--id`, `--lang`, `--image-type` (all|photo|illustration|vector), `--orientation` (all|horizontal|vertical), `--category`, `--colors` (comma-separated), `--min-width`, `--min-height`, `--editors-choice`, `--safesearch`, `--order` (popular|latest), `--page`, `--per-page` (5-200), `--output` (save to file).

### Search Videos

```bash
bun ./scripts/pixabay.ts search-videos --query "ocean waves" --video-type film --per-page 5
```

### Download

```bash
bun ./scripts/pixabay.ts download --url "https://pixabay.com/get/..." --output "/path/to/save.jpg"
```

---

## Freesound (Audio Effects)

### Search Sounds

```bash
bun ./scripts/freesound.ts search --query "piano note" --page-size 10
```

Flags: `--query`, `--filter`, `--sort`, `--fields`, `--page`, `--page-size` (max 150), `--group-by-pack`, `--output`.

### Filter Examples

```bash
bun ./scripts/freesound.ts search --query "drum" --filter "duration:[0 TO 2]"
bun ./scripts/freesound.ts search --query "ambient" --filter "type:wav"
bun ./scripts/freesound.ts search --query "explosion" --sort downloads_desc
```

### Get Sound Details

```bash
bun ./scripts/freesound.ts get --id 12345 --fields id,name,previews,duration
```

### Download Preview

```bash
bun ./scripts/freesound.ts download --id 12345 --output ./sound.mp3
```

---

## Jamendo (Music & BGM)

### Search Music

```bash
bun ./scripts/jamendo.ts search --query "rock" --limit 10
```

Flags: `--query`, `--tags`, `--fuzzytags`, `--artist-name`, `--album-name`, `--order`, `--limit` (max 200), `--offset`, `--output`.

### Music Attribute Filters

```bash
# Instrumental background music
bun ./scripts/jamendo.ts search --query "background" --vocalinstrumental instrumental

# Search by tags (AND logic)
bun ./scripts/jamendo.ts search --tags "electronic+chill" --order popularity_total_desc

# Search by speed
bun ./scripts/jamendo.ts search --query "energetic" --speed high+veryhigh
```

### Get Track Details

```bash
bun ./scripts/jamendo.ts track --id 12345 --include musicinfo,stats
```

### Download Track

```bash
bun ./scripts/jamendo.ts download --id 12345 --output ./music.mp3
```

---

## API Reference

For full parameter tables, response field descriptions, and rate limit details, see `./references/api_reference.md`.
