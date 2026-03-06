#!/usr/bin/env python3
"""Spotify controller.

Usage:
  python3 spotify.py status
  python3 spotify.py play|pause|next|prev
  python3 spotify.py volume <0-100>
  python3 spotify.py search <query>
  python3 spotify.py playtrack <spotify:track:...>
  python3 spotify.py playsearch <query>
  python3 spotify.py devices
  python3 spotify.py setdevice <device_id_or_exact_name>
"""

import os
import sys
from urllib.parse import quote

import requests

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("SPOTIFY_REFRESH_TOKEN")


def fail(msg: str, code: int = 1):
    print(f"❌ {msg}")
    raise SystemExit(code)


def ensure_env():
    missing = [
        name
        for name, value in {
            "SPOTIFY_CLIENT_ID": CLIENT_ID,
            "SPOTIFY_CLIENT_SECRET": CLIENT_SECRET,
            "SPOTIFY_REFRESH_TOKEN": REFRESH_TOKEN,
        }.items()
        if not value
    ]
    if missing:
        fail(f"Missing env vars: {', '.join(missing)}")


def get_access_token() -> str:
    ensure_env()
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=20,
    )
    if r.status_code != 200:
        fail(f"Token refresh failed ({r.status_code}): {r.text[:200]}")

    token = r.json().get("access_token")
    if not token:
        fail("Token response missing access_token")
    return token


def spotify(method: str, endpoint: str, **kwargs) -> requests.Response:
    token = get_access_token()
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {token}"
    url = f"https://api.spotify.com/v1{endpoint}"
    return requests.request(method, url, headers=headers, timeout=20, **kwargs)


def print_active_device_hint():
    print("💡 Hint: Open Spotify on phone/desktop/web and start any track once to activate a device.")
    print("   Then run: python3 spotify.py devices")


def print_player_state(resp: requests.Response):
    if resp.status_code == 204:
        print("Nothing playing (or no active device)")
        print_active_device_hint()
        return
    if resp.status_code != 200:
        print(f"Player status error ({resp.status_code}): {resp.text[:200]}")
        return

    d = resp.json()
    item = d.get("item")
    if not item:
        print("No track info available")
        return

    artists = item.get("artists") or []
    artist = artists[0].get("name") if artists else "Unknown artist"
    icon = "▶" if d.get("is_playing") else "⏸"
    print(f"{icon} {item.get('name', 'Unknown track')} — {artist}")


def require_arg(index: int, message: str) -> str:
    if len(sys.argv) <= index:
        fail(message)
    return sys.argv[index]


def usage():
    print(__doc__.strip())


def print_api_error(prefix: str, r: requests.Response):
    print(f"{prefix} ({r.status_code}): {r.text[:200]}")
    if r.status_code == 404:
        print_active_device_hint()
    if r.status_code == 403 and "VOLUME_CONTROL_DISALLOW" in r.text:
        print("💡 This device does not allow remote volume control via Spotify API.")


def get_search_results(query: str, limit: int = 5):
    q = quote(query)
    r = spotify("GET", f"/search?q={q}&type=track&limit={limit}")
    if r.status_code != 200:
        fail(f"Search error ({r.status_code}): {r.text[:200]}")
    return (r.json().get("tracks") or {}).get("items") or []


def get_devices():
    r = spotify("GET", "/me/player/devices")
    if r.status_code != 200:
        fail(f"Devices error ({r.status_code}): {r.text[:200]}")
    return r.json().get("devices") or []


def cmd_status():
    r = spotify("GET", "/me/player")
    print_player_state(r)


def cmd_play_pause_skip(endpoint: str, ok_text: str, err_prefix: str):
    r = spotify("PUT" if endpoint in ("/me/player/play", "/me/player/pause") else "POST", endpoint)
    if 200 <= r.status_code < 300:
        print(ok_text)
    else:
        print_api_error(err_prefix, r)
        raise SystemExit(1)


def cmd_volume():
    vol_raw = require_arg(2, "Usage: python3 spotify.py volume <0-100>")
    try:
        vol = int(vol_raw)
    except ValueError:
        fail("Volume must be an integer 0-100")
    if not 0 <= vol <= 100:
        fail("Volume must be between 0 and 100")

    r = spotify("PUT", f"/me/player/volume?volume_percent={vol}")
    if 200 <= r.status_code < 300:
        print(f"🔊 Volume set to {vol}%")
    else:
        print_api_error("Volume error", r)
        raise SystemExit(1)


