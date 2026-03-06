---
name: apple-music-dj
description: >
  Ultimate personalization engine for Apple Music. Analyzes listening history, Apple Music Replay
  stats, library data, and taste patterns to create intelligent playlists directly in the user's
  Apple Music library via the MusicKit API. Supports deep cuts discovery, mood/activity playlists,
  trend scouting, constellation discovery ("surprise me"), playlist refresh/evolution,
  automated weekly curation via cron, taste DNA cards, compatibility scoring, listening insights,
  catalog gap analysis, album deep dives, artist rabbit holes, daily song drops, concert prep,
  and personalized new release radar. Use this skill whenever the user mentions Apple Music,
  playlists, music recommendations, listening habits, music taste, "what should I listen to",
  discovering new music, mood playlists, workout playlists, deep cuts, hidden gems, trending music,
  "surprise me", refreshing a playlist, or anything related to curating their music experience.
  Also trigger on: "DJ", "mix", "playlist for", "music for", "songs like", "similar to",
  "what's hot", "new releases for me", "taste DNA", "taste card", "compatibility", "how compatible",
  "year in review", "listening stats", "what have I missed", "album deep dive", "rabbit hole",
  "concert prep", "seeing [artist] live", "daily song", "what should I listen to right now",
  or OpenClaw in the context of music.
version: 3.1.0
emoji: 🎧
author: Andernet (Matthew Anderson) <and3rn3t@icloud.com>
homepage: https://github.com/and3rn3t/apple-music-dj
license: MIT
tags:
  - music
  - apple-music
  - playlists
  - personalization
  - musickit
  - discovery
category: music
icon: assets/icon.svg
metadata:
  openclaw:
    requires:
      env:
        - APPLE_MUSIC_DEV_TOKEN
        - APPLE_MUSIC_USER_TOKEN
      bins:
        - curl
        - jq
        - python3
    primaryEnv: APPLE_MUSIC_DEV_TOKEN
    platforms:
      - macos
      - linux
    minVersion: "1.0.0"
    permissions:
      - network
      - filesystem
---

# Apple Music DJ 🎧

An intelligent Apple Music personalization engine for OpenClaw. Reads your listening history,
Replay stats, ratings, and library to build a deep taste profile — then generates playlists
using five strategies, surfaces insights about your listening, and writes everything directly
to your Apple Music library. Also includes shareable Taste DNA Cards, compatibility scoring,
catalog gap analysis, album deep dives, artist rabbit holes, daily song drops, concert prep
playlists, and personalized new release radar.

## Architecture

```
User Request
     │
     ▼
┌─────────────┐    ┌──────────────────────────────────────────────┐
│  Taste       │◄──│  Apple Music API (read)                      │
│  Profiler    │    │  · recently played    · library songs/artists│
│  (cached)    │    │  · heavy rotation     · ratings (loved/hated)│
│              │    │  · recommendations    · Replay summaries     │
└──────┬───────┘    └──────────────────────────────────────────────┘
       │
       ▼
┌─────────────┐    ┌──────────────────────────────────────────────┐
│  Strategy    │───▶│  Apple Music API (catalog)                   │
│  Engine      │    │  · search · charts · artist albums/top songs │
│              │    │  · genres · new releases                     │
└──────┬───────┘    └──────────────────────────────────────────────┘
       │
       ▼
┌─────────────┐    ┌──────────────────────────────────────────────┐
│  Playlist    │───▶│  Apple Music API (write)                     │
│  Builder     │    │  · POST /me/library/playlists                │
│              │    │  · POST /me/library/playlists/{id}/tracks     │
└─────────────┘    └──────────────────────────────────────────────┘
```

## Prerequisites

Two environment variables must be set. If the user doesn't have them, walk them through
`references/auth-setup.md` before doing anything else.

| Variable | Purpose |
|---|---|
| `APPLE_MUSIC_DEV_TOKEN` | JWT signed with MusicKit private key (Apple Developer portal) |
| `APPLE_MUSIC_USER_TOKEN` | Per-user authorization token (obtained via MusicKit JS `authorize()`) |

Verify with: `scripts/apple_music_api.sh verify`

## Taste Profiling

Before generating any playlist, build (or load from cache) a taste profile.

Run: `python3 scripts/taste_profiler.py [--cache ~/.apple-music-dj/taste_profile.json] [--max-age 0] [--storefront us]`

Use `--max-age 0` to force a refresh, bypassing any cached profile.

