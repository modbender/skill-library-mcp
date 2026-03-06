# Changelog

## [1.0.5] - 2026-03-03

### Changed
- Synced version metadata and retained recent output/path safety fixes.


## [1.0.1] - 2026-02-11

### Fixed

- Switched default actor from `apidojo~tweet-scraper` (returning `{"noResults": true}`) to `quacker~twitter-scraper`
- Updated actor input payloads to match `quacker~twitter-scraper` API:
  - Search: `searchTerms` + `maxItems`
  - User: `startUrls` + `maxItems`
  - URL: `startUrls` + `maxItems`
- Updated tweet field mapping to match actor response shape:
  - `id_str` → `id`
  - `text` → `text`
  - `user.screen_name` → `author`
  - `user.name` → `author_name`
  - `created_at` → `created_at`
  - `favorite_count` → `likes`
  - `conversation_count` → `replies`
  - `retweets` set to `0` (field not provided by actor)
- URL generation now consistently builds `https://x.com/{screen_name}/status/{id_str}` when missing
- Updated docs/config metadata to reference `quacker~twitter-scraper`

## [1.0.0] - 2026-02-11

### Added

- **Tweet Search** - Search tweets by keywords, hashtags, mentions
- **User Profiles** - Get tweets from a specific user
- **Tweet Details** - Get a specific tweet + replies by URL
- **Local Caching** - Save API costs with local file cache
  - Search results: 1 hour TTL
  - User profiles: 24 hours TTL
  - Specific tweets: 24 hours TTL
- **Cache Management**
  - `--cache-stats` - View cache statistics
  - `--clear-cache` - Delete all cached results
  - `--no-cache` - Bypass cache for fresh fetch
- **Output Formats**
  - `--format json` - Structured JSON output
  - `--format summary` - Human-readable summary
- **Safety Features**
  - Bearer token auth (not in query string)
  - Query sanitization (control chars, length limits)
  - No hardcoded paths or personal data

### Technical

- Uses `apidojo~tweet-scraper` (Tweet Scraper V2) actor
- Supports `--max-results` to limit results (default 20)
- Supports `--output` to save to file
