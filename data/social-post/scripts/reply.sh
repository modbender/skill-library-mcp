#!/bin/bash
# Social Reply - Reply to tweets on Twitter and casts on Farcaster

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/../lib"

# Load libraries
source "$LIB_DIR/validate.sh"
source "$LIB_DIR/twitter.sh"
source "$LIB_DIR/farcaster.sh"
source "$LIB_DIR/links.sh"

# Defaults
REPLY_TWITTER=false
REPLY_FARCASTER=false
IMAGE_PATH=""
AUTO_TRUNCATE=false
DRY_RUN=false
SHORTEN_LINKS=false
AUTO_CONFIRM=false
TEXT=""
TWITTER_ID=""
FARCASTER_HASH=""
TWITTER_ACCOUNT="mr_crtee"  # Default account

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --twitter)
      REPLY_TWITTER=true
      TWITTER_ID="$2"
      shift 2
      ;;
    --farcaster)
      REPLY_FARCASTER=true
      FARCASTER_HASH="$2"
      shift 2
      ;;
    --image)
      IMAGE_PATH="$2"
      shift 2
      ;;
    --truncate)
      AUTO_TRUNCATE=true
      shift
      ;;
    --shorten-links)
      SHORTEN_LINKS=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --yes|-y)
      AUTO_CONFIRM=true
      shift
      ;;
    --account)
      TWITTER_ACCOUNT="$2"
      shift 2
      ;;
    --help|-h)
      cat <<EOF
Usage: reply.sh [OPTIONS] "Your reply text"

Reply to tweets on Twitter and/or casts on Farcaster.

Options:
  --twitter <tweet_id>       Reply to Twitter tweet with this ID
  --farcaster <cast_hash>    Reply to Farcaster cast with this hash
  --account <name>           Twitter account (mr_crtee or oxdasx, default: mr_crtee)
  --image <path>             Attach image to reply
  --truncate                 Auto-truncate if over limit
  --shorten-links            Shorten URLs to save characters
  --dry-run                  Preview without posting
  -y, --yes                  Skip confirmation prompt
  --help                     Show this help

Examples:
  # Reply to Twitter tweet
  reply.sh --twitter 1234567890 "Great point!"
  
  # Reply to Farcaster cast
  reply.sh --farcaster 0xabcd1234... "Interesting perspective!"
  
  # Reply to both (if same content)
  reply.sh --twitter 123 --farcaster 0xabc "Nice!"
  
  # Reply with image
  reply.sh --twitter 123 --image photo.jpg "Check this out"
  
  # Shorten links in reply
  reply.sh --twitter 123 --shorten-links "See https://example.com/very-long-url"

Platform Limits:
  Twitter:   252 characters (with 10% buffer)
  Farcaster: 288 bytes (with 10% buffer)

Getting IDs:
  Twitter:   Tweet ID is in the URL: twitter.com/user/status/[ID]
  Farcaster: Cast hash from URL: farcaster.xyz/~/conversations/[HASH]
             Or use "0x" prefixed hash

Costs:
  Twitter:   Consumption-based (pay per API request)
  Farcaster: 0.001 USDC per cast (deducted from custody wallet on Base)
EOF
      exit 0
      ;;
    *)
      TEXT="$1"
      shift
      ;;
  esac
done

# Validate inputs
if [ -z "$TEXT" ]; then
  echo "Error: No reply text provided"
  echo "Usage: reply.sh [OPTIONS] \"Your reply text\""
  echo "Try: reply.sh --help"
  exit 1
fi

if [ "$REPLY_TWITTER" = false ] && [ "$REPLY_FARCASTER" = false ]; then
  echo "Error: No platform specified. Use --twitter or --farcaster"
  echo "Try: reply.sh --help"
  exit 1
fi

if [ "$REPLY_TWITTER" = true ] && [ -z "$TWITTER_ID" ]; then
  echo "Error: Twitter ID required when using --twitter"
  exit 1
fi

if [ "$REPLY_FARCASTER" = true ] && [ -z "$FARCASTER_HASH" ]; then
  echo "Error: Farcaster hash required when using --farcaster"
  exit 1
fi

# Validate image path if provided
if [ -n "$IMAGE_PATH" ] && [ ! -f "$IMAGE_PATH" ]; then
  echo "Error: Image not found at $IMAGE_PATH"
  exit 1
fi

echo "=== Social Reply ==="
echo ""
echo "Reply text: $TEXT"
[ -n "$IMAGE_PATH" ] && echo "Image: $IMAGE_PATH"
echo ""
[ "$REPLY_TWITTER" = true ] && echo "→ Replying to Twitter tweet: $TWITTER_ID"
[ "$REPLY_FARCASTER" = true ] && echo "→ Replying to Farcaster cast: $FARCASTER_HASH"
echo ""

