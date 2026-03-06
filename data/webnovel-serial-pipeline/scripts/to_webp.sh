#!/usr/bin/env bash
set -euo pipefail

in="${1:-}"
out="${2:-}"
q="${3:-78}"      # 70~80 recommended
maxw="${4:-1200}" # web default

if [[ "$in" == "" || "$out" == "" ]]; then
  echo "Usage: to_webp.sh <in.png> <out.webp> [q=78] [maxw=1200]" >&2
  exit 2
fi

ffmpeg -y -hide_banner -loglevel error \
  -i "$in" \
  -vf "scale='min(${maxw},iw)':-2" \
  -vframes 1 -c:v libwebp -q:v "$q" -preset picture \
  "$out"

echo "$out"
