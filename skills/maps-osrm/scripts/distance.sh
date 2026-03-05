#!/bin/bash
# Distance & route lookup via OSRM (free, no API key)
# Usage: distance.sh <origin_lat>,<origin_lon> <dest_lat>,<dest_lon> [mode]
# Mode: driving (default), foot, bicycle
# Example: distance.sh 40.7580,-73.9855 40.6413,-73.7781

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: distance.sh <lat>,<lon> <lat>,<lon> [driving|foot|bicycle]"
  exit 1
fi

ORIGIN="$1"
DEST="$2"
MODE="${3:-driving}"

# Validate and route using python3 (avoids shell injection, proper input checking)
python3 -c "
import json, sys, urllib.request, re

origin = sys.argv[1]
dest = sys.argv[2]
mode = sys.argv[3]

# Validate coordinate format: lat,lon (decimal numbers)
coord_re = re.compile(r'^-?\d+(\.\d+)?,-?\d+(\.\d+)?$')
if not coord_re.match(origin):
    print(f'Invalid origin format: {origin} (expected: lat,lon)', file=sys.stderr)
    sys.exit(1)
if not coord_re.match(dest):
    print(f'Invalid destination format: {dest} (expected: lat,lon)', file=sys.stderr)
    sys.exit(1)

# Validate ranges
olat, olon = [float(x) for x in origin.split(',')]
dlat, dlon = [float(x) for x in dest.split(',')]
for name, lat, lon in [('Origin', olat, olon), ('Dest', dlat, dlon)]:
    if not (-90 <= lat <= 90):
        print(f'{name} latitude out of range: {lat}', file=sys.stderr)
        sys.exit(1)
    if not (-180 <= lon <= 180):
        print(f'{name} longitude out of range: {lon}', file=sys.stderr)
        sys.exit(1)

# Map mode to OSRM profile
profiles = {
    'driving': 'car', 'car': 'car',
    'foot': 'foot', 'walk': 'foot', 'walking': 'foot',
    'bicycle': 'bike', 'bike': 'bike', 'cycling': 'bike',
}
profile = profiles.get(mode)
if not profile:
    print(f'Unknown mode: {mode} (use driving, foot, bicycle)', file=sys.stderr)
    sys.exit(1)

# OSRM wants lon,lat
url = f'https://router.project-osrm.org/route/v1/{profile}/{olon},{olat};{dlon},{dlat}?overview=false&steps=false'

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'OpenClaw-Maps-Skill/1.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
except Exception as e:
    print(f'Request error: {e}', file=sys.stderr)
    sys.exit(1)

if data.get('code') != 'Ok':
    print(f\"OSRM error: {data.get('code', 'unknown')}\", file=sys.stderr)
    sys.exit(1)

route = data['routes'][0]
dist_km = route['distance'] / 1000
dur_min = route['duration'] / 60

print(f'Mode: {mode}')
print(f'Distance: {dist_km:.1f} km')
print(f'Duration: {dur_min:.0f} min')
print(f'Raw: {route[\"distance\"]:.0f}m / {route[\"duration\"]:.0f}s')
" "$ORIGIN" "$DEST" "$MODE"
