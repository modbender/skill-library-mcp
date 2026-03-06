---
name: mal-lookup
version: 1.3.0
description: Direct MyAnimeList lookup tool. Bypasses Jikan/API issues by using MAL's internal endpoints.
metadata:
  openclaw:
    emoji: "🎌"
    requires:
      bins: ["curl", "jq", "grep", "awk"]
    tags: ["anime", "manga", "mal", "search", "list"]
---

# MAL Lookup

Directly query MyAnimeList.net to search for anime/manga or retrieve user lists.
This skill uses MAL's internal `load.json` and `prefix.json` endpoints.

## Usage

**Search:**
`mal search anime "frieren"`
`mal search manga "berserk"`

**Advanced Search (Genre + Score):**
`mal advanced action 8` (Top Action anime with score > 8)
`mal advanced psychological 0` (All Psychological anime sorted by score)

**Get User List:**
`mal list anime zun43d`
`mal list manga zun43d reading`

**Charts:**
`mal top` (Top Airing Anime)
`mal season 2024 spring` (Seasonal Chart)

## Commands

| Command | Description |
|---------|-------------|
| `mal search <type> <query>` | Search for anime/manga by title. |
| `mal advanced <genre> [min]` | Search anime by genre and minimum score. |
| `mal list <type> <user> [status]` | Fetch a user's list. |
| `mal top` | Get top 10 currently airing anime. |
| `mal season <year> <season>` | Get top 10 anime from a specific season. |

### Supported Genres
action, adventure, comedy, drama, sci_fi, mystery, psychological, thriller, romance, slice_of_life, horror, fantasy, sports, mecha, music...
