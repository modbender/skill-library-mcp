#!/bin/bash
# Google Trends - Daily Trending Searches
# Usage: ./trends-daily.sh [country_code]
# Example: ./trends-daily.sh LT

GEO="${1:-US}"
echo "📈 Google Trends - $GEO - $(date '+%Y-%m-%d')"
echo "=================================="
curl -s "https://trends.google.com/trending/rss?geo=$GEO" | \
  grep -o '<title>[^<]*</title>' | \
  sed 's/<[^>]*>//g' | \
  tail -n +2 | \
  head -20 | \
  nl
