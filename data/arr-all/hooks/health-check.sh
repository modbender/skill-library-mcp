#!/bin/bash

# Health check for arr-all

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "$DIR/../scripts/lib/common.sh"

echo "Health Check"
echo ""

check_service() {
    local service=$1
    local name=$2
    local version_api=$3 # v3 or v1
    
    if load_config "$service"; then
        echo -n "$name: "
        
        # Check system health
        health=$(api_request "$service" "GET" "/api/$version_api/health")
        if [ $? -ne 0 ]; then
            echo "${RED}Connection Failed${NC}"
            return 1
        fi
        
        # Check for error/warning messages
        issues=$(echo "$health" | jq '[.[] | select(.type == "Error" or .type == "Warning")]')
        count=$(echo "$issues" | jq 'length')
        
        if [ "$count" -eq 0 ]; then
            echo "${GREEN}Healthy${NC}"
        else
            echo "${YELLOW}$count Issues${NC}"
            echo "$issues" | jq -r '.[] | "   - \(.type): \(.message)"'
        fi
        
        # Check Queue
        queue=$(api_request "$service" "GET" "/api/$version_api/queue")
        q_count=$(echo "$queue" | jq -r '.totalRecords // length')
        
        if [ "$q_count" -gt 0 ]; then
             echo "   Queue: $q_count items"
             echo "$queue" | jq -r '.records[]? // .[] | "      - \(.title) (\(.status))"'
        else
             echo "   Queue: 0 items"
        fi
        
    else
        echo "$name: ${YELLOW}Not configured${NC}"
    fi
    echo ""
}

check_service "radarr" "Radarr" "v3"
check_service "sonarr" "Sonarr" "v3"
check_service "lidarr" "Lidarr" "v1"
