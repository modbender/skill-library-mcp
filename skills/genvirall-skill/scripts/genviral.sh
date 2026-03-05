#!/usr/bin/env bash
# ============================================================================
# genviral.sh - Complete Partner API automation (multi-platform)
# ============================================================================
#
# A comprehensive CLI wrapper for genviral's Partner API. Handles accounts,
# file uploads, slideshow generation, rendering, posting (video + slideshow),
# template/pack management, and the full content pipeline for TikTok, Instagram,
# and any supported platform.
#
# Requirements: bash 4+, curl, jq
# Auth: GENVIRAL_API_KEY environment variable (format: public_id.secret)
#
# Usage: genviral.sh <command> [options]
#
# Account & File Commands:
#   accounts                        List connected BYO and hosted accounts
#   upload                          Upload file to CDN (presigned URL flow)
#   list-files                      List uploaded files
#
# Post Commands:
#   create-post                     Create a post (video or slideshow, multi-account)
#   update-post                     Update an existing post
#   retry-posts                     Retry failed/partial posts
#   list-posts                      List posts
#   get-post                        Get post details
#   delete-posts | delete-post      Bulk delete posts
#
# Slideshow Commands:
#   generate | generate-slideshow   Generate slideshow
#   render | render-slideshow       Render slideshow
#   review | get-slideshow          Get slideshow details
#   update | update-slideshow       Update slideshow
#   regenerate-slide                Regenerate one slide
#   duplicate | duplicate-slideshow Duplicate slideshow
#   delete | delete-slideshow       Delete slideshow
#   list-slideshows                 List slideshows
#
# Pack Commands:
#   list-packs                      List image packs
#   get-pack                        Get a pack
#   create-pack                     Create a pack
#   update-pack                     Update pack
#   delete-pack                     Delete a pack
#   add-pack-image                  Add image to pack
#   delete-pack-image               Remove image from pack
#
# Template Commands:
#   list-templates                  List templates
#   get-template                    Get a template
#   create-template                 Create a template
#   update-template                 Update template
#   delete-template                 Delete template
#   create-template-from-slideshow  Convert slideshow to template
#
# Analytics Commands:
#   analytics-summary               Get analytics summary
#   get-analytics-summary           Alias for analytics-summary
#   analytics-posts                 List analytics posts
#   list-analytics-posts            Alias for analytics-posts
#   analytics-targets               List analytics targets
#   analytics-target-create         Create analytics target
#   analytics-target                Get analytics target
#   analytics-target-update         Update analytics target
#   analytics-target-delete         Delete analytics target
#   analytics-target-refresh        Refresh analytics target
#   analytics-refresh               Get analytics refresh status
#   get-analytics-refresh           Alias for analytics-refresh
#   analytics-workspace-suggestions List workspace suggestions
#   get-analytics-workspace-suggestions
#                                  Alias for analytics-workspace-suggestions
#
# Pipeline:
#   post-draft                      Post rendered slideshow as draft (legacy TikTok-focused)
#   full-pipeline                   End-to-end: generate -> render -> review -> post draft
#
# Other:
#   help                            Show this help message
#
# ============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Paths and Config
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_FILE="${GENVIRAL_CONFIG:-${SKILL_DIR}/defaults.yaml}"

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# Disable colors if NO_COLOR is set or stdout is not a terminal
if [[ -n "${NO_COLOR:-}" ]] || [[ ! -t 1 ]]; then
    RED='' GREEN='' YELLOW='' BLUE='' CYAN='' BOLD='' DIM='' NC=''
fi

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

error() { echo -e "${RED}Error:${NC} $*" >&2; }
warn()  { echo -e "${YELLOW}Warning:${NC} $*" >&2; }
info()  { echo -e "${BLUE}Info:${NC} $*" >&2; }
ok()    { echo -e "${GREEN}OK:${NC} $*" >&2; }
step()  { echo -e "${CYAN}$*${NC}" >&2; }

die() { error "$@"; exit 1; }

# ---------------------------------------------------------------------------
# Dependency Checks
# ---------------------------------------------------------------------------

check_deps() {
    local missing=()
    for cmd in curl jq; do
        command -v "$cmd" >/dev/null 2>&1 || missing+=("$cmd")
    done
    if [[ ${#missing[@]} -gt 0 ]]; then
        die "Missing required dependencies: ${missing[*]}. Install them and try again."
    fi
}

# ---------------------------------------------------------------------------
# Config Parsing (lightweight YAML, no external parser needed)
# ---------------------------------------------------------------------------

# Read a simple key from the flat YAML config.
# Handles: key: value, key: "value", key: 'value'
config_get() {
    local key="$1"
    local default="${2:-}"

    if [[ ! -f "$CONFIG_FILE" ]]; then
        printf '%s' "$default"
        return
    fi

    local value=""
    value="$(grep -E "^[[:space:]]*${key}:" "$CONFIG_FILE" 2>/dev/null \
        | head -n1 \
        | sed -E 's/^[[:space:]]*[^:]+:[[:space:]]*//' \
        | sed -E 's/[[:space:]]*#.*$//' \
        | sed -E 's/^["'"'"'](.*)["'"'"']$/\1/' \
        || true)"

    # Resolve env var references like ${VAR_NAME}
    if [[ "$value" =~ ^\$\{([A-Za-z_][A-Za-z0-9_]*)\}$ ]]; then
        local var_name="${BASH_REMATCH[1]}"
        value="${!var_name:-}"
    fi

    if [[ -z "$value" || "$value" == "null" ]]; then
        printf '%s' "$default"
    else
        printf '%s' "$value"
    fi
}

# ---------------------------------------------------------------------------
# Load Defaults from Config
# ---------------------------------------------------------------------------

load_defaults() {
    # Load env file if available
    [[ -f "${HOME}/.config/env/global.env" ]] && source "${HOME}/.config/env/global.env" 2>/dev/null || true

    API_KEY="${GENVIRAL_API_KEY:-}"
    BASE_URL="$(config_get base_url "https://www.genviral.io/api/partner/v1")"

    DEFAULT_PACK_ID="$(config_get default_pack_id "")"
    DEFAULT_SLIDE_COUNT="$(config_get default_slide_count "5")"
    DEFAULT_ASPECT_RATIO="$(config_get default_aspect_ratio "4:5")"
    DEFAULT_TYPE="$(config_get default_type "educational")"
    DEFAULT_STYLE="$(config_get default_style_preset "tiktok")"
    DEFAULT_LANGUAGE="$(config_get language "en")"
    DEFAULT_ACCOUNT_IDS="$(config_get default_account_ids "")"
    DEFAULT_PRIVACY="$(config_get privacy_level "PUBLIC_TO_EVERYONE")"
    DEFAULT_POST_MODE="$(config_get post_mode "DIRECT_POST")"

    HTTP_CONNECT_TIMEOUT="$(config_get connect_timeout "10")"
    HTTP_MAX_TIME="$(config_get max_time "120")"
    HTTP_RETRIES="$(config_get retries "2")"
    HTTP_RETRY_DELAY="$(config_get retry_delay "2")"
}

# ---------------------------------------------------------------------------
# Auth Check
# ---------------------------------------------------------------------------

check_auth() {
    if [[ -z "$API_KEY" ]]; then
        die "GENVIRAL_API_KEY is not set.\n  Set it via: export GENVIRAL_API_KEY=\"your_public_id.your_secret\"\n  Or add to ~/.config/env/global.env"
    fi
}

# ---------------------------------------------------------------------------
# API Request Helper
# ---------------------------------------------------------------------------

# Makes an authenticated API request. Returns JSON body on stdout.
# Exits with error on HTTP errors or API errors.
#
# Usage: api_call METHOD /endpoint [JSON_BODY]
api_call() {
    local method="$1"
    local endpoint="$2"
    local body="${3:-}"

    local url="${BASE_URL%/}${endpoint}"

    local curl_args=(
        -sS
        --connect-timeout "$HTTP_CONNECT_TIMEOUT"
        --max-time "$HTTP_MAX_TIME"
        --retry "$HTTP_RETRIES"
        --retry-delay "$HTTP_RETRY_DELAY"
        -X "$method"
        -H "Authorization: Bearer ${API_KEY}"
        -H "Content-Type: application/json"
        -w '\n%{http_code}'
    )

    [[ -n "$body" ]] && curl_args+=(-d "$body")

    local response
    response="$(curl "${curl_args[@]}" "$url" 2>&1)" || {
        die "Request failed: curl error for $method $endpoint"
    }

    local http_code
    http_code="$(printf '%s' "$response" | tail -n1)"
    local response_body
    response_body="$(printf '%s' "$response" | sed '$d')"

    # Check for empty response
    if [[ -z "$response_body" ]]; then
        die "Empty response from API: $method $endpoint (HTTP $http_code)"
    fi

    # Check for valid JSON
    if ! printf '%s' "$response_body" | jq empty >/dev/null 2>&1; then
        die "API returned non-JSON response (HTTP $http_code): ${response_body:0:200}"
    fi

    # Check HTTP status
    if [[ "$http_code" -ge 400 ]]; then
        local msg
        msg="$(printf '%s' "$response_body" | jq -r '.message // .error // .data.message // "Unknown API error"')"
        die "HTTP $http_code: $msg"
    fi

    # Check API-level error
    if printf '%s' "$response_body" | jq -e 'has("ok") and (.ok == false)' >/dev/null 2>&1; then
        local code msg
        code="$(printf '%s' "$response_body" | jq -r '.code // "unknown"')"
        msg="$(printf '%s' "$response_body" | jq -r '.message // "Request failed"')"
        die "API error $code: $msg"
    fi

    printf '%s' "$response_body"
}

# Upload helper for presigned URL flow (raw PUT, no auth header)
upload_to_presigned_url() {
    local presigned_url="$1"
    local file_path="$2"
    local content_type="$3"

    local curl_args=(
        -sS
        --connect-timeout "$HTTP_CONNECT_TIMEOUT"
        --max-time "$HTTP_MAX_TIME"
        --retry "$HTTP_RETRIES"
        --retry-delay "$HTTP_RETRY_DELAY"
        -X PUT
        -H "Content-Type: ${content_type}"
        --data-binary "@${file_path}"
        -w '\n%{http_code}'
    )

    local response
    response="$(curl "${curl_args[@]}" "$presigned_url" 2>&1)" || {
        die "Upload failed: curl error uploading to presigned URL"
    }

    local http_code
    http_code="$(printf '%s' "$response" | tail -n1)"

    if [[ "$http_code" -ge 400 ]]; then
        die "Upload to CDN failed with HTTP $http_code"
    fi
}

# ---------------------------------------------------------------------------
# Validation Helpers
# ---------------------------------------------------------------------------

validate_slide_count() {
    local n="$1"
    [[ "$n" =~ ^[0-9]+$ ]] || die "slide count must be an integer, got: $n"
    (( n >= 1 && n <= 10 )) || die "slide count must be between 1 and 10, got: $n"
}

validate_aspect_ratio() {
    case "$1" in
        9:16|4:5|1:1) ;;
        *) die "aspect ratio must be one of: 9:16, 4:5, 1:1. Got: $1" ;;
    esac
}

validate_type() {
    case "$1" in
        educational|personal) ;;
        *) die "type must be 'educational' or 'personal'. Got: $1" ;;
    esac
}

validate_style() {
    [[ -n "$1" ]] || die "style must be a non-empty string"
}

validate_font_size_setting() {
    case "$1" in
        default|small) ;;
        *) die "font-size must be one of: default, small. Got: $1" ;;
    esac
}

validate_text_width_setting() {
    case "$1" in
        default|narrow) ;;
        *) die "text-width must be one of: default, narrow. Got: $1" ;;
    esac
}

validate_boolean() {
    local option_name="$1"
    local value="$2"
    case "$value" in
        true|false) ;;
        *) die "--${option_name} must be true or false. Got: $value" ;;
    esac
}

validate_positive_int() {
    local option_name="$1"
    local value="$2"

    [[ "$value" =~ ^[0-9]+$ ]] || die "--${option_name} must be a positive integer. Got: $value"
    (( value > 0 )) || die "--${option_name} must be greater than 0. Got: $value"
}

validate_nonnegative_int() {
    local option_name="$1"
    local value="$2"

    [[ "$value" =~ ^[0-9]+$ ]] || die "--${option_name} must be a non-negative integer. Got: $value"
}

validate_max_int() {
    local option_name="$1"
    local value="$2"
    local max="$3"

    (( value <= max )) || die "--${option_name} must be <= ${max}. Got: $value"
}

