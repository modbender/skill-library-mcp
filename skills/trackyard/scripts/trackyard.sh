#!/usr/bin/env bash
set -euo pipefail

BASE_URL="https://api.trackyard.com/api/external/v1"

check_api_key() {
  if [[ -z "${TRACKYARD_API_KEY:-}" ]]; then
    echo "Error: TRACKYARD_API_KEY environment variable not set" >&2
    echo "Get your API key at https://trackyard.com" >&2
    exit 1
  fi
}

usage() {
  cat <<EOF
Usage: trackyard.sh <command> [options]

Commands:
  search <query>     Search for music (1 credit)
  download <id>      Download a track (1 credit)
  me                 Show account info and credits (free)
  usage              Show usage history (free)

Search options:
  --limit N          Max results (default: 10)
  --offset N         Pagination offset
  --genres X,Y       Filter by genres (comma-separated)
  --moods X,Y        Filter by moods (comma-separated)
  --min-bpm N        Minimum BPM
  --max-bpm N        Maximum BPM
  --energy LEVEL     Energy level: low, medium, high
  --no-vocals        Instrumental only
  --instruments X,Y  Filter by instruments (comma-separated)

Download options:
  --duration N       Trim to N seconds (smart segment selection)
  --hit-point N      Align peak/drop to N seconds into clip
  --output FILE      Output filename (default: track title)

Examples:
  trackyard.sh search "upbeat electronic for tech video"
  trackyard.sh search "calm piano" --no-vocals --energy low --limit 5
  trackyard.sh download 2YzqBZtG5W9Xk8mKQ3TnLvN4pRv
  trackyard.sh download 2YzqBZtG5W9Xk8mKQ3TnLvN4pRv --duration 22 --hit-point 12
EOF
  exit 1
}

cmd_search() {
  local query=""
  local limit=10
  local offset=0
  local genres=""
  local moods=""
  local min_bpm=""
  local max_bpm=""
  local energy=""
  local no_vocals=false
  local instruments=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --limit) limit="$2"; shift 2 ;;
      --offset) offset="$2"; shift 2 ;;
      --genres) genres="$2"; shift 2 ;;
      --moods) moods="$2"; shift 2 ;;
      --min-bpm) min_bpm="$2"; shift 2 ;;
      --max-bpm) max_bpm="$2"; shift 2 ;;
      --energy) energy="$2"; shift 2 ;;
      --no-vocals) no_vocals=true; shift ;;
      --instruments) instruments="$2"; shift 2 ;;
      -*) echo "Unknown option: $1" >&2; exit 1 ;;
      *) query="$1"; shift ;;
    esac
  done

  if [[ -z "$query" ]]; then
    echo "Error: search query required" >&2
    exit 1
  fi

  # Build filters JSON
  local filters="{"
  local has_filter=false

  if [[ -n "$genres" ]]; then
    filters+="\"genres\":[$(echo "$genres" | sed 's/,/","/g' | sed 's/^/"/;s/$/"/')]"
    has_filter=true
  fi
  if [[ -n "$moods" ]]; then
    [[ "$has_filter" == true ]] && filters+=","
    filters+="\"moods\":[$(echo "$moods" | sed 's/,/","/g' | sed 's/^/"/;s/$/"/')]"
    has_filter=true
  fi
  if [[ -n "$min_bpm" ]]; then
    [[ "$has_filter" == true ]] && filters+=","
    filters+="\"min_bpm\":$min_bpm"
    has_filter=true
  fi
  if [[ -n "$max_bpm" ]]; then
    [[ "$has_filter" == true ]] && filters+=","
    filters+="\"max_bpm\":$max_bpm"
    has_filter=true
  fi
  if [[ -n "$energy" ]]; then
    [[ "$has_filter" == true ]] && filters+=","
    filters+="\"energy_level\":\"$energy\""
    has_filter=true
  fi
  if [[ "$no_vocals" == true ]]; then
    [[ "$has_filter" == true ]] && filters+=","
    filters+="\"has_vocals\":false"
    has_filter=true
  fi
  if [[ -n "$instruments" ]]; then
    [[ "$has_filter" == true ]] && filters+=","
    filters+="\"instruments\":[$(echo "$instruments" | sed 's/,/","/g' | sed 's/^/"/;s/$/"/')]"
    has_filter=true
  fi

  filters+="}"

  # Build request body
  local body
  if [[ "$has_filter" == true ]]; then
    body=$(jq -n \
      --arg query "$query" \
      --argjson limit "$limit" \
      --argjson offset "$offset" \
      --argjson filters "$filters" \
      '{query: $query, limit: $limit, offset: $offset, filters: $filters}')
  else
    body=$(jq -n \
      --arg query "$query" \
      --argjson limit "$limit" \
      --argjson offset "$offset" \
      '{query: $query, limit: $limit, offset: $offset}')
  fi

  curl -sS -X POST "$BASE_URL/search" \
    -H "Authorization: Bearer $TRACKYARD_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$body" | jq .
}

cmd_download() {
  local track_id=""
  local duration=""
  local hit_point=""
  local output=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --duration) duration="$2"; shift 2 ;;
      --hit-point) hit_point="$2"; shift 2 ;;
      --output) output="$2"; shift 2 ;;
      -*) echo "Unknown option: $1" >&2; exit 1 ;;
      *) track_id="$1"; shift ;;
    esac
  done

  if [[ -z "$track_id" ]]; then
    echo "Error: track ID required" >&2
    exit 1
  fi

  # Build request body
  local body
  body=$(jq -n --arg id "$track_id" '{track_id: $id}')

  if [[ -n "$duration" ]]; then
    body=$(echo "$body" | jq --argjson d "$duration" '. + {duration_seconds: $d}')
  fi
  if [[ -n "$hit_point" ]]; then
    body=$(echo "$body" | jq --argjson h "$hit_point" '. + {hit_point_seconds: $h}')
  fi

  # Determine output filename
  if [[ -z "$output" ]]; then
    # Get track title for filename
    local title
    title=$(curl -sS -X POST "$BASE_URL/search" \
      -H "Authorization: Bearer $TRACKYARD_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{\"query\":\"$track_id\",\"limit\":1}" | jq -r '.tracks[0].title // "track"' 2>/dev/null || echo "track")
    
    # Sanitize filename
    output=$(echo "$title" | tr ' ' '_' | tr -cd '[:alnum:]_-').mp3
  fi

  echo "Downloading to: $output" >&2

  curl -sS -X POST "$BASE_URL/download-track" \
    -H "Authorization: Bearer $TRACKYARD_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$body" \
    --output "$output"

  echo "Downloaded: $output"
}

cmd_me() {
  curl -sS -X GET "$BASE_URL/me" \
    -H "Authorization: Bearer $TRACKYARD_API_KEY" | jq .
}

cmd_usage() {
  local limit=100
  local offset=0

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --limit) limit="$2"; shift 2 ;;
      --offset) offset="$2"; shift 2 ;;
      *) shift ;;
    esac
  done

  curl -sS -X GET "$BASE_URL/usage?limit=$limit&offset=$offset" \
    -H "Authorization: Bearer $TRACKYARD_API_KEY" | jq .
}

# Main dispatch
[[ $# -lt 1 ]] && usage

case "$1" in
  -h|--help|help) usage ;;
  search) check_api_key; shift; cmd_search "$@" ;;
  download) check_api_key; shift; cmd_download "$@" ;;
  me) check_api_key; cmd_me ;;
  usage) check_api_key; shift; cmd_usage "$@" ;;
  *) echo "Unknown command: $1" >&2; usage ;;
esac
