---
name: spotify-claw
description: "Full Spotify Premium control + music analysis. Playback: play/pause/next/prev/volume/shuffle/queue. Analysis: top tracks, top artists, liked songs, genre profile, taste breakdown. Discovery: find similar artists & music without Recommendations API. Playlist builder: make-playlist, liked-by-artist, discover. Auto-launches Spotify if closed. Credentials via macOS Keychain. Triggers: play music, pause, next track, what's playing, top tracks, playlist, genres, similar music, open spotify."
homepage: https://github.com/mixx85/spotify-claw
metadata:
  {
    "openclaw":
      {
        "emoji": "🎵",
        "requires": { "bins": [] },
        "install":
          [
            {
              "id": "pip",
              "kind": "pip",
              "package": "spotipy",
              "label": "Install spotipy (pip)",
            },
          ],
      },
  }
---

# spotify-claw

Full Spotify Premium control with music analysis and smart discovery.

> **ALWAYS run `python3 ~/.openclaw/scripts/spotify.py [cmd]`** — never respond with text only.

---

## Setup (first time)

1. Create app at [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
   — Add redirect URI: `http://127.0.0.1:8888/callback`

2. Add to macOS Keychain:
```bash
security add-generic-password -a openclaw -s openclaw.spotify.client_id -w "CLIENT_ID"
security add-generic-password -a openclaw -s openclaw.spotify.client_secret -w "CLIENT_SECRET"
```

3. First auth — run `now`, browser opens, log in once:
```bash
python3 ~/.openclaw/scripts/spotify.py now
```

---

## Playback Commands

```bash
python3 ~/.openclaw/scripts/spotify.py play                          # resume
python3 ~/.openclaw/scripts/spotify.py play "track name"             # search & play
python3 ~/.openclaw/scripts/spotify.py play spotify:track:URI        # by URI
python3 ~/.openclaw/scripts/spotify.py play spotify:playlist:ID      # playlist
python3 ~/.openclaw/scripts/spotify.py pause
python3 ~/.openclaw/scripts/spotify.py next
python3 ~/.openclaw/scripts/spotify.py prev
python3 ~/.openclaw/scripts/spotify.py volume 70
python3 ~/.openclaw/scripts/spotify.py volume up
python3 ~/.openclaw/scripts/spotify.py volume down
python3 ~/.openclaw/scripts/spotify.py shuffle on
python3 ~/.openclaw/scripts/spotify.py shuffle off
python3 ~/.openclaw/scripts/spotify.py queue "track name"
python3 ~/.openclaw/scripts/spotify.py now
python3 ~/.openclaw/scripts/spotify.py devices
```

**Auto-launch:** If Spotify is closed, `play` opens the app automatically, waits for init, then plays.

---

## Analysis Commands

```bash
python3 ~/.openclaw/scripts/spotify.py top-tracks [short|medium|long] [limit]
python3 ~/.openclaw/scripts/spotify.py top-artists [short|medium|long] [limit]
python3 ~/.openclaw/scripts/spotify.py recent [limit]
python3 ~/.openclaw/scripts/spotify.py liked [limit]
python3 ~/.openclaw/scripts/spotify.py liked-all
python3 ~/.openclaw/scripts/spotify.py liked-by-artist "Artist Name"
python3 ~/.openclaw/scripts/spotify.py genres [short|medium|long]
python3 ~/.openclaw/scripts/spotify.py playlists
python3 ~/.openclaw/scripts/spotify.py search "query" [track|artist|album] [limit]
python3 ~/.openclaw/scripts/spotify.py track-info URI
```

Periods: `short` = 4 weeks · `medium` = 6 months · `long` = all time

---

## Discovery & Playlist Builder

```bash
# Find new music by genre profile
python3 ~/.openclaw/scripts/spotify.py discover

# Expand from specific artist (depth=hops, n=tracks per artist)
python3 ~/.openclaw/scripts/spotify.py discover "Portishead" 3 3

# Related artists
python3 ~/.openclaw/scripts/spotify.py related-artists "The Cure" 10

# Top tracks of any artist
python3 ~/.openclaw/scripts/spotify.py artist-top-tracks "Massive Attack" 5

# Create playlist from top tracks (one command: creates + fills)
python3 ~/.openclaw/scripts/spotify.py make-playlist "Top March 2026" short 20

# Manage playlists
python3 ~/.openclaw/scripts/spotify.py create-playlist "My Playlist" "Description"
python3 ~/.openclaw/scripts/spotify.py add-to-playlist PLAYLIST_ID URI1 URI2
```

> **Note:** Spotify's `recommendations` and `audio_features` APIs are blocked for new developer apps (return 403/404). This skill uses `related_artists` + `artist_top_tracks` for discovery instead.

---

## Agent Tips

- Use `playlists` to list user's playlists with IDs before playing one
- Use `now` to confirm what's playing after a `play` command
- Use `liked-by-artist` to find tracks for a themed playlist
- Chain: `related-artists` → `artist-top-tracks` → `add-to-playlist` for smart playlist building
- `genres long` gives the most accurate taste profile