validate_iso_date_ymd() {
    local option_name="$1"
    local value="$2"

    [[ "$value" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || die "--${option_name} must be YYYY-MM-DD. Got: $value"

    local normalized
    normalized="$(date -u -d "$value" '+%Y-%m-%d' 2>/dev/null || true)"
    [[ "$normalized" == "$value" ]] || die "--${option_name} must be a valid calendar date (YYYY-MM-DD). Got: $value"
}

validate_iso_datetime_offset() {
    local option_name="$1"
    local value="$2"

    [[ "$value" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]{1,9})?(Z|[+-][0-9]{2}:[0-9]{2})$ ]] \
        || die "--${option_name} must be ISO 8601 with timezone offset (e.g., 2026-02-14T19:47:00Z). Got: $value"

    date -u -d "$value" '+%Y-%m-%dT%H:%M:%S%:z' >/dev/null 2>&1 \
        || die "--${option_name} must be a valid ISO 8601 datetime. Got: $value"
}

validate_tiktok_music_url() {
    local option_name="$1"
    local value="$2"

    [[ "$value" =~ ^https?:// ]] || die "--${option_name} must be a valid URL. Got: $value"
    [[ "${value,,}" == *"tiktok.com"* ]] || die "--${option_name} must point to tiktok.com. Got: $value"
}

validate_uuid() {
    local option_name="$1"
    local value="$2"

    [[ "$value" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]] || die "--${option_name} must be a UUID. Got: $value"
}

split_csv_to_json_array() {
    local csv="$1"
    printf '%s' "$csv" | tr ',' '\n' | sed '/^[[:space:]]*$/d' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | jq -R . | jq -sc .
}

validate_uuid_csv() {
    local option_name="$1"
    local csv="$2"
    local max_count="$3"

    local -a ids=()
    local -a raw=()
    IFS=',' read -r -a raw <<< "$csv"

    for id in "${raw[@]}"; do
        id="$(printf '%s' "$id" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
        [[ -z "$id" ]] && continue
        validate_uuid "$option_name" "$id"
        ids+=("$id")
    done

    (( ${#ids[@]} > 0 )) || die "--${option_name} requires at least one ID"
    (( ${#ids[@]} <= max_count )) || die "--${option_name} supports at most ${max_count} IDs (got ${#ids[@]})"
}

require_arg() {
    local name="$1"
    local value="$2"
    [[ -n "$value" ]] || die "--$name is required"
}

parse_boolean_flag_or_value() {
    # Supports both:
    #   --flag            => true
    #   --flag true|false => explicit
    local option_name="$1"

    if [[ $# -ge 2 && -n "${2:-}" && "$2" != --* ]]; then
        validate_boolean "$option_name" "$2"
        printf '%s' "$2"
    else
        printf 'true'
    fi
}

validate_json_string() {
    local label="$1"
    local json="$2"
    if ! printf '%s' "$json" | jq empty >/dev/null 2>&1; then
        die "$label is not valid JSON"
    fi
}

read_json_file() {
    local file_path="$1"
    [[ -f "$file_path" ]] || die "File not found: $file_path"

    local content
    content="$(cat "$file_path")"
    validate_json_string "$file_path" "$content"
    printf '%s' "$content"
}

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------

usage() {
    cat <<EOF
${BOLD}genviral.sh${NC} - Complete Partner API automation (multi-platform)

${BOLD}Usage:${NC}
  genviral.sh <command> [options]

${BOLD}Account & File Commands:${NC}
  accounts                        List connected BYO and hosted accounts
  upload                          Upload file to CDN (presigned URL flow)
  list-files                      List uploaded files

${BOLD}Post Commands:${NC}
  create-post                     Create a post (video or slideshow, multi-account)
  update-post                     Update an existing post
  retry-posts                     Retry failed/partial posts
  list-posts                      List posts (optionally filter by status)
  get-post                        Get details for a specific post
  delete-posts | delete-post      Bulk delete posts by IDs

${BOLD}Slideshow Commands:${NC}
  generate | generate-slideshow   Generate slideshow (AI/manual/mixed)
  render | render-slideshow       Render a slideshow
  review | get-slideshow          Get slideshow details
  update | update-slideshow       Update slideshow fields/settings/slides
  regenerate-slide                Regenerate text for one slide
  duplicate | duplicate-slideshow Duplicate slideshow
  delete | delete-slideshow       Delete slideshow
  list-slideshows                 List slideshows

${BOLD}Pack Commands:${NC}
  list-packs                      List image packs
  get-pack                        Get a pack
  create-pack                     Create a pack
  update-pack                     Update pack fields
  delete-pack                     Delete a pack
  add-pack-image                  Add image URL to a pack
  delete-pack-image               Delete image from a pack

${BOLD}Template Commands:${NC}
  list-templates                  List templates
  get-template                    Get template details
  create-template                 Create a template
  update-template                 Update template
  delete-template                 Delete template
  create-template-from-slideshow  Convert slideshow to template

${BOLD}Analytics Commands:${NC}
  analytics-summary | get-analytics-summary
                                  GET /analytics/summary
  analytics-posts | list-analytics-posts
                                  GET /analytics/summary/posts
  analytics-targets               GET /analytics/targets
  analytics-target-create         POST /analytics/targets
  analytics-target                GET /analytics/targets/{id}
  analytics-target-update         PATCH /analytics/targets/{id}
  analytics-target-delete         DELETE /analytics/targets/{id}
  analytics-target-refresh        POST /analytics/targets/{id}/refresh
  analytics-refresh | get-analytics-refresh
                                  GET /analytics/refreshes/{id}
  analytics-workspace-suggestions | get-analytics-workspace-suggestions
                                  GET /analytics/workspace-suggestions

${BOLD}Pipeline (Legacy):${NC}
  post-draft                      Post rendered slideshow as TikTok draft
  full-pipeline                   generate -> render -> review -> post draft

${BOLD}Other:${NC}
  help                            Show this help message

${BOLD}Environment:${NC}
  GENVIRAL_API_KEY                Partner API key (required, format: public_id.secret)
  GENVIRAL_CONFIG                 Optional defaults.yaml path
  NO_COLOR                        Disable colored output

${BOLD}Examples:${NC}
  genviral.sh accounts
  genviral.sh create-post --caption "Text" --media-type video --media-url "https://..." --accounts "id1,id2"
  genviral.sh generate --prompt "5 discipline quotes" --pack-id PACK_ID --slides 5
  genviral.sh update-slideshow --id SLIDESHOW_ID --status draft --settings-json '{"aspect_ratio":"9:16"}'
  genviral.sh analytics-summary --range 30d --platforms tiktok,instagram
  genviral.sh analytics-target-create --platform tiktok --identifier @brand --alias "Brand HQ"
EOF
}

# ===========================================================================
# Commands
# ===========================================================================

# ---------------------------------------------------------------------------
# accounts
# ---------------------------------------------------------------------------
cmd_accounts() {
    local json_output=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --json) json_output=true; shift ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    info "Fetching connected accounts..."

    local response
    response="$(api_call GET /accounts)"

    if [[ "$json_output" == true ]]; then
        printf '%s' "$response" | jq '.data // {}'
        return
    fi

    local count
    count="$(printf '%s' "$response" | jq '.data.accounts | length // 0')"
    ok "Found $count accounts"
    echo ""

    printf '%s' "$response" | jq -r '
        .data.accounts // [] | .[] |
        "  \(.id)\n    Platform: \(.platform)\n    Type: \(.type)\n    Username: @\(.username)\n    Display: \(.display_name)\n    Status: \(.status)\n"
    '
}

# ---------------------------------------------------------------------------
# upload
# ---------------------------------------------------------------------------
cmd_upload() {
    local file_path=""
    local content_type=""
    local filename=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --file)         file_path="$2"; shift 2 ;;
            --content-type) content_type="$2"; shift 2 ;;
            --filename)     filename="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "file" "$file_path"
    require_arg "content-type" "$content_type"

    [[ -f "$file_path" ]] || die "File not found: $file_path"

    [[ -z "$filename" ]] && filename="$(basename "$file_path")"

    info "Requesting upload URL..."

    local payload
    payload="$(jq -n \
        --arg content_type "$content_type" \
        --arg filename "$filename" \
        '{contentType: $content_type, filename: $filename}'
    )"

    local response
    response="$(api_call POST /files "$payload")"

    local upload_url cdn_url
    upload_url="$(printf '%s' "$response" | jq -r '.data.uploadUrl // empty')"
    cdn_url="$(printf '%s' "$response" | jq -r '.data.url // empty')"

    if [[ -z "$upload_url" || -z "$cdn_url" ]]; then
        die "API did not return uploadUrl or url"
    fi

    step "  Upload URL: ${upload_url:0:60}..."
    step "  CDN URL: $cdn_url"

    info "Uploading file to CDN..."

    upload_to_presigned_url "$upload_url" "$file_path" "$content_type"

    ok "Upload complete!"
    echo ""
    echo "  CDN URL: $cdn_url"
    echo ""

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# list-files
# ---------------------------------------------------------------------------
cmd_list_files() {
    local limit=50
    local offset=0
    local type=""
    local context=""
    local json_output=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --limit)   limit="$2"; shift 2 ;;
            --offset)  offset="$2"; shift 2 ;;
            --type)    type="$2"; shift 2 ;;
            --context) context="$2"; shift 2 ;;
            --json)    json_output=true; shift ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    validate_positive_int "limit" "$limit"
    validate_max_int "limit" "$limit" 100
    validate_nonnegative_int "offset" "$offset"

    if [[ -n "$type" ]]; then
        case "$type" in
            image|video) ;;
            *) die "--type must be one of: image, video. Got: $type" ;;
        esac
    fi

    local endpoint="/files?limit=${limit}&offset=${offset}"
    [[ -n "$type" ]] && endpoint="${endpoint}&type=${type}"
    [[ -n "$context" ]] && endpoint="${endpoint}&context=${context}"

    info "Fetching files..."

    local response
    response="$(api_call GET "$endpoint")"

    if [[ "$json_output" == true ]]; then
        printf '%s' "$response" | jq '.data // {}'
        return
    fi

    local total
    total="$(printf '%s' "$response" | jq '.data.total // 0')"
    ok "Found $total files (showing ${limit} from offset ${offset})"
    echo ""

    printf '%s' "$response" | jq -r '
        .data.files // [] | .[] |
        "  \(.filename // "unnamed")\n    URL: \(.url)\n    Type: \(.contentType)\n    Size: \(.size) bytes\n    Created: \(.createdAt)\n"
    '
}

