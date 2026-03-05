# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] — 2026-03-02

### Added

- **Python 3.9+ compatibility** — removed `X | Y` union syntax, works on 3.9, 3.11, and 3.13
- **Genre filter** — `filter_generic_genres()` strips generic "Music" tag from taste data
- **Token expiry warning** — `check_token_expiry()` warns when dev token is near expiration
- **Playlist deduplication** — playlist health checker detects and removes duplicate tracks
- **Storefront auto-detection** — `get_storefront()` resolves storefront from env, cache, or API
- **verify_setup overhaul** — improved output, token validation, and connectivity checks
- **Playlist history** — `playlist_history.py` tracks created playlists with freshness checking
- **clawhub.json** — skill metadata for OpenClaw skill registry
- **Test coverage to 87%** — 431 tests across 12 modules (up from 156 tests / 5 modules)
- **New test suites** — `generate_dev_token`, `playlist_health`, `playlist_history`, `setup_cron`
- **GitHub Actions CI** — Python 3.9/3.11/3.13 matrix with 80% coverage gate
- **Makefile** — `make test`, `make coverage`, `make coverage-html` commands
- **`.env.example`** — template for required environment variables

### Changed

- **README.md** — full rewrite with badges, feature list, quick start, and development section
- **pyproject.toml** — added classifiers, project URLs, `pytest-cov` dev dependency
- **CONTRIBUTING.md** — updated Python version requirement to 3.9+
- **`.gitignore`** — expanded to cover `coverage_html/`, `node_modules/`, `.coverage`

## [3.0.0] — 2026-02-24

### Added

- **Taste DNA Card** — shareable SVG/text visual of listener identity and archetype (`taste_card.py`)
- **Compatibility Score** — taste match percentage against any artist or another user (`compatibility.py`)
- **Listening Insights** — timeline, streaks, milestones, and year-in-review (`listening_insights.py`)
- **Catalog Gap Analysis** — find missing albums from favorite artists (`catalog_explorer.py`)
- **Album Deep Dive** — track-by-track breakdown with singles vs deep cuts (`catalog_explorer.py`)
- **Artist Rabbit Hole** — chain exploration from one artist outward (`catalog_explorer.py`)
- **Daily Song Drop** — one perfect track per day with rationale (`daily_pick.py`)
- **What Should I Listen To Right Now?** — time-of-day-aware instant pick (`daily_pick.py`)
- **Concert Prep Playlist** — top songs + deep cuts for upcoming shows (`concert_prep.sh`)
- **New Release Radar** — personalized scan of new releases (`new_releases.sh`)
- **Shared module** — `_common.py` with `call_api`, `load_profile`, `require_env_tokens`, search helpers
- **Test suite** — 156 pytest unit tests across 5 modules (taste_profiler, compatibility, daily_pick, taste_card, _common)
- **pyproject.toml** — project metadata, pytest config, Python 3.10+ requirement
- **Skill icon** — SVG icon for OpenClaw skill listing
- New API commands: `artist-detail`, `album-tracks`, `song-detail`, `library-playlists` in `apple_music_api.sh`
- Exponential backoff retry logic (429 rate limit handling) in `apple_music_api.sh`
- Heavy rotation and recommendations track extraction in taste profiler
- Library song IDs extraction (with catalog ID preference) in taste profiler
- Cron support for daily song drops and new release watch
- 12 new trigger phrases in SKILL.md

### Changed

- **SKILL.md** — version bumped to 3.0.0, expanded with all engagement features
- `taste_profiler.py` — `call_api()` now accepts `raw=True` for non-JSON outputs
- `taste_profiler.py` — fixed `detect_storefront()` to use raw API mode
- Cache TTL documented as 7-day (was incorrectly stated as 24h)
- Artist repeat gap corrected to 5 tracks (was documented as 4)
- CLI flags updated: `--cache` + `--max-age 0` replaces `--force-refresh`
- Python minimum version updated to 3.10+ (uses `X | Y` union type syntax)
- CONTRIBUTING.md updated with test instructions and corrected Python version

### Fixed — Code Quality (30 issues)

- Extracted shared `_common.py` module — eliminated duplicated API/profile code across 5 scripts
- `score_candidate()` now accepts `rng` as keyword argument (was positional-only, caused crash)
- `genre_evolution` in `extract_replay_highlights()` used wrong data field
- Hardcoded year 2026 replaced with dynamic `datetime.now().year`
- Double-seeded RNG in `cmd_daily` — seeded `random.Random` was passed correctly
- `KeyError` → `.get()` protection across all scripts
- Progress indicators added (stderr) for long-running API operations
- `while read` loops replaced unsafe `for` loops in bash scripts (whitespace safety)
- `grep -qxF` for exact dedup matching in `concert_prep.sh`

### Fixed — Error Handling (25 issues)

- `call_api` propagates stderr from failed API calls
- `score_candidate` signature crash on missing keyword arg
- `build_playlist.sh` checks return codes from API calls
- Environment variable validation via `require_env_tokens()` before any API usage
- Network error detection and user-friendly messages
- Year validation (2015–current) in listening insights
- `JSONDecodeError` reports line/column only (no content leak)

### Fixed — Security (15 issues)

- Tokens passed via `curl -K` config files instead of CLI arguments (prevents `ps aux` exposure)
- Token echo truncated to first 20 chars in verify_setup
- File permissions set to `0o600` for all generated files (cache, cards, config)
- `$TMPDIR` used for temporary files instead of predictable paths
- `.clawignore` expanded: `.env.*` wildcard, tests/, dev artifacts
- Input validation added for all user-supplied arguments (ratings, limits, storefronts)
- `JSONDecodeError` handler no longer leaks file content in error messages

### Fixed

- `disliked_artist_ids` renamed to `disliked_song_ids` (matched actual API data)
- Homepage URL pointed to correct GitHub user (`and3rn3t`)
- README strategy count corrected from 4 to 5

## [2.0.0] — 2026-02-23

### Added

- Taste profiler with 7 data sources (recently played, heavy rotation, library, ratings, recommendations, Replay)
- 5 playlist strategies: Deep Cuts, Mood/Activity, Trend Radar, Constellation Discovery, Playlist Refresh
- Apple Music API wrapper with 20+ commands
- Playlist builder with direct Apple Music library integration
- Developer token generator (PyJWT)
- Cron support for weekly auto-playlists
- Full reference docs: auth setup, API reference, playlist strategies

## [1.0.0] — 2026-02-22

### Added

- Initial skill scaffold
- Basic Apple Music API integration
- README and SKILL.md
