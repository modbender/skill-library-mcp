#!/usr/bin/env bash
# Output the Apple Podcasts URL for The Canadian Real Estate Investor podcast.
# Usage: get_apple_podcast_link.sh [episode_title]
# The episode title arg is accepted but unused — we always return the base show URL.

APPLE_PODCASTS_URL="${APPLE_PODCASTS_URL:-https://podcasts.apple.com/ca/podcast/the-canadian-real-estate-investor/id1634197127}"
echo "$APPLE_PODCASTS_URL"
