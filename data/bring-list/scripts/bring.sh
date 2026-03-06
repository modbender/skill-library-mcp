#!/usr/bin/env bash
# bring.sh — CLI for the Bring! Shopping Lists API
# Requires: curl, jq
# Auth: BRING_EMAIL + BRING_PASSWORD env vars, or ~/.config/bring/credentials.json
set -euo pipefail

###############################################################################
# Constants
###############################################################################
API_BASE="https://api.getbring.com/rest"
# Public Bring! app API key — NOT a secret. Every Bring client uses this same key.
API_KEY="cof4Nc6D8saplXjE3h3HXqHH8m7VU2i1Gs0g85Sp"
TOKEN_FILE="${BRING_TOKEN_FILE:-${HOME}/.cache/bring/token.json}"
CRED_FILE="${BRING_CREDENTIALS_FILE:-${HOME}/.config/bring/credentials.json}"
# Country code for Bring API (affects item catalog language). Override in credentials.json.
BRING_COUNTRY="${BRING_COUNTRY:-DE}"

###############################################################################
# Helpers
###############################################################################
die()  { echo "ERROR: $*" >&2; exit 1; }
info() { echo "$*" >&2; }

require_cmd() {
  for cmd in "$@"; do
    command -v "$cmd" >/dev/null 2>&1 || die "Required command '$cmd' not found. Install it first."
  done
}

# URL-encode a string (handles special chars like #, &, =, spaces, etc.)
# Uses jq (required dep) as primary encoder; falls back to python3 (optional) then sed.
urlencode() {
  printf '%s' "$1" | jq -sRr @uri 2>/dev/null \
    || python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.stdin.read().rstrip('\n'), safe=''))" <<< "$1" 2>/dev/null \
    || printf '%s' "$1" | sed 's/%/%25/g; s/ /%20/g; s/!/%21/g; s/#/%23/g; s/\$/%24/g; s/&/%26/g; s/'\''/%27/g; s/(/%28/g; s/)/%29/g; s/\*/%2A/g; s/+/%2B/g; s/,/%2C/g; s|/|%2F|g; s/:/%3A/g; s/;/%3B/g; s/=/%3D/g; s/?/%3F/g; s/@/%40/g; s/\[/%5B/g; s/\]/%5D/g'
}

require_cmd curl jq

###############################################################################
# Credentials
###############################################################################
load_credentials() {
  # Priority: env vars > credentials file
  if [[ -n "${BRING_EMAIL:-}" && -n "${BRING_PASSWORD:-}" ]]; then
    :
  elif [[ -f "$CRED_FILE" ]]; then
    BRING_EMAIL="$(jq -r '.email // empty' "$CRED_FILE" 2>/dev/null)" || true
    BRING_PASSWORD="$(jq -r '.password // empty' "$CRED_FILE" 2>/dev/null)" || true
    export BRING_EMAIL BRING_PASSWORD
  fi

  if [[ -z "${BRING_EMAIL:-}" || -z "${BRING_PASSWORD:-}" ]]; then
    die "No credentials found. Set BRING_EMAIL and BRING_PASSWORD env vars, or create $CRED_FILE with {\"email\":\"...\",\"password\":\"...\"}"
  fi

  # Load default list if configured
  if [[ -z "${BRING_DEFAULT_LIST:-}" && -f "$CRED_FILE" ]]; then
    BRING_DEFAULT_LIST="$(jq -r '.default_list // empty' "$CRED_FILE" 2>/dev/null)" || true
    export BRING_DEFAULT_LIST
  fi

  # Load country override if configured
  if [[ -f "$CRED_FILE" ]]; then
    local cfg_country
    cfg_country="$(jq -r '.country // empty' "$CRED_FILE" 2>/dev/null)" || true
    if [[ -n "$cfg_country" ]]; then
      BRING_COUNTRY="$cfg_country"
    fi
  fi
}

# Resolve list argument: use provided value or fall back to default
resolve_list_arg() {
  local input="${1:-}"
  if [[ -z "$input" ]]; then
    if [[ -n "${BRING_DEFAULT_LIST:-}" ]]; then
      echo "$BRING_DEFAULT_LIST"
    else
      die "No list specified and no default_list configured. Set \"default_list\" in $CRED_FILE or pass a list name."
    fi
  else
    echo "$input"
  fi
}

