# Changelog

All notable changes to this project will be documented in this file.

## [0.1.17] - 2026-02-16

### Security

- Fix shell injection vulnerability in SKILL.md curl search commands
- Replace direct URL interpolation with `curl -G --data-urlencode` for all user-supplied query parameters
- Add explicit instruction to never interpolate user input directly into URL strings
- Update all curl examples (search, episode, common patterns, auth) to use safe parameter encoding

## [0.1.16] - 2026-02-14

### Security

- Fix shell injection vulnerability in aria2 RPC JSON construction (add-torrent.sh)
- Add magnet URL format validation before passing to torrent clients
- Replace shell string interpolation with `jq --arg` for safe JSON construction
- Refactor detect-client.sh JSON output to use `jq` instead of heredoc interpolation
- Add CI security pattern check to prevent unsafe curl payload regression

## [0.1.13] - 2026-02-13

### Features

- Search movies and TV shows across 30+ torrent sources
- Filter by quality (480p–2160p), genre, year, rating, language, season/episode
- HDR and Dolby Vision filtering (hdr10, dolby_vision, hdr10plus, hlg)
- Audio codec filtering (AAC, FLAC, Opus, Atmos)
- API key authentication with tiered rate limits (anonymous, free, pro)
- Quality scoring (0–100) based on resolution, codec, seeders, source trust
- Multi-language support (11 languages with accent-insensitive search)
- TMDB metadata enrichment: posters, backdrops, genres, cast, director credits
- Detect installed torrent clients (Transmission, aria2)
- Add magnet links directly to torrent clients
- Download .torrent files or copy magnet links
- OS-specific installation guides for torrent clients (Linux, macOS, Windows/WSL)
- MCP server alternative for Claude Desktop, Cursor, and Windsurf
