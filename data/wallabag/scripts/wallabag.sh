#!/usr/bin/env bash
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
ACCESS_TOKEN=""
TOKEN_JSON=""

usage() {
  cat <<USAGE
Usage:
  $SCRIPT_NAME auth [--show-token]
  $SCRIPT_NAME list [--search <text>] [--tag <name>] [--archive 0|1] [--starred 0|1] [--page <n>] [--per-page <n>]
  $SCRIPT_NAME get --id <entry_id>
  $SCRIPT_NAME create --url <url> [--title <title>] [--tags <csv>]
  $SCRIPT_NAME update --id <entry_id> [--title <title>] [--tags <csv>] [--archive 0|1] [--starred 0|1]
  $SCRIPT_NAME delete --id <entry_id>
  $SCRIPT_NAME tag add --id <entry_id> --tags <csv>
  $SCRIPT_NAME tag remove --id <entry_id> --tag <name>
USAGE
}

error() {
  echo "[$SCRIPT_NAME] $*" >&2
}

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    error "Missing required command: $cmd"
    exit 127
  fi
}

has_jq() {
  command -v jq >/dev/null 2>&1
}

require_jq() {
  if ! has_jq; then
    error "This command requires 'jq' to be installed."
    exit 2
  fi
}

require_env() {
  local missing=0
  for key in WALLABAG_BASE_URL WALLABAG_CLIENT_ID WALLABAG_CLIENT_SECRET WALLABAG_USERNAME WALLABAG_PASSWORD; do
    if [[ -z "${!key:-}" ]]; then
      error "Missing required environment variable: $key"
      missing=1
    fi
  done
  if [[ "$missing" -ne 0 ]]; then
    exit 2
  fi
}

normalize_base_url() {
  WALLABAG_BASE_URL="${WALLABAG_BASE_URL%/}"
}

extract_json_field() {
  local json="$1"
  local key="$2"

  if has_jq; then
    jq -r --arg key "$key" '.[$key] // empty' <<<"$json"
    return
  fi

  sed -nE "s/.*\"$key\"[[:space:]]*:[[:space:]]*\"([^\"]+)\".*/\1/p" <<<"$json" | head -n1
}

oauth_token() {
  require_env
  normalize_base_url
  require_cmd curl

  local response
  local http_code

  response="$(curl -sS -w $'\n%{http_code}' -X POST "${WALLABAG_BASE_URL}/oauth/v2/token" \
    --data-urlencode "grant_type=password" \
    --data-urlencode "client_id=${WALLABAG_CLIENT_ID}" \
    --data-urlencode "client_secret=${WALLABAG_CLIENT_SECRET}" \
    --data-urlencode "username=${WALLABAG_USERNAME}" \
    --data-urlencode "password=${WALLABAG_PASSWORD}")"

  http_code="$(tail -n1 <<<"$response")"
  TOKEN_JSON="$(sed '$d' <<<"$response")"

  if [[ ! "$http_code" =~ ^2 ]]; then
    error "OAuth failed with HTTP $http_code"
    echo "$TOKEN_JSON" >&2
    exit 1
  fi

  ACCESS_TOKEN="$(extract_json_field "$TOKEN_JSON" "access_token")"
  if [[ -z "$ACCESS_TOKEN" ]]; then
    error "OAuth succeeded but access_token is missing in response."
    echo "$TOKEN_JSON" >&2
    exit 1
  fi
}

ensure_token() {
  if [[ -z "$ACCESS_TOKEN" ]]; then
    oauth_token
  fi
}

api_call() {
  local method="$1"
  local path="$2"
  shift 2

  ensure_token
  require_cmd curl

  local tmp
  local code
  tmp="$(mktemp)"

  set +e
  code="$(curl -sS -o "$tmp" -w "%{http_code}" -X "$method" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Accept: application/json" \
    "$@" \
    "${WALLABAG_BASE_URL}${path}")"
  local curl_status=$?
  set -e

  if [[ "$curl_status" -ne 0 ]]; then
    error "Network error while calling ${path}"
    cat "$tmp" >&2 || true
    rm -f "$tmp"
    exit "$curl_status"
  fi

  if [[ "$code" =~ ^2 ]]; then
    cat "$tmp"
  else
    error "API request failed: ${method} ${path} (HTTP $code)"
    cat "$tmp" >&2
    rm -f "$tmp"
    exit 1
  fi

  rm -f "$tmp"
}

append_data() {
  local arr_name="$1"
  local key="$2"
  local value="${3:-}"
  if [[ -n "$value" ]]; then
    eval "$arr_name+=(--data-urlencode \"$key=$value\")"
  fi
}

get_entry_tags_csv() {
  local id="$1"
  require_jq
  local entry_json
  entry_json="$(api_call GET "/api/entries/${id}.json")"
  jq -r '[.tags[]? | (.label // .slug // .name // empty)] | join(",")' <<<"$entry_json"
}

tags_add() {
  local id="$1"
  local add_csv="$2"
  require_jq

  local current_csv
  current_csv="$(get_entry_tags_csv "$id")"

  local merged
  merged="$(jq -nr --arg current "$current_csv" --arg add "$add_csv" '
    def splitcsv($s): ($s | split(",") | map(gsub("^\\s+|\\s+$"; "")) | map(select(length > 0)));
    ((splitcsv($current) + splitcsv($add)) | unique | join(","))
  ')"

  api_call PATCH "/api/entries/${id}.json" --data-urlencode "tags=${merged}"
}