###############################################################################
# Token management
###############################################################################
save_token() {
  mkdir -p "$(dirname "$TOKEN_FILE")"
  cat > "$TOKEN_FILE"
  chmod 600 "$TOKEN_FILE"
}

load_token() {
  [[ -f "$TOKEN_FILE" ]] || return 1
  # Check expiry — token file stores expires_at (unix timestamp)
  local expires_at
  expires_at="$(jq -r '.expires_at // 0' "$TOKEN_FILE" 2>/dev/null)" || return 1
  local now
  now="$(date +%s)"
  if (( now >= expires_at - 60 )); then
    # Try refresh
    local refresh_token
    refresh_token="$(jq -r '.refresh_token // empty' "$TOKEN_FILE" 2>/dev/null)" || return 1
    if [[ -n "$refresh_token" ]]; then
      refresh_access_token "$refresh_token" && return 0
    fi
    return 1
  fi
  return 0
}

get_header() {
  local field="$1"
  jq -r ".$field // empty" "$TOKEN_FILE" 2>/dev/null
}

auth_headers() {
  local token_type access_token uuid public_uuid
  token_type="$(get_header token_type)"
  access_token="$(get_header access_token)"
  uuid="$(get_header uuid)"
  public_uuid="$(get_header publicUuid)"

  echo -H "Authorization: ${token_type} ${access_token}" \
       -H "X-BRING-API-KEY: ${API_KEY}" \
       -H "X-BRING-CLIENT: android" \
       -H "X-BRING-APPLICATION: bring" \
       -H "X-BRING-COUNTRY: ${BRING_COUNTRY}" \
       -H "X-BRING-USER-UUID: ${uuid}" \
       -H "X-BRING-PUBLIC-USER-UUID: ${public_uuid}"
}

api_call() {
  local method="$1" url="$2"
  shift 2
  local token_type access_token uuid public_uuid
  token_type="$(get_header token_type)"
  access_token="$(get_header access_token)"
  uuid="$(get_header uuid)"
  public_uuid="$(get_header publicUuid)"

  local response http_code
  response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
    -H "Authorization: ${token_type} ${access_token}" \
    -H "X-BRING-API-KEY: ${API_KEY}" \
    -H "X-BRING-CLIENT: android" \
    -H "X-BRING-APPLICATION: bring" \
    -H "X-BRING-COUNTRY: ${BRING_COUNTRY}" \
    -H "X-BRING-USER-UUID: ${uuid}" \
    -H "X-BRING-PUBLIC-USER-UUID: ${public_uuid}" \
    "$@")

  http_code=$(echo "$response" | tail -1)
  local body
  body=$(echo "$response" | sed '$d')

  case "$http_code" in
    200|204|207) echo "$body" ;;
    401) die "Authentication failed (401). Token may be expired. Run: bring.sh login" ;;
    404) die "Not found (404). Check list UUID or item name." ;;
    *)   die "API error (HTTP $http_code): $body" ;;
  esac
}

###############################################################################
# Auth commands
###############################################################################
do_login() {
  load_credentials
  local enc_email enc_pass
  enc_email="$(urlencode "$BRING_EMAIL")"
  enc_pass="$(urlencode "$BRING_PASSWORD")"
  local response http_code
  response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/v2/bringauth" \
    -H "X-BRING-API-KEY: ${API_KEY}" \
    -H "X-BRING-CLIENT: android" \
    -H "X-BRING-APPLICATION: bring" \
    -d "email=${enc_email}&password=${enc_pass}")

  http_code=$(echo "$response" | tail -1)
  local body
  body=$(echo "$response" | sed '$d')

  case "$http_code" in
    200) ;;
    400) die "Login failed (400 Bad Request). Check your email address." ;;
    401) die "Login failed (401 Unauthorized). Check your email and password." ;;
    *)   die "Login failed (HTTP $http_code): $body" ;;
  esac

  # Calculate absolute expiry timestamp
  local expires_in now expires_at
  expires_in=$(echo "$body" | jq -r '.expires_in // 0')
  now=$(date +%s)
  expires_at=$(( now + expires_in ))

  # Save token with absolute expiry
  echo "$body" | jq --argjson ea "$expires_at" '. + {expires_at: $ea}' | save_token
  info "Login successful. Token cached at $TOKEN_FILE"
}

