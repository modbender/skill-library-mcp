#!/bin/bash

# HubSpot Bulk Export Script
# Usage: ./bulk-export.sh OBJECT_TYPE OUTPUT_FILE [OPTIONS]

set -euo pipefail

# Configuration
BATCH_SIZE=100
RATE_LIMIT_DELAY=0.1
DEFAULT_PROPERTIES=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TOTAL_EXPORTED=0
PAGE_COUNT=0

# Logging functions
log_info() {
    echo -e "${BLUE}INFO: $1${NC}" >&2
}

log_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}" >&2
}

log_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}" >&2
}

log_error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}

# Help function
show_help() {
    cat << EOF
HubSpot Bulk Export Script

Export HubSpot objects to CSV format with filtering and property selection.

Usage: $0 OBJECT_TYPE OUTPUT_FILE [OPTIONS]

Arguments:
  OBJECT_TYPE    HubSpot object type (contacts, companies, deals, tickets)
  OUTPUT_FILE    Path for output CSV file

Options:
  --properties PROPS     Comma-separated list of properties to export
  --filter JSON          JSON filter criteria for search API
  --batch-size N         Records per page (default: $BATCH_SIZE, max: 100)
  --delay N              Delay between requests in seconds (default: $RATE_LIMIT_DELAY)
  --format FORMAT        Output format: csv, json (default: csv)
  --all-properties       Export all available properties
  --with-associations    Include association data
  --help, -h             Show this help message

Environment Variables:
  HUBSPOT_ACCESS_TOKEN   Your HubSpot access token (required)

Examples:
  # Export all contacts with basic properties
  $0 contacts contacts.csv
  
  # Export specific properties
  $0 contacts contacts.csv --properties email,firstname,lastname,phone
  
  # Export with filters (recent leads)
  $0 contacts recent_leads.csv --filter '[{"propertyName":"createdate","operator":"GTE","value":"2024-01-01"}]'
  
  # Export companies with all properties
  $0 companies companies.csv --all-properties
  
  # Export to JSON format
  $0 deals deals.json --format json

Property Shortcuts:
  contacts:  email,firstname,lastname,phone,company,jobtitle,lifecyclestage
  companies: name,domain,industry,city,state,country,numberofemployees
  deals:     dealname,amount,dealstage,closedate,hubspot_owner_id
  tickets:   subject,content,hs_pipeline_stage,hs_ticket_priority

EOF
}

# Parse command line arguments
parse_args() {
    OBJECT_TYPE=""
    OUTPUT_FILE=""
    PROPERTIES=""
    FILTER_JSON=""
    FORMAT="csv"
    ALL_PROPERTIES=false
    WITH_ASSOCIATIONS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            --properties)
                PROPERTIES="$2"
                shift 2
                ;;
            --filter)
                FILTER_JSON="$2"
                shift 2
                ;;
            --batch-size)
                BATCH_SIZE="$2"
                if [[ ! "$BATCH_SIZE" =~ ^[0-9]+$ ]] || [ "$BATCH_SIZE" -gt 100 ] || [ "$BATCH_SIZE" -lt 1 ]; then
                    log_error "Batch size must be between 1 and 100"
                    exit 1
                fi
                shift 2
                ;;
            --delay)
                RATE_LIMIT_DELAY="$2"
                shift 2
                ;;
            --format)
                FORMAT="$2"
                if [[ ! "$FORMAT" =~ ^(csv|json)$ ]]; then
                    log_error "Format must be csv or json"
                    exit 1
                fi
                shift 2
                ;;
            --all-properties)
                ALL_PROPERTIES=true
                shift
                ;;
            --with-associations)
                WITH_ASSOCIATIONS=true
                shift
                ;;
            -*)
                log_error "Unknown option: $1"
                exit 1
                ;;
            *)
                if [ -z "$OBJECT_TYPE" ]; then
                    OBJECT_TYPE="$1"
                elif [ -z "$OUTPUT_FILE" ]; then
                    OUTPUT_FILE="$1"
                else
                    log_error "Too many arguments"
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Validate required arguments
    if [ -z "$OBJECT_TYPE" ] || [ -z "$OUTPUT_FILE" ]; then
        log_error "Object type and output file are required"
        show_help
        exit 1
    fi
    
    # Validate object type
    if [[ ! "$OBJECT_TYPE" =~ ^(contacts|companies|deals|tickets)$ ]]; then
        log_error "Unsupported object type: $OBJECT_TYPE"
        exit 1
    fi
}