tags_remove() {
  local id="$1"
  local remove_tag="$2"
  require_jq

  local current_csv
  current_csv="$(get_entry_tags_csv "$id")"

  local updated
  updated="$(jq -nr --arg current "$current_csv" --arg remove "$remove_tag" '
    def splitcsv($s): ($s | split(",") | map(gsub("^\\s+|\\s+$"; "")) | map(select(length > 0)));
    (splitcsv($current) | map(select(. != $remove)) | unique | join(","))
  ')"

  api_call PATCH "/api/entries/${id}.json" --data-urlencode "tags=${updated}"
}

cmd_auth() {
  local show_token=0

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --show-token) show_token=1; shift ;;
      *) error "Unknown option for auth: $1"; usage; exit 2 ;;
    esac
  done

  oauth_token

  if [[ "$show_token" -eq 1 ]]; then
    echo "$TOKEN_JSON"
  else
    echo '{"status":"ok","message":"Authenticated. Access token kept in-process and not printed."}'
  fi
}

cmd_list() {
  local search=""
  local tag=""
  local archive=""
  local starred=""
  local page=""
  local per_page=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --search) search="${2:-}"; shift 2 ;;
      --tag) tag="${2:-}"; shift 2 ;;
      --archive) archive="${2:-}"; shift 2 ;;
      --starred) starred="${2:-}"; shift 2 ;;
      --page) page="${2:-}"; shift 2 ;;
      --per-page) per_page="${2:-}"; shift 2 ;;
      *) error "Unknown option for list: $1"; usage; exit 2 ;;
    esac
  done

  local args=()
  append_data args "search" "$search"
  append_data args "tags" "$tag"
  append_data args "archive" "$archive"
  append_data args "starred" "$starred"
  append_data args "page" "$page"
  append_data args "perPage" "$per_page"

  api_call GET "/api/entries.json" --get "${args[@]}"
}

cmd_get() {
  local id=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) id="${2:-}"; shift 2 ;;
      *) error "Unknown option for get: $1"; usage; exit 2 ;;
    esac
  done

  if [[ -z "$id" ]]; then
    error "get requires --id"
    exit 2
  fi

  api_call GET "/api/entries/${id}.json"
}

cmd_create() {
  local url=""
  local title=""
  local tags=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --url) url="${2:-}"; shift 2 ;;
      --title) title="${2:-}"; shift 2 ;;
      --tags) tags="${2:-}"; shift 2 ;;
      *) error "Unknown option for create: $1"; usage; exit 2 ;;
    esac
  done

  if [[ -z "$url" ]]; then
    error "create requires --url"
    exit 2
  fi

  local args=(--data-urlencode "url=${url}")
  append_data args "title" "$title"
  append_data args "tags" "$tags"

  api_call POST "/api/entries.json" "${args[@]}"
}

cmd_update() {
  local id=""
  local title=""
  local tags=""
  local archive=""
  local starred=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) id="${2:-}"; shift 2 ;;
      --title) title="${2:-}"; shift 2 ;;
      --tags) tags="${2:-}"; shift 2 ;;
      --archive) archive="${2:-}"; shift 2 ;;
      --starred) starred="${2:-}"; shift 2 ;;
      *) error "Unknown option for update: $1"; usage; exit 2 ;;
    esac
  done

  if [[ -z "$id" ]]; then
    error "update requires --id"
    exit 2
  fi

  local args=()
  append_data args "title" "$title"
  append_data args "tags" "$tags"
  append_data args "archive" "$archive"
  append_data args "starred" "$starred"

  if [[ "${#args[@]}" -eq 0 ]]; then
    error "update requires at least one field to update"
    exit 2
  fi

  api_call PATCH "/api/entries/${id}.json" "${args[@]}"
}

cmd_delete() {
  local id=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) id="${2:-}"; shift 2 ;;
      *) error "Unknown option for delete: $1"; usage; exit 2 ;;
    esac
  done

  if [[ -z "$id" ]]; then
    error "delete requires --id"
    exit 2
  fi

  api_call DELETE "/api/entries/${id}.json"
}

cmd_tag() {
  local action="${1:-}"
  if [[ -z "$action" ]]; then
    error "tag requires an action: add|remove"
    exit 2
  fi
  shift

  case "$action" in
    add)
      local id=""
      local tags=""
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --id) id="${2:-}"; shift 2 ;;
          --tags) tags="${2:-}"; shift 2 ;;
          *) error "Unknown option for tag add: $1"; usage; exit 2 ;;
        esac
      done
      if [[ -z "$id" || -z "$tags" ]]; then
        error "tag add requires --id and --tags"
        exit 2
      fi
      tags_add "$id" "$tags"
      ;;
    remove)
      local id=""
      local tag=""
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --id) id="${2:-}"; shift 2 ;;
          --tag) tag="${2:-}"; shift 2 ;;
          *) error "Unknown option for tag remove: $1"; usage; exit 2 ;;
        esac
      done
      if [[ -z "$id" || -z "$tag" ]]; then
        error "tag remove requires --id and --tag"
        exit 2
      fi
      tags_remove "$id" "$tag"
      ;;
    *)
      error "Unknown tag action: $action"
      usage
      exit 2
      ;;
  esac
}

main() {
  if [[ $# -lt 1 ]]; then
    usage
    exit 2
  fi

  local subcommand="$1"
  shift

  case "$subcommand" in
    auth) cmd_auth "$@" ;;
    list) cmd_list "$@" ;;
    get) cmd_get "$@" ;;
    create) cmd_create "$@" ;;
    update) cmd_update "$@" ;;
    delete) cmd_delete "$@" ;;
    tag) cmd_tag "$@" ;;
    -h|--help|help) usage ;;
    *)
      error "Unknown subcommand: $subcommand"
      usage
      exit 2
      ;;
  esac
}

main "$@"
