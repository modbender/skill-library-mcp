---
name: opensubtitles
description: Read-only OpenSubtitles skill to search and download subtitles via API, then extract scene context by timestamp to answer user questions regarding a show in context and avoid spoilers. Use when the user asks “what’s happening at this timestamp” or needs subtitle context; pairs well with trakt-readonly skill for playback progress. Requires an OpenSubtitles API key and User-Agent.
metadata: {"openclaw":{"requires":{"env":["OPENSUBTITLES_API_KEY","OPENSUBTITLES_USER_AGENT"],"bins":["curl","jq","awk"]},"primaryEnv":"OPENSUBTITLES_API_KEY","emoji":"📝"}}
---

# OpenSubtitles

Use this skill to fetch subtitle context around a timestamp. This is **read‑only**: no uploads or modifications.

## Setup

Users should obtain an API key at: https://www.opensubtitles.com/consumers

Required env vars:
- `OPENSUBTITLES_API_KEY`
- `OPENSUBTITLES_USER_AGENT` (e.g., `OpenClaw 1.0`)

Optional (for downloads):
- `OPENSUBTITLES_USERNAME`
- `OPENSUBTITLES_PASSWORD`
- `OPENSUBTITLES_TOKEN` (if already logged in)
- `OPENSUBTITLES_BASE_URL` (hostname from login response, e.g., `api.opensubtitles.com`)

## Commands

Scripts live in `{baseDir}/scripts/`.

### Search subtitles

```
{baseDir}/scripts/opensubtitles-api.sh search --query "Show Name" --season 3 --episode 5 --languages en
```

Prefer IDs when available (imdb/tmdb). Use parent IDs for TV episodes. Follow redirects for search (script already uses `-L`).

### Login (token)

```
{baseDir}/scripts/opensubtitles-api.sh login
```

Note: Login is rate limited (1/sec, 10/min, 30/hour). If you get 401, stop retrying.
Use `base_url` from the response as `OPENSUBTITLES_BASE_URL` for subsequent requests.

### Request a download link

Before downloading, check the local subtitle cache (see below). Only call the download API if the file is not already cached.

```
OPENSUBTITLES_TOKEN=... {baseDir}/scripts/opensubtitles-api.sh download-link --file-id 123
```

### Extract context at timestamp

After downloading an `.srt` file (default window: 10 minutes before timestamp):

On Windows, use `findstr` or PowerShell `Select-String` to replicate the awk logic (use the shell script as a guide). The agent should pick the best option available on that system.

```
{baseDir}/scripts/subtitle-context.sh ./subtitle.srt 00:12:34,500
```

Custom window:

```
{baseDir}/scripts/subtitle-context.sh ./subtitle.srt 00:12:34,500 --window-mins 5
```

## Trakt synergy

Pair with `trakt-readonly` to identify current episode; when Trakt adds playback progress support, update the Trakt skill to supply a precise timestamp for context‑aware, spoiler‑safe responses.

## Cache

Store downloaded subtitles under `{baseDir}/storage/subtitles/` (create if missing). Use a stable filename like:

`{baseDir}/storage/subtitles/<file_id>__<language>.srt`

Check this cache before calling `/download` to avoid wasting limited daily downloads.

## Guardrails

- Never log or expose API keys, passwords, or tokens.
- Only call `https://api.opensubtitles.com/api/v1` (or the `base_url` returned by login).
- Do not cache download links.
- Prefer IDs over fuzzy queries for accuracy.
- **Avoid wasting downloads:** store downloaded subtitle files locally and check the cache before calling the download API again.
- If a download is requested, always append the remaining download quota (from the `remaining` field) in the user response.
- Subtitle context should include the window from 10 minutes before the timestamp to the timestamp (default), unless the user specifies otherwise.
- The agent can adjust `--window-mins` to get more or less context as needed.
- Only read subtitle files from `{baseDir}/storage/subtitles/` to avoid arbitrary file access.

## References

- `references/opensubtitles-api.md`
