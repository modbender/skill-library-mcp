#!/bin/bash
# Geocode a place name to lat,lon using Nominatim (OSM, free, no key)
# Usage: geocode.sh "Times Square, New York"
# Rate limit: 1 req/sec (Nominatim policy)

set -euo pipefail

if [ $# -lt 1 ] || [ -z "$1" ]; then
  echo "Usage: geocode.sh <place name>"
  exit 1
fi

QUERY="$1"

# URL-encode and fetch using python3 (avoids shell injection)
RESULT=$(python3 -c "
import urllib.parse, urllib.request, json, sys

query = sys.argv[1]
encoded = urllib.parse.quote(query)
url = f'https://nominatim.openstreetmap.org/search?q={encoded}&format=json&limit=3'
req = urllib.request.Request(url, headers={'User-Agent': 'OpenClaw-Maps-Skill/1.0'})

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)

if not data:
    print(f'No results for: {query}')
    sys.exit(1)

for i, r in enumerate(data):
    print(f\"[{i+1}] {r['display_name']}\")
    print(f\"    lat,lon: {r['lat']},{r['lon']}\")
    print(f\"    type: {r.get('type','?')} / {r.get('class','?')}\")
" "$QUERY")

echo "$RESULT"
