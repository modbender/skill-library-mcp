#!/bin/bash
# MoviePilot API helper script
# Usage: moviepilot_api.sh <action> [args...]
#
# Environment variables:
#   MOVIEPILOT_URL  - MoviePilot base URL (e.g., http://fnos.local:3000)
#   MOVIEPILOT_API_KEY - API Key for authentication
#   (or) MOVIEPILOT_TOKEN - Bearer token for authentication

set -euo pipefail

BASE_URL="${MOVIEPILOT_URL:?Set MOVIEPILOT_URL environment variable}"

# Build auth header
auth_header() {
    if [[ -n "${MOVIEPILOT_API_KEY:-}" ]]; then
        echo "X-API-KEY: ${MOVIEPILOT_API_KEY}"
    elif [[ -n "${MOVIEPILOT_TOKEN:-}" ]]; then
        echo "Authorization: Bearer ${MOVIEPILOT_TOKEN}"
    else
        echo "Error: Set MOVIEPILOT_API_KEY or MOVIEPILOT_TOKEN" >&2
        exit 1
    fi
}

api_get() {
    curl -s -H "$(auth_header)" "${BASE_URL}${1}"
}

api_post() {
    curl -s -H "$(auth_header)" -H "Content-Type: application/json" -X POST "${BASE_URL}${1}" -d "${2:-{}}"
}

api_put() {
    curl -s -H "$(auth_header)" -H "Content-Type: application/json" -X PUT "${BASE_URL}${1}" -d "${2:-{}}"
}

api_delete() {
    curl -s -H "$(auth_header)" -X DELETE "${BASE_URL}${1}"
}

# --- Actions ---

action="$1"; shift

case "$action" in

    # Login and get token
    # Usage: moviepilot_api.sh login <username> <password>
    login)
        username="$1"; password="$2"
        curl -s -X POST "${BASE_URL}/api/v1/login/access-token" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "username=${username}&password=${password}"
        ;;

    # Search media by title
    # Usage: moviepilot_api.sh search <title> [page]
    search)
        title="$1"; page="${2:-1}"
        api_get "/api/v1/media/search?title=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$title'))")&page=${page}"
        ;;

    # Get media details
    # Usage: moviepilot_api.sh media_detail <mediaid> [type_name]
    media_detail)
        mediaid="$1"; type_name="${2:-}"
        url="/api/v1/media/${mediaid}"
        [[ -n "$type_name" ]] && url="${url}?type_name=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$type_name'))")"
        api_get "$url"
        ;;

    # List all subscriptions
    # Usage: moviepilot_api.sh sub_list
    sub_list)
        api_get "/api/v1/subscribe/"
        ;;

    # Add subscription
    # Usage: moviepilot_api.sh sub_add '<json_body>'
    sub_add)
        api_post "/api/v1/subscribe/" "$1"
        ;;

    # Delete subscription by subscribe_id
    # Usage: moviepilot_api.sh sub_delete <subscribe_id>
    sub_delete)
        api_delete "/api/v1/subscribe/$1"
        ;;

    # Delete subscription by media ID
    # Usage: moviepilot_api.sh sub_delete_media <mediaid> [season]
    sub_delete_media)
        mediaid="$1"; season="${2:-}"
        url="/api/v1/subscribe/media/${mediaid}"
        [[ -n "$season" ]] && url="${url}?season=${season}"
        api_delete "$url"
        ;;

    # Get subscription by media ID
    # Usage: moviepilot_api.sh sub_get_media <mediaid> [season]
    sub_get_media)
        mediaid="$1"; season="${2:-}"
        url="/api/v1/subscribe/media/${mediaid}"
        [[ -n "$season" ]] && url="${url}?season=${season}"
        api_get "$url"
        ;;

    # Subscription detail by ID
    # Usage: moviepilot_api.sh sub_detail <subscribe_id>
    sub_detail)
        api_get "/api/v1/subscribe/$1"
        ;;

    # Update subscription
    # Usage: moviepilot_api.sh sub_update '<json_body>'
    sub_update)
        api_put "/api/v1/subscribe/" "$1"
        ;;

    # Refresh subscriptions (trigger search)
    # Usage: moviepilot_api.sh sub_refresh
    sub_refresh)
        api_get "/api/v1/subscribe/refresh"
        ;;

    # Subscription history
    # Usage: moviepilot_api.sh sub_history <movie|tv> [page] [count]
    sub_history)
        mtype="$1"; page="${2:-1}"; count="${3:-20}"
        api_get "/api/v1/subscribe/history/${mtype}?page=${page}&count=${count}"
        ;;

    # List active downloads
    # Usage: moviepilot_api.sh downloads [name]
    downloads)
        name="${1:-}"
        url="/api/v1/download/"
        [[ -n "$name" ]] && url="${url}?name=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$name'))")"
        api_get "$url"
        ;;

    # Get recommendations
    # Usage: moviepilot_api.sh recommend <douban_movie_hot|douban_tv_hot|tmdb_trending|tmdb_movies|tmdb_tvs|bangumi_calendar> [page]
    recommend)
        source="$1"; page="${2:-1}"
        api_get "/api/v1/recommend/${source}?page=${page}"
        ;;

    # Search torrent resources
    # Usage: moviepilot_api.sh search_resource <keyword> [page]
    search_resource)
        keyword="$1"; page="${2:-1}"
        api_get "/api/v1/search/title?keyword=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$keyword'))")&page=${page}"
        ;;

    *)
        echo "Unknown action: $action" >&2
        echo "Available actions: login, search, media_detail, sub_list, sub_add, sub_delete, sub_delete_media, sub_get_media, sub_detail, sub_update, sub_refresh, sub_history, downloads, recommend, search_resource" >&2
        exit 1
        ;;
esac