# Shorten links if requested
if [ "$SHORTEN_LINKS" = true ]; then
  echo "Shortening links..."
  ORIGINAL_LENGTH=${#TEXT}
  TEXT=$(shorten_links_in_text "$TEXT")
  NEW_LENGTH=${#TEXT}
  SAVED=$((ORIGINAL_LENGTH - NEW_LENGTH))
  if [ "$SAVED" -gt 0 ]; then
    echo "Saved $SAVED characters"
  fi
  echo ""
fi

# Validate character/byte limits
TWITTER_VALID=true
FARCASTER_VALID=true

if [ "$REPLY_TWITTER" = true ]; then
  validate_twitter "$TEXT" || TWITTER_VALID=false
fi

if [ "$REPLY_FARCASTER" = true ]; then
  validate_farcaster "$TEXT" || FARCASTER_VALID=false
fi

echo ""

# Handle validation failures
if { [ "$REPLY_TWITTER" = true ] && [ "$TWITTER_VALID" = false ]; } || \
   { [ "$REPLY_FARCASTER" = true ] && [ "$FARCASTER_VALID" = false ]; }; then
  
  if [ "$AUTO_TRUNCATE" = true ]; then
    echo "Auto-truncating text..."
    if [ "$REPLY_TWITTER" = true ] && [ "$TWITTER_VALID" = false ]; then
      TEXT=$(truncate_for_twitter "$TEXT")
      echo "Twitter text truncated to: $TEXT"
    fi
    if [ "$REPLY_FARCASTER" = true ] && [ "$FARCASTER_VALID" = false ]; then
      TEXT=$(truncate_for_farcaster "$TEXT")
      echo "Farcaster text truncated to: $TEXT"
    fi
  else
    echo ""
    echo "Text exceeds platform limits. Options:"
    echo "  1. Shorten your text and try again"
    echo "  2. Use --truncate flag to auto-truncate"
    echo "  3. Use --shorten-links to compress URLs"
    exit 1
  fi
fi

# Show draft preview
echo "=== Reply Preview ==="
echo ""
echo "Reply text:"
echo "─────────────────────────────────────────────"
echo "$TEXT"
echo "─────────────────────────────────────────────"
[ -n "$IMAGE_PATH" ] && echo "Image: $IMAGE_PATH"
echo ""
echo "Replying to:"
[ "$REPLY_TWITTER" = true ] && echo "  • Twitter tweet: $TWITTER_ID (as @${TWITTER_ACCOUNT})"
[ "$REPLY_FARCASTER" = true ] && echo "  • Farcaster cast: $FARCASTER_HASH"
echo ""

# Dry run mode
if [ "$DRY_RUN" = true ]; then
  echo "=== Dry Run (not actually replying) ==="
  [ "$REPLY_TWITTER" = true ] && echo "Would reply to Twitter tweet: $TWITTER_ID"
  [ "$REPLY_FARCASTER" = true ] && echo "Would reply to Farcaster cast: $FARCASTER_HASH"
  [ -n "$IMAGE_PATH" ] && echo "Would upload image: $IMAGE_PATH"
  exit 0
fi

# Confirmation prompt (skip if running non-interactively or with --yes flag)
if [ "$AUTO_CONFIRM" = false ] && [ -t 0 ]; then
  echo -n "Proceed with reply? (y/n): "
  read -r CONFIRM
  if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
  fi
  echo ""
elif [ "$AUTO_CONFIRM" = true ]; then
  echo "Auto-confirmed (--yes flag). Proceeding..."
  echo ""
fi

# Export Twitter account for library to use
export TWITTER_ACCOUNT

# Post replies
echo "=== Posting Replies ==="
echo ""

SUCCESS=true

# Twitter reply
if [ "$REPLY_TWITTER" = true ]; then
  echo "→ Replying to Twitter..."
  
  if [ -n "$IMAGE_PATH" ]; then
    # For Twitter replies with images, we need to upload image first and then post
    echo "Uploading image to Twitter..." >&2
    media_id=$(twitter_upload_image "$IMAGE_PATH")
    
    if [ $? -ne 0 ]; then
      echo "Failed to upload image to Twitter" >&2
      SUCCESS=false
    else
      echo "Image uploaded (media_id: $media_id)" >&2
      
      # Post reply with media using inline Python script
      source /home/phan_harry/.openclaw/.env
      
      result=$(python3 - "$TEXT" "$TWITTER_ID" "$media_id" <<'EOF'
import requests
from requests_oauthlib import OAuth1
import os
import sys
import json

text = sys.argv[1]
reply_to = sys.argv[2]
media_id = sys.argv[3]

consumer_key = os.environ['X_CONSUMER_KEY']
consumer_secret = os.environ['X_CONSUMER_SECRET']
access_token = os.environ['X_ACCESS_TOKEN']
access_token_secret = os.environ['X_ACCESS_TOKEN_SECRET']

auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)

url = "https://api.twitter.com/2/tweets"
payload = {
    "text": text,
    "reply": {
        "in_reply_to_tweet_id": reply_to
    },
    "media": {
        "media_ids": [media_id]
    }
}

response = requests.post(url, auth=auth, json=payload)

if response.status_code == 201:
    tweet = response.json()
    tweet_id = tweet['data']['id']
    print(f"✓ Twitter reply posted: https://twitter.com/user/status/{tweet_id}")
else:
    print(f"✗ Twitter reply failed: {response.status_code} - {response.text}", file=sys.stderr)
    exit(1)
EOF
)
      if [ $? -eq 0 ]; then
        echo "$result"
      else
        SUCCESS=false
      fi
    fi
  else
    # Text-only reply
    result=$(twitter_post_text "$TEXT" "$TWITTER_ID")
    if [ $? -eq 0 ]; then
      echo "✓ Twitter reply posted: https://twitter.com/user/status/$result"
    else
      SUCCESS=false
    fi
  fi
  echo ""
fi

# Farcaster reply
if [ "$REPLY_FARCASTER" = true ]; then
  echo "→ Replying to Farcaster..."
  
  if [ -n "$IMAGE_PATH" ]; then
    farcaster_post_with_image "$TEXT" "$IMAGE_PATH" "$FARCASTER_HASH" || SUCCESS=false
  else
    farcaster_post_text "$TEXT" "$FARCASTER_HASH" || SUCCESS=false
  fi
  echo ""
fi

if [ "$SUCCESS" = true ]; then
  echo "✅ Done!"
else
  echo "⚠️ Some replies failed. Check output above."
  exit 1
fi
