#!/bin/bash

set -euo pipefail

usage() {
  cat <<EOF
Usage: subtitle-context.sh <srt_file> <timestamp> [--window-mins N]

Timestamp formats: HH:MM:SS,mmm or HH:MM:SS.mmm
Default window: 10 minutes before the timestamp (inclusive) to the timestamp.
EOF
}

if [[ $# -lt 2 ]]; then
  usage
  exit 1
fi

srt_file="$1"
shift

timestamp="$1"
shift

# Enforce cache directory + .srt extension to avoid arbitrary file reads
base_dir="$(cd "$(dirname "$0")/.." && pwd)"
cache_dir="${base_dir}/storage/subtitles"

case "$srt_file" in
  *.srt) ;;
  *) echo "Error: subtitle file must have .srt extension" >&2; exit 1;;
 esac

# Normalize to absolute path
if [[ "$srt_file" != /* ]]; then
  srt_file="$PWD/$srt_file"
fi

if [[ "$srt_file" != "$cache_dir"/* ]]; then
  echo "Error: subtitle file must be inside $cache_dir" >&2
  exit 1
fi

if [[ ! -f "$srt_file" ]]; then
  echo "Error: subtitle file not found" >&2
  exit 1
fi

window_mins=10
while [[ $# -gt 0 ]]; do
  case "$1" in
    --window-mins)
      window_mins="$2"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

# Normalize timestamp
norm_ts="${timestamp/./,}"

awk -v target="$norm_ts" -v wmins="$window_mins" '
function to_ms(ts,   h,m,s,ms) {
  split(ts, a, ":");
  h=a[1]; m=a[2];
  split(a[3], b, ",");
  s=b[1]; ms=b[2];
  return (h*3600000)+(m*60000)+(s*1000)+ms;
}
BEGIN {
  target_ms = to_ms(target);
  window_ms = wmins * 60 * 1000;
  start_window = target_ms - window_ms;
  if (start_window < 0) start_window = 0;
}
/^[0-9]+$/ { idx=$0; next }
/^[0-9][0-9]:[0-9][0-9]:[0-9][0-9],[0-9][0-9][0-9] --> / {
  start=$1; end=$3;
  start_ms=to_ms(start); end_ms=to_ms(end);
  in_block=1; text=""; next
}
/^$/ {
  if (in_block) {
    if (end_ms >= start_window && start_ms <= target_ms) {
      printf("[%s --> %s]\n%s\n\n", start, end, text);
      found=1;
    }
  }
  in_block=0; text=""; next
}
{
  if (in_block) {
    if (text == "") text=$0; else text=text"\n"$0;
  }
}
END {
  if (!found) print "No subtitles found in window";
}
' "$srt_file"
