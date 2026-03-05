#!/usr/bin/env python3
"""
Spotify CLI helper for OpenClaw agents.
Avoids quoting issues in bash — everything via Python.
Reads CLIENT_ID/SECRET from macOS Keychain automatically.

Usage:
  python3 ~/.openclaw/scripts/spotify.py top-tracks [short|medium|long] [limit]
  python3 ~/.openclaw/scripts/spotify.py top-artists [short|medium|long] [limit]
  python3 ~/.openclaw/scripts/spotify.py recent [limit]
  python3 ~/.openclaw/scripts/spotify.py liked [limit]
  python3 ~/.openclaw/scripts/spotify.py playlists
  python3 ~/.openclaw/scripts/spotify.py create-playlist "Name" ["Description"]
  python3 ~/.openclaw/scripts/spotify.py add-to-playlist PLAYLIST_ID TRACK_URI [TRACK_URI ...]
  python3 ~/.openclaw/scripts/spotify.py search "query" [track|artist|album] [limit]
  python3 ~/.openclaw/scripts/spotify.py genres [short|medium|long]
  python3 ~/.openclaw/scripts/spotify.py now
  python3 ~/.openclaw/scripts/spotify.py track-info TRACK_URI [TRACK_URI ...]
  python3 ~/.openclaw/scripts/spotify.py related-artists ARTIST_NAME_OR_ID [limit]
  python3 ~/.openclaw/scripts/spotify.py artist-top-tracks ARTIST_NAME_OR_ID [limit]
  python3 ~/.openclaw/scripts/spotify.py make-playlist "Name" [short|medium|long] [limit]
  python3 ~/.openclaw/scripts/spotify.py discover ARTIST_NAME [depth] [tracks_per_artist]
  python3 ~/.openclaw/scripts/spotify.py liked-all
  python3 ~/.openclaw/scripts/spotify.py liked-by-artist "Artist Name"

Playback (Spotify Premium):
  python3 ~/.openclaw/scripts/spotify.py play
  python3 ~/.openclaw/scripts/spotify.py play "track name"
  python3 ~/.openclaw/scripts/spotify.py play spotify:track:URI
  python3 ~/.openclaw/scripts/spotify.py play playlist PLAYLIST_ID
  python3 ~/.openclaw/scripts/spotify.py pause
  python3 ~/.openclaw/scripts/spotify.py next
  python3 ~/.openclaw/scripts/spotify.py prev
  python3 ~/.openclaw/scripts/spotify.py volume 70
  python3 ~/.openclaw/scripts/spotify.py volume up/down
  python3 ~/.openclaw/scripts/spotify.py devices
  python3 ~/.openclaw/scripts/spotify.py queue "track name"
  python3 ~/.openclaw/scripts/spotify.py shuffle on/off
"""

import sys
import os
import subprocess
import json
import time
from collections import Counter
from pathlib import Path

CACHE_PATH = str(Path.home() / ".openclaw" / ".spotify_cache")
_ME_CACHE = {}  # lazy cache for user id


def get_my_user_id(sp):
    """Returns the current user's ID via API (with in-process caching)."""
    if "id" not in _ME_CACHE:
        _ME_CACHE["id"] = sp.me()["id"]
    return _ME_CACHE["id"]


