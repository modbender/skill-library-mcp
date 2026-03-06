# Changelog

## v2.1.1 - 2026-03-02

### Fixed
- SKILL.md: fix source counts (65 total), add all env vars (TWITTERAPI_IO_KEY, BRAVE_API_KEYS, TAVILY_API_KEY, TWITTER_API_BACKEND), list all 14 scripts, update optionalBins, fix credentialAccess description

## v2.1.0 - 2026-03-01

### Added
- `enrich-articles.py`: full-text enrichment for top articles (synced from tech v3.13.0)
- `run-pipeline.py`: --enrich flag for article enrichment phase
- `merge-sources.py`: GitHub trending support (inactive for media, no GitHub source)

## v2.0.4 - 2026-03-01

### Fixed
- Strengthen quality_score ordering instruction in digest prompt (CRITICAL tag)

## v2.0.3 - 2026-03-01

### Changed
- Sync fetch-web.py from tech-news-digest v3.11.0: add Tavily Search as alternative web search backend (TAVILY_API_KEY)

## v2.0.2 - 2026-03-01

### Added
- Show quality score (🔥) prefix on each article in digest output
- Articles strictly ordered by quality_score descending within each topic

## v2.0.1 - 2026-02-28

### Changed
- Sync from tech-news-digest v3.10.3:
  - `fetch-web.py`: multi-key Brave API support with quota-aware fallback
  - `merge-sources.py`: exempt multi-author platforms from per-topic domain limits
  - `config_loader.py`: prefixed overlay config files

## v2.0.0 - 2026-02-25

### Added
- `generate-pdf.py`: PDF generation with Chinese typography and emoji support (synced from tech-news-digest v3.10.0)
- `send-email.py`: Proper MIME email with HTML body + PDF attachment (synced from tech-news-digest v3.10.1)
- Updated `sanitize-html.py` from tech-news-digest

### Changed
- Email delivery: switch from mail/msmtp to send-email.py with PDF attachment
- Digest prompt: auto-attach PDF to email delivery

## v1.9.4 - 2026-02-24

### Fixed
- **Root cause fix**: Remove `china` topic tag from general RSS sources (THR, Deadline, Variety, etc.) — was causing every article from these feeds to be classified as China news
- China topic now only assigned by dedicated sources: THR China, Variety Asia, Deadline China tag feeds

## v1.9.3 - 2026-02-24

### Fixed
- China section: add strict verification rule — agent must verify Hollywood films actually released in mainland China before including
- China section: global box office reports mentioning China numbers → Box Office section, not China

## v1.9.2 - 2026-02-24

### Fixed
- China topic: tighten must_include keywords to avoid false positives (Korea/Japan/secondary market mentions)
- China topic: add exclusions for other Asian markets
- Digest prompt: add same-story-different-dates dedup rule
- Digest prompt: add explicit China section filtering rules

## v1.9.1 - 2026-02-24

### Added
- 12 new RSS sources: ET Online, Den of Geek, The Direct, CinemaBlend, MovieWeb, CBR, Roger Ebert, The Film Stage, No Film School, What's on Netflix, Decider, Anime News Network
- 5 new Reddit sources: r/entertainment, r/netflix, r/marvelstudios, r/DC_Cinematic, r/anime
- 4 new Twitter KOLs: @etnow, @TheAcademy, @letterboxd, @A24
- Re-enabled: Vulture, Entertainment Weekly

### Changed
- Total sources: 44 → 65 (64 enabled)

## v1.9.0 - 2026-02-24

### Changed
- **Major sync** from tech-news-digest v3.9.0: all shared scripts updated
- fetch-twitter.py: pagination, rate limiter, retry, dedup (v3.8.0+v3.9.0)
- merge-sources.py: URL dedup, improved scoring
- run-pipeline.py: --skip/--reuse-dir, parallel execution improvements
- fetch-web.py: Brave cache, rate limit handling
- fetch-rss.py: RSS cache improvements
- source-health.py: health tracking updates
- summarize-merged.py: output format improvements
- digest-prompt: switch to unified `run-pipeline.py`, add quality_score selection rule, Reddit format

## v1.8.5 - 2026-02-24

### Changed
- Sync fetch-twitter.py from tech-news-digest: dual backend (official X API + twitterapi.io), auto fallback, 3-worker concurrency, progress logging
- Sync test-pipeline.sh: --only/--skip/--topics/--ids/--twitter-backend filtering, progress stats, timing

## v1.8.4 - 2026-02-24

