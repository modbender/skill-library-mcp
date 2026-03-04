#!/usr/bin/env bash
# seo-analyze.sh — Lightweight SEO analyzer (macOS & Linux compatible)
# Usage: ./seo-analyze.sh <URL>  or  curl -sL <URL> | ./seo-analyze.sh -
set -uo pipefail

if [[ "${1:-}" == "-" ]]; then
  HTML=$(cat)
  URL="(stdin)"
else
  URL="${1:?Usage: seo-analyze.sh <URL>}"
  HTML=$(curl -sL --max-time 15 -A "Mozilla/5.0 SEO-Analyzer/1.0" "$URL")
fi

echo "═══════════════════════════════════════════"
echo "  🦞 SEO Analysis Report"
echo "  URL: $URL"
echo "  Date: $(date '+%Y-%m-%d %H:%M')"
echo "═══════════════════════════════════════════"
echo

# --- Title ---
TITLE=$(echo "$HTML" | sed -n 's/.*<[Tt][Ii][Tt][Ll][Ee][^>]*>\([^<]*\)<\/[Tt][Ii][Tt][Ll][Ee]>.*/\1/p' | head -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
TITLE_LEN=${#TITLE}
echo "📌 TITLE TAG"
if [[ -z "$TITLE" ]]; then
  echo "  ❌ MISSING — No <title> tag found!"
else
  echo "  \"$TITLE\""
  echo "  Length: $TITLE_LEN chars"
  if (( TITLE_LEN < 30 )); then
    echo "  ⚠️  Too short (aim for 50-60 chars)"
  elif (( TITLE_LEN > 65 )); then
    echo "  ⚠️  Too long (may be truncated in SERPs, aim for 50-60)"
  else
    echo "  ✅ Good length"
  fi
fi
echo

# --- Meta Description ---
META_DESC=$(echo "$HTML" | tr '\n' ' ' | sed -n 's/.*<[Mm][Ee][Tt][Aa][^>]*name=["\x27][Dd]escription["\x27][^>]*content=["\x27]\([^"\x27]*\).*/\1/p' | head -1)
if [[ -z "$META_DESC" ]]; then
  META_DESC=$(echo "$HTML" | tr '\n' ' ' | sed -n 's/.*<[Mm][Ee][Tt][Aa][^>]*content=["\x27]\([^"\x27]*\)["\x27][^>]*name=["\x27][Dd]escription["\x27].*/\1/p' | head -1)
fi
META_LEN=${#META_DESC}
echo "📝 META DESCRIPTION"
if [[ -z "$META_DESC" ]]; then
  echo "  ❌ MISSING — No meta description found!"
else
  DISPLAY_META="${META_DESC:0:120}"
  [[ $META_LEN -gt 120 ]] && DISPLAY_META="${DISPLAY_META}..."
  echo "  \"$DISPLAY_META\""
  echo "  Length: $META_LEN chars"
  if (( META_LEN < 120 )); then
    echo "  ⚠️  Too short (aim for 150-160 chars)"
  elif (( META_LEN > 165 )); then
    echo "  ⚠️  Too long (aim for 150-160 chars)"
  else
    echo "  ✅ Good length"
  fi
fi
echo

# --- Headings ---
echo "🏗️  HEADING STRUCTURE"
H1_COUNT=$(echo "$HTML" | grep -ioE '<h1[[:space:]>]' | wc -l | tr -d ' ' || true)
H2_COUNT=$(echo "$HTML" | grep -ioE '<h2[[:space:]>]' | wc -l | tr -d ' ' || true)
H3_COUNT=$(echo "$HTML" | grep -ioE '<h3[[:space:]>]' | wc -l | tr -d ' ' || true)
echo "  H1: $H1_COUNT | H2: $H2_COUNT | H3: $H3_COUNT"
if (( H1_COUNT == 0 )); then
  echo "  ❌ No H1 tag — every page needs exactly one H1"
elif (( H1_COUNT > 1 )); then
  echo "  ⚠️  Multiple H1 tags ($H1_COUNT) — use only one per page"
else
  echo "  ✅ Single H1 — good"
fi
if (( H2_COUNT == 0 )); then
  echo "  ⚠️  No H2 tags — use subheadings to structure content"
fi
echo

# --- Images without alt ---
echo "🖼️  IMAGES"
TOTAL_IMGS=$(echo "$HTML" | grep -ioE '<img[[:space:]]' | wc -l | tr -d ' ')
# Count imgs that lack a non-empty alt
NO_ALT=$(echo "$HTML" | tr '\n' ' ' | grep -ioE '<img[[:space:]][^>]*>' | grep -ivE 'alt=["\x27][^"\x27]+' | wc -l | tr -d ' ')
echo "  Total images: $TOTAL_IMGS"
echo "  Missing/empty alt: $NO_ALT"
if (( NO_ALT > 0 )); then
  echo "  ⚠️  Add descriptive alt text to all images"
elif (( TOTAL_IMGS > 0 )); then
  echo "  ✅ All images have alt text"
fi
echo

# --- Open Graph ---
echo "📱 SOCIAL METADATA"
OG=$(echo "$HTML" | grep -ioE '<meta[[:space:]]+property=["\x27]og:' | wc -l | tr -d ' ')
TC=$(echo "$HTML" | grep -ioE '<meta[[:space:]]+name=["\x27]twitter:' | wc -l | tr -d ' ')
echo "  Open Graph tags: $OG"
echo "  Twitter Card tags: $TC"
[[ $OG -eq 0 ]] && echo "  ⚠️  No Open Graph tags — add og:title, og:description, og:image"
[[ $TC -eq 0 ]] && echo "  ⚠️  No Twitter Card tags — add twitter:card, twitter:title"
echo

# --- Canonical ---
echo "🔗 CANONICAL"
CANONICAL=$(echo "$HTML" | tr '\n' ' ' | sed -n 's/.*<[Ll][Ii][Nn][Kk][^>]*rel=["\x27]canonical["\x27][^>]*href=["\x27]\([^"\x27]*\).*/\1/p' | head -1)
if [[ -z "$CANONICAL" ]]; then
  echo "  ⚠️  No canonical URL set"
else
  echo "  $CANONICAL ✅"
fi
echo

# --- Word Count & Keyword Density ---
echo "📊 CONTENT ANALYSIS"
VISIBLE=$(echo "$HTML" | sed 's/<script[^>]*>.*<\/script>//gi; s/<style[^>]*>.*<\/style>//gi; s/<[^>]*>//g; s/&[a-z]*;//g' | tr -s '[:space:]' '\n')
WORD_COUNT=$(echo "$VISIBLE" | wc -w | tr -d ' ')
echo "  Word count: ~$WORD_COUNT"
if (( WORD_COUNT < 300 )); then
  echo "  ⚠️  Thin content — aim for 300+ words for better rankings"
elif (( WORD_COUNT > 2000 )); then
  echo "  ✅ Long-form content — good for authority"
else
  echo "  ✅ Reasonable content length"
fi
echo
echo "  Top keywords (3+ chars):"

# Stop words to filter
STOP="the|and|for|that|this|with|are|was|have|has|from|but|not|you|all|can|been|will|more|when|would|there|their|what|about|which|them|than|into|could|other|its|also|after|use|your|how|our|may|these|most|any|just|some|very|like|over|such|did|get|back|only|come|made|well|way|own|say|each|she|her|his|him|had|one|two|new|now|old|see|who|let|few|too|should|where|much|does|many|those|know|take|here|still"

echo "$VISIBLE" | tr '[:upper:]' '[:lower:]' | grep -oE '[a-z]{3,}' | \
  grep -ivE "^($STOP)$" | \
  sort | uniq -c | sort -rn | head -10 | \
  awk '{printf "    %4d× %s\n", $1, $2}'
echo

echo "═══════════════════════════════════════════"
echo "  🦞 Analysis complete!"
echo "═══════════════════════════════════════════"
