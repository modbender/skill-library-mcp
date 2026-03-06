# Changelog

## [1.1.3] - 2026-03-03

### Changed
- Improved auth/cache docs and synced metadata cleanup changes.


## [1.1.2] - 2026-02-11

### 🆕 Local Caching

- **FREE Repeat Requests:** Transcripts are cached locally — no API cost for re-fetching!
- **Cache Location:** `.cache/` in skill directory (configurable via `YT_TRANSCRIPT_CACHE_DIR`)
- **Cache Management:**
  - `--cache-stats` — View cache statistics
  - `--no-cache` — Bypass cache, fetch fresh
  - `--clear-cache` — Delete all cached transcripts

### 🆕 Batch Mode

- **Multiple Videos:** Process a list of URLs in one command
- **Usage:** `--batch urls.txt` where file contains one URL per line
- **Output:** Shows progress, cached vs fetched count, total cost estimate

### Changed

- **APIFY Auth:** Uses Bearer header instead of query string (more secure)
- **Cache Key:** Based on video ID for simple lookups

### Usage Examples

```bash
# Batch processing
python3 scripts/fetch_transcript.py --batch urls.txt

# View cache stats
python3 scripts/fetch_transcript.py --cache-stats

# Clear cache
python3 scripts/fetch_transcript.py --clear-cache

# Skip cache
python3 scripts/fetch_transcript.py "URL" --no-cache
```

## [1.0.7] - 2026-02-04

- Privacy cleanup: removed hardcoded paths and personal info from docs
