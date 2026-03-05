#!/bin/bash
# Social Post - Post to Twitter and/or Farcaster

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/../lib"

# Load libraries
source "$LIB_DIR/validate.sh"
source "$LIB_DIR/twitter.sh"
source "$LIB_DIR/farcaster.sh"
source "$LIB_DIR/threads.sh"
source "$LIB_DIR/links.sh"
source "$LIB_DIR/variation.sh"

# Defaults
POST_TWITTER=false
POST_FARCASTER=false
IMAGE_PATH=""
AUTO_TRUNCATE=false
DRY_RUN=false
THREAD_MODE=false
SHORTEN_LINKS=false
AUTO_CONFIRM=false
VARY_TEXT=false
TEXT=""
TWITTER_ACCOUNT="mr_crtee"  # Default account
REFRESH_TIER=false
FORCE_THREAD=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --twitter)
      POST_TWITTER=true
      shift
      ;;
    --farcaster)
      POST_FARCASTER=true
      shift
      ;;
    --image)
      IMAGE_PATH="$2"
      shift 2
      ;;
    --truncate)
      AUTO_TRUNCATE=true
      shift
      ;;
    --thread)
      THREAD_MODE=true
      FORCE_THREAD=true
      shift
      ;;
    --refresh-tier)
      REFRESH_TIER=true
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
    --vary)
      VARY_TEXT=true
      shift
      ;;
    --help|-h)
      cat <<EOF
Usage: post.sh [OPTIONS] "Your message"

Post to Twitter and/or Farcaster with text and optional image.

Options:
  --twitter         Post to Twitter only
  --farcaster       Post to Farcaster only
  --account <name>  Twitter account (mr_crtee or oxdasx, default: mr_crtee)
  --vary            Auto-vary text to avoid duplicate content detection
  --image <path>    Attach image
  --truncate        Auto-truncate if over limit
  --thread          Force thread mode (split into multiple posts)
  --refresh-tier    Force refresh account tier cache (Basic vs Premium)
  --shorten-links   Shorten URLs to save characters
  --dry-run         Preview without posting
  -y, --yes         Skip all confirmation prompts
  --help            Show this help

Examples:
  post.sh "gm!"                                        # Both platforms (mr_crtee)
  post.sh --twitter "Twitter only"                     # Twitter only (mr_crtee)
  post.sh --account oxdasx --twitter "From 0xdas"      # Twitter as @0xdasx
  post.sh --vary --twitter "Same text, auto-varied"    # Auto-vary to avoid dupes
  post.sh --farcaster "Farcaster only"                 # Farcaster only
  post.sh --image photo.jpg "Check this out"          # Both with image
  post.sh --thread "Very long text..."                # Auto-thread
  post.sh --shorten-links "Check https://example.com" # Shorten URLs
  post.sh --twitter --image pic.png "New feature"     # Twitter with image

Platform Limits:
  Twitter:   Auto-detected based on account tier (cached for 24h)
             - Basic/Free: 252 chars (280 - 10% buffer)
             - Premium/Premium+: 22,500 chars (25,000 - 10% buffer)
  Farcaster: 288 bytes (320 - 10% buffer)

Tier Detection:
  The skill automatically detects your Twitter account tier on first use.
  Premium accounts can post up to 25k characters in a single tweet.
  Basic accounts are limited to 280 characters per tweet.
  Use --refresh-tier to force a tier re-check (if subscription changed).

Costs:
  Twitter:   Consumption-based (pay per API request, no tiers/subscriptions)
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

# If no platform specified, post to both
if [ "$POST_TWITTER" = false ] && [ "$POST_FARCASTER" = false ]; then
  POST_TWITTER=true
  POST_FARCASTER=true
fi

# Validate text provided
if [ -z "$TEXT" ]; then
  echo "Error: No text provided"
  echo "Usage: post.sh [OPTIONS] \"Your message\""
  echo "Try: post.sh --help"
  exit 1
fi

# Validate image path if provided
if [ -n "$IMAGE_PATH" ] && [ ! -f "$IMAGE_PATH" ]; then
  echo "Error: Image not found at $IMAGE_PATH"
  exit 1
fi

echo "=== Social Post ==="
echo ""
echo "Original text: $TEXT"
[ -n "$IMAGE_PATH" ] && echo "Image: $IMAGE_PATH"
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

