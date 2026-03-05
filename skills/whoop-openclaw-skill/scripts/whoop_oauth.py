#!/usr/bin/env python3
"""
Whoop OAuth helper - generates auth URL and exchanges code for token

Usage:
  1. Create whoop-config.json with your app credentials:
     {
       "client_id": "your-client-id",
       "client_secret": "your-client-secret",
       "redirect_uri": "https://yourdomain.com/redirect.html"
     }
  
  2. Generate auth URL:
     python3 whoop_oauth.py --config whoop-config.json
  
  3. Authorize and get code from redirect page
  
  4. Exchange code for token:
     python3 whoop_oauth.py --config whoop-config.json exchange <CODE>
"""

import sys
import json
import argparse
import requests
from urllib.parse import urlencode
from pathlib import Path

AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
DEFAULT_TOKEN_FILE = Path.home() / ".whoop_token"

def load_config(config_file):
    """Load OAuth config from JSON file"""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        required = ['client_id', 'client_secret', 'redirect_uri']
        missing = [k for k in required if k not in config]
        
        if missing:
            print(f"❌ Error: Missing required fields in config: {', '.join(missing)}")
            print("\nRequired format:")
            print(json.dumps({k: f"your-{k.replace('_', '-')}" for k in required}, indent=2))
            sys.exit(1)
        
        return config
    except FileNotFoundError:
        print(f"❌ Error: Config file not found: {config_file}")
        print("\nCreate a whoop-config.json file with:")
        print(json.dumps({
            "client_id": "your-client-id",
            "client_secret": "your-client-secret",
            "redirect_uri": "https://yourdomain.com/redirect.html"
        }, indent=2))
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in config file: {e}")
        sys.exit(1)

def generate_auth_url(config):
    """Generate authorization URL"""
    import secrets
    state = secrets.token_urlsafe(16)  # Generate random state for CSRF protection
    
    params = {
        "response_type": "code",
        "client_id": config['client_id'],
        "redirect_uri": config['redirect_uri'],
        "scope": "read:recovery read:sleep read:cycles read:workout read:profile",
        "state": state
    }
    
    url = f"{AUTH_URL}?{urlencode(params)}"
    
    print("=" * 70)
    print("🔗 STEP 1: AUTHORIZE YOUR APP")
    print("=" * 70)
    print("\nClick or copy this URL to your browser:")
    print(f"\n{url}\n")
    print(f"🔐 State (for verification): {state}")
    print("\n" + "=" * 70)
    print("📋 NEXT STEPS:")
    print("=" * 70)
    print("1. Click the link above")
    print("2. Log in to your Whoop account")
    print("3. Click 'Authorize' to grant access")
    print("4. You'll be redirected to your callback page")
    print("5. Copy the authorization CODE from the page")
    print("6. Run:")
    print(f"   python3 {sys.argv[0]} --config {sys.argv[2]} exchange <CODE>")
    print("=" * 70)

def exchange_code(config, code):
    """Exchange authorization code for access token"""
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": config['client_id'],
        "client_secret": config['client_secret'],
        "redirect_uri": config['redirect_uri']
    }
    
    print("🔄 Exchanging authorization code for access token...")
    
    try:
        response = requests.post(TOKEN_URL, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in")
            
            print("\n" + "=" * 70)
            print("✅ SUCCESS! Access token received")
            print("=" * 70)
            print(f"\n🔑 Access Token:\n{access_token[:20]}...{access_token[-20:]}")
            
            if refresh_token:
                print(f"\n🔄 Refresh Token:\n{refresh_token[:20]}...{refresh_token[-20:]}")
            
            hours = expires_in // 3600 if expires_in else 0
            print(f"\n⏰ Token expires in: {expires_in} seconds (~{hours} hours)")
            
            # Save both access and refresh tokens
            DEFAULT_TOKEN_FILE.write_text(access_token)
            print(f"\n💾 Access token saved to: {DEFAULT_TOKEN_FILE}")
            
            if refresh_token:
                refresh_file = DEFAULT_TOKEN_FILE.parent / ".whoop_refresh_token"
                refresh_file.write_text(refresh_token)
                print(f"💾 Refresh token saved to: {refresh_file}")
                print("\n✨ Refresh token will auto-renew your access token when it expires!")
            print("\n" + "=" * 70)
            print("🎉 SETUP COMPLETE!")
            print("=" * 70)
            print("\nTest your connection:")
            print("  python3 scripts/whoop_client.py --action profile")
            print("=" * 70)
            
            return access_token
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 400:
                print("\n💡 Troubleshooting:")
                print("- Make sure the authorization code hasn't expired (use it within a few minutes)")
                print("- Verify your client_id and client_secret are correct")
                print("- Check that redirect_uri matches exactly what you configured in Whoop")
            
            return None
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Network error: {e}")
        return None

def refresh_access_token():
    """Refresh access token using saved refresh token"""
    refresh_token_file = DEFAULT_TOKEN_FILE.parent / ".whoop_refresh_token"
    
    if not refresh_token_file.exists():
        print("❌ No refresh token found. Run authorization first.")
        sys.exit(1)
    
    refresh_token = refresh_token_file.read_text().strip()
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    print("🔄 Refreshing access token...")
    response = requests.post(TOKEN_URL, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        new_access = token_data.get("access_token")
        new_refresh = token_data.get("refresh_token")
        
        DEFAULT_TOKEN_FILE.write_text(new_access)
        if new_refresh:
            refresh_token_file.write_text(new_refresh)
        
        print("\n✅ Token refreshed successfully!")
        print(f"💾 Saved to: {DEFAULT_TOKEN_FILE}")
    else:
        print(f"\n❌ Refresh failed: {response.status_code}")
        print(response.text)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Whoop OAuth helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate authorization URL
  python3 whoop_oauth.py --config whoop-config.json
  
  # Exchange code for token
  python3 whoop_oauth.py --config whoop-config.json exchange <CODE>
  
  # Refresh expired token (no re-auth needed!)
  python3 whoop_oauth.py refresh

Config file format (whoop-config.json):
  {
    "client_id": "your-client-id-from-whoop",
    "client_secret": "your-client-secret-from-whoop",
    "redirect_uri": "https://yourdomain.com/redirect.html"
  }
        """
    )
    parser.add_argument('--config', help='Path to OAuth config JSON file')
    parser.add_argument('action', nargs='?', choices=['exchange', 'refresh'], help='Action to perform')
    parser.add_argument('code', nargs='?', help='Authorization code (for exchange action)')
    
    args = parser.parse_args()
    
    if args.action == 'refresh':
        refresh_access_token()
        return
    
    if not args.config:
        print("❌ Error: --config required (except for refresh action)")
        parser.print_help()
        sys.exit(1)
    
    config = load_config(args.config)
    
    if args.action == 'exchange':
        if not args.code:
            print("❌ Error: Authorization code required for exchange action")
            print(f"Usage: python3 {sys.argv[0]} --config {args.config} exchange <CODE>")
            sys.exit(1)
        exchange_code(config, args.code)
    else:
        # Generate auth URL
        generate_auth_url(config)

if __name__ == "__main__":
    main()