The profiler pulls from **all available data sources**:

| Source | Endpoint | Signal |
|---|---|---|
| Loved/disliked songs | `GET /v1/me/ratings/songs` | ★★★★★ Explicit intent |
| Heavy rotation | `GET /v1/me/history/heavy-rotation` | ★★★★☆ Repeated engagement |
| Recently played | `GET /v1/me/recent/played/tracks` | ★★★★☆ Current mood |
| Replay summaries | `GET /v1/me/music-summaries` | ★★★★☆ Annual deep data |
| Library songs | `GET /v1/me/library/songs?include=catalog` | ★★★☆☆ Broad taste |
| Library artists | `GET /v1/me/library/artists` | ★★★☆☆ Artist affinity |
| Recommendations | `GET /v1/me/recommendations` | ★★☆☆☆ Apple's inference |

**Output:** Taste DNA profile cached at `~/.apple-music-dj/taste_profile.json` (7-day TTL by default).

The profile includes: top artists (weighted), genre distribution, era profile, energy
classification, variety score, loved/disliked IDs, library song IDs, and Replay highlights.

### Sparse Data Handling

If the user has limited history:
1. Check Replay data — covers a full year even if recent history is short
2. Lean on `/me/recommendations`
3. Ask user to name 3–5 artists/songs they love as manual seeds
4. Use catalog search with those seeds to bootstrap

## Playlist Strategies

Five strategies. Read detailed algorithms in `references/playlist-strategies.md`.

### Strategy 1: Deep Cuts Explorer
**Triggers:** "deep cuts", "hidden gems", "B-sides", "underrated", "album tracks"
Find tracks from artists the user loves but hasn't heard yet. Excludes top songs, singles,
and anything in library.

### Strategy 2: Mood / Activity Matcher
**Triggers:** "workout", "chill", "focus", "party", "sleep", "cooking", "driving",
"running", "morning", "sad", "study", "dinner" — any mood/activity word.
Maps mood to musical attributes, filters through user's taste.

### Strategy 3: Trend Radar
**Triggers:** "trending", "what's hot", "charts", "popular", "new releases"
Current charts filtered through user's genre preferences. Includes wildcard picks.

### Strategy 4: Constellation Discovery
**Triggers:** "surprise me", "something new", "expand my taste", "I'm bored", "discovery"
Journey from familiar artists outward to new territory in 3 "rings" of distance.

### Strategy 5: Playlist Refresh / Evolution
**Triggers:** "refresh my [playlist]", "update my [playlist]", "evolve", "getting stale"
Analyzes existing playlist's sonic signature, adds fresh matching tracks, optionally
prunes overplayed songs.

## Engagement Features

Beyond playlist strategies, these features drive daily engagement and deeper music discovery.

### Taste DNA Card
**Triggers:** "taste card", "taste DNA", "share my taste", "my music identity", "listener profile"
Generate a shareable visual card (SVG or text) summarizing the user's taste: archetype label
(e.g., "Deep Catalog Digger", "Genre Drifter"), top genres with bars, top artists, era mix,
and stats (energy, variety, mainstream, velocity).

Run: `python3 scripts/taste_card.py <profile.json> [--format svg|text] [--output card.svg]`

Archetype detection is automatic based on profile data. Always present the text version
in chat; offer to generate the SVG for sharing. The card is designed to be screenshot-friendly.

### Compatibility Score
**Triggers:** "how compatible am I with [artist]", "compatibility", "do I match [artist]",
"compare my taste with", "would I like [artist]"
Score how well the user's taste aligns with an artist's catalog DNA (0-100%).
Also supports comparing two user profiles if both have run the taste profiler.

Run:
- `python3 scripts/compatibility.py artist <profile.json> <storefront> <artist_name>`
- `python3 scripts/compatibility.py profile <profile1.json> <profile2.json>`

Present the percentage, a verdict ("Deeply compatible", "Strong overlap", "Wild card"),
matching genres, and whether the artist is already in their library.

### Listening Insights
**Triggers:** "listening timeline", "how has my taste changed", "listening streaks",
"milestones", "year in review", "my [year] in music", "wrapped", "listening stats"

Three subcommands:

**Timeline:** `python3 scripts/listening_insights.py timeline <profile.json>`
Shows taste evolution across Replay years — top artist, genre, and listen time per year.
Present as a narrative: "In 2022 you were deep into shoegaze, by 2024 you shifted to jazz."

