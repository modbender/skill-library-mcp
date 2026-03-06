#!/usr/bin/env python3
"""
Spotify OAuth Authorization Flow.
Supports both local callback server and manual code exchange.

Usage:
  1. Start auth:  python3 auth.py --client-id <ID> --client-secret <SECRET>
  2. Exchange code: python3 auth.py --client-id <ID> --client-secret <SECRET> --code-url <URL>
  3. Refresh token: python3 auth.py --refresh

Tokens stored in ~/.openclaw/workspace/config/.spotify-tokens.json
"""

import argparse
import json
import http.server
import urllib.parse
import requests
import sys
import os
import base64

TOKEN_PATH = os.path.expanduser("~/.openclaw/workspace/config/.spotify-tokens.json")
REDIRECT_URI = "http://127.0.0.1:8765/callback"
SCOPES = (
    "playlist-modify-public playlist-modify-private playlist-read-private "
    "user-library-read user-read-recently-played user-top-read"
)


def save_tokens(data):
    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
    existing = {}
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH) as f:
            existing = json.load(f)
    existing.update(data)
    with open(TOKEN_PATH, "w") as f:
        json.dump(existing, f, indent=2)
    os.chmod(TOKEN_PATH, 0o600)
    print(f"Tokens saved to {TOKEN_PATH}")


def load_tokens():
    if not os.path.exists(TOKEN_PATH):
        print("No tokens found. Run auth.py with --client-id and --client-secret first.", file=sys.stderr)
        sys.exit(1)
    with open(TOKEN_PATH) as f:
        return json.load(f)


def exchange_code(code, client_id, client_secret):
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    resp = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }, headers={"Authorization": f"Basic {auth_header}"})
    resp.raise_for_status()
    tokens = resp.json()
    save_tokens({
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "client_id": client_id,
        "client_secret": client_secret,
    })
    print("Authorization successful!")


def refresh_token():
    tokens = load_tokens()
    if not tokens.get("refresh_token"):
        print("No refresh token found. Re-authorize.", file=sys.stderr)
        sys.exit(1)
    auth_header = base64.b64encode(
        f"{tokens['client_id']}:{tokens['client_secret']}".encode()
    ).decode()
    resp = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
    }, headers={"Authorization": f"Basic {auth_header}"})
    resp.raise_for_status()
    new_tokens = resp.json()
    save_tokens({
        "access_token": new_tokens["access_token"],
        "refresh_token": new_tokens.get("refresh_token", tokens["refresh_token"]),
    })
    print("Token refreshed successfully!")
    print(json.dumps({"access_token": new_tokens["access_token"]}))


def get_auth_url(client_id):
    return (
        "https://accounts.spotify.com/authorize?"
        + urllib.parse.urlencode({
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPES,
            "show_dialog": "true",
        })
    )


def authorize(client_id, client_secret, code=None):
    if code:
        exchange_code(code, client_id, client_secret)
        return

    auth_url = get_auth_url(client_id)
    print(f"\nOpen this URL to authorize:\n\n{auth_url}\n")
    print("After authorizing, you'll be redirected to a URL like:")
    print("  http://127.0.0.1:8765/callback?code=AQ...")
    print("\nIf the page loads, you're done. If it doesn't load,")
    print("copy the full URL and re-run with --code-url <URL>\n")

    # Try local callback server
    code_holder = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            if "code" in params:
                code_holder["code"] = params["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h2>Authorization successful!</h2>"
                    b"<p>You can close this tab.</p></body></html>"
                )
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Authorization failed - no code received.")

        def log_message(self, *args):
            pass

    try:
        server = http.server.HTTPServer(("127.0.0.1", 8765), Handler)
        print("Listening on http://127.0.0.1:8765 for callback...\n")
        server.timeout = 300
        server.handle_request()
        server.server_close()
        if "code" in code_holder:
            exchange_code(code_holder["code"], client_id, client_secret)
        else:
            print("No code received. Use --code-url to exchange manually.")
    except OSError as e:
        print(f"Could not start local server ({e}). Use --code-url to exchange manually.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spotify OAuth")
    parser.add_argument("--client-id", help="Spotify Client ID")
    parser.add_argument("--client-secret", help="Spotify Client Secret")
    parser.add_argument("--refresh", action="store_true", help="Refresh access token")
    parser.add_argument("--code", help="Authorization code (extracted from URL)")
    parser.add_argument("--code-url", help="Full callback URL (code extracted automatically)")
    args = parser.parse_args()

    code = args.code
    if args.code_url:
        parsed = urllib.parse.urlparse(args.code_url)
        params = urllib.parse.parse_qs(parsed.query)
        code = params.get("code", [None])[0]
        if not code:
            print("Could not extract code from URL.", file=sys.stderr)
            sys.exit(1)

    if args.refresh:
        refresh_token()
    elif args.client_id and args.client_secret:
        authorize(args.client_id, args.client_secret, code=code)
    else:
        parser.print_help()
        sys.exit(1)
