#!/usr/bin/env bash
set -euo pipefail

API_BASE="https://api.typefully.com/v2"
SOCIAL_SET_ID=""
API_KEY=""

# --- Helpers ---

die() { echo "Error: $*" >&2; exit 1; }

get_api_key() {
  API_KEY="${TYPEFULLY_API_KEY:-}"
  if [[ -z "$API_KEY" ]]; then
    command -v pass >/dev/null 2>&1 || die "'pass' is not installed. Set TYPEFULLY_API_KEY env var or install pass."
    API_KEY=$(pass typefully/api-key 2>/dev/null) || die "Could not retrieve API key. Set TYPEFULLY_API_KEY or store in pass typefully/api-key"
  fi
}

resolve_social_set_id() {
  SOCIAL_SET_ID="${TYPEFULLY_SOCIAL_SET_ID:-}"
  if [[ -z "$SOCIAL_SET_ID" ]]; then
    SOCIAL_SET_ID=$(pass typefully/social-set-id 2>/dev/null) || true
  fi
  if [[ -z "$SOCIAL_SET_ID" ]]; then
    # Auto-detect from API
    local response
    response=$(api GET "/social-sets")
    local count
    count=$(printf '%s' "$response" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(len(d))' 2>/dev/null) || die "Failed to parse social sets response"
    if [[ "$count" -eq 0 ]]; then
      die "No social sets found. Check your Typefully account."
    elif [[ "$count" -eq 1 ]]; then
      SOCIAL_SET_ID=$(printf '%s' "$response" | python3 -c 'import sys,json; print(json.load(sys.stdin)[0]["id"])')
    else
      die "Multiple social sets found. Set TYPEFULLY_SOCIAL_SET_ID or store in pass typefully/social-set-id. Use list-social-sets to see options."
    fi
  fi
  [[ "$SOCIAL_SET_ID" =~ ^[0-9]+$ ]] || die "Invalid social_set_id: $SOCIAL_SET_ID"
}

validate_draft_id() {
  [[ "$1" =~ ^[0-9]+$ ]] || die "Invalid draft ID: $1 (must be numeric)"
}

validate_schedule() {
  local val="$1"
  case "$val" in
    next-free-slot|now) return 0 ;;
  esac
  # ISO 8601 pattern
  if [[ "$val" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2} ]]; then
    return 0
  fi
  die "Invalid schedule value: $val (expected ISO 8601, 'next-free-slot', or 'now')"
}

validate_platform() {
  local p="$1"
  [[ "$p" =~ ^(x|linkedin|threads|bluesky|mastodon)$ ]] || die "Invalid platform: $p (allowed: x, linkedin, threads, bluesky, mastodon)"
}

api() {
  local method="$1" endpoint="$2"
  shift 2

  local http_code body tmpfile
  tmpfile=$(mktemp)

  http_code=$(curl -s -w '%{http_code}' -o "$tmpfile" -X "$method" "${API_BASE}${endpoint}" \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/json" \
    "$@") || { rm -f "$tmpfile"; die "curl failed (network error)"; }

  body=$(cat "$tmpfile")
  rm -f "$tmpfile"

  case "$http_code" in
    2[0-9][0-9]) printf '%s' "$body" ;;
    401) die "Authentication failed (401). Check your API key." ;;
    404) die "Not found (404). Check the resource ID." ;;
    429) die "Rate limited (429). Try again later." ;;
    *)   die "API error (HTTP $http_code): $body" ;;
  esac
}

