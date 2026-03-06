#!/usr/bin/env bash
# raindrop.sh - Raindrop.io CLI wrapper
# Requires: RAINDROP_TOKEN env var or --token flag

set -euo pipefail

API="https://api.raindrop.io/rest/v1"
TOKEN="${RAINDROP_TOKEN:-}"
FORMAT="pretty"  # pretty or json
DELAY=0  # ms delay between requests for rate limiting

# Auto-source token from config if not set
if [[ -z "$TOKEN" && -f ~/.config/raindrop.env ]]; then
  source ~/.config/raindrop.env
fi

usage() {
  cat <<EOF
Raindrop.io Bookmarks CLI

Usage: raindrop.sh [OPTIONS] COMMAND [ARGS]

Commands:
  whoami                      Show authenticated user info
  collections                 List all collections
  create-collection NAME      Create a new collection
  list [COLLECTION_ID]        List bookmarks (default: 0 = all)
  count [COLLECTION_ID]       Count bookmarks in collection
  search QUERY [COLLECTION]   Search bookmarks
  get ID                      Get bookmark by ID
  add URL [COLLECTION_ID]     Add bookmark (default: -1 = Unsorted)
  delete ID                   Delete bookmark
  move ID COLLECTION_ID       Move bookmark to collection
  update ID [OPTIONS]         Update bookmark (--tags, --title, --collection)
  bulk-move IDS COLLECTION    Move multiple bookmarks (comma-separated IDs)
  tags                        List all tags with counts
  suggest URL                 Get AI-suggested tags/title for URL
  list-untagged [COLLECTION]  List bookmarks without tags
  cache ID                    Get permanent copy (Pro only)

Options:
  --token TOKEN    API token (or set RAINDROP_TOKEN)
  --json           Output raw JSON
  --limit N        Max results (default: 25)
  --delay MS       Delay between API calls in ms (for bulk ops)
  --page N         Page number for pagination (0-indexed)
  -h, --help       Show this help

Update Options (for 'update' command):
  --tags TAG1,TAG2    Set tags (comma-separated)
  --title TITLE       Set title
  --collection ID     Move to collection

Collection IDs:
  0   = All bookmarks
  -1  = Unsorted
  -99 = Trash
  N   = Specific collection ID

Examples:
  raindrop.sh collections
  raindrop.sh create-collection "AI Coding"
  raindrop.sh list -1 --limit 50              # List unsorted
  raindrop.sh count -1                         # Count unsorted
  raindrop.sh move 12345 50436390             # Move to collection
  raindrop.sh update 12345 --tags "ai,coding" --collection 50436390
  raindrop.sh bulk-move "123,456,789" 50436390 --delay 100
  raindrop.sh list-untagged -1                 # Untagged in unsorted
EOF
  exit 0
}

die() { echo "Error: $1" >&2; exit 1; }

is_int() {
  [[ "${1:-}" =~ ^-?[0-9]+$ ]]
}

is_uint() {
  [[ "${1:-}" =~ ^[0-9]+$ ]]
}

# Rate limiting helper
rate_limit() {
  if [[ "$DELAY" -gt 0 ]]; then
    sleep "$(echo "scale=3; $DELAY/1000" | bc)"
  fi
}

LIMIT=25
PAGE=0
POSITIONAL=()
UPDATE_TAGS=""
UPDATE_TITLE=""
UPDATE_COLLECTION=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --token) TOKEN="$2"; shift 2 ;;
    --json) FORMAT="json"; shift ;;
    --limit) LIMIT="$2"; shift 2 ;;
    --delay) DELAY="$2"; shift 2 ;;
    --page) PAGE="$2"; shift 2 ;;
    --tags) UPDATE_TAGS="$2"; shift 2 ;;
    --title) UPDATE_TITLE="$2"; shift 2 ;;
    --collection) UPDATE_COLLECTION="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) POSITIONAL+=("$1"); shift ;;
  esac
done
set -- "${POSITIONAL[@]:-}"

[[ -z "$TOKEN" ]] && die "Missing token. Set RAINDROP_TOKEN or use --token"

cmd="${1:-}"; shift || true

api() {
  local method="$1" endpoint="$2"
  shift 2
  rate_limit
  curl -sf -X "$method" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    "$@" "${API}${endpoint}"
}

