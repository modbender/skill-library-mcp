#!/bin/bash

set -euo pipefail

TRAKT_API_ROOT="https://api.trakt.tv"

print_usage() {
    cat <<EOF
Usage: trakt-api.sh <command> [options]

Commands:
    watching                 Get currently watching (movie or episode)
    recent [limit]           Recent episode history (default: 10, max: 100)
    watched-shows            List recently watched shows
    stats                    User stats summary
    profile                  User profile info
    playback <type> <start_at> <end_at>   Playback progress (requires token)
    device-code             Start device OAuth (gives user_code)
    device-token <device_code>  Exchange device code for access token

Environment Variables Required:
    TRAKT_CLIENT_ID          Your Trakt API client id
    TRAKT_USERNAME           Your Trakt username or user slug

Optional (for playback):
    TRAKT_ACCESS_TOKEN       OAuth access token (Bearer)
    TRAKT_CLIENT_SECRET      OAuth client secret (required for device token exchange)

Examples:
    TRAKT_CLIENT_ID=xxx TRAKT_USERNAME=user ./trakt-api.sh watching
    TRAKT_CLIENT_ID=xxx TRAKT_USERNAME=user ./trakt-api.sh recent 5
    TRAKT_CLIENT_ID=xxx TRAKT_ACCESS_TOKEN=yyy ./trakt-api.sh playback movies 2016-06-01T00:00:00.000Z 2016-07-01T23:59:59.000Z
    TRAKT_CLIENT_ID=xxx ./trakt-api.sh device-code
    TRAKT_CLIENT_ID=xxx TRAKT_CLIENT_SECRET=zzz ./trakt-api.sh device-token <device_code>
EOF
}