# ---------------------------------------------------------------------------
# create-post
# ---------------------------------------------------------------------------
cmd_create_post() {
    local caption=""
    local media_type=""
    local media_url=""
    local media_urls=""
    local music_url=""
    local accounts=""
    local scheduled_at=""
    local external_id=""
    local tiktok_title=""
    local tiktok_description=""
    local tiktok_post_mode=""
    local tiktok_privacy=""
    local tiktok_disable_comment=""
    local tiktok_disable_duet=""
    local tiktok_disable_stitch=""
    local tiktok_auto_add_music=""
    local tiktok_is_commercial=""
    local tiktok_is_branded_content=""
    local tiktok_user_consent=""
    local tiktok_is_your_brand=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --caption)                caption="$2"; shift 2 ;;
            --media-type)             media_type="$2"; shift 2 ;;
            --media-url)              media_url="$2"; shift 2 ;;
            --media-urls)             media_urls="$2"; shift 2 ;;
            --music-url)              music_url="$2"; shift 2 ;;
            --accounts)               accounts="$2"; shift 2 ;;
            --scheduled-at)           scheduled_at="$2"; shift 2 ;;
            --external-id)            external_id="$2"; shift 2 ;;
            --tiktok-title)           tiktok_title="$2"; shift 2 ;;
            --tiktok-description)     tiktok_description="$2"; shift 2 ;;
            --tiktok-post-mode)       tiktok_post_mode="$2"; shift 2 ;;
            --tiktok-privacy)         tiktok_privacy="$2"; shift 2 ;;
            --tiktok-disable-comment)
                tiktok_disable_comment="$(parse_boolean_flag_or_value "tiktok-disable-comment" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            --tiktok-disable-duet)
                tiktok_disable_duet="$(parse_boolean_flag_or_value "tiktok-disable-duet" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            --tiktok-disable-stitch)
                tiktok_disable_stitch="$(parse_boolean_flag_or_value "tiktok-disable-stitch" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            --auto-add-music)
                tiktok_auto_add_music="$(parse_boolean_flag_or_value "auto-add-music" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            --is-commercial)
                tiktok_is_commercial="$(parse_boolean_flag_or_value "is-commercial" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            --is-branded-content)
                tiktok_is_branded_content="$(parse_boolean_flag_or_value "is-branded-content" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            --user-consent)
                tiktok_user_consent="$(parse_boolean_flag_or_value "user-consent" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            --is-your-brand)
                tiktok_is_your_brand="$(parse_boolean_flag_or_value "is-your-brand" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "caption" "$caption"
    require_arg "media-type" "$media_type"
    require_arg "accounts" "$accounts"

    ((${#caption} <= 500)) || die "--caption max length is 500 characters"
    [[ -n "$external_id" && ${#external_id} -gt 128 ]] && die "--external-id max length is 128 characters"
    [[ -n "$tiktok_title" && ${#tiktok_title} -gt 150 ]] && die "--tiktok-title max length is 150 characters"
    [[ -n "$tiktok_description" && ${#tiktok_description} -gt 2200 ]] && die "--tiktok-description max length is 2200 characters"

    validate_uuid_csv "accounts" "$accounts" 10
    [[ -n "$scheduled_at" ]] && validate_iso_datetime_offset "scheduled-at" "$scheduled_at"
    [[ -n "$music_url" ]] && validate_tiktok_music_url "music-url" "$music_url"

    [[ -n "$tiktok_disable_comment" ]] && validate_boolean "tiktok-disable-comment" "$tiktok_disable_comment"
    [[ -n "$tiktok_disable_duet" ]] && validate_boolean "tiktok-disable-duet" "$tiktok_disable_duet"
    [[ -n "$tiktok_disable_stitch" ]] && validate_boolean "tiktok-disable-stitch" "$tiktok_disable_stitch"
    [[ -n "$tiktok_auto_add_music" ]] && validate_boolean "auto-add-music" "$tiktok_auto_add_music"
    [[ -n "$tiktok_is_commercial" ]] && validate_boolean "is-commercial" "$tiktok_is_commercial"
    [[ -n "$tiktok_is_branded_content" ]] && validate_boolean "is-branded-content" "$tiktok_is_branded_content"
    [[ -n "$tiktok_user_consent" ]] && validate_boolean "user-consent" "$tiktok_user_consent"
    [[ -n "$tiktok_is_your_brand" ]] && validate_boolean "is-your-brand" "$tiktok_is_your_brand"

    # Validate media type
    case "$media_type" in
        video|slideshow) ;;
        *) die "media-type must be 'video' or 'slideshow', got: $media_type" ;;
    esac

    if [[ -n "$tiktok_post_mode" ]]; then
        case "$tiktok_post_mode" in
            DIRECT_POST|MEDIA_UPLOAD) ;;
            *) die "--tiktok-post-mode must be DIRECT_POST or MEDIA_UPLOAD. Got: $tiktok_post_mode" ;;
        esac
    fi

    if [[ -n "$tiktok_privacy" ]]; then
        case "$tiktok_privacy" in
            PUBLIC_TO_EVERYONE|MUTUAL_FOLLOW_FRIENDS|FOLLOWER_OF_CREATOR|SELF_ONLY) ;;
            *) die "--tiktok-privacy must be one of: PUBLIC_TO_EVERYONE, MUTUAL_FOLLOW_FRIENDS, FOLLOWER_OF_CREATOR, SELF_ONLY. Got: $tiktok_privacy" ;;
        esac
    fi

    if [[ "$tiktok_post_mode" == "MEDIA_UPLOAD" && "$media_type" != "slideshow" ]]; then
        die "TikTok MEDIA_UPLOAD is only supported when media-type is slideshow."
    fi

    # Build media object
    local media_obj=""
    if [[ "$media_type" == "video" ]]; then
        require_arg "media-url" "$media_url"
        media_obj="$(jq -n --arg type "$media_type" --arg url "$media_url" '{type: $type, url: $url}')"
    else
        require_arg "media-urls" "$media_urls"
        local urls_array
        urls_array="$(split_csv_to_json_array "$media_urls")"
        local url_count
        url_count="$(printf '%s' "$urls_array" | jq 'length')"
        (( url_count >= 1 && url_count <= 35 )) || die "--media-urls must contain between 1 and 35 URLs (got $url_count)"
        media_obj="$(jq -n --arg type "$media_type" --argjson urls "$urls_array" '{type: $type, urls: $urls}')"
    fi

    # Build accounts array
    local account_ids_array
    account_ids_array="$(split_csv_to_json_array "$accounts")"
    local accounts_array
    accounts_array="$(printf '%s' "$account_ids_array" | jq 'map({id: .})')"

    # Build payload
    local payload
    payload="$(jq -n \
        --arg caption "$caption" \
        --argjson media "$media_obj" \
        --argjson accounts "$accounts_array" \
        '{caption: $caption, media: $media, accounts: $accounts}'
    )"

    # Add optional fields
    [[ -n "$music_url" ]] && payload="$(printf '%s' "$payload" | jq --arg url "$music_url" '. + {music_url: $url}')"
    [[ -n "$scheduled_at" ]] && payload="$(printf '%s' "$payload" | jq --arg ts "$scheduled_at" '. + {scheduled_at: $ts}')"
    [[ -n "$external_id" ]] && payload="$(printf '%s' "$payload" | jq --arg id "$external_id" '. + {external_id: $id}')"

    # Build TikTok settings if any provided
    if [[ -n "$tiktok_title" || -n "$tiktok_description" || -n "$tiktok_post_mode" || -n "$tiktok_privacy" || -n "$tiktok_disable_comment" || -n "$tiktok_disable_duet" || -n "$tiktok_disable_stitch" || -n "$tiktok_auto_add_music" || -n "$tiktok_is_commercial" || -n "$tiktok_is_branded_content" || -n "$tiktok_user_consent" || -n "$tiktok_is_your_brand" ]]; then
        local tiktok_obj='{}'
        [[ -n "$tiktok_title" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --arg t "$tiktok_title" '. + {title: $t}')"
        [[ -n "$tiktok_description" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --arg d "$tiktok_description" '. + {description: $d}')"
        [[ -n "$tiktok_post_mode" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --arg m "$tiktok_post_mode" '. + {post_mode: $m}')"
        [[ -n "$tiktok_privacy" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --arg p "$tiktok_privacy" '. + {privacy_level: $p}')"
        [[ -n "$tiktok_disable_comment" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --argjson v "$tiktok_disable_comment" '. + {disable_comment: $v}')"
        [[ -n "$tiktok_disable_duet" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --argjson v "$tiktok_disable_duet" '. + {disable_duet: $v}')"
        [[ -n "$tiktok_disable_stitch" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --argjson v "$tiktok_disable_stitch" '. + {disable_stitch: $v}')"
        [[ -n "$tiktok_auto_add_music" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --argjson v "$tiktok_auto_add_music" '. + {auto_add_music: $v}')"
        [[ -n "$tiktok_is_commercial" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --argjson v "$tiktok_is_commercial" '. + {is_commercial: $v}')"
        [[ -n "$tiktok_is_branded_content" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --argjson v "$tiktok_is_branded_content" '. + {is_branded_content: $v}')"
        [[ -n "$tiktok_user_consent" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --argjson v "$tiktok_user_consent" '. + {user_consent: $v}')"
        [[ -n "$tiktok_is_your_brand" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --argjson v "$tiktok_is_your_brand" '. + {is_your_brand: $v}')"
        payload="$(printf '%s' "$payload" | jq --argjson tt "$tiktok_obj" '. + {tiktok: $tt}')"
    fi

    info "Creating post..."
    step "  Caption: ${caption:0:80}$([ ${#caption} -gt 80 ] && echo '...')"
    step "  Media: $media_type"
    step "  Accounts: $accounts"

    local response
    response="$(api_call POST /posts "$payload")"

    local post_id status
    post_id="$(printf '%s' "$response" | jq -r '.data.id // empty')"
    status="$(printf '%s' "$response" | jq -r '.data.status // empty')"

    if [[ -n "$post_id" ]]; then
        ok "Post created: $post_id (status: $status)"
    fi

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# update-post
# ---------------------------------------------------------------------------
cmd_update_post() {
    local post_id=""
    local caption=""
    local media_type=""
    local media_url=""
    local media_urls=""
    local music_url=""
    local accounts=""
    local scheduled_at=""
    local external_id=""
    local clear_scheduled_at=false
    local clear_tiktok=false
    local tiktok_title=""
    local tiktok_description=""
    local tiktok_post_mode=""
    local tiktok_privacy=""
    local tiktok_disable_comment=""
    local tiktok_disable_duet=""
    local tiktok_disable_stitch=""
    local tiktok_auto_add_music=""
    local tiktok_is_commercial=""
    local tiktok_is_branded_content=""
    local tiktok_user_consent=""
    local tiktok_is_your_brand=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id)                   post_id="$2"; shift 2 ;;
            --caption)              caption="$2"; shift 2 ;;
            --media-type)           media_type="$2"; shift 2 ;;
            --media-url)            media_url="$2"; shift 2 ;;
            --media-urls)           media_urls="$2"; shift 2 ;;
            --music-url)            music_url="$2"; shift 2 ;;
            --accounts)             accounts="$2"; shift 2 ;;
            --scheduled-at)         scheduled_at="$2"; shift 2 ;;
            --external-id)          external_id="$2"; shift 2 ;;
            --clear-scheduled-at)   clear_scheduled_at=true; shift ;;
            --clear-tiktok)         clear_tiktok=true; shift ;;
            --tiktok-title)         tiktok_title="$2"; shift 2 ;;
            --tiktok-description)   tiktok_description="$2"; shift 2 ;;
            --tiktok-post-mode)     tiktok_post_mode="$2"; shift 2 ;;
            --tiktok-privacy)       tiktok_privacy="$2"; shift 2 ;;
            --tiktok-disable-comment)
                tiktok_disable_comment="$(parse_boolean_flag_or_value "tiktok-disable-comment" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            --tiktok-disable-duet)
                tiktok_disable_duet="$(parse_boolean_flag_or_value "tiktok-disable-duet" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            --tiktok-disable-stitch)
                tiktok_disable_stitch="$(parse_boolean_flag_or_value "tiktok-disable-stitch" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            --auto-add-music)
                tiktok_auto_add_music="$(parse_boolean_flag_or_value "auto-add-music" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            --is-commercial)
                tiktok_is_commercial="$(parse_boolean_flag_or_value "is-commercial" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            --is-branded-content)
                tiktok_is_branded_content="$(parse_boolean_flag_or_value "is-branded-content" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            --user-consent)
                tiktok_user_consent="$(parse_boolean_flag_or_value "user-consent" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            --is-your-brand)
                tiktok_is_your_brand="$(parse_boolean_flag_or_value "is-your-brand" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$post_id"

    [[ -n "$caption" && ${#caption} -gt 500 ]] && die "--caption max length is 500 characters"
    [[ -n "$external_id" && ${#external_id} -gt 128 ]] && die "--external-id max length is 128 characters"
    [[ -n "$tiktok_title" && ${#tiktok_title} -gt 150 ]] && die "--tiktok-title max length is 150 characters"
    [[ -n "$tiktok_description" && ${#tiktok_description} -gt 2200 ]] && die "--tiktok-description max length is 2200 characters"
    [[ -n "$scheduled_at" ]] && validate_iso_datetime_offset "scheduled-at" "$scheduled_at"
    [[ -n "$music_url" && "$music_url" != "null" ]] && validate_tiktok_music_url "music-url" "$music_url"

    [[ -n "$tiktok_disable_comment" ]] && validate_boolean "tiktok-disable-comment" "$tiktok_disable_comment"
    [[ -n "$tiktok_disable_duet" ]] && validate_boolean "tiktok-disable-duet" "$tiktok_disable_duet"
    [[ -n "$tiktok_disable_stitch" ]] && validate_boolean "tiktok-disable-stitch" "$tiktok_disable_stitch"
    [[ -n "$tiktok_auto_add_music" ]] && validate_boolean "auto-add-music" "$tiktok_auto_add_music"
    [[ -n "$tiktok_is_commercial" ]] && validate_boolean "is-commercial" "$tiktok_is_commercial"
    [[ -n "$tiktok_is_branded_content" ]] && validate_boolean "is-branded-content" "$tiktok_is_branded_content"
    [[ -n "$tiktok_user_consent" ]] && validate_boolean "user-consent" "$tiktok_user_consent"
    [[ -n "$tiktok_is_your_brand" ]] && validate_boolean "is-your-brand" "$tiktok_is_your_brand"

    if [[ "$clear_scheduled_at" == true && -n "$scheduled_at" ]]; then
        die "Use either --scheduled-at or --clear-scheduled-at, not both."
    fi

    if [[ "$clear_tiktok" == true && ( -n "$tiktok_title" || -n "$tiktok_description" || -n "$tiktok_post_mode" || -n "$tiktok_privacy" || -n "$tiktok_disable_comment" || -n "$tiktok_disable_duet" || -n "$tiktok_disable_stitch" || -n "$tiktok_auto_add_music" || -n "$tiktok_is_commercial" || -n "$tiktok_is_branded_content" || -n "$tiktok_user_consent" || -n "$tiktok_is_your_brand" ) ]]; then
        die "Use either TikTok update options or --clear-tiktok, not both."
    fi

    if [[ -n "$tiktok_post_mode" ]]; then
        case "$tiktok_post_mode" in
            DIRECT_POST|MEDIA_UPLOAD) ;;
            *) die "--tiktok-post-mode must be DIRECT_POST or MEDIA_UPLOAD. Got: $tiktok_post_mode" ;;
        esac
    fi

    if [[ -n "$tiktok_privacy" ]]; then
        case "$tiktok_privacy" in
            PUBLIC_TO_EVERYONE|MUTUAL_FOLLOW_FRIENDS|FOLLOWER_OF_CREATOR|SELF_ONLY) ;;
            *) die "--tiktok-privacy must be one of: PUBLIC_TO_EVERYONE, MUTUAL_FOLLOW_FRIENDS, FOLLOWER_OF_CREATOR, SELF_ONLY. Got: $tiktok_privacy" ;;
        esac
    fi

    if [[ -n "$media_type" ]]; then
        case "$media_type" in
            video|slideshow) ;;
            *) die "--media-type must be 'video' or 'slideshow'. Got: $media_type" ;;
        esac
    fi

    if [[ "$tiktok_post_mode" == "MEDIA_UPLOAD" && -n "$media_type" && "$media_type" != "slideshow" ]]; then
        die "TikTok MEDIA_UPLOAD is only supported when media-type is slideshow."
    fi

    local payload='{}'

    [[ -n "$caption" ]] && payload="$(printf '%s' "$payload" | jq --arg c "$caption" '. + {caption: $c}')"
    [[ -n "$external_id" ]] && payload="$(printf '%s' "$payload" | jq --arg id "$external_id" '. + {external_id: $id}')"

    if [[ "$clear_scheduled_at" == true ]]; then
        payload="$(printf '%s' "$payload" | jq '. + {scheduled_at: null}')"
    elif [[ -n "$scheduled_at" ]]; then
        payload="$(printf '%s' "$payload" | jq --arg ts "$scheduled_at" '. + {scheduled_at: $ts}')"
    fi

    # Music URL (null to clear)
    if [[ "$music_url" == "null" ]]; then
        payload="$(printf '%s' "$payload" | jq '. + {music_url: null}')"
    elif [[ -n "$music_url" ]]; then
        payload="$(printf '%s' "$payload" | jq --arg url "$music_url" '. + {music_url: $url}')"
    fi

    # Media update
    if [[ -n "$media_type" ]]; then
        local media_obj=""
        if [[ "$media_type" == "video" ]]; then
            require_arg "media-url" "$media_url"
            media_obj="$(jq -n --arg type "$media_type" --arg url "$media_url" '{type: $type, url: $url}')"
        else
            require_arg "media-urls" "$media_urls"
            local urls_array
            urls_array="$(split_csv_to_json_array "$media_urls")"
            local url_count
            url_count="$(printf '%s' "$urls_array" | jq 'length')"
            (( url_count >= 1 && url_count <= 35 )) || die "--media-urls must contain between 1 and 35 URLs (got $url_count)"
            media_obj="$(jq -n --arg type "$media_type" --argjson urls "$urls_array" '{type: $type, urls: $urls}')"
        fi
        payload="$(printf '%s' "$payload" | jq --argjson media "$media_obj" '. + {media: $media}')"
    fi

    # Accounts update
    if [[ -n "$accounts" ]]; then
        validate_uuid_csv "accounts" "$accounts" 10
        local account_ids_array
        account_ids_array="$(split_csv_to_json_array "$accounts")"
        local accounts_array
        accounts_array="$(printf '%s' "$account_ids_array" | jq 'map({id: .})')"
        payload="$(printf '%s' "$payload" | jq --argjson accts "$accounts_array" '. + {accounts: $accts}')"
    fi

    if [[ "$clear_tiktok" == true ]]; then
        payload="$(printf '%s' "$payload" | jq '. + {tiktok: null}')"
    elif [[ -n "$tiktok_title" || -n "$tiktok_description" || -n "$tiktok_post_mode" || -n "$tiktok_privacy" || -n "$tiktok_disable_comment" || -n "$tiktok_disable_duet" || -n "$tiktok_disable_stitch" || -n "$tiktok_auto_add_music" || -n "$tiktok_is_commercial" || -n "$tiktok_is_branded_content" || -n "$tiktok_user_consent" || -n "$tiktok_is_your_brand" ]]; then
        local tiktok_obj='{}'
        [[ -n "$tiktok_title" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --arg t "$tiktok_title" '. + {title: $t}')"
        [[ -n "$tiktok_description" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --arg d "$tiktok_description" '. + {description: $d}')"
        [[ -n "$tiktok_post_mode" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --arg m "$tiktok_post_mode" '. + {post_mode: $m}')"
        [[ -n "$tiktok_privacy" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --arg p "$tiktok_privacy" '. + {privacy_level: $p}')"
        [[ -n "$tiktok_disable_comment" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --argjson v "$tiktok_disable_comment" '. + {disable_comment: $v}')"
        [[ -n "$tiktok_disable_duet" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --argjson v "$tiktok_disable_duet" '. + {disable_duet: $v}')"
        [[ -n "$tiktok_disable_stitch" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --argjson v "$tiktok_disable_stitch" '. + {disable_stitch: $v}')"
        [[ -n "$tiktok_auto_add_music" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --argjson v "$tiktok_auto_add_music" '. + {auto_add_music: $v}')"
        [[ -n "$tiktok_is_commercial" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --argjson v "$tiktok_is_commercial" '. + {is_commercial: $v}')"
        [[ -n "$tiktok_is_branded_content" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --argjson v "$tiktok_is_branded_content" '. + {is_branded_content: $v}')"
        [[ -n "$tiktok_user_consent" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --argjson v "$tiktok_user_consent" '. + {user_consent: $v}')"
        [[ -n "$tiktok_is_your_brand" ]] && tiktok_obj="$(printf '%s' "$tiktok_obj" | jq --argjson v "$tiktok_is_your_brand" '. + {is_your_brand: $v}')"
        payload="$(printf '%s' "$payload" | jq --argjson tt "$tiktok_obj" '. + {tiktok: $tt}')"
    fi

    # Check for empty payload
    if [[ "$payload" == "{}" ]]; then
        die "No fields provided for update. Use --caption, --media-type, --accounts, --scheduled-at, --clear-scheduled-at, TikTok options, etc."
    fi

    info "Updating post $post_id..."

    local response
    response="$(api_call PATCH "/posts/${post_id}" "$payload")"

    ok "Post updated."

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# retry-posts
# ---------------------------------------------------------------------------
cmd_retry_posts() {
    local post_ids=""
    local account_ids=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --post-ids)    post_ids="$2"; shift 2 ;;
            --account-ids) account_ids="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "post-ids" "$post_ids"

    validate_uuid_csv "post-ids" "$post_ids" 20
    local post_ids_array
    post_ids_array="$(split_csv_to_json_array "$post_ids")"

    local payload
    payload="$(jq -n --argjson ids "$post_ids_array" '{post_ids: $ids}')"

    if [[ -n "$account_ids" ]]; then
        validate_uuid_csv "account-ids" "$account_ids" 10
        local account_ids_array
        account_ids_array="$(split_csv_to_json_array "$account_ids")"
        payload="$(printf '%s' "$payload" | jq --argjson accts "$account_ids_array" '. + {account_ids: $accts}')"
    fi

    info "Retrying posts..."

    local response
    response="$(api_call POST /posts/retry "$payload")"

    local retried
    retried="$(printf '%s' "$response" | jq -r '.data.retried // 0')"
    ok "Retried $retried posts"

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# list-packs
# ---------------------------------------------------------------------------
cmd_list_packs() {
    local json_output=false
    local search=""
    local limit=20
    local offset=0
    local include_public=true

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --json)           json_output=true; shift ;;
            --search)         search="$2"; shift 2 ;;
            --limit)          limit="$2"; shift 2 ;;
            --offset)         offset="$2"; shift 2 ;;
            --include-public) include_public="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    validate_boolean "include-public" "$include_public"
    validate_positive_int "limit" "$limit"
    validate_max_int "limit" "$limit" 100
    validate_nonnegative_int "offset" "$offset"

    local endpoint="/packs?limit=${limit}&offset=${offset}&include_public=${include_public}"
    [[ -n "$search" ]] && endpoint="${endpoint}&search=${search}"

    info "Fetching image packs..."

    local response
    response="$(api_call GET "$endpoint")"

    if [[ "$json_output" == true ]]; then
        printf '%s' "$response" | jq '.data // {}'
        return
    fi

    local count private_count public_count
    count="$(printf '%s' "$response" | jq '.data.packs | length // 0')"
    private_count="$(printf '%s' "$response" | jq '[.data.packs // [] | .[] | select(.is_public == false)] | length')"
    public_count="$(printf '%s' "$response" | jq '[.data.packs // [] | .[] | select(.is_public == true)] | length')"
    ok "Found $count packs (yours: $private_count | community: $public_count)"
    echo ""

    printf '%s' "$response" | jq -r '
        .data.packs // [] | .[] |
        "  \(.id)\n    Name: \(.name // "unnamed")\n    Images: \(.image_count // 0)\n    Type: \(if .is_public then "community" else "yours" end)\n"
    '
}

# ---------------------------------------------------------------------------
# get-pack
# ---------------------------------------------------------------------------
cmd_get_pack() {
    local pack_id=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id) pack_id="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$pack_id"
    info "Fetching pack $pack_id..."

    local response
    response="$(api_call GET "/packs/${pack_id}")"

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# create-pack
# ---------------------------------------------------------------------------
cmd_create_pack() {
    local name=""
    local is_public=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --name)      name="$2"; shift 2 ;;
            --is-public)
                is_public="$(parse_boolean_flag_or_value "is-public" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "name" "$name"
    ((${#name} <= 120)) || die "--name max length is 120 characters"

    local payload
    payload="$(jq -n --arg name "$name" --argjson pub "$is_public" '{name: $name, is_public: $pub}')"

    info "Creating pack..."

    local response
    response="$(api_call POST /packs "$payload")"

    local pack_id
    pack_id="$(printf '%s' "$response" | jq -r '.data.id // empty')"

    if [[ -n "$pack_id" ]]; then
        ok "Pack created: $pack_id"
    fi

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# update-pack
# ---------------------------------------------------------------------------
cmd_update_pack() {
    local pack_id=""
    local name=""
    local is_public=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id)        pack_id="$2"; shift 2 ;;
            --name)      name="$2"; shift 2 ;;
            --is-public) is_public="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$pack_id"

    [[ -n "$is_public" ]] && validate_boolean "is-public" "$is_public"
    [[ -n "$name" && ${#name} -gt 120 ]] && die "--name max length is 120 characters"

    local payload='{}'
    [[ -n "$name" ]] && payload="$(printf '%s' "$payload" | jq --arg n "$name" '. + {name: $n}')"
    [[ -n "$is_public" ]] && payload="$(printf '%s' "$payload" | jq --argjson pub "$is_public" '. + {is_public: $pub}')"

    if [[ "$payload" == "{}" ]]; then
        die "No fields provided for update. Use --name or --is-public."
    fi

    info "Updating pack $pack_id..."

    local response
    response="$(api_call PATCH "/packs/${pack_id}" "$payload")"

    ok "Pack updated."

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# delete-pack
# ---------------------------------------------------------------------------
cmd_delete_pack() {
    local pack_id=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id) pack_id="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$pack_id"
    warn "Deleting pack $pack_id..."

    api_call DELETE "/packs/${pack_id}" >/dev/null

    ok "Pack deleted."
}

# ---------------------------------------------------------------------------
# add-pack-image
# ---------------------------------------------------------------------------
cmd_add_pack_image() {
    local pack_id=""
    local image_url=""
    local file_name=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --pack-id)   pack_id="$2"; shift 2 ;;
            --image-url) image_url="$2"; shift 2 ;;
            --file-name) file_name="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "pack-id" "$pack_id"
    require_arg "image-url" "$image_url"

    local payload
    payload="$(jq -n --arg url "$image_url" '{image_url: $url}')"
    [[ -n "$file_name" ]] && payload="$(printf '%s' "$payload" | jq --arg name "$file_name" '. + {file_name: $name}')"

    info "Adding image to pack $pack_id..."

    local response
    response="$(api_call POST "/packs/${pack_id}/images" "$payload")"

    ok "Image added to pack."

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# delete-pack-image
# ---------------------------------------------------------------------------
cmd_delete_pack_image() {
    local pack_id=""
    local image_id=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --pack-id)  pack_id="$2"; shift 2 ;;
            --image-id) image_id="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "pack-id" "$pack_id"
    require_arg "image-id" "$image_id"

    warn "Deleting image $image_id from pack $pack_id..."

    api_call DELETE "/packs/${pack_id}/images/${image_id}" >/dev/null

    ok "Image deleted from pack."
}

# ---------------------------------------------------------------------------
# list-templates
# ---------------------------------------------------------------------------
cmd_list_templates() {
    local search=""
    local limit=20
    local offset=0
    local json_output=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --search) search="$2"; shift 2 ;;
            --limit)  limit="$2"; shift 2 ;;
            --offset) offset="$2"; shift 2 ;;
            --json)   json_output=true; shift ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    validate_positive_int "limit" "$limit"
    validate_max_int "limit" "$limit" 100
    validate_nonnegative_int "offset" "$offset"

    local endpoint="/templates?limit=${limit}&offset=${offset}"
    [[ -n "$search" ]] && endpoint="${endpoint}&search=${search}"

    info "Fetching slideshow templates..."

    local response
    response="$(api_call GET "$endpoint")"

    if [[ "$json_output" == true ]]; then
        printf '%s' "$response" | jq '.data // {}'
        return
    fi

    printf '%s' "$response" | jq '.data // {}'
}

# ---------------------------------------------------------------------------
# get-template
# ---------------------------------------------------------------------------
cmd_get_template() {
    local template_id=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id) template_id="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$template_id"
    info "Fetching template $template_id..."

    local response
    response="$(api_call GET "/templates/${template_id}")"

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# create-template
# ---------------------------------------------------------------------------
cmd_create_template() {
    local name=""
    local description=""
    local visibility="private"
    local config_file=""
    local config_json=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --name)        name="$2"; shift 2 ;;
            --description) description="$2"; shift 2 ;;
            --visibility)  visibility="$2"; shift 2 ;;
            --config-file) config_file="$2"; shift 2 ;;
            --config-json) config_json="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "name" "$name"

    [[ "$visibility" == "private" || "$visibility" == "workspace" ]] || die "--visibility must be private or workspace"
    [[ ${#name} -le 100 ]] || die "--name max length is 100 characters"
    [[ -n "$description" && ${#description} -gt 500 ]] && die "--description max length is 500 characters"

    if [[ -n "$config_file" && -n "$config_json" ]]; then
        die "Use either --config-file or --config-json, not both."
    fi
    if [[ -z "$config_file" && -z "$config_json" ]]; then
        die "Provide --config-file or --config-json"
    fi

    local config
    if [[ -n "$config_file" ]]; then
        config="$(read_json_file "$config_file")"
    else
        validate_json_string "config JSON" "$config_json"
        config="$config_json"
    fi

    local payload
    payload="$(jq -n \
        --arg name "$name" \
        --arg visibility "$visibility" \
        --argjson config "$config" \
        '{name: $name, visibility: $visibility, config: $config}'
    )"

    [[ -n "$description" ]] && payload="$(printf '%s' "$payload" | jq --arg d "$description" '. + {description: $d}')"

    info "Creating template..."

    local response
    response="$(api_call POST /templates "$payload")"

    local template_id
    template_id="$(printf '%s' "$response" | jq -r '.data.id // empty')"

    if [[ -n "$template_id" ]]; then
        ok "Template created: $template_id"
    fi

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# update-template
# ---------------------------------------------------------------------------
cmd_update_template() {
    local template_id=""
    local name=""
    local description=""
    local clear_description=false
    local visibility=""
    local config_file=""
    local config_json=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id)                template_id="$2"; shift 2 ;;
            --name)              name="$2"; shift 2 ;;
            --description)       description="$2"; shift 2 ;;
            --clear-description) clear_description=true; shift ;;
            --visibility)        visibility="$2"; shift 2 ;;
            --config-file)       config_file="$2"; shift 2 ;;
            --config-json)       config_json="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$template_id"

    if [[ "$clear_description" == true && -n "$description" ]]; then
        die "Use either --description or --clear-description, not both."
    fi

    if [[ -n "$config_file" && -n "$config_json" ]]; then
        die "Use either --config-file or --config-json, not both."
    fi

    [[ -z "$visibility" || "$visibility" == "private" || "$visibility" == "workspace" ]] || die "--visibility must be private or workspace"
    [[ -z "$name" || ${#name} -le 100 ]] || die "--name max length is 100 characters"
    [[ -z "$description" || ${#description} -le 500 ]] || die "--description max length is 500 characters"

    local payload='{}'

    [[ -n "$name" ]] && payload="$(printf '%s' "$payload" | jq --arg n "$name" '. + {name: $n}')"
    if [[ "$clear_description" == true ]]; then
        payload="$(printf '%s' "$payload" | jq '. + {description: null}')"
    elif [[ -n "$description" ]]; then
        payload="$(printf '%s' "$payload" | jq --arg d "$description" '. + {description: $d}')"
    fi
    [[ -n "$visibility" ]] && payload="$(printf '%s' "$payload" | jq --arg v "$visibility" '. + {visibility: $v}')"

    if [[ -n "$config_file" || -n "$config_json" ]]; then
        local config
        if [[ -n "$config_file" ]]; then
            config="$(read_json_file "$config_file")"
        else
            validate_json_string "config JSON" "$config_json"
            config="$config_json"
        fi
        payload="$(printf '%s' "$payload" | jq --argjson cfg "$config" '. + {config: $cfg}')"
    fi

    if [[ "$payload" == "{}" ]]; then
        die "No fields provided for update. Use --name, --description, --clear-description, --visibility, --config-file, or --config-json."
    fi

    info "Updating template $template_id..."

    local response
    response="$(api_call PATCH "/templates/${template_id}" "$payload")"

    ok "Template updated."

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# delete-template
# ---------------------------------------------------------------------------
cmd_delete_template() {
    local template_id=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id) template_id="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$template_id"
    warn "Deleting template $template_id..."

    api_call DELETE "/templates/${template_id}" >/dev/null

    ok "Template deleted."
}

# ---------------------------------------------------------------------------
# create-template-from-slideshow
# ---------------------------------------------------------------------------
cmd_create_template_from_slideshow() {
    local slideshow_id=""
    local name=""
    local description=""
    local visibility="private"
    local preserve_text=true

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --slideshow-id)  slideshow_id="$2"; shift 2 ;;
            --name)          name="$2"; shift 2 ;;
            --description)   description="$2"; shift 2 ;;
            --visibility)    visibility="$2"; shift 2 ;;
            --preserve-text)
                preserve_text="$(parse_boolean_flag_or_value "preserve-text" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "slideshow-id" "$slideshow_id"
    validate_boolean "preserve-text" "$preserve_text"
    [[ "$visibility" == "private" || "$visibility" == "workspace" ]] || die "--visibility must be private or workspace"
    [[ -z "$name" || ${#name} -le 100 ]] || die "--name max length is 100 characters"
    [[ -z "$description" || ${#description} -le 500 ]] || die "--description max length is 500 characters"

    local payload
    payload="$(jq -n \
        --arg visibility "$visibility" \
        --argjson preserve "$preserve_text" \
        '{visibility: $visibility, preserve_text: $preserve}'
    )"

    [[ -n "$name" ]] && payload="$(printf '%s' "$payload" | jq --arg n "$name" '. + {name: $n}')"
    [[ -n "$description" ]] && payload="$(printf '%s' "$payload" | jq --arg d "$description" '. + {description: $d}')"

    info "Creating template from slideshow $slideshow_id..."

    local response
    response="$(api_call POST "/templates/from-slideshow/${slideshow_id}" "$payload")"

    local template_id
    template_id="$(printf '%s' "$response" | jq -r '.data.id // empty')"

    if [[ -n "$template_id" ]]; then
        ok "Template created: $template_id"
    fi

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# generate
# ---------------------------------------------------------------------------
cmd_generate() {
    local prompt=""
    local pack_id="$DEFAULT_PACK_ID"
    local slides="$DEFAULT_SLIDE_COUNT"
    local type="$DEFAULT_TYPE"
    local aspect_ratio="$DEFAULT_ASPECT_RATIO"
    local style="$DEFAULT_STYLE"
    local language="$DEFAULT_LANGUAGE"
    local font_size=""
    local text_width=""
    local product_id=""
    local skip_ai=false
    local slide_config_json=""
    local slide_config_file=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --prompt)            prompt="$2"; shift 2 ;;
            --pack-id)           pack_id="$2"; shift 2 ;;
            --slides)            slides="$2"; shift 2 ;;
            --type)              type="$2"; shift 2 ;;
            --aspect-ratio)      aspect_ratio="$2"; shift 2 ;;
            --style|--text-preset) style="$2"; shift 2 ;;
            --language)          language="$2"; shift 2 ;;
            --font-size)         font_size="$2"; shift 2 ;;
            --text-width)        text_width="$2"; shift 2 ;;
            --product-id)        product_id="$2"; shift 2 ;;
            --skip-ai)
                skip_ai="$(parse_boolean_flag_or_value "skip-ai" "${2:-}")"
                if [[ $# -ge 2 && -n "${2:-}" && "${2:-}" != --* ]]; then shift 2; else shift; fi
                ;;
            --slide-config-json|--slide-config) slide_config_json="$2"; shift 2 ;;
            --slide-config-file)               slide_config_file="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    validate_slide_count "$slides"
    validate_aspect_ratio "$aspect_ratio"
    validate_type "$type"
    validate_style "$style"
    [[ -n "$font_size" ]] && validate_font_size_setting "$font_size"
    [[ -n "$text_width" ]] && validate_text_width_setting "$text_width"
    validate_boolean "skip-ai" "$skip_ai"

    if [[ -n "$slide_config_json" && -n "$slide_config_file" ]]; then
        die "Use either --slide-config-json/--slide-config or --slide-config-file, not both."
    fi

    if [[ -n "$slide_config_file" ]]; then
        slide_config_json="$(read_json_file "$slide_config_file")"
    fi

    if [[ "$skip_ai" == false && -z "$prompt" && -z "$product_id" ]]; then
        die "Provide --prompt or --product-id (or set --skip-ai true for manual mode)."
    fi

    if [[ -n "$slide_config_json" ]]; then
        validate_json_string "slide config" "$slide_config_json"
    fi

    info "Generating slideshow..."
    if [[ -n "$prompt" ]]; then
        step "  Prompt: ${prompt:0:80}$([ ${#prompt} -gt 80 ] && echo '...')"
    fi
    step "  Slides: $slides | Type: $type | Ratio: $aspect_ratio | Style: $style"
    [[ -n "$pack_id" ]] && step "  Pack: $pack_id"
    [[ "$skip_ai" == true ]] && step "  Mode: skip_ai=true"

    local payload='{}'

    [[ -n "$prompt" ]] && payload="$(printf '%s' "$payload" | jq --arg v "$prompt" '. + {prompt: $v}')"
    [[ -n "$product_id" ]] && payload="$(printf '%s' "$payload" | jq --arg v "$product_id" '. + {product_id: $v}')"
    [[ -n "$pack_id" ]] && payload="$(printf '%s' "$payload" | jq --arg v "$pack_id" '. + {pack_id: $v}')"
    [[ -n "$slides" ]] && payload="$(printf '%s' "$payload" | jq --argjson v "$slides" '. + {slide_count: $v}')"
    [[ -n "$type" ]] && payload="$(printf '%s' "$payload" | jq --arg v "$type" '. + {slideshow_type: $v}')"
    [[ -n "$aspect_ratio" ]] && payload="$(printf '%s' "$payload" | jq --arg v "$aspect_ratio" '. + {aspect_ratio: $v}')"
    [[ -n "$language" ]] && payload="$(printf '%s' "$payload" | jq --arg v "$language" '. + {language: $v}')"

    local advanced='{}'
    [[ -n "$style" ]] && advanced="$(printf '%s' "$advanced" | jq --arg preset "$style" '. + {text_preset: $preset}')"
    [[ -n "$font_size" ]] && advanced="$(printf '%s' "$advanced" | jq --arg fs "$font_size" '. + {font_size: $fs}')"
    [[ -n "$text_width" ]] && advanced="$(printf '%s' "$advanced" | jq --arg tw "$text_width" '. + {text_width: $tw}')"
    if [[ "$advanced" != '{}' ]]; then
        payload="$(printf '%s' "$payload" | jq --argjson advanced "$advanced" '. + {advanced_settings: $advanced}')"
    fi

    [[ "$skip_ai" == true ]] && payload="$(printf '%s' "$payload" | jq '. + {skip_ai: true}')"
    [[ -n "$slide_config_json" ]] && payload="$(printf '%s' "$payload" | jq --argjson cfg "$slide_config_json" '. + {slide_config: $cfg}')"

    local response
    response="$(api_call POST /slideshows/generate "$payload")"

    local slideshow_id
    slideshow_id="$(printf '%s' "$response" | jq -r '.data.id // .data._id // .data.slideshow.id // empty')"

    if [[ -n "$slideshow_id" ]]; then
        ok "Slideshow generated: $slideshow_id"
    fi

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------
cmd_render() {
    local slideshow_id=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id) slideshow_id="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$slideshow_id"
    info "Rendering slideshow $slideshow_id (this may take 10-30 seconds)..."

    local response
    response="$(api_call POST "/slideshows/${slideshow_id}/render")"

    local status
    status="$(printf '%s' "$response" | jq -r '.data.status // .data.slideshow.status // "unknown"')"
    local url_count
    url_count="$(printf '%s' "$response" | jq '[
        .data.preview_image_url,
        (.data.rendered_image_urls // [])[],
        ((.data.slides // [])[]?.rendered_image_url)
    ] | map(select(. != null and . != "")) | unique | length')"

    ok "Render complete. Status: $status, Images: $url_count"

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# review
# ---------------------------------------------------------------------------
cmd_review() {
    local slideshow_id=""
    local json_output=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id) slideshow_id="$2"; shift 2 ;;
            --json) json_output=true; shift ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$slideshow_id"
    info "Fetching slideshow $slideshow_id..."

    local response
    response="$(api_call GET "/slideshows/${slideshow_id}")"

    local data
    data="$(printf '%s' "$response" | jq '.data')"

    if [[ "$json_output" == true ]]; then
        printf '%s' "$data"
        return
    fi

    # Pretty print summary
    local title status slide_count
    title="$(printf '%s' "$data" | jq -r '.title // "untitled"')"
    status="$(printf '%s' "$data" | jq -r '.status // "unknown"')"
    slide_count="$(printf '%s' "$data" | jq '.slides | length // 0')"

    echo "" >&2
    echo -e "${BOLD}Slideshow Review${NC}" >&2
    echo -e "  ID:     $slideshow_id" >&2
    echo -e "  Title:  $title" >&2
    echo -e "  Status: $status" >&2
    echo -e "  Slides: $slide_count" >&2
    echo "" >&2

    # Show each slide's text
    printf '%s' "$data" | jq -r '
        .slides // [] | to_entries[] |
        "  Slide \(.key + 1): \((.value.text_elements // [] | map(.content // "") | map(select(. != "")) | join(" ") | if . == "" then "no text" else . end))"
    ' >&2

    # Show rendered URLs if available
    local rendered_urls rendered_count
    rendered_urls="$(printf '%s' "$data" | jq '[
        (.rendered_image_urls // [])[],
        ((.slides // [])[]?.rendered_image_url),
        .preview_image_url
    ] | map(select(. != null and . != "")) | unique')"
    rendered_count="$(printf '%s' "$rendered_urls" | jq 'length')"
    if [[ "$rendered_count" -gt 0 ]]; then
        echo "" >&2
        echo -e "  ${GREEN}Rendered images ($rendered_count):${NC}" >&2
        printf '%s' "$rendered_urls" | jq -r '.[] | "    " + .' >&2
    fi

    echo "" >&2

    # Output JSON for programmatic use
    printf '%s' "$data"
}

# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------
cmd_update() {
    local slideshow_id=""
    local title=""
    local status=""
    local slideshow_type=""
    local product_id=""
    local clear_product_id=false
    local settings_json=""
    local settings_file=""
    local slides_json=""
    local slides_file=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id)               slideshow_id="$2"; shift 2 ;;
            --title)            title="$2"; shift 2 ;;
            --status)           status="$2"; shift 2 ;;
            --slideshow-type)   slideshow_type="$2"; shift 2 ;;
            --product-id)       product_id="$2"; shift 2 ;;
            --clear-product-id) clear_product_id=true; shift ;;
            --settings-json)    settings_json="$2"; shift 2 ;;
            --settings-file)    settings_file="$2"; shift 2 ;;
            --slides)           slides_json="$2"; shift 2 ;;
            --slides-file)      slides_file="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$slideshow_id"

    if [[ "$clear_product_id" == true && -n "$product_id" ]]; then
        die "Use either --product-id or --clear-product-id, not both."
    fi

    if [[ -n "$settings_json" && -n "$settings_file" ]]; then
        die "Use either --settings-json or --settings-file, not both."
    fi

    if [[ -n "$slides_json" && -n "$slides_file" ]]; then
        die "Use either --slides or --slides-file, not both."
    fi

    if [[ -n "$status" ]]; then
        case "$status" in
            draft|rendered) ;;
            *) die "--status must be 'draft' or 'rendered'. Got: $status" ;;
        esac
    fi

    [[ -n "$slideshow_type" ]] && validate_type "$slideshow_type"

    if [[ -n "$settings_file" ]]; then
        settings_json="$(read_json_file "$settings_file")"
    fi
    if [[ -n "$slides_file" ]]; then
        slides_json="$(read_json_file "$slides_file")"
    fi

    [[ -n "$settings_json" ]] && validate_json_string "settings JSON" "$settings_json"
    [[ -n "$slides_json" ]] && validate_json_string "slides JSON" "$slides_json"

    local body='{}'
    [[ -n "$title" ]] && body="$(printf '%s' "$body" | jq --arg v "$title" '. + {title: $v}')"
    [[ -n "$status" ]] && body="$(printf '%s' "$body" | jq --arg v "$status" '. + {status: $v}')"
    [[ -n "$slideshow_type" ]] && body="$(printf '%s' "$body" | jq --arg v "$slideshow_type" '. + {slideshow_type: $v}')"

    if [[ "$clear_product_id" == true ]]; then
        body="$(printf '%s' "$body" | jq '. + {product_id: null}')"
    elif [[ -n "$product_id" ]]; then
        body="$(printf '%s' "$body" | jq --arg v "$product_id" '. + {product_id: $v}')"
    fi

    [[ -n "$settings_json" ]] && body="$(printf '%s' "$body" | jq --argjson v "$settings_json" '. + {settings: $v}')"
    [[ -n "$slides_json" ]] && body="$(printf '%s' "$body" | jq --argjson v "$slides_json" '. + {slides: $v}')"

    if [[ "$body" == "{}" ]]; then
        die "No fields provided. Use one or more of: --title, --status, --slideshow-type, --product-id, --clear-product-id, --settings-json/--settings-file, --slides/--slides-file."
    fi

    info "Updating slideshow $slideshow_id..."

    local response
    response="$(api_call PATCH "/slideshows/${slideshow_id}" "$body")"

    ok "Slideshow updated. Re-render if visual content changed."

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# regenerate-slide
# ---------------------------------------------------------------------------
cmd_regenerate_slide() {
    local slideshow_id=""
    local slide_index=""
    local instruction=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id)          slideshow_id="$2"; shift 2 ;;
            --index)       slide_index="$2"; shift 2 ;;
            --instruction) instruction="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$slideshow_id"
    require_arg "index" "$slide_index"

    validate_nonnegative_int "index" "$slide_index"
    if [[ -n "$instruction" ]]; then
        ((${#instruction} <= 500)) || die "--instruction max length is 500 characters"
    fi

    local payload='{}'
    [[ -n "$instruction" ]] && payload="$(printf '%s' "$payload" | jq --arg inst "$instruction" '. + {instruction: $inst}')"

    info "Regenerating slide $slide_index for slideshow $slideshow_id..."

    local response
    response="$(api_call POST "/slideshows/${slideshow_id}/slides/${slide_index}/regenerate" "$payload")"

    ok "Slide $slide_index regenerated."

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# duplicate
# ---------------------------------------------------------------------------
cmd_duplicate() {
    local slideshow_id=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id) slideshow_id="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$slideshow_id"
    info "Duplicating slideshow $slideshow_id..."

    local response
    response="$(api_call POST "/slideshows/${slideshow_id}/duplicate")"

    local new_id
    new_id="$(printf '%s' "$response" | jq -r '.data.id // .data._id // empty')"

    if [[ -n "$new_id" ]]; then
        ok "Duplicated as new slideshow: $new_id"
    fi

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------
cmd_delete() {
    local slideshow_id=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id) slideshow_id="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$slideshow_id"
    warn "Deleting slideshow $slideshow_id..."

    api_call DELETE "/slideshows/${slideshow_id}" >/dev/null

    ok "Slideshow deleted."
}

# ---------------------------------------------------------------------------
# list-slideshows
# ---------------------------------------------------------------------------
cmd_list_slideshows() {
    local status_filter=""
    local search=""
    local limit=20
    local offset=0
    local json_output=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --status) status_filter="$2"; shift 2 ;;
            --search) search="$2"; shift 2 ;;
            --limit)  limit="$2"; shift 2 ;;
            --offset) offset="$2"; shift 2 ;;
            --json)   json_output=true; shift ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    validate_positive_int "limit" "$limit"
    validate_max_int "limit" "$limit" 100
    validate_nonnegative_int "offset" "$offset"

    local endpoint="/slideshows?limit=${limit}&offset=${offset}"
    [[ -n "$status_filter" ]] && endpoint="${endpoint}&status=${status_filter}"
    [[ -n "$search" ]] && endpoint="${endpoint}&search=${search}"

    info "Fetching slideshows..."

    local response
    response="$(api_call GET "$endpoint")"

    if [[ "$json_output" == true ]]; then
        printf '%s' "$response" | jq '.data // {}'
        return
    fi

    local count
    count="$(printf '%s' "$response" | jq '.data.slideshows | length // 0')"
    local total
    total="$(printf '%s' "$response" | jq '.data.total // 0')"

    ok "Found $count slideshows (total: $total, showing ${limit} from offset ${offset})"

    printf '%s' "$response" | jq '.data // {}'
}