**Streaks:** `python3 scripts/listening_insights.py streaks <profile.json>`
Surfaces milestones (from Replay API) and computed insights: artist loyalty, genre dominance,
discovery rate, library size, rating activity.

**Year in Review:** `python3 scripts/listening_insights.py year-review <profile.json> [--year 2025]`
Comprehensive year analysis — deeper than Apple Replay. Includes obscurity score, variety
analysis, top songs/artists/albums, total listen time, and narrative insights.

### Catalog Gap Analysis
**Triggers:** "what have I missed", "what am I missing from [artist]", "catalog gaps",
"albums I haven't heard", "discography check"
Scans the user's favorite artists' full discographies and identifies albums with zero tracks
in the user's library. Ranks recommendations by release date.

Run: `python3 scripts/catalog_explorer.py gap-analysis <profile.json> <storefront>`

Present as: "You love Radiohead but you've only heard 3 of their 9 albums. Here's what
you're missing, ranked by how much you'd probably like each one."

### Album Deep Dive
**Triggers:** "tell me about [album]", "album deep dive", "what's on [album]",
"should I listen to [album]", "break down [album]"
Pull track listing, classify each track as single vs deep cut, show where the album sits
in the artist's discography, and recommend which deep cuts to try first.

Run: `python3 scripts/catalog_explorer.py album-dive <storefront> <album_name> [--artist <name>]`

### Artist Rabbit Hole
**Triggers:** "rabbit hole from [artist]", "take me on a journey from [artist]",
"artist chain", "explore from [artist]", "where does [artist] lead"
Interactive chain exploration. Starts from one artist, searches for adjacent artists,
maps outward step by step. Each step tagged as familiar/adjacent/frontier zone.
Outputs tracks from each artist for a potential journey playlist.

Run: `python3 scripts/catalog_explorer.py rabbit-hole <profile.json> <storefront> <artist_name> [--depth 4]`

Present each step with the artist name, zone, genres, and sample tracks. Ask if the user
wants to go deeper or turn the exploration into a playlist.

### Daily Song Drop
**Triggers:** "daily song", "song of the day", "give me one track", "daily pick"
One track per day with a one-sentence rationale. Uses a date-based seed for consistency
(same pick all day). Draws from deep cuts and trending tracks scored against the user's taste.

Run: `python3 scripts/daily_pick.py daily <profile.json> <storefront>`

### What Should I Listen To Right Now?
**Triggers:** "what should I listen to", "what should I play", "recommend something now",
"I need music", "play something"
Context-aware instant recommendation. Factors in time of day (morning → gentle indie,
late night → ambient), maps to genre boosts, and scores candidates accordingly.

Run: `python3 scripts/daily_pick.py now <profile.json> <storefront>`

### Concert Prep Playlist
**Triggers:** "seeing [artist] live", "concert prep", "going to [artist] show",
"setlist for [artist]", "get ready for [artist] concert"
Builds a prep playlist: top songs (likely setlist material) + deep cuts to learn before
the show. Creates directly in Apple Music library.

Run: `scripts/concert_prep.sh <storefront> <artist_name> [playlist_name]`

### Personalized New Release Radar
**Triggers:** "new releases", "what's new from my artists", "any new music",
"release radar", "new albums this week"
Scans the user's top 20 artists for releases in the last 7 days, plus searches for
genre-relevant new releases from adjacent artists. Can optionally create a playlist.

Run: `scripts/new_releases.sh <profile.json> <storefront> [--create-playlist]`

## Quick Commands

| User says | Action |
|---|---|
| "Analyze my taste" | Run taste profiler, present Taste DNA report |
| "Show my taste card" | Generate and display Taste DNA Card |
| "Make me a playlist" | Ask what kind, then select strategy |
| "Surprise me" | Constellation Discovery — no questions asked |
| "More like [artist]" | Deep Cuts + Constellation hybrid seeded from named artist |
| "Refresh my workout playlist" | Strategy 5 on the named playlist |
| "What have I been into?" | Present recent listening summary |
| "How compatible am I with [artist]?" | Run compatibility score |
| "What have I missed from [artist]?" | Catalog gap analysis |
| "Tell me about [album]" | Album deep dive |
| "Take me on a rabbit hole from [artist]" | Artist chain exploration |
| "Give me one song" | Daily song drop |
| "What should I listen to right now?" | Context-aware instant pick |
| "I'm seeing [artist] next week" | Concert prep playlist |
| "Any new releases for me?" | Personalized new release scan |
| "My year in review" | Year in review (previous year) |
| "Set up weekly playlists" | Configure cron (see below) |