refresh_access_token() {
  local refresh_token="$1"
  local token_type access_token uuid public_uuid
  token_type="$(get_header token_type)"
  access_token="$(get_header access_token)"
  uuid="$(get_header uuid)"
  public_uuid="$(get_header publicUuid)"

  local response http_code
  response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/v2/bringauth/token" \
    -H "Authorization: ${token_type} ${access_token}" \
    -H "X-BRING-API-KEY: ${API_KEY}" \
    -H "X-BRING-CLIENT: android" \
    -H "X-BRING-APPLICATION: bring" \
    -d "grant_type=refresh_token&refresh_token=${refresh_token}")

  http_code=$(echo "$response" | tail -1)
  local body
  body=$(echo "$response" | sed '$d')

  if [[ "$http_code" != "200" ]]; then
    info "Token refresh failed (HTTP $http_code). Re-login required."
    return 1
  fi

  # Merge new token data into existing token file
  local new_expires_in now new_expires_at
  new_expires_in=$(echo "$body" | jq -r '.expires_in // 0')
  now=$(date +%s)
  new_expires_at=$(( now + new_expires_in ))

  jq -s --argjson ea "$new_expires_at" '.[0] * .[1] + {expires_at: $ea}' "$TOKEN_FILE" <(echo "$body") | save_token
  info "Token refreshed successfully."
  return 0
}

ensure_auth() {
  if ! load_token; then
    info "No valid token found. Logging in..."
    do_login
  fi
}

###############################################################################
# API commands
###############################################################################

# Get user UUID from token
get_uuid() {
  get_header uuid
}

# List all shopping lists
do_lists() {
  ensure_auth
  local uuid
  uuid="$(get_uuid)"
  local result
  result=$(api_call GET "${API_BASE}/bringusers/${uuid}/lists")
  echo "$result" | jq -r '.lists[] | select(.name != null and .name != "null") | "\(.listUuid)\t\(.name)\t\(.theme)"' | \
    while IFS=$'\t' read -r id name theme; do
      echo "${id}  ${name}  (theme: ${theme})"
    done
}

do_lists_json() {
  ensure_auth
  local uuid
  uuid="$(get_uuid)"
  api_call GET "${API_BASE}/bringusers/${uuid}/lists"
}

# Resolve list: by UUID or name (partial match)
resolve_list() {
  local input="$1"
  # If it looks like a UUID, use as-is
  if [[ "$input" =~ ^[0-9a-f-]{36}$ ]]; then
    echo "$input"
    return 0
  fi
  # Otherwise search by name
  ensure_auth
  local uuid
  uuid="$(get_uuid)"
  local lists_json
  lists_json=$(api_call GET "${API_BASE}/bringusers/${uuid}/lists")

  local list_uuid
  # Try exact match first (case-insensitive)
  list_uuid=$(echo "$lists_json" | jq -r --arg name "$input" \
    '.lists[] | select(.name | ascii_downcase == ($name | ascii_downcase)) | .listUuid' | head -1)

  if [[ -z "$list_uuid" ]]; then
    # Try partial match
    list_uuid=$(echo "$lists_json" | jq -r --arg name "$input" \
      '.lists[] | select(.name | ascii_downcase | contains($name | ascii_downcase)) | .listUuid' | head -1)
  fi

  if [[ -z "$list_uuid" ]]; then
    die "List not found: '$input'. Use 'bring.sh lists' to see available lists."
  fi
  echo "$list_uuid"
}

# Show items on a list
do_show() {
  local list_id="$1"
  ensure_auth
  local list_uuid
  list_uuid=$(resolve_list "$list_id")

  local result
  result=$(api_call GET "${API_BASE}/v2/bringlists/${list_uuid}")

  local purchase_count recently_count
  purchase_count=$(echo "$result" | jq '.items.purchase | length')
  recently_count=$(echo "$result" | jq '.items.recently | length')

  echo "🛒 Shopping List (${purchase_count} items to buy, ${recently_count} recently completed)"
  echo ""

  if (( purchase_count > 0 )); then
    echo "📋 TO BUY:"
    echo "$result" | jq -r '.items.purchase[] | "  • \(.itemId)\(if .specification != "" then " (\(.specification))" else "" end)"'
  else
    echo "📋 TO BUY: (empty)"
  fi

  echo ""

  if (( recently_count > 0 )); then
    echo "✅ RECENTLY COMPLETED:"
    echo "$result" | jq -r '.items.recently[] | "  ✓ \(.itemId)\(if .specification != "" then " (\(.specification))" else "" end)"'
  fi
}

