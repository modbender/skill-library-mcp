#!/usr/bin/env python3
"""
Simple OAuth1 3-legged authentication script for FatSecret.
Guides the user step-by-step to obtain access tokens.
"""

import json
import os
import sys
import time
import hashlib
import hmac
import base64
import urllib.parse
import requests

# Configuration - use FATSECRET_CONFIG_DIR env var for persistent storage in containers
CONFIG_DIR = os.environ.get("FATSECRET_CONFIG_DIR", os.path.expanduser("~/.config/fatsecret"))
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
TOKENS_FILE = os.path.join(CONFIG_DIR, "oauth1_access_tokens.json")

# OAuth1 URLs
REQUEST_TOKEN_URL = "https://authentication.fatsecret.com/oauth/request_token"
AUTHORIZE_URL = "https://authentication.fatsecret.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://authentication.fatsecret.com/oauth/access_token"

# Proxy configuration (optional - only if FatSecret requires IP whitelisting)
def get_proxies():
    """Get proxy configuration from environment or config file."""
    proxy_url = os.environ.get("FATSECRET_PROXY")
    if not proxy_url and os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                config = json.load(f)
                proxy_url = config.get("proxy")
        except:
            pass
    if proxy_url:
        return {"http": proxy_url, "https": proxy_url}
    return None  # No proxy by default

PROXIES = get_proxies()

def load_config():
    """Load configuration."""
    if not os.path.exists(CONFIG_FILE):
        print("❌ Configuration not found!")
        print(f"Create file: {CONFIG_FILE}")
        print("""
config.json content:
{
  "consumer_key": "YOUR_CONSUMER_KEY",
  "consumer_secret": "YOUR_CONSUMER_SECRET"
}
""")
        sys.exit(1)
    
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    
    consumer_key = config.get("consumer_key")
    consumer_secret = config.get("consumer_secret")
    
    if not consumer_key or not consumer_secret:
        print("❌ Missing credentials in configuration file!")
        sys.exit(1)
    
    return consumer_key, consumer_secret

def make_oauth_request(method, url, params, consumer_key, consumer_secret, token_secret=""):
    """Create an OAuth1 signed request."""
    # Add standard OAuth parameters
    oauth_params = {
        "oauth_consumer_key": consumer_key,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_nonce": hashlib.md5(str(time.time()).encode()).hexdigest(),
        "oauth_version": "1.0"
    }
    
    # Add oauth_token if present
    if "oauth_token" in params:
        oauth_params["oauth_token"] = params["oauth_token"]
    
    # Combine all parameters
    all_params = {**params, **oauth_params}
    
    # Sort parameters
    sorted_params = sorted(all_params.items())
    
    # Create signature string
    parameter_string = "&".join([f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in sorted_params])
    base_string = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(parameter_string, safe='')}"
    
    # Calculate signature
    signing_key = f"{consumer_secret}&{token_secret}"
    signature = base64.b64encode(hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()).decode()
    
    # Add signature
    oauth_params["oauth_signature"] = signature
    
    # Create Authorization header
    auth_header = "OAuth " + ", ".join([f'{k}="{urllib.parse.quote(str(v), safe="")}"' for k, v in oauth_params.items()])
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # Make request
    if method == "GET":
        response = requests.get(url, params=params, headers=headers, proxies=PROXIES)
    else:  # POST
        response = requests.post(url, data=params, headers=headers, proxies=PROXIES)
    
    return response

def step1_get_request_token(consumer_key, consumer_secret):
    """Step 1: Get request token."""
    print("\n" + "="*60)
    print("STEP 1: Getting Request Token")
    print("="*60)
    
    params = {
        "oauth_callback": "oob",  # out-of-band (no callback URL)
        "oauth_consumer_key": consumer_key
    }
    
    print("Requesting...")
    response = make_oauth_request("POST", REQUEST_TOKEN_URL, params, consumer_key, consumer_secret)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None, None
    
    # Parse response
    response_params = dict(urllib.parse.parse_qsl(response.text))
    oauth_token = response_params.get("oauth_token")
    oauth_token_secret = response_params.get("oauth_token_secret")
    
    if not oauth_token or not oauth_token_secret:
        print("❌ Tokens not received in response!")
        return None, None
    
    print(f"✅ Request Token: {oauth_token}")
    print(f"✅ Request Token Secret: {oauth_token_secret}")
    
    return oauth_token, oauth_token_secret

def step2_get_authorization_url(oauth_token):
    """Step 2: Generate authorization URL."""
    print("\n" + "="*60)
    print("STEP 2: User Authorization")
    print("="*60)
    
    auth_url = f"{AUTHORIZE_URL}?oauth_token={oauth_token}"
    
    print("🔗 Authorization URL:")
    print(f"\n{auth_url}\n")
    print("📋 Instructions:")
    print("1. Visit the URL above in your browser")
    print("2. Log in with your FatSecret account (if not already logged in)")
    print("3. Authorize the application")
    print("4. Copy the PIN/verifier code shown")
    
    return auth_url

