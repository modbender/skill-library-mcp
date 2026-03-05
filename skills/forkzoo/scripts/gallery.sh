#!/bin/bash
# ForkZoo - View community gallery
# Usage: ./gallery.sh [limit]

set -e

LIMIT="${1:-10}"

echo "🐾 ForkZoo Community Gallery"
echo "============================"
echo ""

# Fetch forks from the main forkMonkey repo
echo "🔍 Fetching community pets..."
echo ""

FORKS=$(curl -s "https://api.github.com/repos/roeiba/forkMonkey/forks?per_page=$LIMIT&sort=stargazers")

echo "Top $LIMIT pets by activity:"
echo ""

echo "$FORKS" | jq -r '.[] | "🐵 \(.full_name)\n   🌐 https://\(.owner.login).github.io/\(.name)/\n   ⭐ \(.stargazers_count) stars | 🍴 \(.forks_count) children\n"'

echo ""
echo "View full gallery: https://forkzoo.dev/gallery"
echo "Leaderboard: https://roeiba.github.io/forkMonkey/#leaderboard"