# ---------------------------------------------------------------------------
# post-draft (legacy TikTok-focused command)
# ---------------------------------------------------------------------------
cmd_post_draft() {
    local slideshow_id=""
    local caption=""
    local account_ids="$DEFAULT_ACCOUNT_IDS"
    local scheduled_at=""
    local privacy_override=""
    local post_mode_override=""
    local privacy="SELF_ONLY"
    local post_mode="MEDIA_UPLOAD"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id)           slideshow_id="$2"; shift 2 ;;
            --caption)      caption="$2"; shift 2 ;;
            --account-ids)  account_ids="$2"; shift 2 ;;
            --privacy)      privacy_override="$2"; shift 2 ;;
            --post-mode)    post_mode_override="$2"; shift 2 ;;
            --scheduled-at) scheduled_at="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$slideshow_id"
    require_arg "caption" "$caption"

    if [[ -z "$account_ids" ]]; then
        die "--account-ids is required (or set default_account_ids in defaults.yaml)"
    fi

    [[ -n "$privacy_override" ]] && warn "--privacy is ignored for post-draft. Using SELF_ONLY."
    [[ -n "$post_mode_override" ]] && warn "--post-mode is ignored for post-draft. Using MEDIA_UPLOAD."
    [[ -n "$scheduled_at" ]] && validate_iso_datetime_offset "scheduled-at" "$scheduled_at"

    # Fetch rendered image URLs from the slideshow
    info "Fetching rendered slideshow for posting..."

    local slideshow_response
    slideshow_response="$(api_call GET "/slideshows/${slideshow_id}")"

    local rendered_urls
    rendered_urls="$(printf '%s' "$slideshow_response" | jq -c '
        [
            (.data.rendered_image_urls // [])[] ,
            ((.data.slides // [])[] | .rendered_image_url // empty)
        ] | map(select(. != null and . != "")) | unique
    ')"

    local url_count
    url_count="$(printf '%s' "$rendered_urls" | jq 'length')"

    if [[ "$url_count" -eq 0 ]]; then
        die "No rendered images found. Run 'render' first."
    fi

    step "  Found $url_count rendered images"

    # Build accounts array
    validate_uuid_csv "account-ids" "$account_ids" 10
    local account_ids_array
    account_ids_array="$(split_csv_to_json_array "$account_ids")"
    local accounts_array
    accounts_array="$(printf '%s' "$account_ids_array" | jq 'map({id: .})')"

    # Build post body
    local payload
    payload="$(jq -n \
        --arg caption "$caption" \
        --argjson urls "$rendered_urls" \
        --argjson accounts "$accounts_array" \
        --arg privacy_level "$privacy" \
        --arg post_mode "$post_mode" \
        --arg scheduled_at "$scheduled_at" \
        '{
            caption: $caption,
            media: {
                type: "slideshow",
                urls: $urls
            },
            accounts: $accounts,
            tiktok: {
                privacy_level: $privacy_level,
                post_mode: $post_mode
            }
        }
        + (if $scheduled_at != "" then { scheduled_at: $scheduled_at } else {} end)
    ')"

    info "Posting as draft (SELF_ONLY + MEDIA_UPLOAD)..."

    local response
    response="$(api_call POST /posts "$payload")"

    local post_id
    post_id="$(printf '%s' "$response" | jq -r '.data.id // .data._id // .data.post.id // empty')"

    if [[ -n "$post_id" ]]; then
        ok "Draft posted: $post_id"
        step "  Caption: ${caption:0:100}$([ ${#caption} -gt 100 ] && echo '...')"
        echo -e "  ${YELLOW}Action needed: Open TikTok, find the draft, add music, and publish.${NC}" >&2
    fi

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# list-posts
# ---------------------------------------------------------------------------
cmd_list_posts() {
    local status_filter=""
    local limit=50
    local since=""
    local until=""
    local json_output=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --status) status_filter="$2"; shift 2 ;;
            --limit)  limit="$2"; shift 2 ;;
            --since)  since="$2"; shift 2 ;;
            --until)  until="$2"; shift 2 ;;
            --json)   json_output=true; shift ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    validate_positive_int "limit" "$limit"
    validate_max_int "limit" "$limit" 100
    [[ -n "$since" ]] && validate_iso_datetime_offset "since" "$since"
    [[ -n "$until" ]] && validate_iso_datetime_offset "until" "$until"

    local endpoint="/posts?limit=${limit}"
    [[ -n "$status_filter" ]] && endpoint="${endpoint}&status=${status_filter}"
    [[ -n "$since" ]] && endpoint="${endpoint}&since=${since}"
    [[ -n "$until" ]] && endpoint="${endpoint}&until=${until}"

    info "Fetching posts..."

    local response
    response="$(api_call GET "$endpoint")"

    if [[ "$json_output" == true ]]; then
        printf '%s' "$response" | jq '.data // {}'
        return
    fi

    local count
    count="$(printf '%s' "$response" | jq '.data.posts | length // 0')"
    local total
    total="$(printf '%s' "$response" | jq '.data.summary.total // 0')"

    # Print summary header
    local posted scheduled failed pending
    posted="$(printf '%s' "$response" | jq '.data.summary.by_status.posted // 0')"
    scheduled="$(printf '%s' "$response" | jq '.data.summary.by_status.scheduled // 0')"
    failed="$(printf '%s' "$response" | jq '.data.summary.by_status.failed // 0')"
    pending="$(printf '%s' "$response" | jq '.data.summary.by_status.pending // 0')"
    ok "Found $count posts (total: $total) | posted: $posted | scheduled: $scheduled | failed: $failed | pending: $pending"
    echo ""

    # Print compact post list
    printf '%s' "$response" | jq -r '.data.posts[] | "  \(.id)\n    Status: \(.status) | Media: \(.media.type // "unknown") | Scheduled: \(.scheduled_at // "none")\n    Caption: \(.caption[:100] // "no caption")...\n"'
}

