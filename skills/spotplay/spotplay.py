#!/usr/bin/env python3
import base64
import json
import os
import shlex
import subprocess
import sys
import time
import urllib.parse
import urllib.request

CFG = os.path.expanduser("~/.shpotify.cfg")

def run(cmd: str) -> str:
    p = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    out = (p.stdout or "").strip()
    err = (p.stderr or "").strip()
    if p.returncode != 0:
        raise RuntimeError(f"[ERROR] {cmd}\n{err or out}")
    return out

def load_creds():
    cid = os.environ.get("SPOTIFY_CLIENT_ID") or os.environ.get("CLIENT_ID")
    csec = os.environ.get("SPOTIFY_CLIENT_SECRET") or os.environ.get("CLIENT_SECRET")

    if (not cid or not csec) and os.path.exists(CFG):
        txt = open(CFG, "r", encoding="utf-8").read()
        for line in txt.splitlines():
            line = line.strip()
            if line.startswith("CLIENT_ID=") and not cid:
                cid = line.split("=", 1)[1].strip().strip('"')
            if line.startswith("CLIENT_SECRET=") and not csec:
                csec = line.split("=", 1)[1].strip().strip('"')

    if not cid or not csec:
        raise RuntimeError(
            "Missing Spotify client credentials.\n"
            "Provide SPOTIFY_CLIENT_ID/SPOTIFY_CLIENT_SECRET env, or set CLIENT_ID/CLIENT_SECRET in ~/.shpotify.cfg"
        )
    return cid, csec

def http_post(url: str, headers: dict, data: dict) -> dict:
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))

def http_get(url: str, headers: dict) -> dict:
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))

def get_token(cid: str, csec: str) -> str:
    basic = base64.b64encode(f"{cid}:{csec}".encode("utf-8")).decode("ascii")
    j = http_post(
        "https://accounts.spotify.com/api/token",
        {"Authorization": f"Basic {basic}"},
        {"grant_type": "client_credentials"},
    )
    tok = j.get("access_token")
    if not tok:
        raise RuntimeError(f"Token request failed: {j}")
    return tok

def search_track_uri(query: str, token: str) -> tuple[str, str]:
    q = urllib.parse.quote(query)
    url = f"https://api.spotify.com/v1/search?q={q}&type=track&limit=1"
    j = http_get(url, {"Authorization": f"Bearer {token}"})
    items = (((j.get("tracks") or {}).get("items")) or [])
    if not items:
        raise RuntimeError(f"No results for: {query}")
    t = items[0]
    name = t.get("name") or "(unknown)"
    uri = t.get("uri")
    if not uri:
        raise RuntimeError(f"Found track but missing uri: {t}")
    return name, uri

def osascript(script: str) -> str:
    cmd = "osascript -e " + shlex.quote(script)
    return run(cmd)

def ensure_spotify_running():
    is_running = osascript('application "Spotify" is running')
    if is_running.strip().lower() == "false":
        osascript('tell application "Spotify" to activate')
        time.sleep(0.5)

def play_uri(uri: str):
    ensure_spotify_running()
    osascript(f'tell application "Spotify" to play track "{uri}"')

def now_playing_name() -> str:
    try:
        return osascript('tell application "Spotify" to name of current track')
    except Exception:
        return ""

def main():
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        print("Usage: spotplay.py <song query>")
        sys.exit(2)

    cid, csec = load_creds()
    token = get_token(cid, csec)
    want_name, want_uri = search_track_uri(query, token)

    play_uri(want_uri)

    cur = ""
    for _ in range(10):
        cur = now_playing_name()
        if cur:
            break
        time.sleep(0.2)

    print(f"✅ Requested: {want_name}")
    print(f"🔗 URI: {want_uri}")
    print(f"🎵 Now playing: {cur or '(unknown)'}")

if __name__ == "__main__":
    main()