do_show_json() {
  local list_id="$1"
  ensure_auth
  local list_uuid
  list_uuid=$(resolve_list "$list_id")
  api_call GET "${API_BASE}/v2/bringlists/${list_uuid}"
}

# Generate a UUID
gen_uuid() {
  cat /proc/sys/kernel/random/uuid 2>/dev/null || uuidgen 2>/dev/null || python3 -c "import uuid; print(uuid.uuid4())" 2>/dev/null || echo ""
}

# Build a single change entry as JSON (safe for any characters in item/spec)
build_change() {
  local item_name="$1" spec="$2" operation="$3" uuid="${4:-}"
  jq -n --arg item "$item_name" --arg spec "$spec" --arg op "$operation" --arg uuid "$uuid" \
    '{itemId: $item, spec: $spec, uuid: (if $uuid == "" then null else $uuid end), operation: $op, accuracy: "0.0", altitude: "0.0", latitude: "0.0", longitude: "0.0"}'
}

# Add an item to a list
do_add() {
  local list_id="$1"
  local item_name="$2"
  local spec="${3:-}"
  ensure_auth
  local list_uuid
  list_uuid=$(resolve_list "$list_id")

  local item_uuid
  item_uuid=$(gen_uuid)

  local json_data
  json_data=$(jq -n --argjson change "$(build_change "$item_name" "$spec" "TO_PURCHASE" "$item_uuid")" \
    '{changes: [$change], sender: ""}')

  api_call PUT "${API_BASE}/v2/bringlists/${list_uuid}/items" \
    -H "Content-Type: application/json" \
    -d "$json_data" > /dev/null

  if [[ -n "$spec" ]]; then
    echo "Added '${item_name}' (${spec}) to list."
  else
    echo "Added '${item_name}' to list."
  fi
}

# Remove an item from a list
do_remove() {
  local list_id="$1"
  local item_name="$2"
  ensure_auth
  local list_uuid
  list_uuid=$(resolve_list "$list_id")

  # Find the item's UUID from the list for precise removal
  local list_data item_uuid
  list_data=$(api_call GET "${API_BASE}/v2/bringlists/${list_uuid}")
  item_uuid=$(echo "$list_data" | jq -r --arg name "$item_name" \
    '(.items.purchase + .items.recently)[] | select(.itemId == $name) | .uuid' | head -1)

  if [[ -z "$item_uuid" ]]; then
    die "Item '${item_name}' not found on the list. Use 'bring.sh show' to see current items."
  fi

  local json_data
  json_data=$(jq -n --argjson change "$(build_change "$item_name" "" "REMOVE" "$item_uuid")" \
    '{changes: [$change], sender: ""}')

  api_call PUT "${API_BASE}/v2/bringlists/${list_uuid}/items" \
    -H "Content-Type: application/json" \
    -d "$json_data" > /dev/null

  echo "Removed '${item_name}' from list."
}

# Complete (check off) an item
do_complete() {
  local list_id="$1"
  local item_name="$2"
  ensure_auth
  local list_uuid
  list_uuid=$(resolve_list "$list_id")

  # Find the item's UUID for precise completion
  local list_data item_uuid spec
  list_data=$(api_call GET "${API_BASE}/v2/bringlists/${list_uuid}")
  item_uuid=$(echo "$list_data" | jq -r --arg name "$item_name" \
    '.items.purchase[] | select(.itemId == $name) | .uuid' | head -1)
  spec=$(echo "$list_data" | jq -r --arg name "$item_name" \
    '.items.purchase[] | select(.itemId == $name) | .specification' | head -1)

  if [[ -z "$item_uuid" ]]; then
    die "Item '${item_name}' not found on the purchase list. It may already be completed."
  fi

  local json_data
  json_data=$(jq -n --argjson change "$(build_change "$item_name" "${spec:-}" "TO_RECENTLY" "$item_uuid")" \
    '{changes: [$change], sender: ""}')

  api_call PUT "${API_BASE}/v2/bringlists/${list_uuid}/items" \
    -H "Content-Type: application/json" \
    -d "$json_data" > /dev/null

  echo "Completed '${item_name}' (moved to recently)."
}

