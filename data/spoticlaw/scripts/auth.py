#!/usr/bin/env python3
"""
Spotify Authentication Helper (Manual Token Transfer Mode)

This script generates an authorization URL. After user authorizes,
the token is saved locally. User then copies .spotify_cache to the agent.

This keeps tokens secure - never passes through AI model.

Usage:
    1. Run: python auth.py
    2. Open the displayed URL in browser
    3. Authorize the app
    4. Copy .spotify_cache file to your agent's folder:
       - Linux/Mac: cp .spotify_cache /path/to/agent/skills/spoticlaw/
       - Windows: copy .spotify_cache C:\path\to\agent\skills\spoticlaw\

For remote agents: run auth locally, then copy the cache file over.
"""

import os
import json
import socket
import webbrowser
from urllib.parse import urlencode
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

# Load config
load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")

# OAuth scopes (space-separated)
SCOPES = [
    "user-read-playback-state",
    "user-modify-playback-state",
    "playlist-read-private",
    "playlist-modify-public",
    "playlist-modify-private",
    "user-library-read",
    "user-library-modify",
    "user-read-recently-played",
    "user-top-read",
    "user-follow-read",
]

SCOPE = " ".join(SCOPES)


class AuthHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback."""
    
    def do_GET(self):
        if "/callback" in self.path:
            # Parse code from query
            query = self.path.split("?")[1] if "?" in self.path else ""
            params = dict(p.split("=") for p in query.split("&") if "=" in p)
            
            if "code" in params:
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>Authentication successful!</h1><p>You can close this window.</p>")
                global auth_code
                auth_code = params["code"]
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"<h1>Authentication failed.</h1>")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress logging


def get_token():
    """Exchange code for token."""
    import requests
    
    # Start local server
    server = HTTPServer(("localhost", 8888), AuthHandler)
    
    # Build auth URL
    auth_url = "https://accounts.spotify.com/authorize?" + urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
    })
    
    print(f"\nOpening browser for authentication...")
    print(f"If browser doesn't open, go to:\n{auth_url}\n")
    webbrowser.open(auth_url)
    
    # Wait for callback
    print("Waiting for callback...")
    server.handle_request()
    
    if not auth_code:
        print("No auth code received.")
        return
    
    # Exchange for token
    print("Exchanging code for token...")
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
    )
    
    if resp.status_code == 200:
        token = resp.json()
        # Calculate expires_at timestamp
        import time
        token["expires_at"] = time.time() + token.get("expires_in", 3600)
        
        # Save to cache
        cache_file = ".spotify_cache"
        with open(cache_file, "w") as f:
            json.dump(token, f)
        print(f"Token saved to {cache_file}")
        print(f"Scopes: {token.get('scope', '')}")
        print(f"Expires in: {token.get('expires_in')} seconds")
    else:
        print(f"Error: {resp.text}")


if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET not set in .env")
        print("See: https://github.com/your-repo/spoticlaw#setup")
    else:
        get_token()
