#!/usr/bin/env python3
"""Setup script for Strava OpenClaw skill"""
import json
import os
from stravalib.client import Client

print("🏃 Strava OpenClaw Skill Setup")
print("=" * 50)
print()

# Get credentials from user
print("First, create a Strava API app:")
print("1. Go to: https://www.strava.com/settings/api")
print("2. Click 'Create App'")
print("3. Fill in:")
print("   - Application Name: OpenClaw Strava")
print("   - Category: Tool or Analytics")
print("   - Website: http://localhost")
print("   - Authorization Callback Domain: localhost")
print()

client_id = input("Enter your Client ID: ").strip()
client_secret = input("Enter your Client Secret: ").strip()

if not client_id or not client_secret:
    print("❌ Client ID and Secret are required!")
    exit(1)

# Generate authorization URL
client = Client()
authorize_url = client.authorization_url(
    client_id=int(client_id),
    redirect_uri='http://localhost:8282/authorized',
    scope=['read', 'read_all', 'activity:read_all', 'profile:read_all']
)

print()
print("=" * 50)
print("Authorization Required")
print("=" * 50)
print()
print("Open this URL in your browser:")
print(authorize_url)
print()
print("After clicking 'Authorize', you'll be redirected to a URL that won't load.")
print("Copy the ENTIRE URL from your browser and paste it here.")
print()

redirect_url = input("Paste redirect URL: ").strip()

if not redirect_url or 'code=' not in redirect_url:
    print("❌ Invalid redirect URL!")
    exit(1)

# Extract code and exchange for token
try:
    code = client.parse_response_code(redirect_url)
    token_response = client.exchange_code_for_token(
        client_id=int(client_id),
        client_secret=client_secret,
        code=code
    )

    # Save credentials
    credentials = {
        'access_token': token_response['access_token'],
        'refresh_token': token_response['refresh_token'],
        'expires_at': token_response['expires_at'],
        'client_id': int(client_id),
        'client_secret': client_secret
    }

    config_path = os.path.expanduser('~/.strava_credentials.json')
    with open(config_path, 'w') as f:
        json.dump(credentials, f, indent=2)

    print()
    print("✅ Setup complete!")
    print(f"✅ Credentials saved to {config_path}")
    print()
    print("Test it:")
    print("  python3 strava_control.py recent")
    print("  python3 strava_control.py stats")
    print("  python3 strava_control.py last")

except Exception as e:
    print(f"❌ Error during setup: {e}")
    exit(1)