def _keychain_get(service):
    """Reads a value from macOS Keychain."""
    result = subprocess.run(
        ["security", "find-generic-password", "-a", "openclaw", "-s", service, "-w"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def _setup_env():
    """Sets SPOTIPY_* env vars from Keychain if not already set."""
    if not os.environ.get("SPOTIPY_CLIENT_ID"):
        val = _keychain_get("openclaw.spotify.client_id")
        if val:
            os.environ["SPOTIPY_CLIENT_ID"] = val
    if not os.environ.get("SPOTIPY_CLIENT_SECRET"):
        val = _keychain_get("openclaw.spotify.client_secret")
        if val:
            os.environ["SPOTIPY_CLIENT_SECRET"] = val
    os.environ.setdefault("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
    os.environ.setdefault("SPOTIPY_CACHE_PATH", CACHE_PATH)


_setup_env()

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except ImportError:
    print("ERROR: spotipy not installed. Run: pip3 install spotipy --break-system-packages")
    sys.exit(1)


SCOPES = " ".join([
    "user-read-private",
    "user-read-email",
    "user-top-read",
    "user-read-recently-played",
    "user-library-read",
    "user-library-modify",
    "playlist-read-private",
    "playlist-modify-private",
    "playlist-modify-public",
    # Playback (Premium)
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing",
])


def get_sp():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        cache_path=CACHE_PATH,
        scope=SCOPES,
    ))


PERIOD_MAP = {"short": "short_term", "medium": "medium_term", "long": "long_term"}


def normalize_period(p):
    return PERIOD_MAP.get(p, p if p in ("short_term", "medium_term", "long_term") else "medium_term")


def normalize_uri(uri):
    if uri.startswith("spotify:track:"):
        return uri
    elif uri.startswith("https://open.spotify.com/track/"):
        return "spotify:track:" + uri.split("/track/")[1].split("?")[0]
    else:
        return "spotify:track:" + uri


def find_artist_id(sp, name_or_id):
    """Returns artist_id from artist name or direct ID."""
    # If it looks like an ID (22-char base62) — use directly
    if len(name_or_id) == 22 and name_or_id.replace("_", "").replace("-", "").isalnum():
        return name_or_id
    results = sp.search(q=f"artist:{name_or_id}", type="artist", limit=1)
    items = results["artists"]["items"]
    if not items:
        return None
    return items[0]["id"]


# ─── commands ───────────────────────────────────────────────────────────────

def cmd_top_tracks(args):
    period = normalize_period(args[0] if args else "medium")
    limit = int(args[1]) if len(args) > 1 else 10
    sp = get_sp()
    tracks = sp.current_user_top_tracks(limit=limit, time_range=period)["items"]
    print(f"Top {limit} tracks ({period}):")
    for i, t in enumerate(tracks, 1):
        artists = ", ".join(a["name"] for a in t["artists"])
        print(f"  {i}. {t['name']} — {artists}")
        print(f"     URI: {t['uri']}")


def cmd_top_artists(args):
    period = normalize_period(args[0] if args else "medium")
    limit = int(args[1]) if len(args) > 1 else 10
    sp = get_sp()
    artists = sp.current_user_top_artists(limit=limit, time_range=period)["items"]
    print(f"Top {limit} artists ({period}):")
    for i, a in enumerate(artists, 1):
        genres = ", ".join(a["genres"][:3]) if a["genres"] else "—"
        print(f"  {i}. {a['name']} | {a['id']} | {genres}")


def cmd_recent(args):
    limit = int(args[0]) if args else 20
    sp = get_sp()
    items = sp.current_user_recently_played(limit=limit)["items"]
    print(f"Recently played ({len(items)} tracks):")
    for r in items:
        t = r["track"]
        artists = ", ".join(a["name"] for a in t["artists"])
        played = r["played_at"][:16].replace("T", " ")
        print(f"  {played} — {t['name']} ({artists})")
        print(f"     URI: {t['uri']}")


def cmd_liked(args):
    limit = int(args[0]) if args else 50
    sp = get_sp()
    items = sp.current_user_saved_tracks(limit=min(limit, 50))["items"]
    print(f"Liked songs (first {len(items)}):")
    for item in items:
        t = item["track"]
        artists = ", ".join(a["name"] for a in t["artists"])
        print(f"  {t['name']} — {artists}")
        print(f"     URI: {t['uri']}")


def cmd_liked_all(args):
    """All liked songs with pagination."""
    sp = get_sp()
    liked = []
    offset = 0
    while True:
        batch = sp.current_user_saved_tracks(limit=50, offset=offset)["items"]
        if not batch:
            break
        liked.extend(batch)
        offset += 50
        if len(batch) < 50:
            break
    print(f"Total liked songs: {len(liked)}")
    for item in liked:
        t = item["track"]
        artists = ", ".join(a["name"] for a in t["artists"])
        print(f"  {t['name']} — {artists} | URI: {t['uri']}")


def cmd_liked_by_artist(args):
    """All liked songs by a specific artist."""
    if not args:
        print("ERROR: specify artist name")
        sys.exit(1)
    target = args[0].lower()
    sp = get_sp()
    liked = []
    offset = 0
    while True:
        batch = sp.current_user_saved_tracks(limit=50, offset=offset)["items"]
        if not batch:
            break
        liked.extend(batch)
        offset += 50
        if len(batch) < 50:
            break
    found = []
    for item in liked:
        t = item["track"]
        for a in t["artists"]:
            if target in a["name"].lower():
                found.append(t)
                break
    print(f"Liked tracks by '{args[0]}' ({len(found)}):")
    for t in found:
        artists = ", ".join(a["name"] for a in t["artists"])
        print(f"  {t['name']} — {artists} | URI: {t['uri']}")


def cmd_playlists(args):
    sp = get_sp()
    items = sp.current_user_playlists(limit=50)["items"]
    print(f"Playlists ({len(items)}):")
    for p in items:
        print(f"  [{p['id']}] {p['name']} — {p['tracks']['total']} tracks")


def cmd_create_playlist(args):
    if not args:
        print("ERROR: specify playlist name")
        sys.exit(1)
    name = args[0]
    description = args[1] if len(args) > 1 else ""
    sp = get_sp()
    pl = sp.user_playlist_create(
        user=get_my_user_id(sp),
        name=name,
        public=False,
        description=description
    )
    print(f"Playlist created: {pl['name']}")
    print(f"ID: {pl['id']}")
    print(f"URI: {pl['uri']}")
    print(f"URL: {pl['external_urls']['spotify']}")


def cmd_add_to_playlist(args):
    if len(args) < 2:
        print("ERROR: specify PLAYLIST_ID and TRACK_URI")
        sys.exit(1)
    playlist_id = args[0]
    track_uris = [normalize_uri(u) for u in args[1:]]
    sp = get_sp()
    # Add in batches of 100 (API limit)
    for i in range(0, len(track_uris), 100):
        sp.playlist_add_items(playlist_id=playlist_id, items=track_uris[i:i+100])
    print(f"Added {len(track_uris)} tracks to playlist {playlist_id}")


def cmd_search(args):
    if not args:
        print("ERROR: specify search query")
        sys.exit(1)
    query = args[0]
    search_type = args[1] if len(args) > 1 else "track"
    limit = int(args[2]) if len(args) > 2 else 10
    sp = get_sp()
    results = sp.search(q=query, type=search_type, limit=limit)
    if search_type == "track":
        items = results["tracks"]["items"]
        print(f"Tracks for '{query}' ({len(items)}):")
        for t in items:
            artists = ", ".join(a["name"] for a in t["artists"])
            print(f"  {t['name']} — {artists} | pop:{t['popularity']}")
            print(f"     URI: {t['uri']}")
    elif search_type == "artist":
        items = results["artists"]["items"]
        print(f"Artists for '{query}':")
        for a in items:
            genres = ", ".join(a["genres"][:3]) if a["genres"] else "—"
            print(f"  {a['name']} | ID: {a['id']} | {genres}")
    elif search_type == "album":
        items = results["albums"]["items"]
        print(f"Albums for '{query}':")
        for al in items:
            artists = ", ".join(a["name"] for a in al["artists"])
            print(f"  {al['name']} — {artists} ({al['release_date'][:4]})")


def cmd_genres(args):
    period = normalize_period(args[0] if args else "medium")
    sp = get_sp()
    artists = sp.current_user_top_artists(limit=50, time_range=period)["items"]
    genres = []
    for a in artists:
        genres.extend(a["genres"])
    top = Counter(genres).most_common(15)
    print(f"Top genres ({period}):")
    for genre, count in top:
        bar = "█" * count
        print(f"  {genre:<30} {bar} ({count})")


def cmd_now(args):
    sp = get_sp()
    current = sp.current_playback()
    if not current or not current.get("is_playing"):
        print("Nothing is playing")
        return
    t = current["item"]
    artists = ", ".join(a["name"] for a in t["artists"])
    progress = current["progress_ms"] // 1000
    duration = t["duration_ms"] // 1000
    print(f"Now playing: {t['name']} — {artists}")
    print(f"  Progress: {progress//60}:{progress%60:02d} / {duration//60}:{duration%60:02d}")
    print(f"  URI: {t['uri']}")
    print(f"  Device: {current.get('device', {}).get('name', '—')}")


def cmd_track_info(args):
    if not args:
        print("ERROR: specify TRACK_URI or TRACK_ID")
        sys.exit(1)
    sp = get_sp()
    for uri in args:
        if uri.startswith("spotify:track:"):
            track_id = uri.split(":")[-1]
        elif uri.startswith("https://open.spotify.com/track/"):
            track_id = uri.split("/track/")[1].split("?")[0]
        else:
            track_id = uri
        t = sp.track(track_id)
        artists = ", ".join(a["name"] for a in t["artists"])
        print(f"{t['name']} — {artists}")
        print(f"  Album: {t['album']['name']} ({t['album']['release_date'][:4]})")
        print(f"  Popularity: {t['popularity']}/100")
        duration = t["duration_ms"] // 1000
        print(f"  Duration: {duration//60}:{duration%60:02d}")
        print(f"  URI: {t['uri']}")


def cmd_related_artists(args):
    """Similar artists via genre search (related-artists API is unavailable for new apps)."""
    if not args:
        print("ERROR: specify artist name or ID")
        sys.exit(1)
    sp = get_sp()
    limit = int(args[1]) if len(args) > 1 else 10
    artist_id = find_artist_id(sp, args[0])
    if not artist_id:
        print(f"ERROR: artist '{args[0]}' not found")
        sys.exit(1)
    artist = sp.artist(artist_id)
    genres = artist.get("genres", [])
    if not genres:
        print(f"No genres for {artist['name']} in Spotify — searching by name")
        results = sp.search(q=f"artist:{artist['name']}", type="artist", limit=limit+1)
        found = [a for a in results["artists"]["items"] if a["id"] != artist_id][:limit]
    else:
        # Search by primary genre (without 'genre:' prefix — works better)
        found = []
        seen = {artist_id}
        for genre in genres[:3]:
            results = sp.search(q=genre, type="artist", limit=20)
            for a in results["artists"]["items"]:
                if a["id"] not in seen:
                    seen.add(a["id"])
                    found.append(a)
            if len(found) >= limit:
                break
        found = found[:limit]
    print(f"Similar to {artist['name']} (genres: {', '.join(genres[:2]) or '—'}):")
    for a in found:
        a_genres = ", ".join(a["genres"][:3]) if a["genres"] else "—"
        print(f"  {a['name']} | ID: {a['id']} | pop:{a['popularity']} | {a_genres}")


def cmd_artist_top_tracks(args):
    """Top tracks of any artist."""
    if not args:
        print("ERROR: specify artist name or ID")
        sys.exit(1)
    sp = get_sp()
    limit = int(args[1]) if len(args) > 1 else 10
    artist_id = find_artist_id(sp, args[0])
    if not artist_id:
        print(f"ERROR: artist '{args[0]}' not found")
        sys.exit(1)
    artist = sp.artist(artist_id)
    tracks = sp.artist_top_tracks(artist_id)["tracks"][:limit]
    print(f"Top tracks of {artist['name']} ({len(tracks)}):")
    for i, t in enumerate(tracks, 1):
        duration = t["duration_ms"] // 1000
        print(f"  {i}. {t['name']} | pop:{t['popularity']} | {duration//60}:{duration%60:02d}")
        print(f"     URI: {t['uri']}")


def cmd_make_playlist(args):
    """Creates a playlist from the user's top tracks.

    Usage: make-playlist "Name" [short|medium|long] [limit]
    """
    if not args:
        print("ERROR: specify playlist name")
        sys.exit(1)
    name = args[0]
    period = normalize_period(args[1] if len(args) > 1 else "short")
    limit = int(args[2]) if len(args) > 2 else 20
    sp = get_sp()

    # Collect top tracks
    tracks = sp.current_user_top_tracks(limit=limit, time_range=period)["items"]
    uris = [t["uri"] for t in tracks]

    # Create playlist
    from datetime import datetime
    month = datetime.now().strftime("%B %Y")
    pl = sp.user_playlist_create(
        user=get_my_user_id(sp),
        name=name,
        public=False,
        description=f"Created by spotify-claw | {month} | {period}"
    )
    sp.playlist_add_items(playlist_id=pl["id"], items=uris)
    print(f"Playlist created: {pl['name']}")
    print(f"ID: {pl['id']}")
    print(f"URL: {pl['external_urls']['spotify']}")
    print(f"Tracks added: {len(uris)}")
    for i, t in enumerate(tracks, 1):
        artists = ", ".join(a["name"] for a in t["artists"])
        print(f"  {i}. {t['name']} — {artists}")


def cmd_discover(args):
    """Discovers new music by user's genre profile.

    related-artists API is unavailable — uses genre-based search.
    Takes user's top genres → searches artists per genre
    → pulls their top tracks → filters out already-known artists.

    Usage:
      discover                     — by user's top genres
      discover ARTIST_NAME         — by a specific artist's genres
      discover ARTIST_NAME 5 3     — depth=5, tracks=3
    """
    sp = get_sp()
    tracks_per = 3
    limit_artists = 5

    # Build set of already-known artists (from user's top)
    known_artists = set()
    known_names = set()
    for period in ["short_term", "medium_term", "long_term"]:
        for a in sp.current_user_top_artists(limit=50, time_range=period)["items"]:
            known_artists.add(a["id"])
            known_names.add(a["name"].lower())

    if args and not args[0].isdigit():
        # Mode: specific artist — use their genres
        seed_name = args[0]
        limit_artists = int(args[1]) if len(args) > 1 else 5
        tracks_per = int(args[2]) if len(args) > 2 else 3
        artist_id = find_artist_id(sp, seed_name)
        if not artist_id:
            print(f"ERROR: artist '{seed_name}' not found")
            sys.exit(1)
        seed_artist = sp.artist(artist_id)
        seed_genres = seed_artist.get("genres", [])
        if not seed_genres:
            print(f"No genres for {seed_artist['name']}. Trying name search...")
            seed_genres = [seed_artist["name"]]
        print(f"Searching similar to {seed_artist['name']} by genres: {', '.join(seed_genres[:3])}")
    else:
        # Mode: user's genre profile
        limit_artists = int(args[0]) if args else 5
        tracks_per = int(args[1]) if len(args) > 1 else 3
        top_artists = sp.current_user_top_artists(limit=50, time_range="medium_term")["items"]
        genre_counter = Counter()
        for a in top_artists:
            genre_counter.update(a["genres"])
        seed_genres = [g for g, _ in genre_counter.most_common(5)]
        print(f"Your top genres: {', '.join(seed_genres)}")

    discoveries = []
    seen_track_ids = set()
    seen_artist_ids = set(known_artists)

    for genre in seed_genres[:5]:
        print(f"\n  Genre: {genre}")
        try:
            # Search without 'genre:' prefix — works better for niche genres
            results = sp.search(q=genre, type="artist", limit=20)
            artists = results["artists"]["items"]
        except Exception as e:
            print(f"    Search error: {e}")
            continue

        new_artists = [a for a in artists if a["id"] not in seen_artist_ids][:limit_artists]

        for rel in new_artists:
            seen_artist_ids.add(rel["id"])
            a_genres = ", ".join(rel["genres"][:2]) if rel["genres"] else "—"
            print(f"    ★ {rel['name']} | pop:{rel['popularity']} | {a_genres}")

            try:
                top_tracks = sp.artist_top_tracks(rel["id"])["tracks"][:tracks_per]
            except Exception:
                continue

            for t in top_tracks:
                if t["id"] not in seen_track_ids:
                    seen_track_ids.add(t["id"])
                    discoveries.append({
                        "track": t,
                        "genre": genre,
                        "artist": rel,
                    })

    print(f"\n{'═'*55}")
    print(f"Discoveries — {len(discoveries)} tracks from {len(seen_artist_ids - known_artists)} new artists:")
    discoveries.sort(key=lambda x: -x["artist"]["popularity"])
    for d in discoveries:
        t = d["track"]
        artists = ", ".join(a["name"] for a in t["artists"])
        print(f"  {t['name']} — {artists}")
        print(f"     genre: {d['genre']} | pop:{t['popularity']} | URI: {t['uri']}")


def ensure_active_device(sp, retries=3, wait=2.5):
    """Checks for an active device. If none — launches Spotify. Returns device_id or None."""
    devices = sp.devices().get("devices", [])
    if devices:
        # Return active device, otherwise first available
        for d in devices:
            if d.get("is_active"):
                return d["id"]
        return devices[0]["id"]
    # No device — launch Spotify
    print("⚡ Spotify is not running — launching...")
    os.system("open -a Spotify")
    for i in range(retries):
        time.sleep(wait)
        devices = sp.devices().get("devices", [])
        if devices:
            print(f"✅ Spotify launched ({devices[0]['name']})")
            time.sleep(2)  # extra wait for full initialization
            for d in devices:
                if d.get("is_active"):
                    return d["id"]
            return devices[0]["id"]
    print("⚠️  Failed to launch Spotify — please open it manually")
    return None


def cmd_play(args):
    """Playback.
    play                        — resume
    play TRACK_URI              — play specific track
    play "track name"           — search and play
    play playlist PLAYLIST_ID   — play a playlist
    """
    sp = get_sp()
    device_id = ensure_active_device(sp)

    if not args:
        # Just resume
        try:
            sp.start_playback(device_id=device_id)
            print("▶ Playback resumed")
        except Exception as e:
            print(f"ERROR: {e}")
            print("  Make sure Spotify is open on this machine")
        return

    query = args[0]

    # play spotify:playlist:xxx or playlist PLAYLIST_ID
    if query.startswith("spotify:playlist:"):
        try:
            sp.start_playback(context_uri=query, device_id=device_id)
            print(f"▶ Playing playlist")
        except Exception as e:
            print(f"ERROR: {e}")
        return

    if query.lower() == "playlist" and len(args) > 1:
        playlist_id = args[1]
        if not playlist_id.startswith("spotify:"):
            playlist_id = "spotify:playlist:" + playlist_id
        try:
            sp.start_playback(context_uri=playlist_id, device_id=device_id)
            print(f"▶ Playing playlist {playlist_id}")
        except Exception as e:
            print(f"ERROR: {e}")
        return

    # play spotify:track:xxx
    if query.startswith("spotify:track:") or (len(query) == 22 and query.replace("_","").replace("-","").isalnum()):
        uri = normalize_uri(query)
        try:
            sp.start_playback(uris=[uri], device_id=device_id)
            info = sp.track(uri)
            artists = ", ".join(a["name"] for a in info["artists"])
            print(f"▶ {info['name']} — {artists}")
        except Exception as e:
            print(f"ERROR: {e}")
        return

    # play "track name" — search and play
    search_q = " ".join(args)
    results = sp.search(q=search_q, type="track", limit=1)
    items = results["tracks"]["items"]
    if not items:
        print(f"ERROR: track '{search_q}' not found")
        return
    track = items[0]
    artists = ", ".join(a["name"] for a in track["artists"])
    try:
        sp.start_playback(uris=[track["uri"]], device_id=device_id)
        print(f"▶ {track['name']} — {artists}")
        print(f"  URI: {track['uri']}")
    except Exception as e:
        print(f"ERROR: {e}")
        print("  Make sure Spotify is open on this machine")


def cmd_pause(args):
    """Pause playback."""
    sp = get_sp()
    device_id = ensure_active_device(sp)
    try:
        sp.pause_playback(device_id=device_id)
        print("⏸ Paused")
    except Exception as e:
        print(f"ERROR: {e}")


def cmd_next(args):
    """Skip to next track."""
    sp = get_sp()
    device_id = ensure_active_device(sp)
    try:
        sp.next_track(device_id=device_id)
        time.sleep(0.5)
        cur = sp.current_playback()
        if cur and cur.get("item"):
            t = cur["item"]
            artists = ", ".join(a["name"] for a in t["artists"])
            print(f"⏭ {t['name']} — {artists}")
        else:
            print("⏭ Next track")
    except Exception as e:
        print(f"ERROR: {e}")


def cmd_prev(args):
    """Go to previous track."""
    sp = get_sp()
    device_id = ensure_active_device(sp)
    try:
        sp.previous_track(device_id=device_id)
        time.sleep(0.5)
        cur = sp.current_playback()
        if cur and cur.get("item"):
            t = cur["item"]
            artists = ", ".join(a["name"] for a in t["artists"])
            print(f"⏮ {t['name']} — {artists}")
        else:
            print("⏮ Previous track")
    except Exception as e:
        print(f"ERROR: {e}")


def cmd_volume(args):
    """Volume control.
    volume 70      — set to 70%
    volume up      — +10%
    volume down    — -10%
    """
    sp = get_sp()
    device_id = ensure_active_device(sp)
    if not args:
        cur = sp.current_playback()
        if cur and cur.get("device"):
            print(f"🔊 Volume: {cur['device']['volume_percent']}%")
        else:
            print("ERROR: no active device")
        return

    query = args[0].lower()
    if query in ("up", "down"):
        cur = sp.current_playback()
        cur_vol = cur["device"]["volume_percent"] if cur and cur.get("device") else 50
        vol = min(100, cur_vol + 10) if query == "up" else max(0, cur_vol - 10)
    else:
        try:
            vol = int(query)
        except ValueError:
            print(f"ERROR: invalid value '{query}'. Use: volume 70 / volume up / volume down")
            return

    try:
        sp.volume(vol, device_id=device_id)
        print(f"🔊 Volume: {vol}%")
    except Exception as e:
        print(f"ERROR: {e}")


def cmd_devices(args):
    """List active Spotify devices."""
    sp = get_sp()
    devices = sp.devices().get("devices", [])
    if not devices:
        print("No active devices. Open Spotify on this machine.")
        return
    print(f"Devices ({len(devices)}):")
    for d in devices:
        active = "← active" if d["is_active"] else ""
        print(f"  {d['name']} ({d['type']}) | {d['id']} {active}")
        print(f"  vol:{d['volume_percent']}%")


def cmd_queue(args):
    """Add a track to the playback queue.
    queue TRACK_URI
    queue "track name"
    """
    if not args:
        print("ERROR: specify track URI or name")
        sys.exit(1)
    sp = get_sp()
    device_id = ensure_active_device(sp)
    query = " ".join(args)

    if query.startswith("spotify:track:"):
        uri = query
    else:
        results = sp.search(q=query, type="track", limit=1)
        items = results["tracks"]["items"]
        if not items:
            print(f"ERROR: track '{query}' not found")
            return
        track = items[0]
        uri = track["uri"]
        artists = ", ".join(a["name"] for a in track["artists"])
        print(f"Found: {track['name']} — {artists}")

    try:
        sp.add_to_queue(uri, device_id=device_id)
        print(f"✅ Added to queue: {uri}")
    except Exception as e:
        print(f"ERROR: {e}")


def cmd_shuffle(args):
    """Toggle shuffle on/off.
    shuffle on / shuffle off / shuffle (toggle)
    """
    sp = get_sp()
    device_id = ensure_active_device(sp)
    if not args:
        cur = sp.current_playback()
        state = cur.get("shuffle_state", False) if cur else False
        new_state = not state
    else:
        new_state = args[0].lower() in ("on", "true", "1")

    try:
        sp.shuffle(new_state, device_id=device_id)
        print(f"🔀 Shuffle: {'on' if new_state else 'off'}")
    except Exception as e:
        print(f"ERROR: {e}")


COMMANDS = {
    "top-tracks": cmd_top_tracks,
    "top-artists": cmd_top_artists,
    "recent": cmd_recent,
    "liked": cmd_liked,
    "liked-all": cmd_liked_all,
    "liked-by-artist": cmd_liked_by_artist,
    "playlists": cmd_playlists,
    "create-playlist": cmd_create_playlist,
    "add-to-playlist": cmd_add_to_playlist,
    "search": cmd_search,
    "genres": cmd_genres,
    "now": cmd_now,
    "track-info": cmd_track_info,
    "related-artists": cmd_related_artists,
    "artist-top-tracks": cmd_artist_top_tracks,
    "make-playlist": cmd_make_playlist,
    "discover": cmd_discover,
    # Playback (Premium)
    "play": cmd_play,
    "pause": cmd_pause,
    "next": cmd_next,
    "prev": cmd_prev,
    "volume": cmd_volume,
    "devices": cmd_devices,
    "queue": cmd_queue,
    "shuffle": cmd_shuffle,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("Available commands:")
        for cmd in sorted(COMMANDS):
            print(f"  python3 ~/.openclaw/scripts/spotify.py {cmd}")
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]
    COMMANDS[cmd](args)