# Uncomplete — move item from recently back to purchase list
do_uncomplete() {
  local list_id="$1"
  local item_name="$2"
  ensure_auth
  local list_uuid
  list_uuid=$(resolve_list "$list_id")

  # Find item in recently list
  local list_data item_uuid spec
  list_data=$(api_call GET "${API_BASE}/v2/bringlists/${list_uuid}")
  item_uuid=$(echo "$list_data" | jq -r --arg name "$item_name" \
    '.items.recently[] | select(.itemId == $name) | .uuid' | head -1)
  spec=$(echo "$list_data" | jq -r --arg name "$item_name" \
    '.items.recently[] | select(.itemId == $name) | .specification' | head -1)

  if [[ -z "$item_uuid" ]]; then
    die "Item '${item_name}' not found in recently completed items."
  fi

  local json_data
  json_data=$(jq -n --argjson change "$(build_change "$item_name" "${spec:-}" "TO_PURCHASE" "$item_uuid")" \
    '{changes: [$change], sender: ""}')

  api_call PUT "${API_BASE}/v2/bringlists/${list_uuid}/items" \
    -H "Content-Type: application/json" \
    -d "$json_data" > /dev/null

  echo "Moved '${item_name}' back to purchase list."
}

# Add multiple items at once
do_add_multi() {
  local list_id="$1"
  shift
  ensure_auth
  local list_uuid
  list_uuid=$(resolve_list "$list_id")

  local changes="[]"
  for item_spec in "$@"; do
    local item_name spec item_uuid
    # Support "item|spec" format
    item_name="${item_spec%%|*}"
    if [[ "$item_spec" == *"|"* ]]; then
      spec="${item_spec#*|}"
    else
      spec=""
    fi
    item_uuid=$(gen_uuid)

    changes=$(echo "$changes" | jq --argjson entry "$(build_change "$item_name" "$spec" "TO_PURCHASE" "$item_uuid")" '. + [$entry]')
  done

  local json_data
  json_data=$(jq -n --argjson changes "$changes" '{"changes": $changes, "sender": ""}')

  api_call PUT "${API_BASE}/v2/bringlists/${list_uuid}/items" \
    -H "Content-Type: application/json" \
    -d "$json_data" > /dev/null

  echo "Added $# item(s) to list."
}

# Remove multiple items at once
do_remove_multi() {
  local list_id="$1"
  shift
  ensure_auth
  local list_uuid
  list_uuid=$(resolve_list "$list_id")

  local list_data
  list_data=$(api_call GET "${API_BASE}/v2/bringlists/${list_uuid}")

  local changes="[]"
  for item_name in "$@"; do
    local item_uuid
    item_uuid=$(echo "$list_data" | jq -r --arg name "$item_name" \
      '(.items.purchase + .items.recently)[] | select(.itemId == $name) | .uuid' | head -1)
    changes=$(echo "$changes" | jq --argjson entry "$(build_change "$item_name" "" "REMOVE" "$item_uuid")" '. + [$entry]')
  done

  local json_data
  json_data=$(jq -n --argjson changes "$changes" '{"changes": $changes, "sender": ""}')

  api_call PUT "${API_BASE}/v2/bringlists/${list_uuid}/items" \
    -H "Content-Type: application/json" \
    -d "$json_data" > /dev/null

  echo "Removed $# item(s) from list."
}