# Validate environment
validate_environment() {
    if [ -z "${HUBSPOT_ACCESS_TOKEN:-}" ]; then
        log_error "HUBSPOT_ACCESS_TOKEN environment variable is required"
        exit 1
    fi
    
    # Check for required tools
    local required_tools=("curl" "jq")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Required tool not found: $tool"
            exit 1
        fi
    done
    
    # Validate filter JSON if provided
    if [ -n "$FILTER_JSON" ]; then
        if ! echo "$FILTER_JSON" | jq . >/dev/null 2>&1; then
            log_error "Invalid JSON in filter"
            exit 1
        fi
    fi
}

# Get default properties for object type
get_default_properties() {
    local object_type="$1"
    
    case "$object_type" in
        contacts)
            echo "email,firstname,lastname,phone,company,jobtitle,lifecyclestage,createdate,lastmodifieddate"
            ;;
        companies)
            echo "name,domain,industry,city,state,country,numberofemployees,annualrevenue,createdate,lastmodifieddate"
            ;;
        deals)
            echo "dealname,amount,dealstage,closedate,pipeline,hubspot_owner_id,createdate,lastmodifieddate"
            ;;
        tickets)
            echo "subject,content,hs_pipeline_stage,hs_ticket_priority,createdate,lastmodifieddate"
            ;;
        *)
            echo "createdate,lastmodifieddate"
            ;;
    esac
}

# Get all available properties for object type
get_all_properties() {
    local object_type="$1"
    
    log_info "Fetching all available properties for $object_type..."
    
    local response
    response=$(curl -s -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        "https://api.hubapi.com/crm/v3/properties/$object_type")
    
    if ! echo "$response" | jq . >/dev/null 2>&1; then
        log_error "Failed to fetch properties"
        exit 1
    fi
    
    # Extract property names
    echo "$response" | jq -r '.results[].name' | tr '\n' ',' | sed 's/,$//'
}

# Build API endpoint URL
build_api_url() {
    local object_type="$1"
    local properties="$2"
    local after="$3"
    
    local base_url="https://api.hubapi.com/crm/v3/objects/$object_type"
    local params="limit=$BATCH_SIZE"
    
    if [ -n "$properties" ]; then
        params="$params&properties=$properties"
    fi
    
    if [ -n "$after" ]; then
        params="$params&after=$after"
    fi
    
    if [ "$WITH_ASSOCIATIONS" = true ]; then
        case "$object_type" in
            contacts) params="$params&associations=companies,deals" ;;
            companies) params="$params&associations=contacts,deals" ;;
            deals) params="$params&associations=contacts,companies" ;;
            tickets) params="$params&associations=contacts,companies" ;;
        esac
    fi
    
    echo "$base_url?$params"
}

# Build search API payload
build_search_payload() {
    local object_type="$1"
    local properties="$2"
    local filters="$3"
    local after="$4"
    
    local payload="{"
    payload="$payload\"limit\":$BATCH_SIZE"
    
    if [ -n "$properties" ]; then
        # Convert comma-separated to JSON array
        local props_array
        props_array=$(echo "$properties" | sed 's/,/","/g' | sed 's/^/["/' | sed 's/$/"]/')
        payload="$payload,\"properties\":$props_array"
    fi
    
    if [ -n "$filters" ]; then
        payload="$payload,\"filters\":$filters"
    fi
    
    if [ -n "$after" ]; then
        payload="$payload,\"after\":\"$after\""
    fi
    
    if [ "$WITH_ASSOCIATIONS" = true ]; then
        case "$object_type" in
            contacts) payload="$payload,\"associations\":[\"companies\",\"deals\"]" ;;
            companies) payload="$payload,\"associations\":[\"contacts\",\"deals\"]" ;;
            deals) payload="$payload,\"associations\":[\"contacts\",\"companies\"]" ;;
            tickets) payload="$payload,\"associations\":[\"contacts\",\"companies\"]" ;;
        esac
    fi
    
    payload="$payload}"
    echo "$payload"
}

# Initialize output file
init_output_file() {
    local output_file="$1"
    local format="$2"
    local properties="$3"
    
    # Create directory if it doesn't exist
    local dir
    dir=$(dirname "$output_file")
    mkdir -p "$dir"
    
    case "$format" in
        csv)
            # Create CSV header
            local header
            if [ -n "$properties" ]; then
                header=$(echo "$properties" | sed 's/,/,/g')
            else
                header="id,properties"
            fi
            echo "$header" > "$output_file"
            ;;
        json)
            # Start JSON array
            echo "[" > "$output_file"
            ;;
    esac
}

