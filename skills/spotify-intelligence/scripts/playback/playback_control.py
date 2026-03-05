#!/usr/bin/env python3
import os, argparse, base64, json, os, sqlite3, time, urllib.parse, urllib.request

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CFG_PATH = os.path.join(BASE_DIR, "config.json")
DB_PATH = os.path.join(BASE_DIR, "data", "spotify-intelligence.sqlite")
TOK_PATH = os.path.join(BASE_DIR, "data", "tokens.json")


def load_cfg():
    with open(CFG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def read_tokens():
    if not os.path.exists(TOK_PATH):
        raise RuntimeError("No token file. Run oauth first.")
    with open(TOK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def write_tokens(tok):
    os.makedirs(os.path.dirname(TOK_PATH), exist_ok=True)
    with open(TOK_PATH, "w", encoding="utf-8") as f:
        json.dump(tok, f)


def refresh_if_needed(cfg, tok):
    now = int(time.time())
    if int(tok.get("expiresAt", 0)) > now + 30:
        return tok["accessToken"]
    cid = os.getenv("SPOTIFY_CLIENT_ID", "")
    sec = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    if not cid or not sec:
        raise RuntimeError("Missing SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET")
    raw = f"{cid}:{sec}".encode()
    auth = base64.b64encode(raw).decode()
    body = urllib.parse.urlencode({"grant_type": "refresh_token", "refresh_token": tok.get("refreshToken", "")}).encode()
    req = urllib.request.Request("https://accounts.spotify.com/api/token", data=body, method="POST")
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode())
    tok["accessToken"] = data["access_token"]
    tok["expiresAt"] = int(time.time()) + int(data.get("expires_in", 3600))
    if data.get("refresh_token"):
        tok["refreshToken"] = data["refresh_token"]
    write_tokens(tok)
    return tok["accessToken"]


def api(method, url, token, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if body is not None:
        raw = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
        req.data = raw
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            txt = r.read().decode() if r.length != 0 else ""
            return json.loads(txt) if txt else None
    except Exception as e:
        raise RuntimeError(str(e))


def get_devices(base, token):
    data = api("GET", f"{base}/me/player/devices", token)
    return data.get("devices", []) if data else []


def resolve_device(base, token, did, dname):
    if did:
        return did
    if not dname:
        return None
    for d in get_devices(base, token):
        if d.get("name") == dname:
            return d.get("id")
    raise RuntimeError(f"Device not found: {dname}")


def resolve_track(base, token, query, artist, limit=5):
    db_track = None
    if os.path.exists(DB_PATH):
        con = sqlite3.connect(DB_PATH)
        try:
            me = api("GET", f"{base}/me", token)
            uid = me.get("id", "")
            q = "%" + query.lower() + "%"
            if artist:
                a = "%" + artist.lower() + "%"
                sql = """
                SELECT t.track_id,t.name,t.artists,t.uri
                FROM tracks t
                JOIN playlist_track_membership m ON m.track_id=t.track_id AND m.currently_present=1
                JOIN playlists p ON p.playlist_id=m.playlist_id
                WHERE p.owner_id=? AND lower(coalesce(t.name,'')) LIKE ? AND lower(coalesce(t.artists,'')) LIKE ?
                LIMIT 1
                """
                row = con.execute(sql, (uid, q, a)).fetchone()
            else:
                sql = """
                SELECT t.track_id,t.name,t.artists,t.uri
                FROM tracks t
                JOIN playlist_track_membership m ON m.track_id=t.track_id AND m.currently_present=1
                JOIN playlists p ON p.playlist_id=m.playlist_id
                WHERE p.owner_id=? AND lower(coalesce(t.name,'')) LIKE ?
                LIMIT 1
                """
                row = con.execute(sql, (uid, q)).fetchone()
            if row:
                db_track = {"id": row[0], "name": row[1], "uri": row[3], "artists": [{"name": row[2]}]}
        finally:
            con.close()
    if db_track:
        return db_track
    q = f"track:{query} artist:{artist}" if artist else query
    u = f"{base}/search?" + urllib.parse.urlencode({"q": q, "type": "track", "limit": limit})
    data = api("GET", u, token)
    items = data.get("tracks", {}).get("items", []) if data else []
    if not items:
        raise RuntimeError("No track found")
    return items[0]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["status", "devices", "play", "pause", "next", "previous", "volume", "seek_rel", "play_track", "queue_add", "queue_status", "transfer"])
    p.add_argument("--device-id", default="")
    p.add_argument("--device-name", default="")
    p.add_argument("--query", default="")
    p.add_argument("--artist", default="")
    p.add_argument("--volume", type=int, default=50)
    p.add_argument("--delta-sec", type=int, default=15)
    args = p.parse_args()

    cfg = load_cfg()
    tok = read_tokens()
    token = refresh_if_needed(cfg, tok)
    base = cfg["spotify"]["apiBase"]

    if args.action == "status":
        print(json.dumps(api("GET", f"{base}/me/player", token) or {"ok": True, "state": "no_active_player"}))
        return
    if args.action == "devices":
        print(json.dumps(get_devices(base, token)))
        return
    if args.action == "play":
        did = resolve_device(base, token, args.device_id, args.device_name)
        u = f"{base}/me/player/play" + (f"?device_id={urllib.parse.quote(did)}" if did else "")
        api("PUT", u, token)
        print("ok")
        return
    if args.action == "pause":
        api("PUT", f"{base}/me/player/pause", token); print("ok"); return
    if args.action == "next":
        api("POST", f"{base}/me/player/next", token); print("ok"); return
    if args.action == "previous":
        api("POST", f"{base}/me/player/previous", token); print("ok"); return
    if args.action == "transfer":
        did = resolve_device(base, token, args.device_id, args.device_name)
        api("PUT", f"{base}/me/player", token, {"device_ids": [did], "play": True}); print("ok"); return
    if args.action == "volume":
        api("PUT", f"{base}/me/player/volume?volume_percent={args.volume}", token); print("ok"); return
    if args.action == "seek_rel":
        st = api("GET", f"{base}/me/player", token)
        if not st or not st.get("item"):
            raise RuntimeError("No active playback")
        cur = int(st.get("progress_ms", 0)); dur = int(st["item"].get("duration_ms", cur))
        newp = max(0, min(dur, cur + args.delta_sec * 1000))
        api("PUT", f"{base}/me/player/seek?position_ms={newp}", token); print("ok"); return
    if args.action == "play_track":
        tr = resolve_track(base, token, args.query, args.artist)
        did = resolve_device(base, token, args.device_id, args.device_name)
        u = f"{base}/me/player/play" + (f"?device_id={urllib.parse.quote(did)}" if did else "")
        api("PUT", u, token, {"uris": [tr["uri"]]})
        print(json.dumps({"ok": True, "name": tr.get("name"), "artists": ", ".join(a.get("name", "") for a in tr.get("artists", []))}))
        return
    if args.action == "queue_add":
        tr = resolve_track(base, token, args.query, args.artist)
        did = resolve_device(base, token, args.device_id, args.device_name)
        u = f"{base}/me/player/queue?uri={urllib.parse.quote(tr['uri'])}" + (f"&device_id={urllib.parse.quote(did)}" if did else "")
        api("POST", u, token)
        print(json.dumps({"ok": True, "queued": tr.get("name")}))
        return
    if args.action == "queue_status":
        print(json.dumps(api("GET", f"{base}/me/player/queue", token) or {}))


if __name__ == "__main__":
    main()


