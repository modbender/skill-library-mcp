---
name: spoticlaw
description: "Spotify Web API client for Nyx agents. Use when interacting with Spotify: search, playback, playlists, library, tracks, artists, albums, shows, podcasts. Requires SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, and a local .spotify_cache token file."
homepage: https://github.com/ledzgio/spoticlaw
metadata: {"clawdbot":{"emoji":"🎵","requires":{"env":["SPOTIFY_CLIENT_ID","SPOTIFY_CLIENT_SECRET","SPOTIFY_REDIRECT_URI"],"files":[".spotify_cache"]},"primaryEnv":"SPOTIFY_CLIENT_ID"}}
---

# Spoticlaw - Spotify Web API Client

A lightweight Spotify Web API client using direct HTTP requests. No Spotipy dependency.

## Quick Start

```bash
# Install dependencies
pip install requests python-dotenv

# Add to path
import sys
sys.path.insert(0, "skills/spoticlaw/scripts")

from spoticlaw import player, search, playlists, library

# Search for music
results = search().query("coldplay", types=["track"], limit=10)

# Play a track
player().play(uris=["spotify:track:..."])

# Manage playlists
playlists().create("My Playlist")
playlists().add_items("playlist_id", ["spotify:track:..."])

# Save to library
library().save(["spotify:track:..."])
```

Or run from the scripts directory:
```bash
cd skills/spoticlaw/scripts
python -c "from spoticlaw import player; player().play(...)"
```

## Required Configuration

Required env vars in agent runtime:
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `SPOTIFY_REDIRECT_URI` (recommended: `http://127.0.0.1:8888/callback`)

Required file:
- `.spotify_cache` (OAuth token cache)

## Authentication

**Security Note:** Tokens never pass through the AI model. Authentication is done locally, and the token file is copied manually to the agent.

### Setup

1. Create a Spotify app at https://developer.spotify.com/dashboard
2. Get `CLIENT_ID` and `CLIENT_SECRET`
3. Add `http://127.0.0.1:8888/callback` as Redirect URI
4. Create `.env` file in your LOCAL machine:

```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

5. Run authentication on your LOCAL machine:

```bash
cd skills/spoticlaw/scripts
pip install -r requirements.txt
python auth.py
```

6. Open the displayed URL in your browser, authorize

7. **Copy the token file to your agent:**

```bash
# Linux/Mac - copy to agent's skill folder
cp .spotify_cache /path/to/agent/skills/spoticlaw/.spotify_cache

# Or if agent is remote, copy via scp, USB, etc.
scp .spotify_cache user@agent:/path/to/skills/spoticlaw/.spotify_cache
```

**That's it!** No token ever touches the AI. The agent just reads the file.

### Token Auto-Refresh

The library automatically handles token refresh **only if the agent has the same app credentials in `.env`**:

- Access token expires after ~1 hour
- On first API call after expiry, it uses `refresh_token` + client credentials to request a new access token
- Requires `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` in the agent environment
- If `.spotify_cache` exists but `.env` is missing/mismatched, refresh fails (`invalid_client`)
- If you get an error, run `python auth.py` locally again and copy updated `.spotify_cache`

For more on Spotify's OAuth flow, see: https://developer.spotify.com/documentation/web-api/tutorials/code-flow

### Required Scopes

The auth.py script requests these scopes:
- `user-read-playback-state` - Read playback state
- `user-modify-playback-state` - Control playback
- `playlist-read-private` - Read private playlists
- `playlist-modify-public` - Modify public playlists
- `playlist-modify-private` - Modify private playlists
- `user-library-read` - Read user library
- `user-library-modify` - Modify user library
- `user-read-recently-played` - Recently played tracks
- `user-top-read` - Top tracks/artists
- `user-follow-read` - Followed artists

---

## Primitives

**Important:** Add the module path and install deps first:
```bash
pip install requests python-dotenv  # Install dependencies

# For agent execution, add to path:
import sys
sys.path.insert(0, "skills/spoticlaw/scripts")
```

### User

```python
from spoticlaw import user

user().me()  # Get current user profile
```

Returns: `{id, display_name, email, country, ...}`

---

### Search

```python
from spoticlaw import search

# Search for tracks
search().query("song name", types=["track"], limit=10)

# Search for artists
search().query("artist name", types=["artist"], limit=10)

# Search multiple types
search().query("coldplay", types=["track", "artist", "album"], limit=10)
```

**Parameters:**
- `q`: Search query string
- `types`: List of types: `track`, `artist`, `album`, `playlist`, `show`, `episode`, `audiobook`
- `limit`: Max 10 results (Spotify limit)
- `offset`: Pagination offset

---

### Tracks

```python
from spoticlaw import tracks

tracks().get("track_id")  # Get single track
tracks().get_multiple(["id1", "id2"])  # Get multiple tracks
```

Returns track metadata: `{name, artists, album, duration_ms, uri, ...}`

---

### Artists

```python
from spoticlaw import artists

