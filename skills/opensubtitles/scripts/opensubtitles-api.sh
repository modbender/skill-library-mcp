#!/bin/bash

set -euo pipefail

API_ROOT="https://api.opensubtitles.com/api/v1"

base_url() {
    if [[ -n "${OPENSUBTITLES_BASE_URL:-}" ]]; then
        echo "https://${OPENSUBTITLES_BASE_URL}/api/v1"
    else
        echo "${API_ROOT}"
    fi
}

print_usage() {
    cat <<EOF
Usage: opensubtitles-api.sh <command> [options]

Commands:
  search                Search subtitles (read-only)
  login                 Get user token (required for downloads)
  download-link         Request a temporary download URL (requires token)

Environment:
  OPENSUBTITLES_API_KEY         (required)
  OPENSUBTITLES_USER_AGENT      (required, e.g., "OpenClaw 1.0")
  OPENSUBTITLES_USERNAME        (required for login)
  OPENSUBTITLES_PASSWORD        (required for login)
  OPENSUBTITLES_TOKEN           (optional; use instead of login)
  OPENSUBTITLES_BASE_URL        (optional; from login response)

Examples:
  OPENSUBTITLES_API_KEY=xxx OPENSUBTITLES_USER_AGENT="OpenClaw 1.0" \
    ./opensubtitles-api.sh search --query "Game of Thrones" --season 3 --episode 5 --languages en

  OPENSUBTITLES_API_KEY=xxx OPENSUBTITLES_USER_AGENT="OpenClaw 1.0" \
    OPENSUBTITLES_USERNAME=user OPENSUBTITLES_PASSWORD=pass ./opensubtitles-api.sh login

  OPENSUBTITLES_API_KEY=xxx OPENSUBTITLES_USER_AGENT="OpenClaw 1.0" \
    OPENSUBTITLES_TOKEN=token ./opensubtitles-api.sh download-link --file-id 123
EOF
}

check_bins() {
    local bins=("curl" "jq")
    for b in "${bins[@]}"; do
        if ! command -v "$b" >/dev/null 2>&1; then
            echo "Error: missing dependency '$b'" >&2
            exit 1
        fi
    done
}

check_api_key() {
    if [[ -z "${OPENSUBTITLES_API_KEY:-}" ]]; then
        echo "Error: OPENSUBTITLES_API_KEY not set" >&2
        exit 1
    fi
}

check_user_agent() {
    if [[ -z "${OPENSUBTITLES_USER_AGENT:-}" ]]; then
        echo "Error: OPENSUBTITLES_USER_AGENT not set" >&2
        exit 1
    fi
}

api_get() {
    local base="$1"
    local path="$2"
    shift 2
    local qs="$*"

    local url="${base}${path}"
    if [[ -n "$qs" ]]; then
        url+="?${qs}"
    fi

    curl -s -L \
      -H "Accept: application/json" \
      -H "Api-Key: ${OPENSUBTITLES_API_KEY}" \
      -H "User-Agent: ${OPENSUBTITLES_USER_AGENT}" \
      "$url"
}

api_post() {
    local base="$1"
    local path="$2"
    local body="$3"
    local auth_header="$4"

    curl -s \
      -H "Accept: application/json" \
      -H "Api-Key: ${OPENSUBTITLES_API_KEY}" \
      -H "User-Agent: ${OPENSUBTITLES_USER_AGENT}" \
      -H "Content-Type: application/json" \
      ${auth_header:+-H "Authorization: Bearer ${auth_header}"} \
      -d "$body" \
      "${base}${path}"
}

parse_args() {
    local -n _query=$1
    local -n _languages=$2
    local -n _imdb_id=$3
    local -n _tmdb_id=$4
    local -n _parent_imdb_id=$5
    local -n _parent_tmdb_id=$6
    local -n _season=$7
    local -n _episode=$8
    local -n _file_id=$9

    shift 9

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --query) _query="$2"; shift 2;;
            --languages) _languages="$2"; shift 2;;
            --imdb-id) _imdb_id="$2"; shift 2;;
            --tmdb-id) _tmdb_id="$2"; shift 2;;
            --parent-imdb-id) _parent_imdb_id="$2"; shift 2;;
            --parent-tmdb-id) _parent_tmdb_id="$2"; shift 2;;
            --season) _season="$2"; shift 2;;
            --episode) _episode="$2"; shift 2;;
            --file-id) _file_id="$2"; shift 2;;
            *) echo "Unknown arg: $1" >&2; exit 1;;
        esac
    done
}