# Detect Twitter account tier (if posting to Twitter)
TWITTER_TIER="basic"
TWITTER_LIMIT=252
if [ "$POST_TWITTER" = true ]; then
  echo "Detecting Twitter account tier..."
  source "$LIB_DIR/tier-detection.sh"
  TWITTER_TIER=$(detect_twitter_tier "$TWITTER_ACCOUNT" "$REFRESH_TIER")
  TWITTER_LIMIT=$(get_twitter_char_limit_buffered "$TWITTER_ACCOUNT" "$REFRESH_TIER")
  
  case "$TWITTER_TIER" in
    premium|premium_plus)
      echo "✓ Twitter account: Premium ($TWITTER_LIMIT chars available)"
      ;;
    basic)
      echo "✓ Twitter account: Basic ($TWITTER_LIMIT chars available)"
      ;;
  esac
  echo ""
fi

# Validate character/byte limits
TWITTER_VALID=true
FARCASTER_VALID=true

if [ "$POST_TWITTER" = true ]; then
  validate_twitter "$TEXT" "$REFRESH_TIER" || TWITTER_VALID=false
fi

if [ "$POST_FARCASTER" = true ]; then
  validate_farcaster "$TEXT" || FARCASTER_VALID=false
fi

echo ""

# Handle validation failures
if { [ "$POST_TWITTER" = true ] && [ "$TWITTER_VALID" = false ]; } || \
   { [ "$POST_FARCASTER" = true ] && [ "$FARCASTER_VALID" = false ]; }; then
  
  if [ "$THREAD_MODE" = true ]; then
    echo "Text exceeds limit. Thread mode enabled - will split into multiple posts."
    # Thread handling is done later in posting section
  elif [ "$AUTO_TRUNCATE" = true ]; then
    echo "Auto-truncating text..."
    if [ "$POST_TWITTER" = true ] && [ "$TWITTER_VALID" = false ]; then
      TEXT=$(truncate_for_twitter "$TEXT")
      echo "Twitter text truncated to: $TEXT"
    fi
    if [ "$POST_FARCASTER" = true ] && [ "$FARCASTER_VALID" = false ]; then
      TEXT=$(truncate_for_farcaster "$TEXT")
      echo "Farcaster text truncated to: $TEXT"
    fi
  else
    echo ""
    echo "Text exceeds platform limits. Options:"
    echo "  1. Shorten your text and try again"
    echo "  2. Use --truncate flag to auto-truncate"
    echo "  3. Use --thread flag to split into multiple posts"
    echo "  4. Use --shorten-links to compress URLs"
    echo "  5. Post to one platform only (--twitter or --farcaster)"
    exit 1
  fi
fi

# Apply text variation if --vary flag is set
if [ "$VARY_TEXT" = true ]; then
  echo "→ Applying text variation to avoid duplicate content detection..."
  ORIGINAL_TEXT="$TEXT"
  TEXT=$(vary_text "$TEXT")
  echo ""
fi

