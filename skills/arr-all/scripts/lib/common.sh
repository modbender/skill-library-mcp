#!/bin/bash

# Common utilities for arr-all

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}INFO:${NC} $1"; }
log_success() { echo -e "${GREEN}SUCCESS:${NC} $1"; }
log_warn() { echo -e "${YELLOW}WARNING:${NC} $1"; }
log_error() { echo -e "${RED}ERROR:${NC} $1" >&2; }

# check dependencies
check_deps() {
    for cmd in curl jq; do
        if ! command -v $cmd &> /dev/null; then
            log_error "$cmd is required but not installed."
            exit 1
        fi
    done
}

# Load config for a specific service (radarr, sonarr, lidarr)
# Returns 0 if loaded, 1 if not configured
load_config() {
    local service=$1
    local unified_config="$HOME/.openclaw/credentials/arr-all/config.json"
    local legacy_config="$HOME/.openclaw/credentials/$service/config.json"

    # Try unified config first
    if [[ -f "$unified_config" ]]; then
        if jq -e ".$service" "$unified_config" >/dev/null 2>&1; then
            URL=$(jq -r ".$service.url" "$unified_config")
            API_KEY=$(jq -r ".$service.apiKey" "$unified_config")
            # Load optional defaults
            DEFAULT_PROFILE=$(jq -r ".$service.defaultQualityProfile // empty" "$unified_config")
             # Service specific defaults
            if [[ "$service" == "sonarr" ]]; then
                 DEFAULT_SERIES_TYPE=$(jq -r ".$service.defaultSeriesType // \"standard\"" "$unified_config")
                 DEFAULT_MONITOR=$(jq -r ".$service.defaultMonitor // \"all\"" "$unified_config")
            fi
            if [[ "$service" == "lidarr" ]]; then
                 DEFAULT_METADATA_PROFILE=$(jq -r ".$service.defaultMetadataProfile // empty" "$unified_config")
            fi
            return 0
        fi
    fi

    # Fallback to legacy config
    if [[ -f "$legacy_config" ]]; then
        URL=$(jq -r ".url" "$legacy_config")
        API_KEY=$(jq -r ".apiKey" "$legacy_config")
         DEFAULT_PROFILE=$(jq -r ".defaultQualityProfile // empty" "$legacy_config")
         if [[ "$service" == "sonarr" ]]; then
             DEFAULT_SERIES_TYPE=$(jq -r ".defaultSeriesType // \"standard\"" "$legacy_config")
             DEFAULT_MONITOR=$(jq -r ".defaultMonitor // \"all\"" "$legacy_config")
         fi
         if [[ "$service" == "lidarr" ]]; then
              DEFAULT_METADATA_PROFILE=$(jq -r ".defaultMetadataProfile // empty" "$legacy_config")
         fi
        return 0
    fi

    return 1
}

# Generic API request
# Usage: api_request <service> <method> <endpoint> [data]
api_request() {
    local service=$1
    local method=$2
    local endpoint=$3
    local data=$4

    # Ensure config is loaded for the service call
    if [ -z "$URL" ] || [ -z "$API_KEY" ]; then
         if ! load_config "$service"; then
             log_error "$service is not configured."
             return 1
         fi
    fi

    # Safe curl command construction
    if [[ -n "$data" ]]; then
        curl -s -X "$method" "$URL$endpoint" -H "X-Api-Key: $API_KEY" -H "Content-Type: application/json" -d "$data"
    else
        curl -s -X "$method" "$URL$endpoint" -H "X-Api-Key: $API_KEY"
    fi
}
