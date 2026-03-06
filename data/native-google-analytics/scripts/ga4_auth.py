#!/usr/bin/env python3
"""
One-time OAuth flow to get a refresh token for GA4.
Run once, then store the printed refresh token as GOOGLE_REFRESH_TOKEN.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    print("Error: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set", file=sys.stderr)
    sys.exit(1)

SCOPE = "https://www.googleapis.com/auth/analytics.readonly"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"

auth_url = (
    "https://accounts.google.com/o/oauth2/auth?"
    + urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "response_type": "code",
        "access_type": "offline",
    })
)

print("\n1. Open this URL in your browser:\n")
print(auth_url)
print("\n2. Authorize and paste the code below:")
code = input("Authorization code: ").strip()

data = urllib.parse.urlencode({
    "code": code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI,
    "grant_type": "authorization_code",
}).encode()

req = urllib.request.Request(
    "https://oauth2.googleapis.com/token",
    data=data,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)

try:
    with urllib.request.urlopen(req) as resp:
        tokens = json.loads(resp.read())
except urllib.error.HTTPError as e:
    print(f"Error: {e.read().decode()}", file=sys.stderr)
    sys.exit(1)

if "refresh_token" not in tokens:
    print("Error: No refresh token returned. Make sure you revoked previous access first.", file=sys.stderr)
    sys.exit(1)

print("\n✓ Success! Add this to your environment:\n")
print(f"export GOOGLE_REFRESH_TOKEN={tokens['refresh_token']}")
