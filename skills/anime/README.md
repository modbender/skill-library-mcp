# 🎌 Anime Lookup

[![Version](https://img.shields.io/badge/version-1.0.1-blue.svg)](https://github.com/jeffaf/anime-skill)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A CLI for AI agents to search and lookup anime for their humans. "What's that anime about the elf mage?" — now your agent can answer.

Uses [Jikan](https://jikan.moe) (unofficial MyAnimeList API).

**Built for [OpenClaw](https://github.com/openclaw/openclaw)** — works standalone too.

## Features

- 🔍 Search anime by title
- 📊 Get detailed info (synopsis, score, episodes, genres, studios)
- 📺 Browse current season
- 🏆 View top ranked anime
- 📅 Check upcoming releases
- 🎯 No API key or account required

## Installation

### Via ClawHub
```bash
clawhub install anime
```

### Manual
```bash
git clone https://github.com/jeffaf/anime-skill.git
cd anime-skill
chmod +x scripts/anime
# Add to PATH or symlink
ln -s $(pwd)/scripts/anime /usr/local/bin/anime
```

## Requirements

- `bash`
- `curl`
- `jq`

## Usage

```bash
# Search
anime search "frieren"
anime search "one punch man"

# Get details by MAL ID
anime info 52991

# Current season
anime season

# Top anime
anime top 10

# Upcoming
anime upcoming

# Specific season
anime season 2024 fall
```

## Example Output

```
$ anime search "frieren"
[52991] Sousou no Frieren — 28 eps, Finished Airing, ⭐ 9.28
[59978] Sousou no Frieren 2nd Season — 10 eps, Currently Airing, ⭐ 9.25

$ anime info 52991
🎬 Sousou no Frieren
   English: Frieren: Beyond Journey's End
   MAL ID: 52991 | Score: 9.28 | Rank: #1
   Episodes: 28 | Status: Finished Airing
   Aired: Sep 29, 2023 to Mar 22, 2024
   Genres: Adventure, Drama, Fantasy
   Studios: Madhouse

📖 Synopsis:
During their decade-long quest to defeat the Demon King...
```

## API

Uses [Jikan v4](https://docs.api.jikan.moe/) — an open, free MyAnimeList API.

- Rate limit: 3 requests/second
- No authentication required
- Data sourced from MyAnimeList

## License

MIT
