#!/bin/bash
# ForkZoo - Check pet status
# Usage: ./status.sh [repo-name]

set -e

REPO_NAME="${1:-}"

# Check for GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
  echo "❌ GITHUB_TOKEN not set"
  exit 1
fi

# Get current user
GITHUB_USER=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user | jq -r '.login')

# If no repo specified, try to find one
if [ -z "$REPO_NAME" ]; then
  echo "🔍 Looking for your pets..."
  
  # Search for forkzoo-related repos
  REPOS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/users/$GITHUB_USER/repos?per_page=100" | \
    jq -r '.[] | select(.name | test("fork(Monkey|Cat|Dog|Lion|monkey|cat|dog|lion)"; "i")) | .name')
  
  if [ -z "$REPOS" ]; then
    echo "❌ No pets found. Adopt one with: ./adopt.sh <animal>"
    exit 1
  fi
  
  # Use first found
  REPO_NAME=$(echo "$REPOS" | head -1)
  echo "📍 Found: $REPO_NAME"
fi

echo ""
echo "🐾 Fetching status for $GITHUB_USER/$REPO_NAME..."
echo ""

# Get stats.json
STATS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3.raw" \
  "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME/contents/monkey_data/stats.json" 2>/dev/null || echo "{}")

if [ "$STATS" == "{}" ] || [ "$STATS" == "404: Not Found" ]; then
  # Try alternate location
  STATS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3.raw" \
    "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME/contents/pet_data/stats.json" 2>/dev/null || echo "{}")
fi

if [ "$STATS" == "{}" ] || [ -z "$STATS" ]; then
  echo "⚠️  Could not fetch pet stats. Pet may still be initializing."
  echo "   Check: https://github.com/$GITHUB_USER/$REPO_NAME"
  exit 0
fi

# Parse and display stats
GENERATION=$(echo "$STATS" | jq -r '.generation // "?"')
AGE=$(echo "$STATS" | jq -r '.age_days // .age // "?"')
MUTATIONS=$(echo "$STATS" | jq -r '.mutations // .total_mutations // "?"')
RARITY=$(echo "$STATS" | jq -r '.rarity_score // .rarity // "?"')
STREAK=$(echo "$STATS" | jq -r '.evolution_streak // .streak // 0')
NAME=$(echo "$STATS" | jq -r '.name // "Unnamed"')

# Determine rarity tier
if [ "$RARITY" != "?" ]; then
  RARITY_NUM=$(echo "$RARITY" | cut -d'/' -f1)
  if (( $(echo "$RARITY_NUM >= 35" | bc -l) )); then
    TIER="🦄 Legendary"
  elif (( $(echo "$RARITY_NUM >= 25" | bc -l) )); then
    TIER="💙 Rare"
  elif (( $(echo "$RARITY_NUM >= 15" | bc -l) )); then
    TIER="💚 Uncommon"
  else
    TIER="⚪ Common"
  fi
else
  TIER="?"
fi

echo "╔════════════════════════════════════╗"
echo "║         🐾 PET STATUS 🐾           ║"
echo "╠════════════════════════════════════╣"
echo "║ Name:       $NAME"
echo "║ Generation: $GENERATION"
echo "║ Age:        $AGE days"
echo "║ Mutations:  $MUTATIONS"
echo "║ Rarity:     $RARITY ($TIER)"
echo "║ Streak:     🔥 $STREAK days"
echo "╚════════════════════════════════════╝"
echo ""
echo "🌐 View live: https://$GITHUB_USER.github.io/$REPO_NAME/"
echo "📂 Repo: https://github.com/$GITHUB_USER/$REPO_NAME"