## Cron / Automated Playlists

OpenClaw has first-class cron and heartbeat support. This skill can automate:

**Weekly Mix** (recommended default):
```
Schedule: Every Sunday at 9:00 AM (user's local time)
Task:
  1. Refresh taste profile cache
  2. Run Trend Radar (15 tracks)
  3. Run Constellation Discovery (10 tracks)
  4. Merge into "Weekly Mix · {date}" playlist
  5. Create in library
  6. Notify user: "🎧 Your weekly mix is ready — 25 fresh tracks"
```

**New Release Watch:**
```
Schedule: Daily at 8:00 AM
Task:
  1. scripts/new_releases.sh <profile> <storefront>
  2. If found: notify user with artist + album/single name
  3. Optionally: --create-playlist to auto-create a playlist
```

**Daily Song Drop:**
```
Schedule: Daily at 9:00 AM
Task:
  1. python3 scripts/daily_pick.py daily <profile> <storefront>
  2. Notify user: "🎧 Today's pick: {song} by {artist} — {reason}"
```

**Playlist Health Check:**
```
Schedule: Weekly (Saturday)
Task:
  1. Scan user's playlists
  2. Flag any tracks removed from Apple Music catalog (404 on lookup)
  3. Suggest replacements
```

When the user asks to set up automation, configure via OpenClaw's cron system and
confirm the schedule with them before activating.

## Assembly Rules

After any strategy produces candidate tracks, apply before creating:

**Sequencing:**
1. Tracks 1–3: Open strong (high-confidence picks)
2. Tracks 4–8: Build energy, introduce variety
3. Tracks 9–15: Peak — best discoveries here
4. Tracks 16–22: Sustain interest, new textures
5. Tracks 23–28: Wind down
6. Final track: Memorable closer, not filler

**Hard rules:**
- Min 5 tracks between same-artist repeats
- Max 2 tracks from same album
- No tracks from disliked artists
- No explicit content unless user's library already has it
- All IDs must be catalog IDs (not library IDs)
- Target: 25–40 tracks unless user specifies otherwise

**Naming:** `{Strategy} · {Context} · {Mon YYYY}`

## Storefront Detection

Catalog endpoints need a storefront code (us, gb, jp...).
Detection order:
1. `APPLE_MUSIC_STOREFRONT` env var → use it
2. `GET /v1/me/storefront` → auto-detect and cache
3. Fall back to `us`, warn user

## Error Handling

| Code | Meaning | Action |
|---|---|---|
| 401 | Dev token invalid/expired | Regenerate JWT. See `references/auth-setup.md` |
| 403 | User token expired (~6mo) | Re-authorize via browser. No refresh flow exists |
| 404 | Resource removed from catalog | Skip, log warning, continue |
| 429 | Rate limited | Exponential backoff: 1s→2s→4s→8s, max 3 retries |
| Empty data | New user or privacy settings | Fall back: Replay → recs → manual seeds |

## Presenting Results

