# spotify-claw

Full-featured Spotify skill for OpenClaw agents. Controls playback, analyzes your music taste, builds smart playlists — all via Spotify Web API.

---

## Why I built this

I'm a music person. Always have been. When I set up my OpenClaw agent, the existing Spotify skills felt too basic — play/pause, that's it. I wanted my agent to actually *know* my taste.

So I built this for myself. The result: an agent that understands my genre profile, can dig through my 480+ liked songs to find everything by a specific artist, builds playlists from my actual top tracks in one command, and discovers new music without relying on Spotify's broken Recommendations API (they killed it for new developer apps).

If you care about music and want your agent to feel like it genuinely gets what you listen to — this is for you.

---

## Why this over other Spotify skills?

| Feature | spotify-claw | spotify-player | spoticlaw |
|---|---|---|---|
| Auto-launch app if closed | ✅ | ❌ | ❌ |
| Music taste analysis | ✅ | ❌ | ❌ |
| Smart discovery (no Recs API) | ✅ | ❌ | ❌ |
| One-command playlist builder | ✅ | ❌ | ❌ |
| Liked songs by artist | ✅ | ❌ | ❌ |
| Genre profile | ✅ | ❌ | partial |
| macOS Keychain (no plaintext secrets) | ✅ | ❌ | ❌ |
| device_id everywhere (no "no active device") | ✅ | ❌ | ❌ |

### Key differentiators

**1. Auto-launch**
When Spotify is closed, `play` automatically opens the app, waits for initialization, and starts playback. No manual intervention needed.

**2. Works around Spotify's broken Recommendations API**
Spotify deprecated `recommendations` and `audio_features` for new apps (403/404). This skill uses a manual approach:
- Related artists via `artist_related_artists`
- Genre-based search
- Top tracks per artist
- All combined in the `discover` command

**3. Music taste analysis**
- Genre profile breakdown (trip-hop 18%, post-punk 12%...)
- Liked songs analysis: popularity buckets (underground/indie/mainstream), decades, top artists
- Compare taste across 3 time periods (4 weeks / 6 months / all time)

**4. Smart playlist commands**
- `make-playlist "Name" short 20` — creates + fills a playlist from your top tracks in one command
- `discover "Placebo"` — finds artists similar to your favorites, pulls their best tracks
- `liked-by-artist "Artist Name"` — surfaces all liked songs by one artist

---

## Requirements

- Spotify Premium account
- macOS (uses Keychain for credentials)
- Python 3.9+
- spotipy: `pip3 install spotipy --break-system-packages`

---

## Setup

### 1. Create Spotify App
Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard):
- Create app
- Add redirect URI: `http://127.0.0.1:8888/callback`
- Copy Client ID and Client Secret

### 2. Add credentials to Keychain
```bash
security add-generic-password -a openclaw -s openclaw.spotify.client_id -w "YOUR_CLIENT_ID"
security add-generic-password -a openclaw -s openclaw.spotify.client_secret -w "YOUR_CLIENT_SECRET"
```

### 3. First auth (one-time)
```bash
python3 scripts/spotify.py now
```
Browser opens → log in → authorize → done. Token cached at `~/.openclaw/.spotify_cache`.

---

## Commands

### Playback
```bash
play                              # resume
play "track name"                 # search and play
play spotify:track:URI            # play by URI
play spotify:playlist:ID          # play playlist
pause
next
prev
volume 70 / volume up / volume down
shuffle on / shuffle off
devices
queue "track name"
now                               # currently playing
```

### Library & Analysis
```bash
top-tracks [short|medium|long] [limit]   # your top tracks
top-artists [short|medium|long] [limit]  # your top artists
recent [limit]                           # recently played
liked [limit]                            # liked songs (first N)
liked-all                                # all liked songs
liked-by-artist "Artist Name"            # liked by specific artist
genres [short|medium|long]               # genre breakdown
playlists                                # list your playlists
```

### Smart Discovery
```bash
discover                          # explore new music by your genre profile
discover "Artist" [depth] [n]    # expand from specific artist
related-artists "Artist" [limit] # similar artists
artist-top-tracks "Artist" [n]  # top tracks of any artist
```

### Playlist Builder
```bash
make-playlist "Name" [short|medium|long] [limit]  # create from top tracks
create-playlist "Name" ["Description"]             # empty playlist
add-to-playlist PLAYLIST_ID URI [URI...]           # add tracks
search "query" [track|artist|album] [limit]        # search
track-info URI [URI...]                            # track details
```

---

## How it works

### Authentication
Reads `SPOTIPY_CLIENT_ID` / `SPOTIPY_CLIENT_SECRET` from macOS Keychain (`security find-generic-password`). Falls back to environment variables. Token cached at `~/.openclaw/.spotify_cache`.

### Auto-launch
Before any playback command, `ensure_active_device()` checks for available devices. If none found:
1. Runs `open -a Spotify`
2. Polls for device every 2.5 seconds (3 attempts)
3. Extra 2s wait after detection for full initialization
4. Returns `device_id` passed explicitly to all API calls

All playback commands (`play`, `pause`, `next`, `prev`, `volume`, `queue`, `shuffle`) use explicit `device_id` — avoids the common "No active device" error.

### Discovery without Recommendations API
Since Spotify blocked `recommendations` for new developer apps:
```
your top artists → related_artists() → their top tracks → filter unseen
```
Configurable depth (how many hops from seed artist) and tracks per artist.

### User ID
Fetched lazily via `sp.me()["id"]` on first use. Cached in-process. No hardcoding.