build_posts_json() {
  local text="$1" is_thread="$2"
  if [[ "$is_thread" == true ]]; then
    local posts_json="["
    local first=true
    while IFS= read -r post; do
      if [[ "$first" == true ]]; then first=false; else posts_json+=","; fi
      local escaped
      escaped=$(printf '%s' "$post" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')
      posts_json+="{\"text\":${escaped}}"
    done <<< "$(printf '%b' "$text" | sed 's/\\n---\\n/\n/g')"
    posts_json+="]"
    printf '%s' "$posts_json"
  else
    local escaped
    escaped=$(printf '%s' "$text" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')
    printf '%s' "[{\"text\":${escaped}}]"
  fi
}

build_platform_json() {
  local platforms="$1" posts_json="$2"
  local platform_json=""
  IFS=',' read -ra plats <<< "$platforms"
  for p in "${plats[@]}"; do
    validate_platform "$p"
    if [[ -n "$platform_json" ]]; then platform_json+=","; fi
    platform_json+="\"${p}\":{\"enabled\":true,\"posts\":${posts_json}}"
  done
  printf '%s' "$platform_json"
}

# --- Commands ---

cmd_list_social_sets() {
  api GET "/social-sets"
}

cmd_list_drafts() {
  local status="${1:-}" limit="${2:-10}"
  local url="/social-sets/${SOCIAL_SET_ID}/drafts?limit=${limit}"
  if [[ -n "$status" ]]; then
    url="${url}&status=${status}"
  fi
  api GET "$url"
}

cmd_get_draft() {
  local draft_id="$1"
  validate_draft_id "$draft_id"
  api GET "/social-sets/${SOCIAL_SET_ID}/drafts/${draft_id}"
}

cmd_create_draft() {
  local text=""
  local platforms="x" schedule="" is_thread=false

  # Support reading from stdin if no text arg or text is "-"
  if [[ $# -eq 0 ]] || [[ "$1" == "-" ]]; then
    text=$(cat)
    [[ $# -gt 0 ]] && shift
  else
    text="$1"
    shift
  fi

  [[ -z "$text" ]] && die "No text provided"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --platform) platforms="$2"; shift 2 ;;
      --schedule) schedule="$2"; shift 2 ;;
      --thread) is_thread=true; shift ;;
      *) die "Unknown option: $1" ;;
    esac
  done

  local posts_json
  posts_json=$(build_posts_json "$text" "$is_thread")
  local platform_json
  platform_json=$(build_platform_json "$platforms" "$posts_json")

  local body="{\"platforms\":{${platform_json}}"
  if [[ -n "$schedule" ]]; then
    validate_schedule "$schedule"
    body+=",\"publish_at\":\"${schedule}\""
  fi
  body+="}"

  api POST "/social-sets/${SOCIAL_SET_ID}/drafts" -d "$body"
}

cmd_edit_draft() {
  local draft_id="$1"
  validate_draft_id "$draft_id"
  local text="$2"
  shift 2
  local platforms="x" is_thread=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --platform) platforms="$2"; shift 2 ;;
      --thread) is_thread=true; shift ;;
      *) die "Unknown option: $1" ;;
    esac
  done

  local posts_json
  posts_json=$(build_posts_json "$text" "$is_thread")
  local platform_json
  platform_json=$(build_platform_json "$platforms" "$posts_json")

  api PUT "/social-sets/${SOCIAL_SET_ID}/drafts/${draft_id}" \
    -d "{\"platforms\":{${platform_json}}}"
}

cmd_schedule_draft() {
  local draft_id="$1" when="$2"
  validate_draft_id "$draft_id"
  validate_schedule "$when"
  api PUT "/social-sets/${SOCIAL_SET_ID}/drafts/${draft_id}" \
    -d "{\"publish_at\":\"${when}\"}"
}

cmd_delete_draft() {
  local draft_id="$1"
  validate_draft_id "$draft_id"
  api DELETE "/social-sets/${SOCIAL_SET_ID}/drafts/${draft_id}"
}

usage() {
  cat <<'EOF'
Usage: typefully.sh <command> [args]

Commands:
  list-social-sets                         List social sets (accounts)
  list-drafts [status] [limit]             List drafts (status: draft|scheduled|published)
  get-draft <draft_id>                     Get draft details
  create-draft <text> [options]            Create a draft (use "-" or omit text to read from stdin)
    --thread                               Treat text as thread (split on \n---\n)
    --platform <x,linkedin,...>            Platforms (default: x)
    --schedule <iso8601|next-free-slot>    Schedule the draft
  edit-draft <draft_id> <text> [options]   Edit a draft
    --thread                               Treat text as thread (split on \n---\n)
    --platform <x,linkedin,...>            Platforms (default: x)
  schedule-draft <draft_id> <when>         Schedule/publish (iso8601|next-free-slot|now)
  delete-draft <draft_id>                  Delete a draft

Environment:
  TYPEFULLY_API_KEY        API key (fallback: pass typefully/api-key)
  TYPEFULLY_SOCIAL_SET_ID  Social set ID (fallback: pass typefully/social-set-id, then auto-detect)
EOF
  exit 0
}

main() {
  [[ $# -lt 1 ]] && usage

  case "$1" in
    --help|-h) usage ;;
  esac

  get_api_key

  local cmd="$1"
  shift

  # list-social-sets doesn't need social_set_id
  if [[ "$cmd" != "list-social-sets" ]]; then
    resolve_social_set_id
  fi

  case "$cmd" in
    list-social-sets) cmd_list_social_sets ;;
    list-drafts) cmd_list_drafts "$@" ;;
    get-draft) [[ $# -lt 1 ]] && usage; cmd_get_draft "$@" ;;
    create-draft) cmd_create_draft "$@" ;;
    edit-draft) [[ $# -lt 2 ]] && usage; cmd_edit_draft "$@" ;;
    schedule-draft) [[ $# -lt 2 ]] && usage; cmd_schedule_draft "$@" ;;
    delete-draft) [[ $# -lt 1 ]] && usage; cmd_delete_draft "$@" ;;
    --help|-h) usage ;;
    *) die "Unknown command: $cmd. Run with --help for usage." ;;
  esac
}

main "$@"
