---
name: lyrics-search
description: Search song lyrics by title and artist using the LrcApi public API. Use when the user asks to find, display, or print lyrics for a song.
---

# Lyrics Search

Search lyrics via the LrcApi public API (`api.lrc.cx`).

## API

```
GET https://api.lrc.cx/lyrics?title={title}&artist={artist}
```

- Returns LRC format (with timestamps) as `text/plain`
- `artist` is optional but improves accuracy
- URL-encode Chinese/special characters

## Usage

1. Fetch lyrics via `web_fetch` on the API URL
2. The response is LRC format with `[mm:ss.xxx]` timestamps and metadata lines at the top
3. Strip timestamps and metadata lines (credits, producer info at `[00:00]`–`[00:24]`) for clean display
4. For printing: format as plain text with song title, artist, and credits header

## Example

```
web_fetch("https://api.lrc.cx/lyrics?title=世界赠予我的&artist=王菲")
```

## Notes

- Public API may be slow; set a reasonable timeout
- If no results, try with only `title` (omit `artist`)
- If still no results, try alternate song name spellings