# ---------------------------------------------------------------------------
# get-post
# ---------------------------------------------------------------------------
cmd_get_post() {
    local post_id=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id) post_id="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$post_id"
    info "Fetching post $post_id..."

    local response
    response="$(api_call GET "/posts/${post_id}")"

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# delete-posts
# ---------------------------------------------------------------------------
cmd_delete_posts() {
    local ids=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --ids|--post-ids|--postIds) ids="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "ids (or --post-ids)" "$ids"

    validate_uuid_csv "ids" "$ids" 50

    # Convert comma-separated IDs to JSON array
    local post_ids_json
    post_ids_json="$(split_csv_to_json_array "$ids")"

    warn "Deleting posts..."

    local payload
    payload="$(jq -n --argjson post_ids "$post_ids_json" '{postIds: $post_ids}')"

    local response
    response="$(api_call POST /posts/delete "$payload")"

    local deleted_count blocked_count skipped_count errors_count
    deleted_count="$(printf '%s' "$response" | jq '.data.deletedIds | length // 0')"
    blocked_count="$(printf '%s' "$response" | jq '.data.blockedStatuses | length // 0')"
    skipped_count="$(printf '%s' "$response" | jq '.data.skipped | length // 0')"
    errors_count="$(printf '%s' "$response" | jq '.data.errors | length // 0')"

    ok "Delete processed. Deleted: ${deleted_count}, Blocked: ${blocked_count}, Skipped: ${skipped_count}, Errors: ${errors_count}."

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# analytics-summary
# ---------------------------------------------------------------------------
cmd_analytics_summary() {
    local range=""
    local start=""
    local end=""
    local platforms=""
    local accounts=""
    local json_output=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --range)       range="$2"; shift 2 ;;
            --start)       start="$2"; shift 2 ;;
            --end)         end="$2"; shift 2 ;;
            --platforms|--platform) platforms="$2"; shift 2 ;;
            --accounts|--account-ids) accounts="$2"; shift 2 ;;
            --json)        json_output=true; shift ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    if [[ -n "$start" || -n "$end" ]]; then
        [[ -n "$start" && -n "$end" ]] || die "Use --start and --end together."
        validate_iso_date_ymd "start" "$start"
        validate_iso_date_ymd "end" "$end"
    fi

    if [[ -n "$range" ]]; then
        case "$range" in
            14d|30d|90d|1y|all) ;;
            *) die "--range must be one of: 14d, 30d, 90d, 1y, all. Got: $range" ;;
        esac
    fi

    local endpoint="/analytics/summary"
    local qs=()
    [[ -n "$range" ]] && qs+=("range=${range}")
    [[ -n "$start" ]] && qs+=("start=${start}")
    [[ -n "$end" ]] && qs+=("end=${end}")
    [[ -n "$platforms" ]] && qs+=("platforms=${platforms}")
    [[ -n "$accounts" ]] && qs+=("accounts=${accounts}")

    if [[ ${#qs[@]} -gt 0 ]]; then
        endpoint+="?$(IFS='&'; echo "${qs[*]}")"
    fi

    info "Fetching analytics summary..."
    local response
    response="$(api_call GET "$endpoint")"

    if [[ "$json_output" == true ]]; then
        printf '%s' "$response" | jq '.data'
        return
    fi

    local posting_streak
    posting_streak="$(printf '%s' "$response" | jq -r '.data.postingStreak // 0')"
    ok "Analytics summary retrieved (posting streak: ${posting_streak})"

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# analytics-posts
# ---------------------------------------------------------------------------
cmd_analytics_posts() {
    local range=""
    local start=""
    local end=""
    local platforms=""
    local accounts=""
    local sort_by=""
    local sort_order=""
    local limit=50
    local offset=0
    local json_output=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --range)       range="$2"; shift 2 ;;
            --start)       start="$2"; shift 2 ;;
            --end)         end="$2"; shift 2 ;;
            --platforms|--platform) platforms="$2"; shift 2 ;;
            --accounts|--account-ids) accounts="$2"; shift 2 ;;
            --sort-by)     sort_by="$2"; shift 2 ;;
            --sort-order)  sort_order="$2"; shift 2 ;;
            --limit)       limit="$2"; shift 2 ;;
            --offset)      offset="$2"; shift 2 ;;
            --json)        json_output=true; shift ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    if [[ -n "$start" || -n "$end" ]]; then
        [[ -n "$start" && -n "$end" ]] || die "Use --start and --end together."
        validate_iso_date_ymd "start" "$start"
        validate_iso_date_ymd "end" "$end"
    fi

    if [[ -n "$range" ]]; then
        case "$range" in
            14d|30d|90d|1y|all) ;;
            *) die "--range must be one of: 14d, 30d, 90d, 1y, all. Got: $range" ;;
        esac
    fi

    validate_positive_int "limit" "$limit"
    validate_max_int "limit" "$limit" 100
    validate_nonnegative_int "offset" "$offset"
    validate_max_int "offset" "$offset" 10000

    if [[ -n "$sort_by" ]]; then
        case "$sort_by" in
            published_at|views|likes|comments|shares) ;;
            *) die "--sort-by must be one of: published_at, views, likes, comments, shares. Got: $sort_by" ;;
        esac
    fi

    if [[ -n "$sort_order" ]]; then
        case "$sort_order" in
            asc|desc) ;;
            *) die "--sort-order must be asc or desc. Got: $sort_order" ;;
        esac
    fi

    local endpoint="/analytics/summary/posts"
    local qs=("limit=${limit}" "offset=${offset}")
    [[ -n "$range" ]] && qs+=("range=${range}")
    [[ -n "$start" ]] && qs+=("start=${start}")
    [[ -n "$end" ]] && qs+=("end=${end}")
    [[ -n "$platforms" ]] && qs+=("platforms=${platforms}")
    [[ -n "$accounts" ]] && qs+=("accounts=${accounts}")
    [[ -n "$sort_by" ]] && qs+=("sortBy=${sort_by}")
    [[ -n "$sort_order" ]] && qs+=("sortOrder=${sort_order}")
    endpoint+="?$(IFS='&'; echo "${qs[*]}")"

    info "Fetching analytics posts..."
    local response
    response="$(api_call GET "$endpoint")"

    if [[ "$json_output" == true ]]; then
        printf '%s' "$response" | jq '.data'
        return
    fi

    local total
    total="$(printf '%s' "$response" | jq -r '.data.totalCount // 0')"
    ok "Analytics posts retrieved (total: ${total})"

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# analytics-targets
# ---------------------------------------------------------------------------
cmd_analytics_targets() {
    local json_output=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --json) json_output=true; shift ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    info "Fetching analytics targets..."
    local response
    response="$(api_call GET /analytics/targets)"

    if [[ "$json_output" == true ]]; then
        printf '%s' "$response" | jq '.data'
        return
    fi

    local count
    count="$(printf '%s' "$response" | jq -r '.data.targets | length // 0')"
    ok "Found ${count} analytics targets"

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# analytics-target-create
# ---------------------------------------------------------------------------
cmd_analytics_target_create() {
    local platform=""
    local identifier=""
    local alias=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --platform)   platform="$2"; shift 2 ;;
            --identifier) identifier="$2"; shift 2 ;;
            --alias)      alias="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "platform" "$platform"
    require_arg "identifier" "$identifier"

    case "$platform" in
        tiktok|instagram|youtube) ;;
        *) die "--platform must be one of: tiktok, instagram, youtube. Got: $platform" ;;
    esac

    local payload
    payload="$(jq -n --arg platform "$platform" --arg identifier "$identifier" '{platform: $platform, identifier: $identifier}')"
    [[ -n "$alias" ]] && payload="$(printf '%s' "$payload" | jq --arg alias "$alias" '. + {alias: $alias}')"

    info "Creating analytics target..."
    local response
    response="$(api_call POST /analytics/targets "$payload")"

    ok "Analytics target created"
    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# analytics-target (GET)