# Convert JSON record to CSV row
json_to_csv() {
    local json_record="$1"
    local properties="$2"
    
    if [ -n "$properties" ]; then
        # Extract specific properties in order
        local values=""
        IFS=',' read -ra PROPS <<< "$properties"
        for prop in "${PROPS[@]}"; do
            local value
            value=$(echo "$json_record" | jq -r ".properties.${prop} // \"\"")
            # Escape commas and quotes for CSV
            value=$(echo "$value" | sed 's/"/""/g')
            if [[ "$value" == *","* ]] || [[ "$value" == *'"'* ]]; then
                value="\"$value\""
            fi
            
            if [ -z "$values" ]; then
                values="$value"
            else
                values="$values,$value"
            fi
        done
        echo "$values"
    else
        # Fallback: just export ID and all properties as JSON
        local id
        local props
        id=$(echo "$json_record" | jq -r '.id')
        props=$(echo "$json_record" | jq -c '.properties')
        echo "$id,\"$props\""
    fi
}

# Process a page of results
process_page() {
    local object_type="$1"
    local response="$2"
    local output_file="$3"
    local format="$4"
    local properties="$5"
    
    local results
    results=$(echo "$response" | jq -r '.results')
    
    local count
    count=$(echo "$results" | jq '. | length')
    
    if [ "$count" -eq 0 ]; then
        return 0
    fi
    
    case "$format" in
        csv)
            echo "$results" | jq -c '.[]' | while IFS= read -r record; do
                local csv_row
                csv_row=$(json_to_csv "$record" "$properties")
                echo "$csv_row" >> "$output_file"
            done
            ;;
        json)
            # Add records to JSON array (with comma separation)
            if [ "$PAGE_COUNT" -gt 1 ]; then
                echo "," >> "$output_file"
            fi
            echo "$results" | jq -c '.[]' | while IFS= read -r record; do
                if [ "$TOTAL_EXPORTED" -gt 0 ]; then
                    echo "," >> "$output_file"
                fi
                echo "$record" >> "$output_file"
            done
            ;;
    esac
    
    TOTAL_EXPORTED=$((TOTAL_EXPORTED + count))
    log_info "Exported $count records (Total: $TOTAL_EXPORTED)"
}

# Main export function
export_data() {
    local object_type="$1"
    local output_file="$2"
    local format="$3"
    
    # Determine properties to export
    local properties="$PROPERTIES"
    if [ "$ALL_PROPERTIES" = true ]; then
        properties=$(get_all_properties "$object_type")
        log_info "Using all available properties"
    elif [ -z "$properties" ]; then
        properties=$(get_default_properties "$object_type")
        log_info "Using default properties for $object_type"
    fi
    
    log_info "Properties: $properties"
    log_info "Starting export to $output_file"
    
    # Initialize output file
    init_output_file "$output_file" "$format" "$properties"
    
    local after=""
    PAGE_COUNT=0
    
    while true; do
        PAGE_COUNT=$((PAGE_COUNT + 1))
        log_info "Fetching page $PAGE_COUNT..."
        
        local response
        if [ -n "$FILTER_JSON" ]; then
            # Use search API with filters
            local search_payload
            search_payload=$(build_search_payload "$object_type" "$properties" "$FILTER_JSON" "$after")
            
            response=$(curl -s -X POST \
                "https://api.hubapi.com/crm/v3/objects/$object_type/search" \
                -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
                -H "Content-Type: application/json" \
                -d "$search_payload")
                
            # Rate limit for search API (4 req/sec)
            sleep 0.25
        else
            # Use regular list API
            local api_url
            api_url=$(build_api_url "$object_type" "$properties" "$after")
            
            response=$(curl -s -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" "$api_url")
            
            # Standard rate limiting
            sleep "$RATE_LIMIT_DELAY"
        fi
        
        # Check for API errors
        if ! echo "$response" | jq . >/dev/null 2>&1; then
            log_error "Invalid API response"
            exit 1
        fi
        
        local status
        status=$(echo "$response" | jq -r '.status // "success"')
        if [ "$status" = "error" ]; then
            local message
            message=$(echo "$response" | jq -r '.message')
            log_error "API error: $message"
            exit 1
        fi
        
        # Process the page
        process_page "$object_type" "$response" "$output_file" "$format" "$properties"
        
        # Check for next page
        after=$(echo "$response" | jq -r '.paging.next.after // empty')
        if [ -z "$after" ]; then
            break
        fi
    done
    
    # Finalize output file
    case "$format" in
        json)
            echo "]" >> "$output_file"
            ;;
    esac
    
    log_success "Export completed: $TOTAL_EXPORTED records exported to $output_file"
}

# Main function
main() {
    parse_args "$@"
    validate_environment
    
    log_info "Exporting $OBJECT_TYPE to $OUTPUT_FILE (format: $FORMAT)"
    
    export_data "$OBJECT_TYPE" "$OUTPUT_FILE" "$FORMAT"
}

# Run main function
main "$@"