# Complete multiple items at once
do_complete_multi() {
  local list_id="$1"
  shift
  ensure_auth
  local list_uuid
  list_uuid=$(resolve_list "$list_id")

  local list_data
  list_data=$(api_call GET "${API_BASE}/v2/bringlists/${list_uuid}")

  local changes="[]"
  local count=0
  for item_name in "$@"; do
    local item_uuid spec
    item_uuid=$(echo "$list_data" | jq -r --arg name "$item_name" \
      '.items.purchase[] | select(.itemId == $name) | .uuid' | head -1)
    spec=$(echo "$list_data" | jq -r --arg name "$item_name" \
      '.items.purchase[] | select(.itemId == $name) | .specification' | head -1)
    if [[ -n "$item_uuid" ]]; then
      changes=$(echo "$changes" | jq --argjson entry "$(build_change "$item_name" "${spec:-}" "TO_RECENTLY" "$item_uuid")" '. + [$entry]')
      (( count++ )) || true
    else
      info "Warning: '${item_name}' not found on purchase list, skipping."
    fi
  done

  if (( count > 0 )); then
    local json_data
    json_data=$(jq -n --argjson changes "$changes" '{"changes": $changes, "sender": ""}')
    api_call PUT "${API_BASE}/v2/bringlists/${list_uuid}/items" \
      -H "Content-Type: application/json" \
      -d "$json_data" > /dev/null
  fi

  echo "Completed ${count} item(s)."
}

###############################################################################
# Setup credentials helper
###############################################################################
# Available themes: grocery, home, work, school, trip, party, baby, pet, christmas, easter
THEMES=(
  "grocery:ch.publisheria.bring.theme.grocery"
  "home:ch.publisheria.bring.theme.home"
  "work:ch.publisheria.bring.theme.work"
  "school:ch.publisheria.bring.theme.school"
  "trip:ch.publisheria.bring.theme.trip"
  "party:ch.publisheria.bring.theme.party"
  "baby:ch.publisheria.bring.theme.baby"
  "pet:ch.publisheria.bring.theme.pet"
  "christmas:ch.publisheria.bring.theme.christmas"
  "easter:ch.publisheria.bring.theme.easter"
)

resolve_theme() {
  local input="${1:-grocery}"
  input=$(echo "$input" | tr '[:upper:]' '[:lower:]')
  for entry in "${THEMES[@]}"; do
    local key="${entry%%:*}"
    local val="${entry#*:}"
    if [[ "$key" == "$input" ]]; then
      echo "$val"
      return 0
    fi
  done
  # Default to grocery if unknown
  echo "ch.publisheria.bring.theme.grocery"
}

do_create_list() {
  local name="$1"
  local theme_key="${2:-grocery}"
  [[ -n "$name" ]] || die "Usage: bring.sh create-list <name> [theme]"

  ensure_auth
  local uuid
  uuid="$(get_uuid)"
  local theme
  theme="$(resolve_theme "$theme_key")"

  local body
  body=$(api_call POST "${API_BASE}/bringusers/${uuid}/lists" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "name=$(urlencode "$name")&theme=${theme}")

  local new_uuid
  new_uuid=$(echo "$body" | jq -r '.bringListUUID // empty')
  echo "Created list '${name}' (theme: ${theme_key}, uuid: ${new_uuid})"
}

do_delete_list() {
  die "The Bring! API does not support deleting lists. Please delete lists in the Bring! app."
}

###############################################################################
do_setup() {
  echo "Bring! Credentials Setup"
  echo "========================"
  echo ""
  echo "Your credentials will be stored in: $CRED_FILE"
  echo ""
  read -rp "Bring! Email: " email
  read -rsp "Bring! Password: " password
  echo ""

  mkdir -p "$(dirname "$CRED_FILE")"
  cat > "$CRED_FILE" <<EOF
{
  "email": "${email}",
  "password": "${password}"
}
EOF
  chmod 600 "$CRED_FILE"
  echo "Credentials saved to $CRED_FILE"
  echo ""
  echo "Testing login..."
  BRING_EMAIL="$email" BRING_PASSWORD="$password" do_login

  # Show lists and ask for default
  echo ""
  echo "Your Bring! lists:"
  local uuid
  uuid="$(get_uuid)"
  local lists_json
  lists_json=$(api_call GET "${API_BASE}/bringusers/${uuid}/lists")
  local list_count
  list_count=$(echo "$lists_json" | jq '.lists | length')

  local i=1
  echo "$lists_json" | jq -r '.lists[] | .name' | while read -r name; do
    echo "  ${i}. ${name}"
    (( i++ )) || true
  done

  echo ""
  if (( list_count == 1 )); then
    local single_name
    single_name=$(echo "$lists_json" | jq -r '.lists[0].name')
    echo "Only one list found — setting '${single_name}' as default."
    jq --arg list "$single_name" '. + {default_list: $list}' "$CRED_FILE" > /tmp/bring_conf.json && mv /tmp/bring_conf.json "$CRED_FILE"
    chmod 600 "$CRED_FILE"
  elif (( list_count > 1 )); then
    read -rp "Which list should be the default? (name or number, Enter to skip): " choice
    if [[ -n "$choice" ]]; then
      local chosen_name
      if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= list_count )); then
        chosen_name=$(echo "$lists_json" | jq -r --argjson idx "$(( choice - 1 ))" '.lists[$idx].name')
      else
        chosen_name="$choice"
      fi
      jq --arg list "$chosen_name" '. + {default_list: $list}' "$CRED_FILE" > /tmp/bring_conf.json && mv /tmp/bring_conf.json "$CRED_FILE"
      chmod 600 "$CRED_FILE"
      echo "Default list set to '${chosen_name}'."
    fi
  fi

  echo ""
  echo "Setup complete! Try: bring.sh show"
}