format_bookmarks() {
  if [[ "$FORMAT" == "json" ]]; then
    cat
  else
    jq -r '.items[] | "[\(.collectionId)] \(.title)\n    \(.link)\n    tags: \(.tags | join(", ") | if . == "" then "-" else . end)\n    id: \(._id)\n"'
  fi
}

format_collections() {
  if [[ "$FORMAT" == "json" ]]; then
    cat
  else
    jq -r '.items[] | "\(.title) (id: \(._id), count: \(.count))"'
  fi
}

case "$cmd" in
  whoami)
    api GET "/user" | if [[ "$FORMAT" == "json" ]]; then cat; else jq -r '.user | "User: \(.name)\nEmail: \(.email)\nPro: \(.pro)"'; fi
    ;;
  
  collections)
    api GET "/collections" | format_collections
    ;;
  
  create-collection)
    [[ -z "${1:-}" ]] && die "Collection name required"
    name="$1"
    payload=$(jq -cn --arg title "$name" '{title: $title}')
    api POST "/collection" -d "$payload" | if [[ "$FORMAT" == "json" ]]; then cat; else jq -r '"Created: \(.item.title)\nID: \(.item._id)"'; fi
    ;;
  
  list)
    collection="${1:-0}"
    is_int "$collection" || die "Collection ID must be an integer"
    api GET "/raindrops/${collection}?perpage=${LIMIT}&page=${PAGE}" | format_bookmarks
    ;;
  
  count)
    collection="${1:-0}"
    if [[ "$collection" == "0" ]]; then
      # For "all", get user stats
      api GET "/user" | jq -r '.user.files.count'
    else
      # For specific collection, get collection info
      if [[ "$collection" == "-1" ]]; then
        # Unsorted - need to query and get count from response
        api GET "/raindrops/-1?perpage=1" | jq -r '.count'
      elif [[ "$collection" == "-99" ]]; then
        api GET "/raindrops/-99?perpage=1" | jq -r '.count'
      else
        is_int "$collection" || die "Collection ID must be an integer"
        api GET "/collection/$collection" | jq -r '.item.count'
      fi
    fi
    ;;
  
  search)
    [[ -z "${1:-}" ]] && die "Search query required"
    query="$1"
    collection="${2:-0}"
    is_int "$collection" || die "Collection ID must be an integer"
    encoded=$(printf '%s' "$query" | jq -sRr @uri)
    api GET "/raindrops/${collection}?search=${encoded}&perpage=${LIMIT}" | format_bookmarks
    ;;
  
  get)
    [[ -z "${1:-}" ]] && die "Bookmark ID required"
    id="$1"
    is_uint "$id" || die "Bookmark ID must be an unsigned integer"
    api GET "/raindrop/$id" | if [[ "$FORMAT" == "json" ]]; then cat; else jq -r '.item | "Title: \(.title)\nURL: \(.link)\nCollection: \(.collectionId)\nTags: \(.tags | join(", "))\nCreated: \(.created)\nNote: \(.note // "-")\nCache: \(.cache.status // "none")"'; fi
    ;;
  
  add)
    [[ -z "${1:-}" ]] && die "URL required"
    url="$1"
    collection="${2:--1}"
    is_int "$collection" || die "Collection ID must be an integer"
    payload=$(jq -cn --arg link "$url" --argjson collectionId "$collection" '{link: $link, collectionId: $collectionId}')
    api POST "/raindrop" -d "$payload" | if [[ "$FORMAT" == "json" ]]; then cat; else jq -r '"Added: \(.item.title)\nID: \(.item._id)"'; fi
    ;;
  
  delete)
    [[ -z "${1:-}" ]] && die "Bookmark ID required"
    id="$1"
    is_uint "$id" || die "Bookmark ID must be an unsigned integer"
    api DELETE "/raindrop/$id" | if [[ "$FORMAT" == "json" ]]; then cat; else jq -r 'if .result then "Deleted" else "Failed" end'; fi
    ;;
  
  move)
    [[ -z "${1:-}" ]] && die "Bookmark ID required"
    [[ -z "${2:-}" ]] && die "Collection ID required"
    id="$1"
    collection="$2"
    is_uint "$id" || die "Bookmark ID must be an unsigned integer"
    is_int "$collection" || die "Collection ID must be an integer"
    payload=$(jq -cn --argjson collectionId "$collection" '{collectionId: $collectionId}')
    api PUT "/raindrop/$id" -d "$payload" | if [[ "$FORMAT" == "json" ]]; then cat; else jq -r '"Moved: \(.item.title) -> collection \(.item.collectionId)"'; fi
    ;;
  
  update)
    [[ -z "${1:-}" ]] && die "Bookmark ID required"
    id="$1"
    is_uint "$id" || die "Bookmark ID must be an unsigned integer"
    
    if [[ -n "$UPDATE_COLLECTION" ]]; then
      is_int "$UPDATE_COLLECTION" || die "--collection must be an integer"
    fi

    payload=$(jq -cn \
      --arg tags "$UPDATE_TAGS" \
      --arg title "$UPDATE_TITLE" \
      --arg collection "$UPDATE_COLLECTION" \
      '
      (if ($tags | length) > 0 then
        {
          tags: (
            $tags
            | split(",")
            | map(gsub("^\\s+|\\s+$"; ""))
            | map(select(length > 0))
          )
        }
      else {} end)
      +
      (if ($title | length) > 0 then {title: $title} else {} end)
      +
      (if ($collection | length) > 0 then {collectionId: ($collection | tonumber)} else {} end)
      ')

    [[ "$payload" == "{}" ]] && die "No update options provided. Use --tags, --title, or --collection"

    api PUT "/raindrop/$id" -d "$payload" | if [[ "$FORMAT" == "json" ]]; then cat; else jq -r '"Updated: \(.item.title)\nTags: \(.item.tags | join(", "))\nCollection: \(.item.collectionId)"'; fi
    ;;
  
  bulk-move)
    [[ -z "${1:-}" ]] && die "Comma-separated bookmark IDs required"
    [[ -z "${2:-}" ]] && die "Target collection ID required"
    ids="$1"
    target_collection="$2"
    source_collection="${3:--1}"  # Default to Unsorted (-1) if not specified

    is_int "$target_collection" || die "Target collection ID must be an integer"
    is_int "$source_collection" || die "Source collection ID must be an integer"

    ids_json=$(jq -cn --arg ids "$ids" '
      $ids
      | split(",")
      | map(gsub("^\\s+|\\s+$"; ""))
      | map(select(length > 0))
      | map(tonumber)
    ')
    payload=$(jq -cn --argjson ids "$ids_json" --argjson target "$target_collection" '{ids: $ids, collection: {"$id": $target}}')

    # Use bulk update API - requires source collection in path, target as collection.$id in body
    api PUT "/raindrops/${source_collection}" -d "$payload" | if [[ "$FORMAT" == "json" ]]; then cat; else jq -r '"Moved \(.modified) bookmarks to collection '"$target_collection"'"'; fi
    ;;
  
  tags)
    api GET "/tags" | if [[ "$FORMAT" == "json" ]]; then cat; else jq -r '.items[] | "\(._id) (\(.count))"'; fi
    ;;
  
  suggest)
    [[ -z "${1:-}" ]] && die "URL required"
    url="$1"
    encoded=$(printf '%s' "$url" | jq -sRr @uri)
    api GET "/import/url/parse?url=${encoded}" | if [[ "$FORMAT" == "json" ]]; then cat; else jq -r '"Title: \(.item.title // "-")\nType: \(.item.type // "-")\nSuggested tags: \(.item.meta.tags // [] | join(", ") | if . == "" then "-" else . end)"'; fi
    ;;
  
  list-untagged)
    collection="${1:--1}"
    is_int "$collection" || die "Collection ID must be an integer"
    # Search for bookmarks and filter those with empty tags
    api GET "/raindrops/${collection}?perpage=${LIMIT}&page=${PAGE}" | \
      if [[ "$FORMAT" == "json" ]]; then
        jq '{items: [.items[] | select(.tags | length == 0)], count: .count}'
      else
        jq -r '.items[] | select(.tags | length == 0) | "[\(.collectionId)] \(.title)\n    \(.link)\n    id: \(._id)\n"'
      fi
    ;;
  
  cache)
    [[ -z "${1:-}" ]] && die "Bookmark ID required"
    id="$1"
    is_uint "$id" || die "Bookmark ID must be an unsigned integer"
    curl -sL -H "Authorization: Bearer $TOKEN" "${API}/raindrop/$id/cache"
    ;;
  
  ""|help)
    usage
    ;;
  
  *)
    die "Unknown command: $cmd. Run with --help for usage."
    ;;
esac