### Changed
- Enable all 14 Twitter/X sources (were all disabled)

## v1.8.3 - 2026-02-24

### Changed
- Title/subject: 中文标题 `🎬 每日影视日报 — YYYY-MM-DD`（对齐 tech-news-digest 风格）
- Email h1 + Discord h1 + email subject 统一使用中文标题

## v1.8.2 - 2026-02-22

### Changed
- Align HTML templates with tech-news-digest: add GitHub repo link in footer
- Email footer: repo link as clickable `<a>` tag
- Discord footer: add repo link with embed suppression `<>`
- Email style guidelines: add headings/lists/footer/no-images/no-tables rules
- Discord template: add delivery section (channel vs DM)

## v1.8.1 - 2026-02-22

### Changed
- Cron job: add second email recipient support

## v1.8.0 - 2026-02-21

### Changed
- Simplify digest-prompt: ~200→130 lines, remove redundancy, align with tech-news-digest structure
- Email delivery: prefer mail/msmtp, fallback to gog CLI
- Email content parity: must contain ALL same items as Discord
- Add EMAIL_FROM placeholder for optional sender display name

### Added
- CONTRIBUTING.md with development conventions
- `source` field in SKILL.md metadata

## [1.7.1] - 2026-02-18

### Security
- Sanitize untrusted titles/snippets in summarize-merged.py (prompt injection filter)
- Add untrusted content warning banner per topic section

## [1.7.0] - 2026-02-18

### Added
- `summarize-merged.py`: structured summary tool for LLM consumption, avoids ad-hoc JSON parsing
- digest-prompt now references summarize-merged.py for article selection

### Fixed
- test-pipeline.sh: zsh-compatible array syntax for merge args
- Archive path: `media-digest/` → `media-news-digest/` for consistency

## [1.6.1] - 2026-02-17

### Improved
- KOL entries now show display name with handle: **Display Name** (@handle)
- Code quality: bare `except:` → `except Exception:` across all scripts
- Removed unused imports (URLError, tempfile, List, timezone)
- Added `display_name` field to merged Twitter articles

## [1.6.0] - 2026-02-17

### Added
- `run-pipeline.py`: Unified parallel pipeline — runs all 4 fetch steps concurrently, then merges (synced from tech-news-digest v3.4.0)
- Brave API auto rate-limit detection for optimal concurrency in `fetch-web.py`

### Fixed
- Reddit 403 errors: added SSL context and proper Accept/Accept-Language headers
- Reddit fetching now parallel (ThreadPoolExecutor) instead of sequential
- All fetch timeouts increased from 15s to 30s for reliability

## [1.3.0] - 2026-02-16

### Added
- 🇨🇳 **China / 中国影视** section (1st position) — China box office, co-productions, policy, streaming platforms
- 🎞️ **Upcoming Releases / 北美近期上映** section (4th position) — theater openings, release date announcements, scheduling moves
- 6 Reddit sources: r/movies, r/boxoffice, r/television, r/Oscars, r/TrueFilm, r/flicks
- 3 China-specific RSS feeds: THR China, Variety Asia, Deadline China
- Reddit pipeline step in digest-prompt

### Changed
- Expanded to 9 topic sections (from 7)
- Total sources: 41 (19 RSS + 11 Twitter + 6 Reddit + Web Search)

## [1.2.0] - 2026-02-16

### Added
- 🇨🇳 China section and RSS feeds
- Reddit data layer (6 subreddits)

## [1.1.0] - 2026-02-16

### Added
- 4 replacement RSS sources: JoBlo, FirstShowing.net, ComingSoon.net, World of Reel

### Changed
- Improved production topic search queries (greenlit, sequel, filming keywords)
- Enforce all topic sections appear in report (min 1 item)
- Hardcode section order in digest-prompt (production → deals first)
- Cross-section deduplication rule

### Fixed
- Disabled broken RSS feeds: Vulture (404), Screen Daily (404), EW (403)

## [1.0.0] - 2026-02-16

### Added
- Initial release
- 15 RSS feeds: THR, Deadline, Variety, Screen Daily, IndieWire, The Wrap, Collider, Vulture, Awards Daily, Gold Derby, Screen Rant, Empire, The Playlist, EW, /Film
- 13 Twitter/X KOLs
- 7 topic sections: Box Office, Streaming, Production, Awards, Deals, Festivals, Reviews
- Pipeline scripts (fetch-rss, fetch-twitter, fetch-web, merge-sources)
- Discord + email templates
- Chinese body text with English source links
- Cron-ready digest-prompt.md template