artists().get("artist_id")  # Get artist details
artists().get_albums("artist_id", limit=10)  # Get artist albums
```

**Album filters (include_groups):**
- `album`, `single`, `compilation`, `appears_on`

---

### Albums

```python
from spoticlaw import albums

albums().get("album_id")  # Get album details
albums().get_tracks("album_id")  # Get album tracks
```

---

### Shows (Podcasts)

```python
from spoticlaw import shows

shows().get("show_id")  # Get show details
shows().get_episodes("show_id", limit=10)  # Get show episodes
```

---

### Episodes

```python
from spoticlaw import episodes

episodes().get("episode_id")  # Get episode details
```

---

### Playlists

```python
from spoticlaw import playlists, user_playlists

# Get user's playlists
user_playlists().get(limit=50)

# Get playlist details
playlists().get("playlist_id")

# Get playlist tracks
# Note: Each item has 'item' key (not 'track'), e.g. item['item']['name']
# Also can contain episodes (podcasts), not just tracks
playlists().get_items("playlist_id", limit=50)

# Create playlist
playlists().create(name="My Playlist", description="...", public=False)

# Update playlist
playlists().update("playlist_id", name="New Name")

# Add tracks
playlists().add_items("playlist_id", ["spotify:track:...", "spotify:track:..."])

# Remove tracks
playlists().remove_items("playlist_id", ["spotify:track:..."])

# Delete playlist (unfollow)
playlists().delete("playlist_id")
```

---

### Library

```python
from spoticlaw import library

library().save(["spotify:track:..."])  # Save to library
library().remove(["spotify:track:..."])  # Remove from library
library().check(["spotify:track:..."])  # Check if saved, returns [True, False]
```

---

### Player

```python
from spoticlaw import player

# Get playback state
player().get_playback_state()  # Returns {} if nothing playing
player().get_currently_playing()

# Get devices
player().get_devices()  # Returns list of devices with IDs

# Transfer playback to device
player().transfer("device_id", play=True)

# Playback control
player().play(uris=["spotify:track:..."])  # Start playing
player().play(context_uri="spotify:album:...")  # Play album/playlist
player().pause()
player().next()
player().previous()
player().seek(60000)  # Seek to 1:00 (milliseconds)
player().set_volume(80)  # Set volume 0-100

# Queue
player().add_to_queue("spotify:track:...")
player().get_queue()

# Modes
player().set_shuffle(True)
player().set_repeat("off")  # off, track, context

# Recently played
player().get_recently_played(limit=50)
```

---

### Personalisation

```python
from spoticlaw import personalisation

personalisation().get_top("tracks", time_range="medium_term", limit=20)
personalisation().get_top("artists", time_range="long_term", limit=20)

# time_range: short_term (4 weeks), medium_term (6 months), long_term (years)
```

---

### Follow

```python
from spoticlaw import follow

follow().get_followed(limit=50)  # Get followed artists
```

---

## Composite Workflows

The primitives can be mixed and matched to create powerful automations. Here are practical examples:

### Workflow 1: Play a Specific Song

```python
from spoticlaw import search, player

# 1. Search for the song
results = search().query("stairway to heaven", types=["track"], limit=5)
song = results["tracks"]["items"][0]
song_uri = song["uri"]
print(f"Playing: {song['name']} by {song['artists'][0]['name']}")

# 2. Play it
player().play(uris=[song_uri])
```

### Workflow 2: Create Playlist from Search Results

```python
from spoticlaw import search, playlists

# 1. Search for songs
results = search().query("led zeppelin", types=["track"], limit=10)
track_uris = [t["uri"] for t in results["tracks"]["items"][:5]]

# 2. Create playlist
pl = playlists().create("Led Zeppelin Mix", public=False)
playlist_id = pl["id"]

# 3. Add tracks
playlists().add_items(playlist_id, track_uris)
print(f"Created playlist: {pl['name']}")
```

### Workflow 3: Save Album to Library

```python
from spoticlaw import artists, albums, library

# 1. Find artist
artist = search().query("the weeknd", types=["artist"], limit=1)["artists"]["items"][0]

# 2. Get albums
albums_list = artists().get_albums(artist["id"], include_groups="album", limit=5)

# 3. Save first album
album = albums_list["items"][0]
library().save([album["uri"]])
print(f"Saved album: {album['name']}")
```

### Workflow 4: Play Podcast Episode

```python
from spoticlaw import search, shows, player

# 1. Find podcast
podcast = search().query("joe rogan", types=["show"], limit=1)["shows"]["items"][0]
show_id = podcast["id"]

# 2. Get latest episode
episodes = shows().get_episodes(show_id, limit=1)
episode = episodes["items"][0]
episode_uri = episode["uri"]