After creating a playlist:
1. ✅ Confirmation with playlist name
2. Brief explanation connecting the curation to their taste
3. Track listing (# · Song · Artist)
4. Offer refinement: "Want me to adjust the energy, swap tracks, or make it longer?"

**Tone:** Music-savvy friend. Be specific about why tracks were chosen.
Say "I noticed you've been deep into shoegaze lately, so I pulled Slowdive deep cuts and
some bands in that orbit" — not "Here's an awesome playlist just for you!"

## Reference Files

| File | Read when... |
|---|---|
| `references/auth-setup.md` | User needs token setup help |
| `references/api-reference.md` | Need endpoint details, formats, genre IDs |
| `references/playlist-strategies.md` | Before executing any playlist strategy |
| `references/troubleshooting.md` | User hits errors, things aren't working |

## Privacy & Data Disclosure

This skill accesses user data through the Apple Music API. Here's exactly what it reads,
stores, and transmits.

**Data read (via Apple Music API):**

| Data | Endpoint | Purpose |
|---|---|---|
| Recently played tracks | `/v1/me/recent/played/tracks` | Current taste signal |
| Heavy rotation | `/v1/me/history/heavy-rotation` | Repeated listening signal |
| Library songs & artists | `/v1/me/library/songs`, `/artists` | Broad taste mapping |
| Ratings (loved/disliked) | `/v1/me/ratings/songs` | Explicit preferences |
| Recommendations | `/v1/me/recommendations` | Apple's inference data |
| Replay summaries | `/v1/me/music-summaries` | Annual listening stats |
| Storefront | `/v1/me/storefront` | Region detection |

**Data stored locally:**

| File | Contents | Location |
|---|---|---|
| Taste profile cache | Aggregated taste data (JSON) | `~/.apple-music-dj/taste_profile.json` |
| Taste DNA Card | Generated SVG image | User-specified output path |

**Data NOT collected:**
- No data is sent to any third-party service
- No analytics or telemetry
- No data leaves the user's machine (all API calls go directly to Apple)
- Tokens are never logged or stored by the skill (env vars only)

**Cache management:**
- Taste profile cache has a 7-day TTL by default
- Cache can be cleared: `rm -rf ~/.apple-music-dj/`
- Use `--max-age 0` to bypass cache and fetch fresh data

## Scripts

| Script | Lang | Purpose |
|---|---|---|
| `scripts/_common.py` | Python | Shared utilities (API calls, profile loading, search) |
| `scripts/apple_music_api.sh` | Bash | API wrapper — all endpoints, retry logic |
| `scripts/taste_profiler.py` | Python | Taste DNA profiler with caching |
| `scripts/build_playlist.sh` | Bash | Playlist creation & refresh (create or add tracks) |
| `scripts/generate_dev_token.py` | Python | Developer JWT generator |
| `scripts/taste_card.py` | Python | Shareable Taste DNA Card (SVG/text) |
| `scripts/compatibility.py` | Python | Taste compatibility scoring (artist or profile) |
| `scripts/listening_insights.py` | Python | Timeline, streaks, milestones, year in review |
| `scripts/catalog_explorer.py` | Python | Gap analysis, album deep dive, artist rabbit hole |
| `scripts/daily_pick.py` | Python | Daily song drop & instant recommendation |
| `scripts/playlist_history.py` | Python | Playlist creation history tracking |
| `scripts/concert_prep.sh` | Bash | Concert prep playlist builder |
| `scripts/new_releases.sh` | Bash | Personalized new release radar |
| `scripts/verify_setup.sh` | Bash | Setup verification (prereqs, tokens, API) |

## Example Interactions

**"I've been in a funk, make me something uplifting"**
→ Strategy 2 (Mood). Target: uplifting energy from their preferred genres.

**"I keep listening to the same 20 songs"**
→ Strategy 4 (Constellation). Start from heavy rotation, expand outward.

**"Make me a running playlist"**
→ Strategy 2 (Activity). 140–180 BPM feel, high energy, filtered through taste.

**"What's trending that I'd actually like?"**
→ Strategy 3 (Trend Radar). Charts filtered through taste fingerprint + wildcards.

**"I love Radiohead and Björk but I've heard everything"**
→ Strategy 1 (Deep Cuts) + Strategy 4 (Constellation) combined.

**"My gym playlist is getting stale"**
→ Strategy 5 (Refresh). Analyze vibe, add fresh tracks, prune overplayed ones.

**"Set me up with weekly auto-playlists"**
→ Cron config. Confirm schedule, set up weekly Trend Radar + Constellation mix.

**"Show me my taste card"**
→ Generate Taste DNA Card. Present text version in chat, offer SVG export.

**"How compatible am I with Tyler, the Creator?"**
→ Compatibility score. Show percentage, verdict, matching genres.

**"What albums am I missing from Radiohead?"**
→ Catalog gap analysis. List unheard albums, recommend starting points.

**"Tell me about In Rainbows"**
→ Album deep dive. Track listing, deep cuts vs singles, discography context.

**"Take me on a rabbit hole from Radiohead"**
→ Artist chain: Radiohead → Talk Talk → Bark Psychosis → Disco Inferno. Offer playlist.

**"Give me one song for today"**
→ Daily song drop. One track, one reason, done.

**"What should I listen to right now?"**
→ Context-aware pick. Time of day + taste → instant recommendation.

**"I'm seeing Phoebe Bridgers next month"**
→ Concert prep playlist. Top songs + deep cuts, created in Apple Music.

**"Any new releases from my artists?"**
→ New release radar. Scan top artists + genre discoveries, report findings.

**"How was my 2025 in music?"**
→ Year in review. Listen time, top artists, obscurity score, narrative insights.
