#!/usr/bin/env python3
import os, argparse, base64, json, os, time, urllib.parse, urllib.request

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CFG_PATH = os.path.join(BASE_DIR, "config.json")
TOK_PATH = os.path.join(BASE_DIR, "data", "tokens.json")


def load_cfg():
    with open(CFG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tokens(tok):
    os.makedirs(os.path.dirname(TOK_PATH), exist_ok=True)
    with open(TOK_PATH, "w", encoding="utf-8") as f:
        json.dump(tok, f)


def exchange(code, redirect_uri, cid, sec):
    raw = f"{cid}:{sec}".encode()
    auth = base64.b64encode(raw).decode()
    body = urllib.parse.urlencode({"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri}).encode()
    req = urllib.request.Request("https://accounts.spotify.com/api/token", data=body, method="POST")
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--callback-url", required=True)
    args = ap.parse_args()

    cfg = load_cfg()
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", cfg["spotify"]["redirectUri"])
    cid = os.getenv("SPOTIFY_CLIENT_ID", "")
    sec = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    if not cid or not sec:
        raise SystemExit("Missing SPOTIFY_CLIENT_ID/SPOTIFY_CLIENT_SECRET")

    cb = urllib.parse.urlparse(args.callback_url)
    qs = urllib.parse.parse_qs(cb.query)
    code = (qs.get("code") or [""])[0]
    if not code:
        raise SystemExit("callback-url missing code")

    tok = exchange(code, redirect_uri, cid, sec)
    out = {
        "accessToken": tok.get("access_token"),
        "refreshToken": tok.get("refresh_token"),
        "tokenType": tok.get("token_type"),
        "scope": tok.get("scope"),
        "expiresIn": int(tok.get("expires_in", 3600)),
        "expiresAt": int(time.time()) + int(tok.get("expires_in", 3600)),
        "obtainedAt": int(time.time()),
    }
    save_tokens(out)
    print(json.dumps({"ok": True, "tokenPath": TOK_PATH}))


if __name__ == "__main__":
    main()


