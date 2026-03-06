#!/usr/bin/env python3
"""EVE SSO OAuth2 PKCE authentication flow.

Usage:
    python auth_flow.py --client-id <CLIENT_ID> [--char-name <NAME>] [--port 8080]

Stores refresh token to ~/.openclaw/eve-tokens.json
"""
import argparse
import base64
import hashlib
import http.server
import json
import os
import secrets
import threading
import urllib.parse
import urllib.request

TOKENS_FILE = os.path.expanduser("~/.openclaw/eve-tokens.json")

SCOPES = " ".join([
    "esi-wallet.read_character_wallet.v1",
    "esi-assets.read_assets.v1",
    "esi-skills.read_skills.v1",
    "esi-skills.read_skillqueue.v1",
    "esi-clones.read_clones.v1",
    "esi-clones.read_implants.v1",
    "esi-location.read_location.v1",
    "esi-location.read_ship_type.v1",
    "esi-location.read_online.v1",
    "esi-characters.read_notifications.v1",
    "esi-industry.read_character_jobs.v1",
    "esi-markets.read_character_orders.v1",
    "esi-contracts.read_character_contracts.v1",
    "esi-killmails.read_killmails.v1",
    "esi-planets.manage_planets.v1",
    "esi-characters.read_fatigue.v1",
    "esi-mail.read_mail.v1",
])


def pkce_pair():
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def exchange_code(code, verifier, client_id, redirect_uri):
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "code_verifier": verifier,
        "redirect_uri": redirect_uri,
    }).encode()
    req = urllib.request.Request(
        "https://login.eveonline.com/v2/oauth/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def verify_token(access_token):
    req = urllib.request.Request(
        "https://login.eveonline.com/oauth/verify",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE) as f:
            return json.load(f)
    return {"characters": {}}


def save_tokens(data):
    os.makedirs(os.path.dirname(TOKENS_FILE), exist_ok=True)
    with open(TOKENS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(TOKENS_FILE, 0o600)


def main():
    parser = argparse.ArgumentParser(description="EVE SSO OAuth2 PKCE auth flow")
    parser.add_argument("--client-id", required=True,
                        help="EVE Developer App Client ID")
    parser.add_argument("--char-name", default="main",
                        help="Short name to save this character as (e.g. 'main', 'alt1')")
    parser.add_argument("--port", type=int, default=8080,
                        help="Local callback port (default: 8080)")
    args = parser.parse_args()

    verifier, challenge = pkce_pair()
    state = secrets.token_urlsafe(16)
    redirect_uri = f"http://127.0.0.1:{args.port}/callback"

    auth_url = (
        "https://login.eveonline.com/v2/oauth/authorize/?"
        + urllib.parse.urlencode({
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "client_id": args.client_id,
            "scope": SCOPES,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        })
    )

    result = {}
    server_ready = threading.Event()

    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass  # suppress default logs

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != "/callback":
                self.send_response(404)
                self.end_headers()
                return

            params = urllib.parse.parse_qs(parsed.query)
            code = params.get("code", [None])[0]
            got_state = params.get("state", [None])[0]

            if got_state != state:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"State mismatch. Try again.")
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>Authorized! You can close this tab.</h2>")
            result["code"] = code
            threading.Thread(target=self.server.shutdown).start()

    httpd = http.server.HTTPServer(("127.0.0.1", args.port), CallbackHandler)

    print(f"\n{'='*60}")
    print("EVE SSO Auth Flow")
    print(f"{'='*60}")
    print(f"\nIf running on a remote server, set up SSH tunnel first:")
    print(f"  ssh -L {args.port}:127.0.0.1:{args.port} user@your-server -N")
    print(f"\nThen open this URL in your browser:")
    print(f"\n  {auth_url}\n")
    print(f"Waiting for callback on port {args.port}...")
    print(f"{'='*60}\n")

    httpd.serve_forever()

    if not result.get("code"):
        print("ERROR: No auth code received.")
        return

    print("Auth code received. Exchanging for tokens...")
    token_data = exchange_code(result["code"], verifier, args.client_id, redirect_uri)

    print("Verifying token...")
    char_info = verify_token(token_data["access_token"])

    char_id = char_info["CharacterID"]
    char_name = char_info["CharacterName"]

    tokens = load_tokens()
    tokens["characters"][args.char_name] = {
        "character_id": char_id,
        "character_name": char_name,
        "client_id": args.client_id,
        "refresh_token": token_data["refresh_token"],
    }
    save_tokens(tokens)

    print(f"\n✓ Authenticated as: {char_name} (ID: {char_id})")
    print(f"✓ Saved as key: '{args.char_name}'")
    print(f"✓ Tokens stored in: {TOKENS_FILE}")
    print(f"\nUsage:")
    print(f"  python get_token.py --char {args.char_name}")


if __name__ == "__main__":
    main()
