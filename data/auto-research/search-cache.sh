#!/bin/bash
#
# search-cache.sh - Cache search results for auto-research
#
# Usage:
#   search-cache.sh get <key>     - Retrieve cached value
#   search-cache.sh set <key> <value> [ttl]  - Store value with TTL (default 86400)
#   search-cache.sh delete <key>  - Remove cached value
#   search-cache.sh clear         - Clear all research cache
#

set -euo pipefail

# Configuration
REDIS_HOST="${REDIS_HOST:-10.0.0.120}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD="${REDIS_PASSWORD:-$(python3 "$(dirname "$0")/../../tools/secrets.py" get REDIS_PASSWORD 2>/dev/null)}"
REDIS_DB="${REDIS_DB:-0}"
CACHE_PREFIX="research:"
DEFAULT_TTL=86400  # 24 hours

# File cache fallback
FILE_CACHE_DIR="/tmp/research-cache"
mkdir -p "$FILE_CACHE_DIR"

# Build Redis connection string
REDIS_CONN="-h $REDIS_HOST -p $REDIS_PORT -n $REDIS_DB"
if [[ -n "$REDIS_PASSWORD" ]]; then
    REDIS_CONN="$REDIS_CONN -a $REDIS_PASSWORD"
fi

# Check if Redis is available
redis_available() {
    redis-cli $REDIS_CONN ping >/dev/null 2>&1
}

# Cross-platform hash
hash_key() {
    if command -v sha256sum > /dev/null 2>&1; then
        echo -n "$1" | sha256sum | cut -d' ' -f1
    else
        echo -n "$1" | shasum -a 256 | cut -d' ' -f1
    fi
}

# Get cache file path for key
get_cache_file() {
    local key="$1"
    local hash=$(hash_key "$key")
    echo "$FILE_CACHE_DIR/$hash.json"
}

# Store value in cache
store_cache() {
    local key="$1"
    local value="$2"
    local ttl="${3:-$DEFAULT_TTL}"
    local full_key="${CACHE_PREFIX}${key}"
    
    # Try Redis first
    if redis_available; then
        # Redis expects TTL in seconds
        echo "$value" | redis-cli $REDIS_CONN -x SETEX "$full_key" "$ttl" >/dev/null 2>&1 && return 0
    fi
    
    # Fall back to file cache
    local cache_file=$(get_cache_file "$key")
    local expiry=$(($(date +%s) + ttl))
    
    printf '{"expiry":%d,"data":%s}\n' "$expiry" "$(echo "$value" | jq -Rs '.')" > "$cache_file"
    return 0
}

# Get value from cache
get_cache() {
    local key="$1"
    local full_key="${CACHE_PREFIX}${key}"
    
    # Try Redis first
    if redis_available; then
        local value=$(redis-cli $REDIS_CONN GET "$full_key" 2>/dev/null)
        if [[ -n "$value" && "$value" != "nil" ]]; then
            echo "$value"
            return 0
        fi
    fi
    
    # Fall back to file cache
    local cache_file=$(get_cache_file "$key")
    if [[ -f "$cache_file" ]]; then
        local now=$(date +%s)
        local expiry=$(jq -r '.expiry // 0' "$cache_file" 2>/dev/null || echo 0)
        
        if [[ "$expiry" -gt "$now" ]]; then
            jq -r '.data' "$cache_file" 2>/dev/null
            return 0
        else
            # Expired, remove it
            rm -f "$cache_file"
        fi
    fi
    
    echo "NOT_FOUND"
    return 1
}

# Delete value from cache
delete_cache() {
    local key="$1"
    local full_key="${CACHE_PREFIX}${key}"
    
    # Try Redis
    if redis_available; then
        redis-cli $REDIS_CONN DEL "$full_key" >/dev/null 2>&1
    fi
    
    # Also remove file cache
    local cache_file=$(get_cache_file "$key")
    rm -f "$cache_file"
    
    return 0
}

# Clear all research cache
clear_cache() {
    # Clear Redis keys with prefix
    if redis_available; then
        redis-cli $REDIS_CONN --eval <(echo '
            local keys = redis.call("keys", ARGV[1] .. "*")
            for i=1,#keys,5000 do
                redis.call("del", unpack(keys, i, math.min(i+4999, #keys)))
            end
            return #keys
        ') , "$CACHE_PREFIX" 2>/dev/null || true
    fi
    
    # Clear file cache
    rm -rf "$FILE_CACHE_DIR"/*
    mkdir -p "$FILE_CACHE_DIR"
    
    echo "Cache cleared"
    return 0
}

# Main command handler
case "${1:-}" in
    get)
        if [[ -z "${2:-}" ]]; then
            echo "Usage: $0 get <key>" >&2
            exit 1
        fi
        get_cache "$2"
        ;;
    set)
        if [[ -z "${2:-}" || -z "${3:-}" ]]; then
            echo "Usage: $0 set <key> <value> [ttl_seconds]" >&2
            exit 1
        fi
        store_cache "$2" "$3" "${4:-$DEFAULT_TTL}"
        ;;
    delete|del)
        if [[ -z "${2:-}" ]]; then
            echo "Usage: $0 delete <key>" >&2
            exit 1
        fi
        delete_cache "$2"
        ;;
    clear|flush)
        clear_cache
        ;;
    status)
        echo "Cache Status:"
        echo "============="
        echo "Redis Server: $REDIS_HOST:$REDIS_PORT"
        if redis_available; then
            echo "Redis Status: ✓ Connected"
            local key_count=$(redis-cli $REDIS_CONN --eval <(echo '
                return #redis.call("keys", ARGV[1] .. "*")
            ') , "$CACHE_PREFIX" 2>/dev/null || echo "unknown")
            echo "Research Keys: $key_count"
        else
            echo "Redis Status: ✗ Not available"
        fi
        echo "File Cache: $FILE_CACHE_DIR"
        file_count=$(find "$FILE_CACHE_DIR" -type f 2>/dev/null | wc -l)
        echo "Cached Files: $file_count"
        ;;
    *)
        cat <<EOF
search-cache.sh - Cache utility for auto-research

Usage:
  $0 get <key>                    Retrieve cached value
  $0 set <key> <value> [ttl]      Store value (TTL default: 86400s = 24h)
  $0 delete <key>                 Remove cached value
  $0 clear                        Clear all research cache
  $0 status                       Show cache status

Environment:
  REDIS_HOST      Redis server hostname (default: 10.0.0.120)
  REDIS_PORT      Redis server port (default: 6379)
  REDIS_PASSWORD  Redis password (from secrets.py or environment)
  REDIS_DB        Redis database number (default: 0)

The cache uses Redis if available, falling back to file-based storage.
EOF
        exit 1
        ;;
esac
