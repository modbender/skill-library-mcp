#!/usr/bin/env bash
# Quick people search across multiple free aggregators
# Usage: people-search.sh "First Last" [State] [City]
# Example: people-search.sh "John Smith" FL Miami

set -euo pipefail

NAME="${1:?Usage: people-search.sh \"First Last\" [State] [City]}"
STATE="${2:-}"
CITY="${3:-}"

FIRST=$(echo "$NAME" | awk '{print $1}')
LAST=$(echo "$NAME" | awk '{print $NF}')

echo "=== People Search: $NAME ==="
echo ""

# TruePeopleSearch (actually free, good results)
TPS_URL="https://www.truepeoplesearch.com/results?name=${FIRST}%20${LAST}"
[ -n "$STATE" ] && TPS_URL="${TPS_URL}&citystatezip=${CITY:+${CITY}%20}${STATE}"
echo "🔍 TruePeopleSearch: $TPS_URL"

# FastPeopleSearch (free)
FPS_URL="https://www.fastpeoplesearch.com/name/${FIRST}-${LAST}"
[ -n "$STATE" ] && FPS_URL="${FPS_URL}_${STATE}"
echo "🔍 FastPeopleSearch: $FPS_URL"

# Spokeo
SPOKEO_URL="https://www.spokeo.com/${FIRST}-${LAST}"
[ -n "$STATE" ] && SPOKEO_URL="${SPOKEO_URL}/${STATE}"
[ -n "$CITY" ] && SPOKEO_URL="${SPOKEO_URL}/${CITY}"
echo "🔍 Spokeo: $SPOKEO_URL"

# WhitePages
WP_URL="https://www.whitepages.com/name/${FIRST}-${LAST}"
[ -n "$STATE" ] && WP_URL="${WP_URL}/${STATE}"
echo "🔍 WhitePages: $WP_URL"

# ClustrMaps
CM_URL="https://clustrmaps.com/persons/${FIRST}-${LAST}"
echo "🔍 ClustrMaps: $CM_URL"

# CourtListener (federal courts)
CL_URL="https://www.courtlistener.com/?q=%22${FIRST}+${LAST}%22&type=r"
echo "🔍 CourtListener: $CL_URL"

# FEC (political donations)
FEC_URL="https://www.fec.gov/data/receipts/individual-contributions/?contributor_name=${FIRST}+${LAST}"
[ -n "$STATE" ] && FEC_URL="${FEC_URL}&contributor_state=${STATE}"
echo "🔍 FEC Contributions: $FEC_URL"

echo ""
echo "Note: Most of these are JS-rendered. Use browser tool or web_search"
echo "with site: operator for best results. TruePeopleSearch often works"
echo "with web_fetch for basic info."
