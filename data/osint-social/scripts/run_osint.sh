#!/bin/bash
# osint-social: Quick wrapper for social-analyzer
# Usage: ./run_osint.sh <username> [top_count]
#
# Examples:
#   ./run_osint.sh johndoe
#   ./run_osint.sh johndoe 200
#   ./run_osint.sh "johndoe,john_doe" 100

USERNAME="${1}"
TOP="${2:-100}"

if [ -z "$USERNAME" ]; then
  echo "Usage: $0 <username> [top_count]"
  exit 1
fi

echo "[*] Investigating username: $USERNAME"
echo "[*] Scanning top $TOP platforms..."
echo ""

python3 -m social-analyzer \
  --username "$USERNAME" \
  --metadata \
  --output json \
  --filter "good" \
  --top "$TOP" \
  2>/dev/null | python3 -c "
import sys, json

try:
    data = json.load(sys.stdin)
except:
    print('No results or parse error.')
    sys.exit(0)

# Handle both list and dict response formats
if isinstance(data, list):
    profiles = data
elif isinstance(data, dict):
    profiles = data.get('detected', data.get('found', []))
else:
    profiles = []

if not profiles:
    print('No accounts found.')
    sys.exit(0)

print(f'Found {len(profiles)} account(s):\n')
for p in sorted(profiles, key=lambda x: x.get('rate', 0), reverse=True):
    rate = p.get('rate', '?')
    site = p.get('website', p.get('name', '?'))
    url  = p.get('url', p.get('link', ''))
    meta = p.get('metadata', {})
    bio  = meta.get('bio', meta.get('description', ''))
    name = meta.get('name', '')

    line = f'  [{rate:>3}] {site}: {url}'
    if name:
        line += f' | name: {name}'
    if bio:
        line += f' | bio: {bio[:60]}'
    print(line)

print()
print('Note: rate = confidence score (0-100). >= 80 is high confidence.')
"