format_search() {
    local json="$1"

    if echo "$json" | jq -e '.error' >/dev/null 2>&1; then
        echo "Error: $(echo "$json" | jq -r '.message // .error')" >&2
        exit 1
    fi

    echo "🎬 Subtitles (top 5):"
    echo ""
    echo "$json" | jq -r '.data[:5][] | "- \(.attributes.release) | \(.attributes.language) | file_id=\(.attributes.files[0].file_id) | \(.attributes.files[0].file_name)"'
}

main() {
    if [[ $# -lt 1 ]]; then
        print_usage
        exit 1
    fi

    check_bins
    check_api_key
    check_user_agent

    local command="$1"
    shift

    case "$command" in
        search)
            local query="" languages="" imdb_id="" tmdb_id="" parent_imdb_id="" parent_tmdb_id="" season="" episode=""
            local file_id=""
            parse_args query languages imdb_id tmdb_id parent_imdb_id parent_tmdb_id season episode file_id "$@"

            local qs=()
            [[ -n "$query" ]] && qs+=("query=$(jq -nr --arg s "$query" '$s|@uri')")
            [[ -n "$languages" ]] && qs+=("languages=$(jq -nr --arg s "$languages" '$s|@uri')")
            [[ -n "$imdb_id" ]] && qs+=("imdb_id=${imdb_id}")
            [[ -n "$tmdb_id" ]] && qs+=("tmdb_id=${tmdb_id}")
            [[ -n "$parent_imdb_id" ]] && qs+=("parent_imdb_id=${parent_imdb_id}")
            [[ -n "$parent_tmdb_id" ]] && qs+=("parent_tmdb_id=${parent_tmdb_id}")
            [[ -n "$season" ]] && qs+=("season_number=${season}")
            [[ -n "$episode" ]] && qs+=("episode_number=${episode}")

            local json
            local qs_str=""
            if (( ${#qs[@]} )); then
                qs_str="${qs[0]}"
                for ((i=1;i<${#qs[@]};i++)); do
                    qs_str+="&${qs[i]}"
                done
            fi
            json=$(api_get "$(base_url)" "/subtitles" "$qs_str")
            format_search "$json"
            ;;
        login)
            if [[ -z "${OPENSUBTITLES_USERNAME:-}" || -z "${OPENSUBTITLES_PASSWORD:-}" ]]; then
                echo "Error: OPENSUBTITLES_USERNAME and OPENSUBTITLES_PASSWORD required for login" >&2
                exit 1
            fi
            local body
            body=$(jq -nr --arg u "$OPENSUBTITLES_USERNAME" --arg p "$OPENSUBTITLES_PASSWORD" '{username:$u,password:$p}')
            api_post "$API_ROOT" "/login" "$body" "" | jq
            ;;
        download-link)
            local query="" languages="" imdb_id="" tmdb_id="" parent_imdb_id="" parent_tmdb_id="" season="" episode=""
            local file_id=""
            parse_args query languages imdb_id tmdb_id parent_imdb_id parent_tmdb_id season episode file_id "$@"
            if [[ -z "$file_id" ]]; then
                echo "Error: --file-id required" >&2
                exit 1
            fi
            local token="${OPENSUBTITLES_TOKEN:-}"
            if [[ -z "$token" ]]; then
                echo "Error: OPENSUBTITLES_TOKEN not set. Run login and pass the token." >&2
                exit 1
            fi
            local body
            body=$(jq -nr --argjson id "$file_id" '{file_id:$id}')
            api_post "$(base_url)" "/download" "$body" "$token" | jq
            ;;
        help|--help|-h)
            print_usage
            ;;
        *)
            echo "Error: Unknown command '$command'" >&2
            print_usage
            exit 1
            ;;
    esac
}

main "$@"
