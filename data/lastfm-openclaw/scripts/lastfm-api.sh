#!/bin/bash

set -euo pipefail

LASTFM_API_ROOT="https://ws.audioscrobbler.com/2.0/"

print_usage() {
    cat <<EOF
Usage: lastfm-api.sh <command> [options]

Commands:
    now-playing, np              Get currently playing track
    top-tracks [period]          Get top tracks (period: 7day, 1month, 3month, 6month, 12month, overall)
    top-artists [period]         Get top artists
    top-albums [period]          Get top albums
    loved                        Get loved tracks
    recent [limit]               Get recent tracks (default: 10)
    profile                      Get user profile info
    love <artist> <track>        Love a track (requires session key)
    unlove <artist> <track>      Unlove a track (requires session key)

Environment Variables Required:
    LASTFM_API_KEY               Your Last.fm API key
    LASTFM_USERNAME              Your Last.fm username

Optional for Write Operations:
    LASTFM_SESSION_KEY           Session key for authenticated requests
    LASTFM_API_SECRET            API secret for signing requests

Examples:
    LASTFM_API_KEY=xxx LASTFM_USERNAME=user ./lastfm-api.sh now-playing
    LASTFM_API_KEY=xxx LASTFM_USERNAME=user ./lastfm-api.sh top-tracks 7day
    LASTFM_API_KEY=xxx LASTFM_USERNAME=user LASTFM_SESSION_KEY=yyy LASTFM_API_SECRET=zzz ./lastfm-api.sh love "Radiohead" "Creep"
EOF
}