# For Premium accounts posting > 280 chars (but within Premium limit):
# Offer threading as an option (unless --thread was explicitly set or --auto-confirm)
if [ "$POST_TWITTER" = true ] && [ "$TWITTER_VALID" = true ] && [ "$FORCE_THREAD" = false ]; then
  local char_count=${#TEXT}
  if [[ "$TWITTER_TIER" =~ ^premium ]]; then
    # Premium account - check if text is > 280 (traditional limit)
    if [ "$char_count" -gt 280 ] && [ "$char_count" -le "$TWITTER_LIMIT" ]; then
      # Text would fit in single Premium post, but offer threading
      if [ "$AUTO_CONFIRM" = false ] && [ -t 0 ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📝 Premium account: Your text ($char_count chars) can be posted as:"
        echo "   1. Single long post (uses Premium 25k char limit)"
        echo "   2. Thread (split into multiple tweets)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo -n "Thread this instead? (y/n): "
        read -r THREAD_CHOICE
        if [[ "$THREAD_CHOICE" =~ ^[Yy]$ ]]; then
          THREAD_MODE=true
          echo "→ Preparing threaded draft..."
        else
          echo "→ Posting as single long tweet..."
        fi
        echo ""
      fi
    fi
  fi
fi

# Show draft preview
echo "=== Draft Preview ==="
echo ""
if [ "$VARY_TEXT" = true ] && [ -n "$ORIGINAL_TEXT" ]; then
  echo "Original text:"
  echo "─────────────────────────────────────────────"
  echo "$ORIGINAL_TEXT"
  echo "─────────────────────────────────────────────"
  echo ""
  echo "Varied text (will be posted):"
  echo "─────────────────────────────────────────────"
  echo "$TEXT"
  echo "─────────────────────────────────────────────"
else
  echo "Text to post:"
  echo "─────────────────────────────────────────────"
  echo "$TEXT"
  echo "─────────────────────────────────────────────"
fi
[ -n "$IMAGE_PATH" ] && echo "Image: $IMAGE_PATH"
echo ""
echo "Targets:"
[ "$POST_TWITTER" = true ] && echo "  • Twitter (@${TWITTER_ACCOUNT})"
[ "$POST_FARCASTER" = true ] && echo "  • Farcaster"
echo ""

# Dry run mode
if [ "$DRY_RUN" = true ]; then
  echo "=== Dry Run (not actually posting) ==="
  [ "$POST_TWITTER" = true ] && echo "Would post to Twitter"
  [ "$POST_FARCASTER" = true ] && echo "Would post to Farcaster"
  [ -n "$IMAGE_PATH" ] && echo "Would upload image: $IMAGE_PATH"
  exit 0
fi

# Confirmation prompt (skip if running non-interactively or with --yes flag)
if [ "$AUTO_CONFIRM" = false ] && [ -t 0 ]; then
  echo -n "Proceed with posting? (y/n): "
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

# Post to platforms
echo "=== Posting ==="
echo ""

SUCCESS=true

# Check if we need threading
NEEDS_THREAD_TWITTER=false
NEEDS_THREAD_FARCASTER=false

if [ "$THREAD_MODE" = true ]; then
  if [ "$POST_TWITTER" = true ]; then
    needs_threading "$TEXT" "twitter" && NEEDS_THREAD_TWITTER=true
  fi
  if [ "$POST_FARCASTER" = true ]; then
    needs_threading "$TEXT" "farcaster" && NEEDS_THREAD_FARCASTER=true
  fi
fi

# Twitter posting
if [ "$POST_TWITTER" = true ]; then
  echo "→ Twitter..."
  
  if [ "$NEEDS_THREAD_TWITTER" = true ]; then
    echo "Creating thread..."
    thread_parts=$(split_into_thread "$TEXT" "twitter")
    part_num=1
    previous_tweet_id=""
    
    while IFS= read -r part; do
      if [ "$part" = "---THREAD_SEPARATOR---" ]; then
        continue
      fi
      
      echo "  Part $part_num..."
      
      if [ "$part_num" -eq 1 ]; then
        # First post
        if [ -n "$IMAGE_PATH" ]; then
          result=$(twitter_post_with_image "$part" "$IMAGE_PATH")
        else
          result=$(twitter_post_text "$part")
        fi
        # Extract tweet ID from result
        previous_tweet_id=$(echo "$result" | grep -oE 'status/[0-9]+' | sed 's/status\///' | tail -1)
        echo "$result"
      else
        # Reply to previous tweet
        result=$(twitter_post_text "$part" "$previous_tweet_id")
        previous_tweet_id="$result"
        echo "✓ Tweet posted: https://twitter.com/user/status/$previous_tweet_id"
      fi
      
      part_num=$((part_num + 1))
      sleep 2  # Brief delay between thread posts
    done <<< "$thread_parts"
  else
    if [ -n "$IMAGE_PATH" ]; then
      twitter_post_with_image "$TEXT" "$IMAGE_PATH" || SUCCESS=false
    else
      twitter_post_text "$TEXT" || SUCCESS=false
    fi
  fi
  echo ""
fi

# Farcaster posting
if [ "$POST_FARCASTER" = true ]; then
  echo "→ Farcaster..."
  
  if [ "$NEEDS_THREAD_FARCASTER" = true ]; then
    echo "Creating thread..."
    thread_parts=$(split_into_thread "$TEXT" "farcaster")
    part_num=1
    previous_cast_hash=""
    
    while IFS= read -r part; do
      if [ "$part" = "---THREAD_SEPARATOR---" ]; then
        continue
      fi
      
      echo "  Part $part_num..."
      
      if [ "$part_num" -eq 1 ]; then
        # First post
        if [ -n "$IMAGE_PATH" ]; then
          result=$(farcaster_post_with_image "$part" "$IMAGE_PATH" "")
        else
          result=$(farcaster_post_text "$part" "")
        fi
        # Extract cast hash from result
        previous_cast_hash=$(echo "$result" | grep "Cast hash:" | sed 's/Cast hash: //')
        echo "$result"
      else
        # Reply to previous cast
        result=$(farcaster_post_text "$part" "$previous_cast_hash")
        previous_cast_hash=$(echo "$result" | grep "Cast hash:" | sed 's/Cast hash: //')
        echo "$result"
      fi
      
      part_num=$((part_num + 1))
      sleep 2  # Brief delay between thread posts
    done <<< "$thread_parts"
  else
    if [ -n "$IMAGE_PATH" ]; then
      farcaster_post_with_image "$TEXT" "$IMAGE_PATH" "" || SUCCESS=false
    else
      farcaster_post_text "$TEXT" "" || SUCCESS=false
    fi
  fi
  echo ""
fi

if [ "$SUCCESS" = true ]; then
  echo "✅ Done!"
else
  echo "⚠️ Some posts failed. Check output above."
  exit 1
fi
