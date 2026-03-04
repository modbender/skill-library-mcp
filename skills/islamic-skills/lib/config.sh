#!/bin/bash

# Configuration Loader
# Handles loading config.json and generating config.bash for performance

# Define paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_JSON="${ROOT_DIR}/config.json"
CONFIG_BASH="${ROOT_DIR}/config.bash"
EXAMPLE_CONFIG="${ROOT_DIR}/config.example.json"

source "${SCRIPT_DIR}/json.sh"

# Generate bash config from JSON
generate_bash_config() {
    local json_file="$1"
    local bash_file="$2"
    
    if [ ! -f "$json_file" ]; then
        echo "Error: Config file not found at $json_file" >&2
        return 1
    fi
    
    local json_content=$(cat "$json_file")
    
    # Extract values using our json helper
    local lat=$(json_get "$json_content" "location.latitude")
    local long=$(json_get "$json_content" "location.longitude")
    local name=$(json_get "$json_content" "location.name")
    
    local method=$(json_get "$json_content" "calculation.method")
    local school=$(json_get "$json_content" "calculation.school")
    
    local zakat_curr=$(json_get "$json_content" "zakat.currency")
    local zakat_gold=$(json_get "$json_content" "zakat.gold_gram_threshold")
    local zakat_key=$(json_get "$json_content" "zakat.api_key")
    
    local quran_lang=$(json_get "$json_content" "quran_language")
    
    # Write to bash file
    cat > "$bash_file" <<EOF
# Auto-generated config - DO NOT EDIT MANUALLY
# Edit config.json instead

LOCATION_LATITUDE="${lat:- -6.2088}"
LOCATION_LONGITUDE="${long:- 106.8456}"
LOCATION_NAME="${name:-Jakarta}"

CALCULATION_METHOD="${method:-20}"
CALCULATION_SCHOOL="${school:-1}"

ZAKAT_CURRENCY="${zakat_curr:-IDR}"
ZAKAT_GOLD_THRESHOLD="${zakat_gold:-85}"
ZAKAT_API_KEY="\${ZAKAT_API_KEY:-$zakat_key}"

QURAN_LANGUAGE="${quran_lang:-id}"
EOF
}

# Load configuration
load_config() {
    # Check if config exists, copy example if not
    if [ ! -f "$CONFIG_JSON" ]; then
        if [ -f "$EXAMPLE_CONFIG" ]; then
            cp "$EXAMPLE_CONFIG" "$CONFIG_JSON"
            echo "Created config.json from example." >&2
        else
            echo "Error: No config found and no example available." >&2
            return 1
        fi
    fi
    
    # Check if we need to regenerate bash config
    # Regenerate if bash config doesn't exist OR json config is newer
    if [ ! -f "$CONFIG_BASH" ] || [ "$CONFIG_JSON" -nt "$CONFIG_BASH" ]; then
        generate_bash_config "$CONFIG_JSON" "$CONFIG_BASH"
    fi
    
    # Source the bash config
    if [ -f "$CONFIG_BASH" ]; then
        source "$CONFIG_BASH"
    else
        echo "Error: Failed to load configuration." >&2
        return 1
    fi
}