###############################################################################
# Usage
###############################################################################
usage() {
  cat <<EOF
bring.sh — Bring! Shopping Lists CLI

USAGE:
  bring.sh <command> [arguments]

COMMANDS:
  setup                                Interactive credentials setup
  login                                Login and cache auth token
  lists [--json]                       List all shopping lists
  show [list] [--json]                 Show items on a list
  add [list] <item> [spec]             Add an item (with optional description)
  add-multi [list] <items...>          Add multiple items ("item" or "item|spec")
  remove [list] <item>                 Remove an item from a list
  remove-multi [list] <items...>       Remove multiple items at once
  complete [list] <item>               Check off an item (move to recently)
  complete-multi [list] <items...>     Check off multiple items at once
  uncomplete [list] <item>             Move item back to purchase list

LIST ARGUMENT:
  Can be a list UUID, a list name (partial match), or omitted if
  "default_list" is set in credentials.json.

DEFAULT LIST:
  Add "default_list" to ~/.config/bring/credentials.json to skip
  specifying the list name every time:
  {"email": "...", "password": "...", "default_list": "Einkaufsliste"}

AUTHENTICATION:
  Set BRING_EMAIL and BRING_PASSWORD env vars, or run 'bring.sh setup'
  to store credentials in ~/.config/bring/credentials.json

EXAMPLES:
  bring.sh setup
  bring.sh lists
  bring.sh show                        # uses default list
  bring.sh show "Einkaufsliste"
  bring.sh add "Milch" "fettarm, 1L"   # uses default list
  bring.sh add "Einkaufsliste" "Milch" "fettarm, 1L"
  bring.sh add-multi "Brot" "Käse|Gouda" "Butter|irische"
  bring.sh complete "Milch"
  bring.sh complete-multi "Milch" "Brot" "Käse"
  bring.sh remove-multi "Milch" "Brot"
EOF
}

