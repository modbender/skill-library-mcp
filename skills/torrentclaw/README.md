# torrentclaw-skill

**Version:** 0.1.16
**License:** MIT
**Homepage:** https://torrentclaw.com

Search and download movies and TV shows from 30+ torrent sources directly from your AI agent. TorrentClaw aggregates torrents from YTS, EZTV, Knaben, Prowlarr, Bitmagnet, Torrentio, DonTorrent, Torrents.csv and more — enriched with TMDB metadata, quality scoring, and multi-language support.

Compatible with **Claude Code**, **OpenClaw**, **Codex CLI**, **Cline**, **Roo Code**, and any tool supporting the [Agent Skills](https://agentskills.io) specification.

**Alternative:** For Claude Desktop, Cursor, or Windsurf, use the [MCP Server](https://torrentclaw.com/mcp) instead (`npx @torrentclaw/mcp`).

## Features

- Search movies and TV shows across 30+ torrent sources (YTS, EZTV, Knaben, Prowlarr, Bitmagnet, Torrentio, DonTorrent, Torrents.csv, and more)
- Filter by quality (480p–2160p), genre, year, rating, language, audio codec, HDR format, season/episode
- HDR and Dolby Vision filtering (hdr10, dolby_vision) and audio codec filtering (AAC, FLAC, Opus, Atmos)
- Quality scoring (0–100) based on resolution, codec, seeders, source trust
- Multi-language support (11 languages with accent-insensitive search)
- TMDB metadata enrichment: posters, backdrops, genres, cast, director credits
- Detect installed torrent clients (Transmission, aria2) and add magnets directly
- Download .torrent files or copy magnet links
- OS-specific installation guides for torrent clients (Linux, macOS, Windows/WSL)
- API key authentication for higher rate limits (anonymous 30/min, free 120/min, pro 1K/min)

## Install

### Claude Code

```bash
# Personal (all projects)
ln -s /path/to/torrentclaw-skill ~/.claude/skills/torrentclaw

# Or project-specific
ln -s /path/to/torrentclaw-skill .claude/skills/torrentclaw
```

### OpenClaw

```bash
claw skill install torrentclaw
# or from local
ln -s /path/to/torrentclaw-skill ~/.openclaw/skills/torrentclaw
```

### ClawHub

```bash
clawhub install torrentclaw
```

## Usage

```
/torrentclaw "Inception 1080p"
/torrentclaw "Breaking Bad S05E14"
/torrentclaw "best 4K movies 2024"
```

Or just ask naturally:

> "Find me Inception in the best quality"
> "I need Breaking Bad season 5 episode 14"
> "Search for sci-fi movies from 2023 in 4K"

The skill will:
1. Detect your torrent client (Transmission, aria2)
2. Search TorrentClaw across 30+ sources
3. Present results ranked by quality score (0-100)
4. Add best torrent to your client or provide magnet link
5. Show install guide if no client detected

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/detect-client.sh` | Detect Transmission/aria2 and output JSON |
| `scripts/add-torrent.sh` | Add magnet to detected client |
| `scripts/install-guide.sh` | Show OS-specific install instructions |

## API

Public API at `https://torrentclaw.com/api/v1/`.

**Authentication:** Optional. Anonymous usage allows 30 req/min. API keys provide higher limits:
- **Free tier**: 120 req/min, 1,000 req/day
- **Pro tier**: 1,000 req/min, 10,000 req/day

See [references/api-reference.md](references/api-reference.md) for full documentation and [SKILL.md](SKILL.md) for workflow examples.

## Links

- **Website**: https://torrentclaw.com
- **Skill Documentation**: https://torrentclaw.com/skill
- **MCP Server**: https://torrentclaw.com/mcp
- **API Reference**: https://torrentclaw.com/api/docs
- **OpenAPI Spec**: https://torrentclaw.com/api/openapi.json
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **GitHub**: https://github.com/torrentclaw/torrentclaw-skill

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — See [LICENSE](LICENSE) for details.
