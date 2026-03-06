#!/bin/bash

# Caching Utility

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
CACHE_DIR="${ROOT_DIR}/cache"

# Ensure cache dir exists
if [ ! -d "$CACHE_DIR" ]; then
    mkdir -p "$CACHE_DIR"
fi

# Get path to cache file
# Usage: get_cache_path "key"
get_cache_path() {
    local key="$1"
    # Replace slashes with underscores to be safe
    local safe_key=$(echo "$key" | tr '/' '_')
    echo "${CACHE_DIR}/${safe_key}.json"
}

# Check if cache exists
# Usage: cache_exists "key"
cache_exists() {
    local key="$1"
    local file=$(get_cache_path "$key")
    if [ -f "$file" ]; then
        return 0
    else
        return 1
    fi
}

# Read from cache
# Usage: cache_read "key"
cache_read() {
    local key="$1"
    local file=$(get_cache_path "$key")
    if [ -f "$file" ]; then
        cat "$file"
    fi
}

# Write to cache
# Usage: cache_write "key" "content"
cache_write() {
    local key="$1"
    local content="$2"
    local file=$(get_cache_path "$key")
    echo "$content" > "$file"
}