# ---------------------------------------------------------------------------
cmd_analytics_target_get() {
    local id=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id) id="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$id"
    info "Fetching analytics target $id..."

    local response
    response="$(api_call GET "/analytics/targets/${id}")"

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# analytics-target-update (PATCH)
# ---------------------------------------------------------------------------
cmd_analytics_target_update() {
    local id=""
    local display_name=""
    local clear_display_name=false
    local favorite=""
    local refresh_policy_json=""
    local refresh_policy_file=""
    local clear_refresh_policy=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id)                 id="$2"; shift 2 ;;
            --display-name)       display_name="$2"; shift 2 ;;
            --clear-display-name) clear_display_name=true; shift ;;
            --favorite)            favorite="$2"; shift 2 ;;
            --refresh-policy-json) refresh_policy_json="$2"; shift 2 ;;
            --refresh-policy-file) refresh_policy_file="$2"; shift 2 ;;
            --clear-refresh-policy) clear_refresh_policy=true; shift ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$id"

    if [[ "$clear_display_name" == true && -n "$display_name" ]]; then
        die "Use either --display-name or --clear-display-name, not both."
    fi

    if [[ -n "$refresh_policy_json" && -n "$refresh_policy_file" ]]; then
        die "Use either --refresh-policy-json or --refresh-policy-file, not both."
    fi

    if [[ "$clear_refresh_policy" == true && ( -n "$refresh_policy_json" || -n "$refresh_policy_file" ) ]]; then
        die "Use either --clear-refresh-policy or --refresh-policy-json/--refresh-policy-file, not both."
    fi

    [[ -n "$favorite" ]] && validate_boolean "favorite" "$favorite"

    if [[ -n "$refresh_policy_file" ]]; then
        refresh_policy_json="$(read_json_file "$refresh_policy_file")"
    fi
    [[ -n "$refresh_policy_json" ]] && validate_json_string "refresh policy JSON" "$refresh_policy_json"

    local payload='{}'

    if [[ "$clear_display_name" == true ]]; then
        payload="$(printf '%s' "$payload" | jq '. + {displayName: null}')"
    elif [[ -n "$display_name" ]]; then
        payload="$(printf '%s' "$payload" | jq --arg v "$display_name" '. + {displayName: $v}')"
    fi

    [[ -n "$favorite" ]] && payload="$(printf '%s' "$payload" | jq --argjson v "$favorite" '. + {favorite: $v}')"
    if [[ "$clear_refresh_policy" == true ]]; then
        payload="$(printf '%s' "$payload" | jq '. + {refreshPolicy: null}')"
    elif [[ -n "$refresh_policy_json" ]]; then
        payload="$(printf '%s' "$payload" | jq --argjson v "$refresh_policy_json" '. + {refreshPolicy: $v}')"
    fi

    if [[ "$payload" == "{}" ]]; then
        die "No updates provided. Use --display-name/--clear-display-name, --favorite, --clear-refresh-policy, or --refresh-policy-json/--refresh-policy-file."
    fi

    info "Updating analytics target $id..."
    local response
    response="$(api_call PATCH "/analytics/targets/${id}" "$payload")"

    ok "Analytics target updated"
    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# analytics-target-delete (DELETE)
