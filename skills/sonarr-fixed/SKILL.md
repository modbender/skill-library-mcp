---
name: sonarr-fixed
version: 1.0.2
description: Search and add TV shows to Sonarr. Supports monitor options, search-on-add. FORK of jordyvandomselaar/sonarr with fixed metadata.
metadata:
  openclaw:
    emoji: "📺"
    requires:
      bins:
        - curl
        - jq
      config:
        - path: ~/.openclaw/credentials/sonarr/config.json
          description: "Sonarr API configuration with url, apiKey, and defaultQualityProfile"
      env:
        - name: SONARR_URL
          optional: true
          description: "Sonarr instance URL (overrides config file)"
        - name: SONARR_API_KEY
          optional: true
          description: "Sonarr API key (overrides config file)"
    fork:
      original: jordyvandomselaar/sonarr
      original_url: https://clawhub.com/jordyvandomselaar/sonarr
      reason: "Fixed metadata to properly declare required credentials and config paths"
---

# Sonarr (Fixed)

**⚠️ FORK NOTICE:** This is a fork of [jordyvandomselaar/sonarr](https://clawhub.com/jordyvandomselaar/sonarr) with corrected metadata declarations.

Add TV shows to your Sonarr library.

## Setup

Create `~/.openclaw/credentials/sonarr/config.json`:
```json
{
  "url": "http://localhost:8989",
  "apiKey": "your-api-key",
  "defaultQualityProfile": 1
}
```
- `defaultQualityProfile`: Quality profile ID (run `config` to see options)

### Alternative: Environment Variables
Instead of config file, you can use:
- `SONARR_URL` - Sonarr instance URL
- `SONARR_API_KEY` - Sonarr API key

## Workflow

1. **Search**: `search "Show Name"` - returns numbered list
2. **Present results with TVDB links** - always show clickable links
3. **Check**: User picks a number
4. **Add**: Add show and start search

## Important
- **Always include TVDB links** when presenting search results to user
- Format: `[Title (Year)](https://thetvdb.com/series/SLUG)`
- Uses `defaultQualityProfile` from config; can override per-add

## Commands

### Search for shows
```bash
bash scripts/sonarr.sh search "Breaking Bad"
```

### Check if show exists in library
```bash
bash scripts/sonarr.sh exists <tvdbId>
```

### Add a show (searches immediately by default)
```bash
bash scripts/sonarr.sh add <tvdbId>              # searches right away
bash scripts/sonarr.sh add <tvdbId> --no-search  # don't search
```

### Remove a show
```bash
bash scripts/sonarr.sh remove <tvdbId>                # keep files
bash scripts/sonarr.sh remove <tvdbId> --delete-files # delete files too
```
**Always ask user if they want to delete files when removing!**

### Get root folders & quality profiles (for config)
```bash
bash scripts/sonarr.sh config
```

---
*Original skill by [jordyvandomselaar](https://clawhub.com/jordyvandomselaar). Fork maintained with permission under open source principles.*
