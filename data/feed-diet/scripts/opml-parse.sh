#!/usr/bin/env bash
# opml-parse.sh — Parse an OPML file and fetch recent items from each RSS feed
# Outputs JSON lines: {"feed_title":..., "item_title":..., "url":..., "time":...}
#
# Usage: ./opml-parse.sh PATH_TO_OPML [MAX_ITEMS_PER_FEED]

set -euo pipefail
source "$(dirname "$0")/common.sh"

OPML_FILE="${1:?Usage: opml-parse.sh PATH_TO_OPML [MAX_ITEMS_PER_FEED]}"
MAX_PER_FEED="${2:-10}"

if [ ! -f "$OPML_FILE" ]; then
  err "OPML file not found: $OPML_FILE"
  exit 1
fi

CACHE_FILE="${CACHE_DIR}/opml_items.jsonl"
> "$CACHE_FILE"

# ─── Extract feed URLs from OPML ─────────────────────────────────────
info "Parsing OPML file: $OPML_FILE"

FEEDS=$(OPML_FILE_ENV="$OPML_FILE" python3 -c "
import xml.etree.ElementTree as ET
import json, sys, os

tree = ET.parse(os.environ['OPML_FILE_ENV'])
root = tree.getroot()

feeds = []
for outline in root.iter('outline'):
    xml_url = outline.get('xmlUrl', outline.get('xmlurl', ''))
    title = outline.get('title', outline.get('text', 'Unknown Feed'))
    html_url = outline.get('htmlUrl', outline.get('htmlurl', ''))
    if xml_url:
        feeds.append({
            'title': title,
            'xml_url': xml_url,
            'html_url': html_url
        })

for f in feeds:
    print(json.dumps(f))
" 2>/dev/null) || {
  err "Failed to parse OPML file. Is it valid XML?"
  exit 1
}

FEED_COUNT=$(echo "$FEEDS" | grep -c '^{' || echo 0)
if [ "$FEED_COUNT" -eq 0 ]; then
  err "No feeds found in OPML file."
  exit 1
fi

info "Found ${FEED_COUNT} feeds in OPML"

# ─── Fetch items from each feed ──────────────────────────────────────
CURRENT=0
TOTAL_ITEMS=0

while IFS= read -r FEED_JSON; do
  CURRENT=$((CURRENT + 1))
  FEED_TITLE=$(echo "$FEED_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin)['title'])" 2>/dev/null)
  FEED_URL=$(echo "$FEED_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin)['xml_url'])" 2>/dev/null)
  
  progress "$CURRENT" "$FEED_COUNT" "feeds"

  # Validate URL scheme — only allow http/https to prevent SSRF
  case "$FEED_URL" in
    http://*|https://*) ;;
    *)
      warn "Skipping non-HTTP feed URL: $FEED_URL"
      continue
      ;;
  esac

  # Fetch the RSS/Atom feed with timeout
  FEED_XML=$(curl -sf --max-time 10 -L "$FEED_URL" 2>/dev/null) || {
    warn "Could not fetch feed: $FEED_TITLE ($FEED_URL)"
    continue
  }

  # Parse RSS/Atom items
  ITEMS=$(echo "$FEED_XML" | FEED_TITLE_ENV="$FEED_TITLE" MAX_PER_FEED_ENV="$MAX_PER_FEED" python3 -c "
import xml.etree.ElementTree as ET
import json, sys, re, os
from datetime import datetime

feed_title = os.environ['FEED_TITLE_ENV']
max_items = int(os.environ['MAX_PER_FEED_ENV'])

try:
    content = sys.stdin.read()
    root = ET.fromstring(content)
except:
    sys.exit(0)

ns = {
    'atom': 'http://www.w3.org/2005/Atom',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'content': 'http://purl.org/rss/1.0/modules/content/'
}

items = []

# Try RSS format
for item in root.iter('item'):
    title_el = item.find('title')
    link_el = item.find('link')
    if title_el is not None and title_el.text:
        entry = {
            'feed_title': feed_title,
            'item_title': title_el.text.strip(),
            'url': (link_el.text or '').strip() if link_el is not None else '',
            'source': 'rss'
        }
        items.append(entry)
    if len(items) >= max_items:
        break

# Try Atom format if no RSS items found
if not items:
    for entry_el in root.findall('atom:entry', ns) + root.findall('entry'):
        title_el = entry_el.find('atom:title', ns)
        if title_el is None:
            title_el = entry_el.find('title')
        link_el = entry_el.find('atom:link', ns)
        if link_el is None:
            link_el = entry_el.find('link')
        
        if title_el is not None and title_el.text:
            url = ''
            if link_el is not None:
                url = link_el.get('href', link_el.text or '')
            entry = {
                'feed_title': feed_title,
                'item_title': title_el.text.strip(),
                'url': url.strip(),
                'source': 'atom'
            }
            items.append(entry)
        if len(items) >= max_items:
            break

for item in items:
    print(json.dumps(item))
" 2>/dev/null) || continue

  if [ -n "$ITEMS" ]; then
    ITEM_COUNT=$(echo "$ITEMS" | grep -c '^{' || echo 0)
    TOTAL_ITEMS=$((TOTAL_ITEMS + ITEM_COUNT))
    echo "$ITEMS" >> "$CACHE_FILE"
  fi

done <<< "$FEEDS"

progress_done

if [ "$TOTAL_ITEMS" -eq 0 ]; then
  err "No items fetched from any feeds. Check feed URLs and connectivity."
  exit 1
fi

info "Fetched ${TOTAL_ITEMS} items from ${FEED_COUNT} feeds"

cat "$CACHE_FILE"