# ---------------------------------------------------------------------------
cmd_analytics_target_delete() {
    local id=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id) id="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$id"
    warn "Deleting analytics target $id..."

    local response
    response="$(api_call DELETE "/analytics/targets/${id}")"

    ok "Analytics target deleted"
    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# analytics-target-refresh (POST)
# ---------------------------------------------------------------------------
cmd_analytics_target_refresh() {
    local id=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id) id="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$id"
    info "Refreshing analytics target $id..."

    local response
    response="$(api_call POST "/analytics/targets/${id}/refresh")"

    ok "Analytics refresh triggered"
    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# analytics-refresh (GET)
# ---------------------------------------------------------------------------
cmd_analytics_refresh_get() {
    local id=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --id) id="$2"; shift 2 ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "id" "$id"
    info "Fetching analytics refresh $id..."

    local response
    response="$(api_call GET "/analytics/refreshes/${id}")"

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# analytics-workspace-suggestions
# ---------------------------------------------------------------------------
cmd_analytics_workspace_suggestions() {
    local json_output=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --json) json_output=true; shift ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    info "Fetching analytics workspace suggestions..."
    local response
    response="$(api_call GET /analytics/workspace-suggestions)"

    if [[ "$json_output" == true ]]; then
        printf '%s' "$response" | jq '.data'
        return
    fi

    local count
    count="$(printf '%s' "$response" | jq '.data | length // 0')"
    ok "Retrieved ${count} workspace suggestion(s)"

    printf '%s' "$response" | jq '.data'
}