# 3. Get device and play
devices = player().get_devices()
if devices.get("devices"):
    device_id = devices["devices"][0]["id"]
    player().transfer(device_id, play=True)
    player().play(uris=[episode_uri])
    print(f"Playing: {episode['name']}")
```

### Workflow 5: Transfer Playback and Play

```python
from spoticlaw import player, search

# 1. Get available devices
devices = player().get_devices()
print("Available devices:", [d["name"] for d in devices.get("devices", [])])

# 2. Transfer to phone
if devices.get("devices"):
    device_id = devices["devices"][0]["id"]
    player().transfer(device_id, play=True)
    
    # 3. Search and play
    results = search().query("dream on", types=["track"], limit=1)
    track_uri = results["tracks"]["items"][0]["uri"]
    player().play(uris=[track_uri])
```

### Workflow 6: Get User's Top Artists and Follow One

```python
from spoticlaw import personalisation, search, library

# 1. Get top artists
top = personalisation().get_top("artists", limit=10)
print("Your top artists:")
for i, a in enumerate(top["items"], 1):
    print(f"  {i}. {a['name']}")

# 2. Search for a new artist
new_artist = search().query("tame impala", types=["artist"], limit=1)["artists"]["items"][0]
print(f"\nFound: {new_artist['name']}")

# Note: Follow functionality requires additional scope (not in current scope list)
# Use Spotify app to follow manually
```

### Workflow 7: Build Queue from Album

```python
from spoticlaw import albums, player

# 1. Get album tracks
album_id = "4aawyAB9vmqN3uQ7FjRGTy"  # Example album
tracks = albums().get_tracks(album_id)

# 2. Add all tracks to queue
for track in tracks["items"][:5]:  # First 5 tracks
    player().add_to_queue(track["uri"])

print("Added 5 tracks to queue")
```

### Workflow 8: Check Library for Multiple Tracks

```python
from spoticlaw import library, search

# 1. Search for tracks
results = search().query("classic rock", types=["track"], limit=20)
track_uris = [t["uri"] for t in results["tracks"]["items"]]

# 2. Check which are in library
saved = library().check(track_uris)

# 3. Show results
for i, (track, is_saved) in enumerate(zip(results["tracks"]["items"], saved)):
    status = "✓ saved" if is_saved else "○ not saved"
    print(f"{i+1}. {track['name']} - {status}")
```

### Workflow 9: Get Recently Played and Save One

```python
from spoticlaw import player, library

# 1. Get recently played
recent = player().get_recently_played(limit=10)

print("Recently played:")
for i, item in enumerate(recent["items"], 1):
    track = item["track"]
    print(f"  {i}. {track['name']} - {track['artists'][0]['name']}")

# 2. Save the first one
if recent["items"]:
    track_uri = recent["items"][0]["track"]["uri"]
    library().save([track_uri])
    print(f"\nSaved: {recent['items'][0]['track']['name']}")
```

### Workflow 10: Play from Playlist

```python
from spoticlaw import playlists, player

# 1. Get user's playlists
my_playlists = user_playlists().get(limit=10)

print("Your playlists:")
for p in my_playlists["items"]:
    print(f"  - {p['name']} ({p['tracks']['total']} tracks)")

# 2. Pick first playlist and play
if my_playlists["items"]:
    playlist_id = my_playlists["items"][0]["id"]
    # Get device first
    devices = player().get_devices()
    if devices.get("devices"):
        player().transfer(devices["devices"][0]["id"], play=True)
        
        # Play playlist
        player().play(context_uri=f"spotify:playlist:{playlist_id}")
        print(f"Playing: {my_playlists['items'][0]['name']}")
```

---

## Error Handling

```python
from spoticlaw import player, SpotifyException

try:
    player().play(uris=["spotify:track:..."])
except SpotifyException as e:
    if "NO_ACTIVE_DEVICE" in str(e):
        print("No device found. Open Spotify and try again.")
    elif "Invalid token" in str(e):
        print("Token expired. Re-authenticate: python auth.py")
    else:
        print(f"Error: {e}")
```

---

## Common Issues

| Error | Solution |
|-------|----------|
| `No token. Re-authenticate.` | Run `python auth.py` |
| `The access token expired` | Should auto-refresh. If not, run `python auth.py` |
| `Insufficient client scope` | Re-auth with more scopes |
| `NO_ACTIVE_DEVICE` | Open Spotify app, then retry |
| `Invalid limit` | Use max 10 for search, 50 for playlists |
| `Resource not found` | Invalid ID or item unavailable |

---

## API Limits

- **Search:** max 10 results
- **Playlist items:** max 50
- **Pagination:** Use `offset` parameter
- **Player:** Requires active Spotify session

---

## Files

- `scripts/spoticlaw.py` - Main API client
- `scripts/auth.py` - Authentication helper
- `scripts/requirements.txt` - Dependencies

---

## More Info

For setup, troubleshooting, and contributions:
https://github.com/your-org/spoticlaw