def cmd_search():
    query = " ".join(sys.argv[2:]).strip()
    if not query:
        fail("Usage: python3 spotify.py search <query>")

    items = get_search_results(query, limit=5)
    if not items:
        print("No results")
        return

    for t in items:
        artists = t.get("artists") or []
        artist = artists[0].get("name") if artists else "Unknown artist"
        print(f"{t.get('name', 'Unknown track')} — {artist} | {t.get('uri', '-')}")


def cmd_playtrack(uri: str):
    r = spotify("PUT", "/me/player/play", json={"uris": [uri]})
    if 200 <= r.status_code < 300:
        print(f"▶ Playing {uri}")
    else:
        print_api_error("Playtrack error", r)
        raise SystemExit(1)


def cmd_playsearch():
    query = " ".join(sys.argv[2:]).strip()
    if not query:
        fail("Usage: python3 spotify.py playsearch <query>")

    items = get_search_results(query, limit=1)
    if not items:
        print("No results")
        return

    t = items[0]
    uri = t.get("uri")
    artists = t.get("artists") or []
    artist = artists[0].get("name") if artists else "Unknown artist"
    name = t.get("name", "Unknown track")
    if not uri:
        fail("Search returned track without URI")

    r = spotify("PUT", "/me/player/play", json={"uris": [uri]})
    if 200 <= r.status_code < 300:
        print(f"▶ Playing {name} — {artist}")
    else:
        print_api_error("Playsearch error", r)
        raise SystemExit(1)


def cmd_devices():
    devices = get_devices()
    if not devices:
        print("No Spotify devices found")
        print_active_device_hint()
        return

    for d in devices:
        active = "*" if d.get("is_active") else " "
        name = d.get("name", "Unknown")
        dev_id = d.get("id", "-")
        typ = d.get("type", "?")
        vol = d.get("volume_percent")
        print(f"{active} {name} [{typ}] id={dev_id} vol={vol}%")


def cmd_setdevice(target: str):
    devices = get_devices()
    if not devices:
        fail("No devices available to set")

    chosen = None

    # Exact ID first
    for d in devices:
        if d.get("id") == target:
            chosen = d
            break

    # Exact (case-insensitive) name fallback
    if not chosen:
        for d in devices:
            if (d.get("name") or "").lower() == target.lower():
                chosen = d
                break

    # Partial name fallback if unique
    if not chosen:
        matches = [d for d in devices if target.lower() in (d.get("name") or "").lower()]
        if len(matches) == 1:
            chosen = matches[0]
        elif len(matches) > 1:
            print("Multiple device matches found:")
            for d in matches:
                print(f"- {d.get('name')} (id={d.get('id')})")
            fail("Please provide exact name or id")

    if not chosen or not chosen.get("id"):
        fail("Device not found. Run: python3 spotify.py devices")

    r = spotify("PUT", "/me/player", json={"device_ids": [chosen["id"]], "play": False})
    if 200 <= r.status_code < 300:
        print(f"✅ Active device set to: {chosen.get('name')}")
    else:
        print_api_error("Setdevice error", r)
        raise SystemExit(1)


cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

if cmd in {"-h", "--help", "help"}:
    usage()
    raise SystemExit(0)

if cmd == "status":
    cmd_status()
elif cmd == "play":
    cmd_play_pause_skip("/me/player/play", "▶ Playing", "Play error")
elif cmd == "pause":
    cmd_play_pause_skip("/me/player/pause", "⏸ Paused", "Pause error")
elif cmd == "next":
    cmd_play_pause_skip("/me/player/next", "⏭ Skipped", "Next error")
elif cmd == "prev":
    cmd_play_pause_skip("/me/player/previous", "⏮ Previous", "Previous error")
elif cmd == "volume":
    cmd_volume()
elif cmd == "search":
    cmd_search()
elif cmd == "playtrack":
    cmd_playtrack(require_arg(2, "Usage: python3 spotify.py playtrack <spotify:track:...>"))
elif cmd == "playsearch":
    cmd_playsearch()
elif cmd == "devices":
    cmd_devices()
elif cmd == "setdevice":
    cmd_setdevice(require_arg(2, "Usage: python3 spotify.py setdevice <device_id_or_exact_name>"))
else:
    usage()
    fail(f"Unknown command: {cmd}")