check_required_vars() {
    if [[ -z "${TRAKT_CLIENT_ID:-}" ]]; then
        echo "Error: TRAKT_CLIENT_ID not set" >&2
        exit 1
    fi
    if [[ -z "${TRAKT_USERNAME:-}" ]]; then
        echo "Error: TRAKT_USERNAME not set" >&2
        exit 1
    fi
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

validate_limit() {
    local limit="$1"
    if [[ ! "$limit" =~ ^[0-9]+$ ]]; then
        echo "Error: limit must be a number" >&2
        exit 1
    fi
    if (( limit < 1 || limit > 100 )); then
        echo "Error: limit must be between 1 and 100" >&2
        exit 1
    fi
}

api_get() {
    local endpoint="$1"
    shift
    local params="$*"

    local url="${TRAKT_API_ROOT}${endpoint}"
    if [[ -n "$params" ]]; then
        url+="?${params}"
    fi

    curl -s \
      -H "Content-Type: application/json" \
      -H "trakt-api-version: 2" \
      -H "trakt-api-key: ${TRAKT_CLIENT_ID}" \
      "$url"
}

api_get_auth() {
    local endpoint="$1"
    shift
    local params="$*"

    if [[ -z "${TRAKT_ACCESS_TOKEN:-}" ]]; then
        echo "Error: TRAKT_ACCESS_TOKEN not set (required for playback)" >&2
        exit 1
    fi

    local url="${TRAKT_API_ROOT}${endpoint}"
    if [[ -n "$params" ]]; then
        url+="?${params}"
    fi

    curl -s \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer ${TRAKT_ACCESS_TOKEN}" \
      -H "trakt-api-version: 2" \
      -H "trakt-api-key: ${TRAKT_CLIENT_ID}" \
      "$url"
}

oauth_post() {
    local endpoint="$1"
    local body="$2"

    curl -s \
      -H "Content-Type: application/json" \
      -H "trakt-api-version: 2" \
      -H "trakt-api-key: ${TRAKT_CLIENT_ID}" \
      -d "$body" \
      "${TRAKT_API_ROOT}${endpoint}"
}

format_watching() {
    local json="$1"
    if [[ -z "$json" || "$json" == "null" ]]; then
        echo "Nothing currently watching"
        return
    fi

    local type
    type=$(echo "$json" | jq -r '.type // empty')

    if [[ -z "$type" ]]; then
        echo "Nothing currently watching"
        return
    fi

    if [[ "$type" == "episode" ]]; then
        local show
        show=$(echo "$json" | jq -r '.show.title')
        local title
        title=$(echo "$json" | jq -r '.episode.title')
        local season
        season=$(echo "$json" | jq -r '.episode.season')
        local number
        number=$(echo "$json" | jq -r '.episode.number')
        echo "📺 Watching: ${show}"
        printf 'S%02dE%02d — %s\n' "$season" "$number" "$title"
    elif [[ "$type" == "movie" ]]; then
        local movie
        movie=$(echo "$json" | jq -r '.movie.title')
        local year
        year=$(echo "$json" | jq -r '.movie.year // empty')
        if [[ -n "$year" ]]; then
            echo "🎬 Watching: ${movie} (${year})"
        else
            echo "🎬 Watching: ${movie}"
        fi
    else
        echo "Watching: ${type}"
    fi
}

format_recent() {
    local json="$1"
    local limit="$2"

    if echo "$json" | jq -e '.error' > /dev/null 2>&1; then
        echo "Error: $(echo "$json" | jq -r '.message // .error')"
        exit 1
    fi

    echo "📺 Recent Episodes:"
    echo ""

    echo "$json" | jq -r --argjson limit "$limit" '.[:$limit][] | [.show.title, .episode.season, .episode.number, .episode.title, .watched_at] | @tsv' | \
    while IFS=$'\t' read -r show season number title watched_at; do
        printf -- "- %s S%02dE%02d — %s [%s]\n" "$show" "$season" "$number" "$title" "$watched_at"
    done
}

format_watched_shows() {
    local json="$1"

    if echo "$json" | jq -e '.error' > /dev/null 2>&1; then
        echo "Error: $(echo "$json" | jq -r '.message // .error')"
        exit 1
    fi

    echo "📺 Watched Shows (recent):"
    echo ""

    echo "$json" | jq -r '.[0:10][] | "- \(.show.title) (plays: \(.plays), last: \(.last_watched_at))"'
}

format_profile() {
    local json="$1"

    if echo "$json" | jq -e '.error' > /dev/null 2>&1; then
        echo "Error: $(echo "$json" | jq -r '.message // .error')"
        exit 1
    fi

    local name
    name=$(echo "$json" | jq -r '.name // .username')
    local username
    username=$(echo "$json" | jq -r '.username')
    local joined
    joined=$(echo "$json" | jq -r '.joined_at // ""')
    local url
    url=$(echo "$json" | jq -r '.url // ""')

    echo "🎬 Trakt Profile: ${name}"
    echo "@${username}"
    if [[ -n "$joined" ]]; then
        echo "📅 Joined: ${joined}"
    fi
    if [[ -n "$url" ]]; then
        echo "🔗 ${url}"
    fi
    return 0
}

format_stats() {
    local json="$1"

    if echo "$json" | jq -e '.error' > /dev/null 2>&1; then
        echo "Error: $(echo "$json" | jq -r '.message // .error')"
        exit 1
    fi

    local movies
    movies=$(echo "$json" | jq -r '.movies.watched // 0')
    local shows
    shows=$(echo "$json" | jq -r '.shows.watched // 0')
    local episodes
    episodes=$(echo "$json" | jq -r '.episodes.watched // 0')

    echo "🎬 Trakt Stats"
    echo "Movies watched: ${movies}"
    echo "Shows watched: ${shows}"
    echo "Episodes watched: ${episodes}"
}

main() {
    if [[ $# -lt 1 ]]; then
        print_usage
        exit 1
    fi

    local command="$1"
    shift

    case "$command" in
        watching)
            check_required_vars
            check_bins
            format_watching "$(api_get "/users/${TRAKT_USERNAME}/watching")"
            ;;
        recent)
            check_required_vars
            check_bins
            local limit="${1:-10}"
            validate_limit "$limit"
            format_recent "$(api_get "/users/${TRAKT_USERNAME}/history/episodes" "limit=${limit}")" "$limit"
            ;;
        watched-shows)
            check_required_vars
            check_bins
            format_watched_shows "$(api_get "/users/${TRAKT_USERNAME}/watched/shows")"
            ;;
        stats)
            check_required_vars
            check_bins
            format_stats "$(api_get "/users/${TRAKT_USERNAME}/stats")"
            ;;
        profile)
            check_required_vars
            check_bins
            format_profile "$(api_get "/users/${TRAKT_USERNAME}")"
            ;;
        playback)
            check_required_vars
            check_bins
            local type="${1:-}"
            local start_at="${2:-}"
            local end_at="${3:-}"
            if [[ -z "$type" || -z "$start_at" || -z "$end_at" ]]; then
                echo "Usage: trakt-api.sh playback <type> <start_at> <end_at>" >&2
                exit 1
            fi
            local params
            params="start_at=$(jq -nr --arg s "$start_at" '$s|@uri')&end_at=$(jq -nr --arg s "$end_at" '$s|@uri')"
            api_get_auth "/sync/playback/${type}" "$params" | jq
            ;;
        device-code)
            check_required_vars
            check_bins
            local body
            body=$(jq -nr --arg cid "$TRAKT_CLIENT_ID" '{client_id:$cid}')
            oauth_post "/oauth/device/code" "$body" | jq
            ;;
        device-token)
            check_required_vars
            check_bins
            local device_code="${1:-}"
            if [[ -z "$device_code" ]]; then
                echo "Usage: trakt-api.sh device-token <device_code>" >&2
                exit 1
            fi
            if [[ -z "${TRAKT_CLIENT_SECRET:-}" ]]; then
                echo "Error: TRAKT_CLIENT_SECRET not set (required for device token exchange)" >&2
                exit 1
            fi
            local body
            body=$(jq -nr --arg cid "$TRAKT_CLIENT_ID" --arg cs "$TRAKT_CLIENT_SECRET" --arg code "$device_code" '{code:$code, client_id:$cid, client_secret:$cs}')
            oauth_post "/oauth/device/token" "$body" | jq
            ;;
        help|--help|-h)
            print_usage
            ;;
        *)
            echo "Error: Unknown command '$command'" >&2
            echo "Run 'trakt-api.sh help' for usage" >&2
            exit 1
            ;;
    esac
}

main "$@"
