---
name: dj-set-ripper
description: >
  Download individual songs from a DJ set or mix. Given a link from YouTube, SoundCloud, Mixcloud,
  or 1001Tracklists, extract the tracklist from the page description or metadata, then look up and
  download each track individually using the dj-mp3-sourcer skill. Use when a user shares a DJ set/mix
  link and wants the individual tracks downloaded, or when they paste a tracklist and want all tracks sourced.
  Generates a timestamped log file showing the status of every track (downloaded, purchase link, not found,
  bootleg/unavailable, unidentified). Also optionally downloads the full mix as a backup.
---

# DJ Set Ripper

Extract tracklists from DJ sets and download each track individually.

> **⚠️ Legal Notice:** This skill is intended for downloading music you have the right to access — purchases, free releases, creative commons, etc. Respect copyright laws in your jurisdiction. The author is not responsible for misuse.

## Dependencies

Same as [dj-mp3-sourcer](https://clawhub.ai/Robinnnnn/dj-mp3-sourcer) (yt-dlp, ffmpeg/ffprobe, spotdl). No additional dependencies.

## Workflow

### 1. Extract Page Content

Fetch the set URL and extract raw text (description, metadata, comments):

**YouTube:**
```bash
yt-dlp --dump-json "<url>" | jq -r '.description'
```

**SoundCloud / Mixcloud:**
Use `web_fetch` to grab the page content in markdown mode.

**1001Tracklists:**
Use `web_fetch` — this source has the most structured data. Prefer it when available.

### 2. Parse the Tracklist (LLM-Powered)

Feed the raw page content to the model with this prompt structure:

```
Extract all tracks from this DJ set description. Return a JSON array of objects:
[{"number": 1, "timestamp": "0:00", "artist": "Artist Name", "title": "Track Title (Mix Name)"}]

Rules:
- Preserve remix/mix names in the title (e.g. "Original Mix", "Extended Mix", "Remix")
- If a track is listed as "ID - ID" or "ID", set artist and title both to "ID"
- If only a timestamp exists with no track info, skip it
- Normalize artist names (fix ALL CAPS, etc.)
- If no timestamps exist, set timestamp to null
- Number tracks sequentially starting from 1

Raw content:
"""
{description_text}
"""
```

If parsing returns zero tracks, inform the user the tracklist couldn't be extracted and suggest:
- Checking 1001Tracklists manually
- Pasting the tracklist directly

### 3. Download Each Track

For each parsed track (skipping any with artist AND title = "ID"):

1. Use the **[dj-mp3-sourcer](https://clawhub.ai/Robinnnnn/dj-mp3-sourcer)** workflow: search sources in priority order, prefer extended mixes, download or surface purchase links
2. Use `sessions_spawn` to parallelize downloads (batch of 3-5 at a time to avoid rate limits)
3. Save files to: `~/Downloads/{set-name}/`

Set name is derived from the mix title (sanitized for filesystem).

### 4. Optionally Download the Full Mix

Ask the user if they also want the full mix downloaded. If yes:

```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 \
  --embed-thumbnail --add-metadata \
  -o "~/Downloads/{set-name}/{set-name} [Full Mix].%(ext)s" "<url>"
```

### 5. Normalize Filenames

After **all** downloads complete (not per-batch — wait for every sub-agent to finish), run the normalization script once:

```bash
# 1. Write the parsed tracklist as JSON
cat > /tmp/tracklist.json << 'EOF'
[{"artist": "Artist", "title": "Title"}, ...]
EOF

# 2. Run normalize
scripts/normalize-filenames.sh ~/Downloads/{set-name} /tmp/tracklist.json
```

This fuzzy-matches each mp3 to a tracklist entry and renames to clean `Artist - Title.mp3`. Handles `NA -` prefixes, `(Official Video)` junk, wrong artist credits, label names, etc.

**Critical:** Run this in the parent agent after all batches return — do NOT rely on sub-agents to rename. The parsed tracklist is the **source of truth** for filenames.

### 6. Generate the Log File

Create `~/Downloads/{set-name}/{timestamp}.log` with format:

```
DJ Set Ripper Log
=================
Set: {set title}
URL: {original url}
Date: {ISO timestamp}
Tracks found: {total}

#   | Artist              | Title                          | Status         | Source   | Bitrate | Size  | File/Link
----|---------------------|--------------------------------|----------------|----------|---------|-------|----------
01  | Argy                | Aria (Original Mix)            | ✅ downloaded   | spotdl   | 320k    | 8.2MB | Argy - Aria (Original Mix).mp3
02  | ID                  | ID                             | ⬛ unidentified | —        | —       | —     | —
03  | Massano             | Odyssey                        | ✅ downloaded   | youtube  | 271k    | 6.5MB | Massano - Odyssey.mp3
04  | Boris Brejcha       | Gravity (Extended Mix)         | 🛒 purchase     | beatport | —       | —     | https://...
05  | Some Bootleg        | Unreleased VIP                 | ❌ not found    | —        | —       | —     | —

Summary: 3 downloaded, 1 purchase link, 1 not found, 1 unidentified
Total size: ~XXM (individual tracks) + XXM (full mix)
Full mix: ✅ downloaded → {set-name} [Full Mix].mp3

Notes:
- Bitrate via `ffprobe -v quiet -show_entries format=bit_rate -of csv=p=0 "<file>"`
- File size via `ls -lh`
```

## Edge Cases

- **No tracklist in description** — check 1001Tracklists via web_search: `"{set title}" site:1001tracklists.com`
- **"ID - ID" tracks** — log as unidentified, don't attempt download
- **Bootlegs / mashups** — search anyway, but expect failures. log as `not found` with note
- **B2B sets** — multiple artists in set title, handle gracefully
- **Duplicate tracks** — deduplicate by artist+title before downloading
- **Very long sets (50+ tracks)** — batch in groups of 5, report progress as batches complete

## Configuration

| Setting | Default | Notes |
|---------|---------|-------|
| Output directory | `~/Downloads/{set-name}/` | Per-set subfolder |
| Format | mp3 320k | Via dj-mp3-sourcer |
| Download full mix | ask user | Can be set to always/never |
| Free only mode | true | Passed through to dj-mp3-sourcer (skip paid sources, use spotdl/yt-dlp only) |
| Parallel downloads | 5 | Max concurrent track downloads |
