# Troubleshooting

## Cookie auth failures

### Symptoms
- Playlist appears empty (`LL`, `WL`)
- yt-dlp reports private/unavailable playlist
- Auth-related extraction errors

### Fixes
1. Confirm you are signed into YouTube in the configured browser.
2. Set `browser` in `.config.json` to the actual browser in use.
3. **macOS:** The terminal app (Terminal, iTerm, etc.) needs **Full Disk Access** in System Settings > Privacy & Security to read Chrome's cookie database. Without it, `yt-dlp` silently gets no cookies and private playlists appear empty.
4. **macOS (Chrome specifically):** Chrome may also prompt "allow Terminal to access data from other apps" — click Allow.
5. Test directly:
   - `yt-dlp --cookies-from-browser chrome --flat-playlist "https://www.youtube.com/playlist?list=LL"`
6. If browser cookie extraction still fails, export cookies via a browser extension (e.g. "Get cookies.txt LOCALLY") and set `cookies_file` in config.

---

## Rate limiting / transient network errors

### Symptoms
- HTTP 429
- Timeouts
- intermittent 5xx errors

### Fixes
1. Run in smaller batches: `yt-enrich.py --limit 5`.
2. Retry later; built-in backoff already retries transient failures.
3. Prefer authenticated requests (`browser`/`cookies_file`) over anonymous requests.

---

## Missing transcripts

### Symptoms
- No `## Transcript` section after enrichment
- `transcript_status: missing`

### Why this happens
- Video has no subtitles/auto-captions available.
- Subtitle language is unavailable.
- Captions are restricted.

### Fixes
1. Verify captions exist on YouTube for that video.
2. Re-run enrichment later (captions can appear after upload).
3. If installed, `summarize` CLI is used as fallback transcript extractor.

---

## API key / provider issues

### Symptoms
- Missing summaries or tags
- `summary_status: failed`
- `tags_status: keyword` when LLM expected

### Fixes
1. Confirm env vars are set in the same shell/session running scripts.
   - macOS/Linux example: `echo $OPENAI_API_KEY`
2. Confirm `api_key_env` in config exactly matches env var name.
3. Confirm model name is valid for provider.
4. Set provider to `none` temporarily to continue pipeline without LLM.

---

## Windows-specific issues

### Cookie extraction fails on Windows
- Browser cookie access can fail due to profile encryption/permissions.
- Workaround: export `cookies.txt` via browser extension and set `cookies_file`.

### Path quoting issues
- Use full quoted paths for `--output`, `--config`, `--cookies`.
- Prefer PowerShell examples:
  - `python .\yt-import.py --output "C:\Users\you\YouTube-Archive"`

### Python launcher differences
- Use `py -3` when `python3` is unavailable.

---

## Lockfile says another process is running

If `.yt-archiver.lock` exists, another run is active or a stale lock remained.

1. Wait for the current run to finish.
2. If no process is running, delete `<output>/.yt-archiver.lock`.
3. Re-run command.
