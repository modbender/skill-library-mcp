#!/usr/bin/env python3
"""
Spotify API client for playlist management.
Updated for February 2026 Web API changes (Dev Mode).

Commands:
  search <query> [--type track|artist|album] [--limit N]
  create <name> [--description DESC] [--private]
  add <playlist_id> <track_uris...>
  remove <playlist_id> <track_uris...>
  my-playlists [--limit N]
  playlist-tracks <playlist_id> [--limit N]
  top-tracks [--time-range short|medium|long] [--limit N]
  recently-played [--limit N]
  me

All commands output JSON for easy parsing by agents.
"""

import argparse
import json
import sys
import os
import subprocess

TOKEN_PATH = os.path.expanduser("~/.openclaw/workspace/config/.spotify-tokens.json")
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
API_BASE = "https://api.spotify.com/v1"


def get_token():
    if not os.path.exists(TOKEN_PATH):
        print(json.dumps({"error": "Not authenticated. Run auth.py first."}))
        sys.exit(1)
    with open(TOKEN_PATH) as f:
        tokens = json.load(f)
    return tokens.get("access_token")


def refresh_and_retry():
    """Refresh token and return new access token."""
    try:
        subprocess.run(
            [sys.executable, os.path.join(SKILL_DIR, "auth.py"), "--refresh"],
            capture_output=True, check=True
        )
        with open(TOKEN_PATH) as f:
            return json.load(f).get("access_token")
    except Exception:
        return None


def api(method, path, token, data=None, params=None):
    import requests
    url = f"{API_BASE}{path}" if path.startswith("/") else path
    headers = {"Authorization": f"Bearer {token}"}
    if data:
        headers["Content-Type"] = "application/json"

    resp = requests.request(method, url, headers=headers, json=data, params=params)

    # Auto-refresh on 401
    if resp.status_code == 401:
        new_token = refresh_and_retry()
        if new_token:
            headers["Authorization"] = f"Bearer {new_token}"
            resp = requests.request(method, url, headers=headers, json=data, params=params)

    if resp.status_code == 204:
        return {}

    if not resp.ok:
        try:
            err = resp.json()
        except Exception:
            err = {"status": resp.status_code, "message": resp.text}
        print(json.dumps({"error": err}, indent=2))
        sys.exit(1)

    return resp.json()


# --- Commands ---

def cmd_search(args):
    token = get_token()
    params = {"q": args.query, "type": args.type, "limit": args.limit}
    result = api("GET", "/search", token, params=params)

    if args.type == "track":
        items = []
        for t in result.get("tracks", {}).get("items", []):
            items.append({
                "name": t["name"],
                "artist": ", ".join(a["name"] for a in t["artists"]),
                "album": t.get("album", {}).get("name", ""),
                "uri": t["uri"],
                "duration_ms": t.get("duration_ms", 0),
                "popularity": t.get("popularity", 0),
            })
        print(json.dumps(items, indent=2))
    elif args.type == "artist":
        items = []
        for a in result.get("artists", {}).get("items", []):
            items.append({
                "name": a["name"],
                "uri": a["uri"],
                "genres": a.get("genres", []),
                "popularity": a.get("popularity", 0),
                "followers": a.get("followers", {}).get("total", 0),
            })
        print(json.dumps(items, indent=2))
    elif args.type == "album":
        items = []
        for a in result.get("albums", {}).get("items", []):
            items.append({
                "name": a["name"],
                "artist": ", ".join(ar["name"] for ar in a["artists"]),
                "uri": a["uri"],
                "release_date": a.get("release_date", ""),
                "total_tracks": a.get("total_tracks", 0),
            })
        print(json.dumps(items, indent=2))
    else:
        print(json.dumps(result, indent=2))


def cmd_create(args):
    token = get_token()
    data = {
        "name": args.name,
        "description": args.description or "",
        "public": not args.private,
    }
    result = api("POST", "/me/playlists", token, data=data)
    print(json.dumps({
        "id": result["id"],
        "name": result["name"],
        "url": result["external_urls"]["spotify"],
        "uri": result["uri"],
    }, indent=2))


def cmd_add(args):
    token = get_token()
    uris = args.track_uris
    for i in range(0, len(uris), 100):
        batch = uris[i:i + 100]
        api("POST", f"/playlists/{args.playlist_id}/items", token, data={"uris": batch})
    print(json.dumps({"added": len(uris), "playlist_id": args.playlist_id}))


