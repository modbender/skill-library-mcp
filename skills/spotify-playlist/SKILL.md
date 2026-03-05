---
name: spotify-playlist
description: Build and manage Spotify playlists from natural language requests. Search tracks/artists/albums, create playlists, manage tracks, view listening history. Use when the user asks to create a playlist, find music, check what they've been listening to, or any Spotify-related request. Examples - "make me a playlist for a rainy Sunday", "what have I been listening to lately", "find songs like Bonobo".
---

# Spotify Playlist Builder

Build playlists from natural language using the Spotify Web API.
Updated for the February 2026 API changes (Dev Mode).

## Prerequisites

- Spotify Premium account (required for Dev Mode apps since Feb 2026)
- Python 3 with `requests` library

## Setup

1. Create an app at https://developer.spotify.com/dashboard
2. Set redirect URI to `http://127.0.0.1:8765/callback` (must be `127.0.0.1`, not `localhost` - Spotify blocks `localhost`)
3. Run auth:

```bash
python3 scripts/auth.py --client-id <ID> --client-secret <SECRET>
```

4. Open the printed URL in a browser and authorize
5. If the callback page loads automatically, done. Otherwise copy the full redirect URL and run:

```bash
python3 scripts/auth.py --client-id <ID> --client-secret <SECRET> --code-url "<FULL_REDIRECT_URL>"
```

Tokens are saved to `~/.openclaw/workspace/config/.spotify-tokens.json` and auto-refresh on 401.

## API Script Reference

All commands in `scripts/spotify.py`. All output JSON.

```bash
# Search (tracks, artists, or albums)
python3 scripts/spotify.py search "bohemian rhapsody" --limit 5
python3 scripts/spotify.py search "Bonobo" --type artist --limit 3
python3 scripts/spotify.py search "Moon Safari" --type album --limit 3

# Create playlist
python3 scripts/spotify.py create "Rainy Sunday" --description "Chill vibes" --private

# Add/remove tracks (by Spotify URI)
python3 scripts/spotify.py add <playlist_id> spotify:track:xxx spotify:track:yyy
python3 scripts/spotify.py remove <playlist_id> spotify:track:xxx

# List playlists
python3 scripts/spotify.py my-playlists --limit 10

# View playlist contents
python3 scripts/spotify.py playlist-tracks <playlist_id> --limit 50

# Listening history
python3 scripts/spotify.py top-tracks --time-range short --limit 20
python3 scripts/spotify.py recently-played --limit 20

# Profile
python3 scripts/spotify.py me
```

## Playlist Building Workflow

When a user asks for a playlist:

1. **Interpret the request** - extract mood, genre, era, activity, or specific artists/songs
2. **Search for tracks** - use multiple targeted searches to find tracks matching the vibe
3. **Use listening history** - check `top-tracks` and `recently-played` to personalize if relevant
4. **Create and populate** - create the playlist with a creative name and description, add 15-30 tracks
5. **Share the link** - return the Spotify URL

### Tips

- Run multiple searches with different angles (artist names, genre keywords, era + mood combos)
- Mix well-known tracks with deeper cuts for a good playlist feel
- `top-tracks --time-range short` shows what the user's been into recently (last 4 weeks)
- `top-tracks --time-range long` shows all-time favourites
- Aim for 15-30 tracks unless the user specifies otherwise
- Name playlists creatively based on the vibe, not just the literal request

## Feb 2026 API Limitations (Dev Mode)

- **Recommendations endpoint removed** - build playlists via search + curation instead
- **No popularity field** on some responses - may return 0
- **Playlist endpoints renamed** from `/tracks` to `/items` (already handled in scripts)
- **Premium required** for the app owner
- **Max 5 users** per app, 1 app per developer
- **No batch endpoints** for albums/artists/tracks (use individual lookups)

## Cron Ideas

Combine with OpenClaw cron for automated playlists:

- **Weekly refresh** - build a new playlist every Monday based on a rotating theme
- **Time-of-day playlists** - morning focus, afternoon energy, evening wind-down
- **Commute playlist** - auto-build a playlist matched to journey duration
- **Weather-reactive** - check weather, adjust playlist mood accordingly