check_required_vars() {
    if [[ -z "${LASTFM_API_KEY:-}" ]]; then
        echo "Error: LASTFM_API_KEY not set" >&2
        exit 1
    fi
    if [[ -z "${LASTFM_USERNAME:-}" ]]; then
        echo "Error: LASTFM_USERNAME not set" >&2
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

check_write_vars() {
    if [[ -z "${LASTFM_SESSION_KEY:-}" ]]; then
        echo "Error: LASTFM_SESSION_KEY not set (required for write operations)" >&2
        echo "See references/auth-guide.md for authentication instructions" >&2
        exit 1
    fi
    if [[ -z "${LASTFM_API_SECRET:-}" ]]; then
        echo "Error: LASTFM_API_SECRET not set (required for signing write requests)" >&2
        exit 1
    fi
}

url_encode() {
    local string="$1"
    jq -nr --arg str "$string" '$str | @uri'
}

generate_signature() {
    local params=("$@")
    local secret="${LASTFM_API_SECRET}"
    
    local sorted_params
    sorted_params=$(printf '%s\n' "${params[@]}" | sort)
    
    local sig_string=""
    while IFS= read -r param; do
        sig_string+="${param}"
    done <<< "$sorted_params"
    sig_string+="${secret}"
    
    echo -n "$sig_string" | md5sum | cut -d' ' -f1
}

make_request() {
    local method="$1"
    shift
    local extra_params=("$@")
    
    local url="${LASTFM_API_ROOT}?method=${method}&user=$(url_encode "$LASTFM_USERNAME")&api_key=${LASTFM_API_KEY}&format=json"
    
    for param in "${extra_params[@]}"; do
        url+="&${param}"
    done
    
    curl -s "$url"
}

make_write_request() {
    local method="$1"
    local artist="$2"
    local track="$3"
    
    check_write_vars
    
    local artist_enc
    artist_enc=$(url_encode "$artist")
    local track_enc
    track_enc=$(url_encode "$track")
    
    local api_sig
    api_sig=$(generate_signature \
        "api_key${LASTFM_API_KEY}" \
        "artist${artist}" \
        "method${method}" \
        "sk${LASTFM_SESSION_KEY}" \
        "track${track}"
    )
    
    local url="${LASTFM_API_ROOT}"
    local data="method=${method}&api_key=${LASTFM_API_KEY}&artist=${artist_enc}&track=${track_enc}&sk=${LASTFM_SESSION_KEY}&api_sig=${api_sig}&format=json"
    
    curl -s -X POST -d "$data" "$url"
}

format_now_playing() {
    local json="$1"
    
    if echo "$json" | jq -e '.error' > /dev/null 2>&1; then
        echo "Error: $(echo "$json" | jq -r '.message // .error')"
        exit 1
    fi
    
    local track
    track=$(echo "$json" | jq -r '.recenttracks.track[0]')
    
    if [[ -z "$track" || "$track" == "null" ]]; then
        echo "No recent tracks found"
        exit 0
    fi
    
    local is_now_playing
    is_now_playing=$(echo "$json" | jq -r '.recenttracks.track[0]."@attr".nowplaying // "false"')
    local artist
    artist=$(echo "$json" | jq -r '.recenttracks.track[0].artist."#text" // .recenttracks.track[0].artist')
    local name
    name=$(echo "$json" | jq -r '.recenttracks.track[0].name')
    local album
    album=$(echo "$json" | jq -r '.recenttracks.track[0].album."#text" // "Unknown Album"')
    
    if [[ "$is_now_playing" == "true" ]]; then
        echo "🎵 Now Playing:"
    else
        local date
        date=$(echo "$json" | jq -r '.recenttracks.track[0].date."#text" // "Unknown time"')
        echo "🎵 Last Played:"
    fi
    
    echo "\"${name}\" by ${artist}"
    echo "from ${album}"
    
    if [[ "$is_now_playing" != "true" ]]; then
        echo "Listened: ${date}"
    fi
}

format_top_tracks() {
    local json="$1"
    local period="${2:-overall}"
    
    if echo "$json" | jq -e '.error' > /dev/null 2>&1; then
        echo "Error: $(echo "$json" | jq -r '.message // .error')"
        exit 1
    fi
    
    echo "🎵 Top Tracks (${period}):"
    echo ""
    
    echo "$json" | jq -r '.toptracks.track[:10][] | "\(.["@attr"].rank). \"\(.name)\" by \(.artist.name) (\(.playcount) plays)"'
}

format_top_artists() {
    local json="$1"
    local period="${2:-overall}"
    
    if echo "$json" | jq -e '.error' > /dev/null 2>&1; then
        echo "Error: $(echo "$json" | jq -r '.message // .error')"
        exit 1
    fi
    
    echo "🎵 Top Artists (${period}):"
    echo ""
    
    echo "$json" | jq -r '.topartists.artist[:10][] | "\(.["@attr"].rank). \(.name) (\(.playcount) plays)"'
}

format_top_albums() {
    local json="$1"
    local period="${2:-overall}"
    
    if echo "$json" | jq -e '.error' > /dev/null 2>&1; then
        echo "Error: $(echo "$json" | jq -r '.message // .error')"
        exit 1
    fi
    
    echo "🎵 Top Albums (${period}):"
    echo ""
    
    echo "$json" | jq -r '.topalbums.album[:10][] | "\(.["@attr"].rank). \"\(.name)\" by \(.artist.name) (\(.playcount) plays)"'
}

format_loved() {
    local json="$1"
    
    if echo "$json" | jq -e '.error' > /dev/null 2>&1; then
        echo "Error: $(echo "$json" | jq -r '.message // .error')"
        exit 1
    fi
    
    local count
    count=$(echo "$json" | jq -r '.lovedtracks."@attr".total // 0')
    
    echo "🎵 Loved Tracks (${count} total):"
    echo ""
    
    if [[ "$count" == "0" ]]; then
        echo "No loved tracks found"
        return
    fi
    
    echo "$json" | jq -r '.lovedtracks.track[:10][] | "- \"\(.name)\" by \(.artist.name)"'
}

format_recent() {
    local json="$1"
    local limit="${2:-10}"
    
    if echo "$json" | jq -e '.error' > /dev/null 2>&1; then
        echo "Error: $(echo "$json" | jq -r '.message // .error')"
        exit 1
    fi
    
    echo "🎵 Recent Tracks:"
    echo ""
    
    echo "$json" | jq -r --argjson limit "$limit" '.recenttracks.track[:$limit][] | "- \"\(.name)\" by \(.artist."#text" // .artist) [\(.date."#text" // "now playing")]"'
}

format_profile() {
    local json="$1"
    
    if echo "$json" | jq -e '.error' > /dev/null 2>&1; then
        echo "Error: $(echo "$json" | jq -r '.message // .error')"
        exit 1
    fi
    
    local name
    name=$(echo "$json" | jq -r '.user.name')
    local realname
    realname=$(echo "$json" | jq -r '.user.realname // ""')
    local playcount
    playcount=$(echo "$json" | jq -r '.user.playcount')
    local country
    country=$(echo "$json" | jq -r '.user.country // "Unknown"')
    local registered
    registered=$(echo "$json" | jq -r '.user.registered."#text" // "Unknown"')
    local url
    url=$(echo "$json" | jq -r '.user.url')
    
    echo "🎵 Last.fm Profile: ${name}"
    [[ -n "$realname" && "$realname" != "null" ]] && echo "   ($realname)"
    echo ""
    echo "📊 ${playcount} total scrobbles"
    echo "🌍 ${country}"
    echo "📅 Member since: ${registered}"
    echo "🔗 ${url}"
}

format_write_response() {
    local json="$1"
    local action="$2"
    
    if echo "$json" | jq -e '.error' > /dev/null 2>&1; then
        echo "Error: $(echo "$json" | jq -r '.message // .error')"
        exit 1
    fi
    
    echo "✓ Track ${action}!"
}

validate_period() {
    local period="$1"
    local valid="7day 1month 3month 6month 12month overall"
    
    if [[ ! " $valid " =~ " $period " ]]; then
        echo "Error: Invalid period '$period'" >&2
        echo "Valid periods: 7day, 1month, 3month, 6month, 12month, overall" >&2
        exit 1
    fi
}

validate_limit() {
    local limit="$1"
    if [[ ! "$limit" =~ ^[0-9]+$ ]]; then
        echo "Error: limit must be a number" >&2
        exit 1
    fi
    if (( limit < 1 || limit > 200 )); then
        echo "Error: limit must be between 1 and 200" >&2
        exit 1
    fi
}

main() {
    if [[ $# -lt 1 ]]; then
        print_usage
        exit 1
    fi
    
    local command="$1"
    shift
    
    case "$command" in
        now-playing|np)
            check_required_vars
            check_bins
            format_now_playing "$(make_request "user.getRecentTracks" "limit=1")"
            ;;
        top-tracks)
            check_required_vars
            check_bins
            local period="${1:-overall}"
            validate_period "$period"
            format_top_tracks "$(make_request "user.getTopTracks" "period=${period}")" "$period"
            ;;
        top-artists)
            check_required_vars
            check_bins
            local period="${1:-overall}"
            validate_period "$period"
            format_top_artists "$(make_request "user.getTopArtists" "period=${period}")" "$period"
            ;;
        top-albums)
            check_required_vars
            check_bins
            local period="${1:-overall}"
            validate_period "$period"
            format_top_albums "$(make_request "user.getTopAlbums" "period=${period}")" "$period"
            ;;
        loved)
            check_required_vars
            check_bins
            format_loved "$(make_request "user.getLovedTracks")"
            ;;
        recent)
            check_required_vars
            check_bins
            local limit="${1:-10}"
            validate_limit "$limit"
            format_recent "$(make_request "user.getRecentTracks" "limit=${limit}")" "$limit"
            ;;
        profile)
            check_required_vars
            check_bins
            format_profile "$(make_request "user.getInfo")"
            ;;
        love)
            if [[ $# -lt 2 ]]; then
                echo "Usage: lastfm-api.sh love <artist> <track>" >&2
                exit 1
            fi
            check_required_vars
            check_bins
            format_write_response "$(make_write_request "track.love" "$1" "$2")" "loved"
            ;;
        unlove)
            if [[ $# -lt 2 ]]; then
                echo "Usage: lastfm-api.sh unlove <artist> <track>" >&2
                exit 1
            fi
            check_required_vars
            check_bins
            format_write_response "$(make_write_request "track.unlove" "$1" "$2")" "unloved"
            ;;
        help|--help|-h)
            print_usage
            ;;
        *)
            echo "Error: Unknown command '$command'" >&2
            echo "Run 'lastfm-api.sh help' for usage" >&2
            exit 1
            ;;
    esac
}

main "$@"
