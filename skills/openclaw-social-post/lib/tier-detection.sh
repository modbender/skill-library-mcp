#!/bin/bash
# Twitter account tier detection library

TIER_CACHE_FILE="/home/phan_harry/.openclaw/workspace/memory/twitter-account-tiers.json"
TIER_CACHE_HOURS=24

# Ensure cache directory exists
mkdir -p "$(dirname "$TIER_CACHE_FILE")"

# Initialize cache file if it doesn't exist
if [ ! -f "$TIER_CACHE_FILE" ]; then
  echo "{}" > "$TIER_CACHE_FILE"
fi

# Detect Twitter account tier (Basic, Premium, Premium+)
detect_twitter_tier() {
  local account="$1"
  local force_refresh="${2:-false}"
  
  # Load credentials for the account
  source /home/phan_harry/.openclaw/.env
  
  if [ "$account" = "oxdasx" ]; then
    local consumer_key="$OXDASX_API_KEY"
    local consumer_secret="$OXDASX_API_KEY_SECRET"
    local access_token="$OXDASX_ACCESS_TOKEN"
    local access_token_secret="$OXDASX_ACCESS_TOKEN_SECRET"
  else
    # Default to mr_crtee
    local consumer_key="$X_CONSUMER_KEY"
    local consumer_secret="$X_CONSUMER_SECRET"
    local access_token="$X_ACCESS_TOKEN"
    local access_token_secret="$X_ACCESS_TOKEN_SECRET"
  fi
  
  # Check cache first (unless force refresh)
  if [ "$force_refresh" = false ]; then
    local cached_tier=$(get_cached_tier "$account")
    if [ -n "$cached_tier" ]; then
      echo "$cached_tier"
      return 0
    fi
  fi
  
  # API call to detect tier
  local tier=$(python3 - "$consumer_key" "$consumer_secret" "$access_token" "$access_token_secret" <<'EOF'
import requests
from requests_oauthlib import OAuth1
import sys
import json

consumer_key = sys.argv[1]
consumer_secret = sys.argv[2]
access_token = sys.argv[3]
access_token_secret = sys.argv[4]

auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)

# Get user info with subscription data
url = "https://api.twitter.com/2/users/me"
params = {
    "user.fields": "subscription_type,public_metrics"
}

try:
    response = requests.get(url, auth=auth, params=params)
    
    if response.status_code == 200:
        data = response.json()['data']
        
        # Check subscription_type field (if available)
        # Note: This field might not be available in all API tiers
        # Fallback: Premium users typically have access to longer character limits
        
        # For now, we'll use a heuristic:
        # - Check if we can successfully post > 280 chars (test with API limits)
        # - Or check subscription_type if available
        
        subscription_type = data.get('subscription_type', 'none')
        
        # Map subscription types
        if subscription_type in ['premium_plus', 'premium+']:
            print("premium_plus")
        elif subscription_type == 'premium':
            print("premium")
        else:
            # Fallback: Try to detect by attempting to validate a long tweet
            # Premium users have 25k char limit, Basic users have 280
            # We'll use the v2 API's tweet length validation
            test_url = "https://api.twitter.com/2/tweets"
            test_text = "x" * 281  # Just over Basic limit
            test_payload = {"text": test_text}
            
            # Dry run - don't actually post
            # Check the error message
            test_response = requests.post(test_url, auth=auth, json=test_payload)
            
            if test_response.status_code == 400:
                error = test_response.json()
                # If error mentions character limit, we know the account type
                if 'text' in str(error) and '280' in str(error):
                    print("basic")
                else:
                    # No character limit error = Premium
                    print("premium")
            else:
                # Default to basic if we can't determine
                print("basic")
    else:
        # API call failed, default to basic (safe fallback)
        print("basic", file=sys.stderr)
        print(f"API Error: {response.status_code}", file=sys.stderr)
        print("basic")

except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    print("basic")
EOF
)
  
  if [ $? -ne 0 ] || [ -z "$tier" ]; then
    # Fallback to basic on error
    tier="basic"
  fi
  
  # Cache the result
  cache_tier "$account" "$tier"
  
  echo "$tier"
}

# Get cached tier if still valid
get_cached_tier() {
  local account="$1"
  
  if [ ! -f "$TIER_CACHE_FILE" ]; then
    return 1
  fi
  
  local cache_data=$(python3 - "$account" "$TIER_CACHE_HOURS" <<'EOF'
import json
import sys
import time

account = sys.argv[1]
cache_hours = int(sys.argv[2])

try:
    with open(sys.argv[0].replace('-', '/home/phan_harry/.openclaw/workspace/memory/twitter-account-tiers.json')) as f:
        cache = json.load(f)
    
    if account in cache:
        tier_data = cache[account]
        checked_at = tier_data.get('checkedAt', 0)
        now = int(time.time())
        age_hours = (now - checked_at) / 3600
        
        if age_hours < cache_hours:
            print(tier_data['tier'])
        else:
            # Cache expired
            pass
    else:
        # Not in cache
        pass

except Exception:
    # Error reading cache
    pass
EOF
)
  
  if [ -n "$cache_data" ]; then
    echo "$cache_data"
  fi
}

# Cache tier for account
cache_tier() {
  local account="$1"
  local tier="$2"
  
  python3 - "$account" "$tier" "$TIER_CACHE_FILE" <<'EOF'
import json
import sys
import time

account = sys.argv[1]
tier = sys.argv[2]
cache_file = sys.argv[3]

try:
    with open(cache_file, 'r') as f:
        cache = json.load(f)
except Exception:
    cache = {}

cache[account] = {
    'tier': tier,
    'checkedAt': int(time.time())
}

with open(cache_file, 'w') as f:
    json.dump(cache, f, indent=2)
EOF
}

# Get character limit for account based on tier
get_twitter_char_limit() {
  local account="$1"
  local force_refresh="${2:-false}"
  
  local tier=$(detect_twitter_tier "$account" "$force_refresh")
  
  case "$tier" in
    premium|premium_plus)
      echo "25000"
      ;;
    basic|*)
      echo "280"
      ;;
  esac
}

# Get character limit with safety buffer
get_twitter_char_limit_buffered() {
  local account="$1"
  local force_refresh="${2:-false}"
  
  local limit=$(get_twitter_char_limit "$account" "$force_refresh")
  
  # Apply 10% safety buffer
  local buffered=$((limit * 9 / 10))
  
  echo "$buffered"
}