def step3_get_access_token(consumer_key, consumer_secret, oauth_token, oauth_token_secret):
    """Step 3: Get access token with PIN."""
    print("\n" + "="*60)
    print("STEP 3: Getting Access Token")
    print("="*60)
    
    # Ask user for PIN
    verifier = input("\nEnter the PIN/verifier code: ").strip()
    
    if not verifier:
        print("❌ PIN not provided!")
        return None, None
    
    params = {
        "oauth_token": oauth_token,
        "oauth_verifier": verifier,
        "oauth_consumer_key": consumer_key
    }
    
    print("Requesting...")
    response = make_oauth_request("GET", ACCESS_TOKEN_URL, params, consumer_key, consumer_secret, oauth_token_secret)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None, None
    
    # Parse response
    response_params = dict(urllib.parse.parse_qsl(response.text))
    access_token = response_params.get("oauth_token")
    access_token_secret = response_params.get("oauth_token_secret")
    
    if not access_token or not access_token_secret:
        print("❌ Access tokens not received!")
        return None, None
    
    print(f"✅ Access Token: {access_token}")
    print(f"✅ Access Token Secret: {access_token_secret}")
    
    return access_token, access_token_secret

def save_tokens(access_token, access_token_secret, consumer_key, consumer_secret):
    """Save access tokens."""
    print("\n" + "="*60)
    print("STEP 4: Saving Tokens")
    print("="*60)
    
    token_data = {
        "access_token": access_token,
        "access_token_secret": access_token_secret,
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret,
        "created": time.time(),
        "created_human": time.ctime()
    }
    
    # Create directory if needed
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # Save file
    with open(TOKENS_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print(f"✅ Tokens saved to: {TOKENS_FILE}")
    print("\n🔐 These tokens allow you to:")
    print("   - Read your food diary")
    print("   - Add foods to diary")
    print("   - Access your personal data")
    
    return TOKENS_FILE

def test_api_access(consumer_key, consumer_secret, access_token, access_token_secret):
    """Test API access."""
    print("\n" + "="*60)
    print("TEST: Verifying API Access")
    print("="*60)
    
    params = {
        "format": "json",
        "method": "foods.search",
        "search_expression": "apple",
        "max_results": "1",
        "oauth_token": access_token,
        "oauth_consumer_key": consumer_key
    }
    
    response = make_oauth_request("GET", "https://platform.fatsecret.com/rest/server.api", 
                                 params, consumer_key, consumer_secret, access_token_secret)
    
    if response.status_code == 200:
        print("✅ API connection successful!")
        data = response.json()
        if "foods" in data and "food" in data["foods"]:
            food = data["foods"]["food"]
            if isinstance(food, list):
                food = food[0]
            print(f"   Example: {food.get('food_name')}")
    else:
        print(f"❌ API error: {response.status_code}")
        print(f"   Message: {response.text[:200]}")

def main():
    """Main authentication flow."""
    print("="*60)
    print("FATSECRET OAuth1 3-LEGGED AUTHENTICATION")
    print("="*60)
    print("\nThis script guides you step-by-step through OAuth1 authentication")
    print("to access your FatSecret diary.\n")
    
    # Note about proxy
    if PROXIES:
        print(f"ℹ️  Using proxy: {PROXIES.get('http')}\n")
    else:
        print("ℹ️  No proxy configured (set FATSECRET_PROXY if needed)\n")
    
    # Load configuration
    consumer_key, consumer_secret = load_config()
    print(f"✅ Configuration loaded from: {CONFIG_FILE}")
    
    # Step 1: Request token
    oauth_token, oauth_token_secret = step1_get_request_token(consumer_key, consumer_secret)
    if not oauth_token:
        return
    
    # Step 2: Authorization URL
    auth_url = step2_get_authorization_url(oauth_token)
    
    # Pause to let user authorize
    input("\nPress ENTER when you have authorized the app and have the PIN...")
    
    # Step 3: Access token
    access_token, access_token_secret = step3_get_access_token(
        consumer_key, consumer_secret, oauth_token, oauth_token_secret
    )
    if not access_token:
        return
    
    # Step 4: Save tokens
    tokens_file = save_tokens(access_token, access_token_secret, consumer_key, consumer_secret)
    
    # Step 5: Test API
    test_api_access(consumer_key, consumer_secret, access_token, access_token_secret)
    
    print("\n" + "="*60)
    print("✅ AUTHENTICATION COMPLETE!")
    print("="*60)
    print("\nYou can now use the tokens to:")
    print("1. Search foods")
    print("2. Add foods to diary")
    print("3. Read your food diary")
    print(f"\nTokens saved in: {tokens_file}")

def load_tokens():
    """Load saved tokens (for use in other scripts)."""
    if not os.path.exists(TOKENS_FILE):
        return None
    
    with open(TOKENS_FILE) as f:
        return json.load(f)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        sys.exit(1)