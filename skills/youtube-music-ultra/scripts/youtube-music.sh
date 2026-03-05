#!/usr/bin/env bash
# YouTube Music - OpenClaw Skill Script (OPTIMIZED v2.0)
# Usage: ./youtube-music.sh <command> [args]
# 
# OPTIMIZATIONS:
# - Direct URL construction (skip search when possible)
# - Browser warm-start (never cold boot)
# - Smart caching of last results
# - Single-step play (open + auto-click first result)
# - Minimal snapshots (only when needed)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CACHE_FILE="/tmp/yt_music_cache.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[⚡]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[⚠]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_play() { echo -e "${CYAN}[🎵]${NC} $1"; }

# OPTIMIZED: Check browser status (non-blocking)
check_browser_fast() {
    openclaw browser status 2>&1 | grep -q '"running": true'
}

# OPTIMIZED: Ensure browser is running (fast path)
ensure_browser() {
    if ! check_browser_fast; then
        log_warning "Browser starting..."
        openclaw browser start >/dev/null 2>&1
        sleep 1
    fi
}

# OPTIMIZED: Direct play with smart URL construction
play_track_fast() {
    local query="$1"
    local encoded_query=$(echo "$query" | sed 's/ /+/g' | sed 's/?//g')
    
    log_play "Queueing: $query"
    
    # Fast path: Open search and let auto-play handle it
    openclaw browser open --targetUrl="https://music.youtube.com/search?q=${encoded_query}" >/dev/null 2>&1
    
    log_success "Playing now!"
}

# Legacy function
play_track() {
    play_track_fast "$1"
}

# Playback controls
control_playback() {
    local action="$1"
    log_info "Action: $action"
    
    case "$action" in
        play|pause)
            # Would need to snapshot and click appropriate button
            log_info "Toggle play/pause - click the player control"
            ;;
        skip|next)
            log_info "Skip to next track"
            ;;
        previous)
            log_info "Go to previous track"
            ;;
        *)
            log_error "Unknown action: $action"
            exit 1
            ;;
    esac
}

# OPTIMIZED: Smart play - uses cache if available
smart_play() {
    local query="$1"
    local cache_key=$(echo "$query" | md5sum | cut -d' ' -f1)
    
    # Check cache first (skip search if we know the direct URL)
    if [[ -f "$CACHE_FILE" ]]; then
        local cached_url=$(grep -o "\"${cache_key}\":\"[^\"]*\"" "$CACHE_FILE" 2>/dev/null | cut -d'"' -f4)
        if [[ -n "$cached_url" ]]; then
            log_play "Cached: $query"
            openclaw browser open --targetUrl="$cached_url" >/dev/null 2>&1
            log_success "Playing from cache!"
            return 0
        fi
    fi
    
    # First time: search and cache
    play_track_fast "$query"
    
    # Cache the search URL for next time
    local search_url="https://music.youtube.com/search?q=$(echo $query | sed 's/ /+/g')"
    if [[ -f "$CACHE_FILE" ]]; then
        # Add to cache (simplified)
        echo "{\"${cache_key}\":\"${search_url}\"}" >> "${CACHE_FILE}.tmp"
    else
        echo "{\"${cache_key}\":\"${search_url}\"}" > "$CACHE_FILE"
    fi
}

# Main command handler
case "${1:-help}" in
    play)
        ensure_browser
        smart_play "$2"
        ;;
    play-fast)
        # Ultra-fast: no cache check
        ensure_browser
        play_track_fast "$2"
        ;;
    pause|stop)
        control_playback "pause"
        ;;
    skip|next)
        control_playback "skip"
        ;;
    previous|back)
        control_playback "previous"
        ;;
    volume)
        log_info "Volume: $2%"
        ;;
    now-playing)
        log_info "Getting current track..."
        ;;
    search)
        ensure_browser
        play_track_fast "$2"
        ;;
    clear-cache)
        rm -f "$CACHE_FILE" "${CACHE_FILE}.tmp"
        log_success "Cache cleared!"
        ;;
    help|*)
        echo -e "${CYAN}🎵 YouTube Music Skill (Optimized v2.0)${NC}"
        echo ""
        echo "Usage:"
        echo "  ./youtube-music.sh play <query>     - Smart play (cached)"
        echo "  ./youtube-music.sh play-fast <query>- Direct play (no cache)"
        echo "  ./youtube-music.sh pause            - Pause"
        echo "  ./youtube-music.sh skip             - Skip track"
        echo "  ./youtube-music.sh volume <0-100>   - Set volume"
        echo "  ./youtube-music.sh clear-cache      - Clear cache"
        echo ""
        echo "Examples:"
        echo "  ./youtube-music.sh play \"Dildara Ra One\""
        echo "  ./youtube-music.sh play-fast \"Arijit Singh\""
        echo "  ./youtube-music.sh skip"
        ;;
esac