###############################################################################
# Main
###############################################################################
main() {
  local cmd="${1:-help}"
  shift || true

  case "$cmd" in
    setup)
      do_setup
      ;;
    login)
      load_credentials
      do_login
      ;;
    lists)
      if [[ "${1:-}" == "--json" ]]; then
        do_lists_json
      else
        do_lists
      fi
      ;;
    create-list|delete-list)
      die "The Bring! API does not reliably support creating or deleting lists. Please manage lists in the Bring! app."
      ;;
    show)
      load_credentials
      local show_list
      if [[ "${1:-}" == "--json" ]]; then
        show_list="$(resolve_list_arg "")"
        do_show_json "$show_list"
      elif [[ "${2:-}" == "--json" ]]; then
        do_show_json "$1"
      else
        show_list="$(resolve_list_arg "${1:-}")"
        do_show "$show_list"
      fi
      ;;
    add)
      load_credentials
      [[ $# -ge 1 ]] || die "Usage: bring.sh add [list] <item> [specification]"
      local add_list add_item add_spec
      local _try_list=""
      if [[ $# -ge 2 ]]; then _try_list=$(resolve_list "$1" 2>/dev/null) || true; fi
      if [[ $# -ge 2 && -n "$_try_list" ]]; then
        # First arg is a valid list name
        add_list="$1"
        add_item="$2"
        add_spec="${3:-}"
      elif [[ $# -ge 2 ]] && [[ -n "${BRING_DEFAULT_LIST:-}" ]]; then
        # First arg is not a list — use default, treat args as item + spec
        add_list="$BRING_DEFAULT_LIST"
        add_item="$1"
        add_spec="${2:-}"
      elif [[ $# -eq 1 ]]; then
        add_list="$(resolve_list_arg "")"
        add_item="$1"
        add_spec=""
      else
        add_list="$(resolve_list_arg "$1")"
        add_item="$2"
        add_spec="${3:-}"
      fi
      do_add "$add_list" "$add_item" "$add_spec"
      ;;
    add-multi)
      load_credentials
      [[ $# -ge 1 ]] || die "Usage: bring.sh add-multi [list] <item1> [item2|spec] ..."
      local aml _try_aml=""
      _try_aml=$(resolve_list "$1" 2>/dev/null) || true
      if [[ -n "$_try_aml" ]]; then
        aml="$1"; shift
      else
        aml="$(resolve_list_arg "")"
      fi
      do_add_multi "$aml" "$@"
      ;;
    remove)
      load_credentials
      [[ $# -ge 1 ]] || die "Usage: bring.sh remove [list] <item>"
      local rm_list rm_item _try_rm=""
      if [[ $# -ge 2 ]]; then _try_rm=$(resolve_list "$1" 2>/dev/null) || true; fi
      if [[ $# -ge 2 && -n "$_try_rm" ]]; then
        rm_list="$1"; rm_item="$2"
      elif [[ -n "${BRING_DEFAULT_LIST:-}" ]]; then
        rm_list="$BRING_DEFAULT_LIST"; rm_item="$1"
      else
        rm_list="$(resolve_list_arg "$1")"; rm_item="$2"
      fi
      do_remove "$rm_list" "$rm_item"
      ;;
    remove-multi)
      load_credentials
      [[ $# -ge 1 ]] || die "Usage: bring.sh remove-multi [list] <item1> [item2] ..."
      local rml _try_rml=""
      _try_rml=$(resolve_list "$1" 2>/dev/null) || true
      if [[ -n "$_try_rml" ]]; then
        rml="$1"; shift
      else
        rml="$(resolve_list_arg "")"
      fi
      do_remove_multi "$rml" "$@"
      ;;
    complete)
      load_credentials
      [[ $# -ge 1 ]] || die "Usage: bring.sh complete [list] <item>"
      local comp_list comp_item _try_comp=""
      if [[ $# -ge 2 ]]; then _try_comp=$(resolve_list "$1" 2>/dev/null) || true; fi
      if [[ $# -ge 2 && -n "$_try_comp" ]]; then
        comp_list="$1"; comp_item="$2"
      elif [[ -n "${BRING_DEFAULT_LIST:-}" ]]; then
        comp_list="$BRING_DEFAULT_LIST"; comp_item="$1"
      else
        comp_list="$(resolve_list_arg "$1")"; comp_item="$2"
      fi
      do_complete "$comp_list" "$comp_item"
      ;;
    complete-multi)
      load_credentials
      [[ $# -ge 1 ]] || die "Usage: bring.sh complete-multi [list] <item1> [item2] ..."
      local cml _try_cml=""
      _try_cml=$(resolve_list "$1" 2>/dev/null) || true
      if [[ -n "$_try_cml" ]]; then
        cml="$1"; shift
      else
        cml="$(resolve_list_arg "")"
      fi
      do_complete_multi "$cml" "$@"
      ;;
    uncomplete)
      load_credentials
      [[ $# -ge 1 ]] || die "Usage: bring.sh uncomplete [list] <item>"
      local unc_list unc_item _try_unc=""
      if [[ $# -ge 2 ]]; then _try_unc=$(resolve_list "$1" 2>/dev/null) || true; fi
      if [[ $# -ge 2 && -n "$_try_unc" ]]; then
        unc_list="$1"; unc_item="$2"
      elif [[ -n "${BRING_DEFAULT_LIST:-}" ]]; then
        unc_list="$BRING_DEFAULT_LIST"; unc_item="$1"
      else
        unc_list="$(resolve_list_arg "$1")"; unc_item="$2"
      fi
      do_uncomplete "$unc_list" "$unc_item"
      ;;
    help|--help|-h)
      usage
      ;;
    *)
      die "Unknown command: $cmd. Run 'bring.sh help' for usage."
      ;;
  esac
}

main "$@"
