---
name: dj-mp3-sourcer
description: >
  Download music from links (YouTube, Spotify, etc.) by finding the best available source.
  Searches across platforms in priority order: Bandcamp, Beatport, Amazon Music, Spotify (via spotdl),
  YouTube (via yt-dlp). Use when a user sends music links and wants high-quality audio files downloaded,
  or when batch-downloading tracks from mixed sources. Handles single tracks or batch lists.
  Surfaces purchase links for paid platforms, downloads directly from free sources.
  Default output is MP3 320k. Supports a "free only" mode that skips paid platforms entirely.
---

# DJ MP3 Sourcer

DJ-oriented music downloading skill. Takes any music link and finds the best available source, prioritizing extended mixes and MP3 320k output.

> **⚠️ Legal Notice:** This skill is intended for downloading music you have the right to access — purchases, free releases, creative commons, etc. Respect copyright laws in your jurisdiction. The author is not responsible for misuse.

## Dependencies

```bash
pip install yt-dlp spotdl
brew install ffmpeg  # needed by yt-dlp for audio extraction

# optional
pip install bandcamp-dl  # for free bandcamp downloads
```

## Source Priority

Search in this order — stop at the first match:

1. **Bandcamp** — supports artists directly, often has extended mixes
2. **Beatport** — DJ-standard, has BPM/key metadata, extended mixes
3. **Amazon Music** — digital purchase option
4. **Spotify** (via `spotdl`) — good metadata/tagging, 320k MP3
5. **YouTube** (via `yt-dlp`) — fallback, always works

For paid sources (bandcamp, beatport, amazon), surface the purchase link with price. For free sources, download directly.

If **free only** mode is enabled, skip steps 1-3 and go straight to spotdl → yt-dlp.

## Core Rule: Prefer Extended Mixes

**Always prefer the extended mix over radio edits.** An extended mix from a lower-priority source beats a radio edit from a higher-priority one.

Example: extended mix on YouTube > radio edit on Spotify.

When searching, append "extended mix" to queries. If only a radio edit exists, note it in the output.

## Workflow

1. **Identify the track** — extract artist + title:
   ```bash
   yt-dlp --dump-json "<url>" | jq '{title, artist: .artist // .uploader, duration}'
   ```
2. **Search each source** using web_search:
   ```
   "<artist> <title> extended mix site:bandcamp.com"
   "<artist> <title> extended mix site:beatport.com"
   "<artist> <title> site:amazon.com/music"
   ```
3. **Download or link** — free sources download; paid sources return purchase URL with price
4. **Tag the file** — artist, title, album, cover art. Note BPM/key if available from beatport.

## Download Commands

### spotdl
```bash
spotdl download "<spotify-url>" --output "{artist} - {title}" --format mp3 --bitrate 320k
```

### yt-dlp
```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 \
  --embed-thumbnail --add-metadata \
  --metadata-from-title "%(artist)s - %(title)s" \
  -o "%(artist)s - %(title)s.%(ext)s" "<url>"
```

## Post-Download: Filename Normalization

yt-dlp filenames are often messy (`NA -` prefixes, `(Official Video)` suffixes, label names, wrong artist credits). **Always** run the normalization script after downloads complete.

**Usage:**
```bash
# 1. Write the tracklist as JSON (from the parsed tracklist in step 2)
cat > /tmp/tracklist.json << 'EOF'
[{"artist": "Karol G", "title": "Ivonny Bonita"}, {"artist": "Doja Cat", "title": "Woman (Never Dull's Disco Rework)"}]
EOF

# 2. Run the normalize script
scripts/normalize-filenames.sh ~/Downloads/set-name /tmp/tracklist.json
```

The script fuzzy-matches each mp3 in the directory to a tracklist entry and renames to clean `Artist - Title.mp3` format. Unmatched files are left untouched.

**The tracklist is the source of truth for filenames**, not YouTube metadata.

## Configuration

| Setting | Default | Notes |
|---------|---------|-------|
| Output directory | `~/Downloads/` | Where files are saved (subfolder per set when used with dj-set-ripper) |
| Format | mp3 320k | High-bitrate MP3; configurable to flac if needed |
| Extended mix | always | Prefer extended/original mix over radio edit |
| Free only | false | When true, skip paid sources (bandcamp, beatport, amazon) — only use spotdl and yt-dlp |

## Batch Processing

When given multiple links, process in parallel using sub-agents (`sessions_spawn`). Report results as each track completes.

## Edge Cases

- **DJ mixes / long sets** — download via yt-dlp directly, skip source searching
- **Unavailable tracks** — report clearly, suggest alternatives if found
- **Region-locked content** — note restriction, try alternative sources
- **Remix vs original** — if the link is a specific remix, search for that exact remix, not the original