def cmd_remove(args):
    token = get_token()
    items = [{"uri": uri} for uri in args.track_uris]
    for i in range(0, len(items), 100):
        batch = items[i:i + 100]
        api("DELETE", f"/playlists/{args.playlist_id}/items", token, data={"tracks": batch})
    print(json.dumps({"removed": len(items), "playlist_id": args.playlist_id}))


def cmd_my_playlists(args):
    token = get_token()
    result = api("GET", "/me/playlists", token, params={"limit": args.limit})
    playlists = []
    for p in result.get("items", []):
        playlists.append({
            "id": p["id"],
            "name": p["name"],
            "tracks": p["tracks"]["total"],
            "url": p["external_urls"]["spotify"],
        })
    print(json.dumps(playlists, indent=2))


def cmd_playlist_tracks(args):
    token = get_token()
    result = api("GET", f"/playlists/{args.playlist_id}/items", token, params={"limit": args.limit})
    tracks = []
    for item in result.get("items", []):
        t = item.get("track")
        if not t:
            continue
        tracks.append({
            "name": t["name"],
            "artist": ", ".join(a["name"] for a in t.get("artists", [])),
            "album": t.get("album", {}).get("name", ""),
            "uri": t["uri"],
            "duration_ms": t.get("duration_ms", 0),
        })
    print(json.dumps(tracks, indent=2))


def cmd_top_tracks(args):
    token = get_token()
    params = {"time_range": args.time_range + "_term", "limit": args.limit}
    result = api("GET", "/me/top/tracks", token, params=params)
    tracks = []
    for t in result.get("items", []):
        tracks.append({
            "name": t["name"],
            "artist": ", ".join(a["name"] for a in t["artists"]),
            "uri": t["uri"],
            "popularity": t.get("popularity", 0),
        })
    print(json.dumps(tracks, indent=2))


def cmd_recently_played(args):
    token = get_token()
    result = api("GET", "/me/player/recently-played", token, params={"limit": args.limit})
    tracks = []
    for item in result.get("items", []):
        t = item.get("track", {})
        tracks.append({
            "name": t["name"],
            "artist": ", ".join(a["name"] for a in t.get("artists", [])),
            "uri": t["uri"],
            "played_at": item.get("played_at", ""),
        })
    print(json.dumps(tracks, indent=2))


def cmd_me(args):
    token = get_token()
    result = api("GET", "/me", token)
    print(json.dumps({
        "id": result["id"],
        "display_name": result.get("display_name"),
        "email": result.get("email"),
        "country": result.get("country"),
        "product": result.get("product"),
    }, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spotify Playlist Manager")
    sub = parser.add_subparsers(dest="command")

    p_search = sub.add_parser("search")
    p_search.add_argument("query")
    p_search.add_argument("--type", choices=["track", "artist", "album"], default="track")
    p_search.add_argument("--limit", type=int, default=20)
    p_search.set_defaults(func=cmd_search)

    p_create = sub.add_parser("create")
    p_create.add_argument("name")
    p_create.add_argument("--description", default="")
    p_create.add_argument("--private", action="store_true")
    p_create.set_defaults(func=cmd_create)

    p_add = sub.add_parser("add")
    p_add.add_argument("playlist_id")
    p_add.add_argument("track_uris", nargs="+")
    p_add.set_defaults(func=cmd_add)

    p_remove = sub.add_parser("remove")
    p_remove.add_argument("playlist_id")
    p_remove.add_argument("track_uris", nargs="+")
    p_remove.set_defaults(func=cmd_remove)

    p_playlists = sub.add_parser("my-playlists")
    p_playlists.add_argument("--limit", type=int, default=20)
    p_playlists.set_defaults(func=cmd_my_playlists)

    p_ptracks = sub.add_parser("playlist-tracks")
    p_ptracks.add_argument("playlist_id")
    p_ptracks.add_argument("--limit", type=int, default=50)
    p_ptracks.set_defaults(func=cmd_playlist_tracks)

    p_top = sub.add_parser("top-tracks")
    p_top.add_argument("--time-range", choices=["short", "medium", "long"], default="medium")
    p_top.add_argument("--limit", type=int, default=20)
    p_top.set_defaults(func=cmd_top_tracks)

    p_recent = sub.add_parser("recently-played")
    p_recent.add_argument("--limit", type=int, default=20)
    p_recent.set_defaults(func=cmd_recently_played)

    p_me = sub.add_parser("me")
    p_me.set_defaults(func=cmd_me)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)
