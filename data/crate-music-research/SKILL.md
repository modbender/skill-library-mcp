---
name: music-research
description: "AI-powered music research with 92+ tools across 17 sources — MusicBrainz, Bandcamp, Discogs, Genius, Last.fm, Wikipedia, and more. Influence tracing, track verification, playlist building, and publishing."
version: 0.2.3
metadata: '{"openclaw":{"requires":{"env":["ANTHROPIC_API_KEY"],"bins":["npx"]},"primaryEnv":"ANTHROPIC_API_KEY","emoji":"🎵","homepage":"https://github.com/tmoody1973/crate-cli"}}'
---

# Music Research with Crate

You have access to Crate's music research tools via MCP. These tools connect to 17 real music databases and 26 publications. Use them to answer music questions with verified, cited data.

## MCP Server Setup

Add Crate as an MCP server in your configuration:

```json
{
  "mcpServers": {
    "crate": {
      "command": "npx",
      "args": ["-y", "crate-cli", "--mcp-server"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

This exposes all active tools over stdio. Additional API keys unlock more servers (see Optional API Keys below).

## Research Patterns

### Artist Research

Cross-reference multiple sources for comprehensive artist profiles:

1. `musicbrainz_search_artist` — canonical artist ID, discography, relationships
2. `genius_get_artist` — bio, aliases, social links, annotations
3. `lastfm_get_artist_info` — listening stats, similar artists, tags
4. `discogs_search_artist` — label history, pressings, catalog numbers
5. `bandcamp_search` — independent releases, merch, direct-support links
6. `wikipedia_search` — biographical context, career timeline

Always start with MusicBrainz for the canonical ID, then fan out to other sources.

### Influence Tracing

Discover how artists connect through published music criticism:

1. Use `influence_trace_influence` to search 26 publications for co-mentions
2. Results include publication name, critic byline, date, and URL for every connection
3. Use `influencecache_get_path` for cached paths (instant BFS results)
4. Use `influencecache_get_neighbors` to explore an artist's immediate connections
5. The influence graph grows with every query — cached in local SQLite

Always cite the publication and review when presenting influence connections. Every claim needs a URL.

### Track Verification

**CRITICAL: Never invent track names. Always verify tracks exist before presenting them.**

1. `bandcamp_get_artist_tracks` — primary source for independent artists
2. `musicbrainz_search_recording` — primary source for mainstream releases
3. `youtube_search` — fallback verification source
4. If a track cannot be verified against any real database, do not include it

### Vinyl & Collecting

1. `discogs_get_release` — pressing details, labels, catalog numbers, condition notes
2. `discogs_get_master_release` — all versions/pressings of an album
3. `discogs_get_marketplace_stats` — current market prices and trends
4. `collection_add_record` / `collection_search` — manage the user's personal collection

### Playlist Building

1. Research tracks using the sources above — verify every track exists
2. `playlist_create` — create a new playlist
3. `playlist_add_track` — add verified tracks with source URLs
4. `playlist_export_m3u` — export to M3U format for external players
5. Never include a track that hasn't been confirmed against a real database

### Publishing

Share research as public web pages or blog posts:

1. `telegraph_create_page` — instant shareable page, no account needed
2. `telegraph_create_index` — create a living index of all published pages
3. `tumblr_create_post` — post to the user's Tumblr blog with markdown formatting
4. `tumblr_tag_post` — auto-tag posts with artist names and genres
5. Always include citations and source links in published research

## Critical Rules

- **Every claim must be backed by a real data source** — never hallucinate facts, tracks, or connections
- **Influence connections require full attribution**: publication name, critic, date, and URL
- **Verify tracks** against Bandcamp, MusicBrainz, or YouTube before including in any list
- **Cross-reference facts** across multiple sources when possible
- **The influence system searches 26 publications** including Pitchfork, The Wire, Resident Advisor, Stereogum, The Guardian, NPR, NME, Bandcamp Daily, and more

## Available Servers

| Server | Tools | Env Required | Description |
|--------|-------|-------------|-------------|
| MusicBrainz | 6 | — | Artist/release/recording metadata |
| Bandcamp | 7 | — | Independent music, artist tracks |
| Wikipedia | 3 | — | Biographical context |
| YouTube | 6 | — | Video search, audio playback |
| Radio | varies | — | Internet radio streaming |
| News | varies | — | Music news via RSS |
| Collection | 5 | — | Local record collection (SQLite) |
| Playlist | varies | — | Playlist management (SQLite) |
| Influence Cache | 8 | — | Local influence graph (SQLite) |
| Telegraph | 5 | — | Anonymous publishing |
| Last.fm | 7 | `LASTFM_API_KEY` | Scrobbles, similar artists |
| Genius | 8 | `GENIUS_ACCESS_TOKEN` | Lyrics, annotations |
| Discogs | 9 | `DISCOGS_KEY`, `DISCOGS_SECRET` | Vinyl catalog, marketplace |
| Web Search | 4 | `TAVILY_API_KEY` or `EXA_API_KEY` | Publication search |
| Influence | 3 | `TAVILY_API_KEY` or `EXA_API_KEY` | Live influence tracing |
| Tumblr | 5 | `TUMBLR_CONSUMER_KEY`, `TUMBLR_CONSUMER_SECRET` | Blog publishing |
| Memory | 3 | `MEM0_API_KEY` | Persistent user preferences |

## Optional API Keys

Set these environment variables to unlock additional servers:

```
LASTFM_API_KEY        — Last.fm listening stats and similar artists
GENIUS_ACCESS_TOKEN   — Lyrics, annotations, and artist bios
DISCOGS_KEY           — Vinyl catalog, labels, and marketplace
DISCOGS_SECRET        — Required with DISCOGS_KEY
TAVILY_API_KEY        — Web search across 26 music publications
EXA_API_KEY           — Neural semantic search for influence tracing
YOUTUBE_API_KEY       — Improved YouTube search results
TUMBLR_CONSUMER_KEY   — Publish research to your Tumblr blog
TUMBLR_CONSUMER_SECRET — Required with TUMBLR_CONSUMER_KEY
MEM0_API_KEY          — Persistent memory across sessions
```

Only `ANTHROPIC_API_KEY` is required. All other servers are optional.