# ---------------------------------------------------------------------------
# full-pipeline (legacy TikTok-focused command)
# ---------------------------------------------------------------------------
cmd_full_pipeline() {
    local prompt=""
    local caption=""
    local pack_id="$DEFAULT_PACK_ID"
    local slides="$DEFAULT_SLIDE_COUNT"
    local type="$DEFAULT_TYPE"
    local aspect_ratio="$DEFAULT_ASPECT_RATIO"
    local style="$DEFAULT_STYLE"
    local language="$DEFAULT_LANGUAGE"
    local account_ids="$DEFAULT_ACCOUNT_IDS"
    local skip_post=false
    local font_size=""
    local text_width=""
    local product_id=""
    local skip_ai=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --prompt)       prompt="$2"; shift 2 ;;
            --caption)      caption="$2"; shift 2 ;;
            --pack-id)      pack_id="$2"; shift 2 ;;
            --slides)       slides="$2"; shift 2 ;;
            --type)         type="$2"; shift 2 ;;
            --aspect-ratio) aspect_ratio="$2"; shift 2 ;;
            --style)        style="$2"; shift 2 ;;
            --language)     language="$2"; shift 2 ;;
            --account-ids)  account_ids="$2"; shift 2 ;;
            --font-size)    font_size="$2"; shift 2 ;;
            --text-width)   text_width="$2"; shift 2 ;;
            --product-id)   product_id="$2"; shift 2 ;;
            --skip-ai)      skip_ai=true; shift ;;
            --skip-post)    skip_post=true; shift ;;
            *) die "Unknown option: $1" ;;
        esac
    done

    require_arg "prompt" "$prompt"

    if [[ "$skip_post" == false && -z "$caption" ]]; then
        die "--caption is required (or use --skip-post to skip posting)"
    fi

    echo "" >&2
    echo -e "${BOLD}=== Full Pipeline ===${NC}" >&2

    # ----- Step 1: Generate -----
    echo "" >&2
    step "Step 1/4: Generate slideshow"

    local gen_args=(--prompt "$prompt" --pack-id "$pack_id" --slides "$slides" --type "$type" --aspect-ratio "$aspect_ratio" --style "$style" --language "$language")
    [[ -n "$font_size" ]] && gen_args+=(--font-size "$font_size")
    [[ -n "$text_width" ]] && gen_args+=(--text-width "$text_width")
    [[ -n "$product_id" ]] && gen_args+=(--product-id "$product_id")
    [[ "$skip_ai" == true ]] && gen_args+=(--skip-ai)

    local gen_result
    gen_result="$(cmd_generate "${gen_args[@]}")" || die "Pipeline failed at generation step."

    local slideshow_id
    slideshow_id="$(printf '%s' "$gen_result" | jq -r '.id // ._id // .slideshow.id // empty')"

    if [[ -z "$slideshow_id" ]]; then
        die "Could not extract slideshow ID from generation response."
    fi

    step "  Slideshow ID: $slideshow_id"

    # ----- Step 2: Render -----
    echo "" >&2
    step "Step 2/4: Render slideshow"

    local render_result
    render_result="$(cmd_render --id "$slideshow_id")" || die "Pipeline failed at render step."

    # ----- Step 3: Review -----
    echo "" >&2
    step "Step 3/4: Review rendered slideshow"

    local review_result
    review_result="$(cmd_review --id "$slideshow_id" --json)" || die "Pipeline failed at review step."

    # ----- Step 4: Post -----
    local post_id=""
    if [[ "$skip_post" == true ]]; then
        echo "" >&2
        step "Step 4/4: Skipped (--skip-post)"
    else
        echo "" >&2
        step "Step 4/4: Post as draft"

        local post_result
        post_result="$(cmd_post_draft --id "$slideshow_id" --caption "$caption" --account-ids "$account_ids")" || die "Pipeline failed at post step."

        post_id="$(printf '%s' "$post_result" | jq -r '.id // ._id // .post.id // empty')"
    fi

    # ----- Summary -----
    echo "" >&2
    echo -e "${GREEN}${BOLD}=== Pipeline Complete ===${NC}" >&2
    step "  Slideshow: $slideshow_id"

    # Show rendered URLs
    local urls
    urls="$(printf '%s' "$render_result" | jq -r '[
        (.rendered_image_urls // [])[],
        ((.slides // [])[]?.rendered_image_url),
        .preview_image_url
    ] | map(select(. != null and . != "")) | unique | .[]' 2>/dev/null || true)"
    if [[ -n "$urls" ]]; then
        step "  Rendered slides:"
        while IFS= read -r url; do
            step "    $url"
        done <<< "$urls"
    fi

    if [[ "$skip_post" == false && -n "$post_id" ]]; then
        step "  Post: $post_id"
        step "  Caption: ${caption:0:100}$([ ${#caption} -gt 100 ] && echo '...')"
    fi

    echo "" >&2

    # Output structured JSON result
    local output
    if [[ "$skip_post" == true ]]; then
        output="$(jq -n \
            --arg slideshow_id "$slideshow_id" \
            '{
                slideshow_id: $slideshow_id,
                status: "rendered",
                posted: false
            }'
        )"
    else
        output="$(jq -n \
            --arg slideshow_id "$slideshow_id" \
            --arg post_id "${post_id:-unknown}" \
            --arg caption "$caption" \
            '{
                slideshow_id: $slideshow_id,
                post_id: $post_id,
                caption: $caption,
                status: "draft_posted",
                posted: true
            }'
        )"
    fi

    printf '%s' "$output"
}

# ===========================================================================
# Main Entry Point
# ===========================================================================

check_deps
load_defaults

COMMAND="${1:-help}"
shift 2>/dev/null || true

case "$COMMAND" in
    # Account & File Commands
    accounts)                         check_auth; cmd_accounts "$@" ;;
    upload)                           check_auth; cmd_upload "$@" ;;
    list-files)                       check_auth; cmd_list_files "$@" ;;

    # Post Commands
    create-post)                      check_auth; cmd_create_post "$@" ;;
    update-post)                      check_auth; cmd_update_post "$@" ;;
    retry-posts)                      check_auth; cmd_retry_posts "$@" ;;
    list-posts)                       check_auth; cmd_list_posts "$@" ;;
    get-post)                         check_auth; cmd_get_post "$@" ;;
    delete-posts|delete-post)         check_auth; cmd_delete_posts "$@" ;;

    # Slideshow Commands
    generate|generate-slideshow)      check_auth; cmd_generate "$@" ;;
    render|render-slideshow)          check_auth; cmd_render "$@" ;;
    review|get-slideshow)             check_auth; cmd_review "$@" ;;
    update|update-slideshow)          check_auth; cmd_update "$@" ;;
    regenerate-slide)                 check_auth; cmd_regenerate_slide "$@" ;;
    duplicate|duplicate-slideshow)    check_auth; cmd_duplicate "$@" ;;
    delete|delete-slideshow)          check_auth; cmd_delete "$@" ;;
    list-slideshows)                  check_auth; cmd_list_slideshows "$@" ;;

    # Pack Commands
    list-packs)                       check_auth; cmd_list_packs "$@" ;;
    get-pack)                         check_auth; cmd_get_pack "$@" ;;
    create-pack)                      check_auth; cmd_create_pack "$@" ;;
    update-pack)                      check_auth; cmd_update_pack "$@" ;;
    delete-pack)                      check_auth; cmd_delete_pack "$@" ;;
    add-pack-image)                   check_auth; cmd_add_pack_image "$@" ;;
    delete-pack-image)                check_auth; cmd_delete_pack_image "$@" ;;

    # Template Commands
    list-templates)                   check_auth; cmd_list_templates "$@" ;;
    get-template)                     check_auth; cmd_get_template "$@" ;;
    create-template)                  check_auth; cmd_create_template "$@" ;;
    update-template)                  check_auth; cmd_update_template "$@" ;;
    delete-template)                  check_auth; cmd_delete_template "$@" ;;
    create-template-from-slideshow)   check_auth; cmd_create_template_from_slideshow "$@" ;;

    # Analytics Commands
    analytics-summary|get-analytics-summary)
                                      check_auth; cmd_analytics_summary "$@" ;;
    analytics-posts|list-analytics-posts)
                                      check_auth; cmd_analytics_posts "$@" ;;
    analytics-targets|analytics-targets-list)
                                      check_auth; cmd_analytics_targets "$@" ;;
    analytics-target-create)          check_auth; cmd_analytics_target_create "$@" ;;
    analytics-target)                 check_auth; cmd_analytics_target_get "$@" ;;
    analytics-target-update)          check_auth; cmd_analytics_target_update "$@" ;;
    analytics-target-delete)          check_auth; cmd_analytics_target_delete "$@" ;;
    analytics-target-refresh)         check_auth; cmd_analytics_target_refresh "$@" ;;
    analytics-refresh|get-analytics-refresh)
                                      check_auth; cmd_analytics_refresh_get "$@" ;;
    analytics-workspace-suggestions|get-analytics-workspace-suggestions)
                                      check_auth; cmd_analytics_workspace_suggestions "$@" ;;

    # Legacy Pipeline Commands
    post-draft)                       check_auth; cmd_post_draft "$@" ;;
    full-pipeline)                    check_auth; cmd_full_pipeline "$@" ;;

    # Help
    help|--help|-h)                   usage ;;

    *)
        error "Unknown command: $COMMAND"
        echo "" >&2
        usage >&2
        exit 1
        ;;
esac
