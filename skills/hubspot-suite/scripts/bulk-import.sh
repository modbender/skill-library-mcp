#!/bin/bash

# HubSpot Bulk Import Script
# Usage: ./bulk-import.sh OBJECT_TYPE CSV_FILE [OPTIONS]

set -euo pipefail

# Configuration
BATCH_SIZE=100
RATE_LIMIT_DELAY=0.1
MAX_RETRIES=3

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TOTAL_RECORDS=0
SUCCESS_COUNT=0
ERROR_COUNT=0
SKIP_COUNT=0

# Logging functions
log_info() {
    echo -e "${BLUE}INFO: $1${NC}"
}

log_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

log_error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}

# Help function
show_help() {
    cat << EOF
HubSpot Bulk Import Script

Import CSV data into HubSpot objects using batch API operations.

Usage: $0 OBJECT_TYPE CSV_FILE [OPTIONS]

Arguments:
  OBJECT_TYPE    HubSpot object type (contacts, companies, deals, tickets)
  CSV_FILE       Path to CSV file to import

Options:
  --batch-size N     Records per batch (default: $BATCH_SIZE, max: 100)
  --delay N          Delay between batches in seconds (default: $RATE_LIMIT_DELAY)
  --dry-run          Validate data without importing
  --skip-duplicates  Skip records that already exist
  --upsert           Update existing records instead of creating duplicates
  --help, -h         Show this help message

Environment Variables:
  HUBSPOT_ACCESS_TOKEN   Your HubSpot access token (required)

Examples:
  $0 contacts contacts.csv
  $0 companies companies.csv --batch-size 50 --delay 0.5
  $0 deals deals.csv --dry-run
  $0 contacts leads.csv --upsert

CSV Format:
  - First row must contain property names (internal HubSpot names)
  - Email required for contacts
  - Domain recommended for companies
  
EOF
}

# Parse command line arguments
parse_args() {
    OBJECT_TYPE=""
    CSV_FILE=""
    DRY_RUN=false
    SKIP_DUPLICATES=false
    UPSERT=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
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
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --skip-duplicates)
                SKIP_DUPLICATES=true
                shift
                ;;
            --upsert)
                UPSERT=true
                shift
                ;;
            -*)
                log_error "Unknown option: $1"
                exit 1
                ;;
            *)
                if [ -z "$OBJECT_TYPE" ]; then
                    OBJECT_TYPE="$1"
                elif [ -z "$CSV_FILE" ]; then
                    CSV_FILE="$1"
                else
                    log_error "Too many arguments"
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Validate required arguments
    if [ -z "$OBJECT_TYPE" ] || [ -z "$CSV_FILE" ]; then
        log_error "Object type and CSV file are required"
        show_help
        exit 1
    fi
    
    # Validate object type
    if [[ ! "$OBJECT_TYPE" =~ ^(contacts|companies|deals|tickets|custom)$ ]]; then
        log_error "Unsupported object type: $OBJECT_TYPE"
        log_error "Supported types: contacts, companies, deals, tickets, custom"
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
}

# Validate CSV file
validate_csv() {
    local csv_file="$1"
    
    if [ ! -f "$csv_file" ]; then
        log_error "CSV file not found: $csv_file"
        exit 1
    fi
    
    if [ ! -r "$csv_file" ]; then
        log_error "Cannot read CSV file: $csv_file"
        exit 1
    fi
    
    # Check if file is empty
    if [ ! -s "$csv_file" ]; then
        log_error "CSV file is empty: $csv_file"
        exit 1
    fi
    
    # Count total records (excluding header)
    TOTAL_RECORDS=$(tail -n +2 "$csv_file" | wc -l)
    
    if [ "$TOTAL_RECORDS" -eq 0 ]; then
        log_error "No data rows found in CSV file"
        exit 1
    fi
    
    log_info "Found $TOTAL_RECORDS records to import"
    
    # Validate headers for specific object types
    local header
    header=$(head -n 1 "$csv_file")
    
    case "$OBJECT_TYPE" in
        contacts)
            if [[ "$header" != *"email"* ]]; then
                log_error "Email column is required for contacts"
                exit 1
            fi
            ;;
        companies)
            if [[ "$header" != *"name"* ]]; then
                log_warning "Name column is recommended for companies"
            fi
            ;;
        deals)
            if [[ "$header" != *"dealname"* ]]; then
                log_warning "dealname column is recommended for deals"
            fi
            ;;
    esac
}

# Convert CSV row to JSON
csv_to_json() {
    local headers="$1"
    local values="$2"
    
    # Split headers and values into arrays
    IFS=',' read -ra HEADERS <<< "$headers"
    IFS=',' read -ra VALUES <<< "$values"
    
    # Build JSON properties object
    local json_properties="{"
    local first=true
    
    for i in "${!HEADERS[@]}"; do
        local header="${HEADERS[i]}"
        local value="${VALUES[i]:-}"
        
        # Skip empty values
        if [ -z "$value" ]; then
            continue
        fi
        
        # Add comma separator
        if [ "$first" = true ]; then
            first=false
        else
            json_properties+=","
        fi
        
        # Clean up header and value
        header=$(echo "$header" | sed 's/^"//; s/"$//')
        value=$(echo "$value" | sed 's/^"//; s/"$//')
        
        # Escape JSON special characters
        value=$(echo "$value" | sed 's/\\/\\\\/g; s/"/\\"/g')
        
        json_properties+="\"$header\":\"$value\""
    done
    
    json_properties+="}"
    
    echo "{\"properties\":$json_properties}"
}

# Check if record exists (for upsert/skip duplicates)
record_exists() {
    local object_type="$1"
    local identifier_property="$2"
    local identifier_value="$3"
    
    local search_payload="{
        \"filters\": [{
            \"propertyName\": \"$identifier_property\",
            \"operator\": \"EQ\",
            \"value\": \"$identifier_value\"
        }],
        \"limit\": 1
    }"
    
    local response
    response=$(curl -s -X POST \
        "https://api.hubapi.com/crm/v3/objects/$object_type/search" \
        -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$search_payload")
    
    local total
    total=$(echo "$response" | jq -r '.total // 0')
    
    if [ "$total" -gt 0 ]; then
        echo "$response" | jq -r '.results[0].id'
        return 0
    else
        return 1
    fi
}

# Process a single batch
process_batch() {
    local object_type="$1"
    local batch_data="$2"
    local batch_num="$3"
    
    if [ "$DRY_RUN" = true ]; then
        log_info "DRY RUN: Batch $batch_num - would process $(echo "$batch_data" | jq '. | length') records"
        return 0
    fi
    
    log_info "Processing batch $batch_num ($(echo "$batch_data" | jq '. | length') records)..."
    
    # Create batch payload
    local batch_payload="{\"inputs\":$batch_data}"
    
    # Make API request
    local response
    local http_code
    
    response=$(curl -s -w "%{http_code}" -X POST \
        "https://api.hubapi.com/crm/v3/objects/$object_type/batch/create" \
        -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$batch_payload")
    
    http_code="${response: -3}"
    local body="${response%???}"
    
    case $http_code in
        201|200)
            local created_count
            created_count=$(echo "$body" | jq -r '.results | length')
            log_success "Batch $batch_num: Created $created_count records"
            SUCCESS_COUNT=$((SUCCESS_COUNT + created_count))
            ;;
        400)
            log_error "Batch $batch_num failed: Bad request"
            echo "$body" | jq -r '.message // .error' >&2
            ERROR_COUNT=$((ERROR_COUNT + BATCH_SIZE))
            ;;
        429)
            log_warning "Rate limited - waiting and retrying..."
            sleep 10
            process_batch "$object_type" "$batch_data" "$batch_num"
            return
            ;;
        *)
            log_error "Batch $batch_num failed with HTTP $http_code"
            echo "$body" >&2
            ERROR_COUNT=$((ERROR_COUNT + BATCH_SIZE))
            ;;
    esac
}

# Main import function
import_data() {
    local csv_file="$1"
    local object_type="$2"
    
    log_info "Starting import of $csv_file into $object_type"
    
    # Read CSV header
    local header
    header=$(head -n 1 "$csv_file")
    
    # Process records in batches
    local batch_data="[]"
    local batch_count=0
    local batch_num=1
    local line_num=1
    
    # Determine identifier property for duplicates
    local identifier_property="email"
    case "$object_type" in
        companies) identifier_property="domain" ;;
        deals) identifier_property="dealname" ;;
        tickets) identifier_property="subject" ;;
    esac
    
    # Process each data row
    tail -n +2 "$csv_file" | while IFS= read -r line; do
        line_num=$((line_num + 1))
        
        # Skip empty lines
        if [ -z "$line" ]; then
            continue
        fi
        
        # Convert to JSON
        local json_record
        if ! json_record=$(csv_to_json "$header" "$line"); then
            log_warning "Skipping invalid record on line $line_num"
            SKIP_COUNT=$((SKIP_COUNT + 1))
            continue
        fi
        
        # Check for duplicates if requested
        if [ "$SKIP_DUPLICATES" = true ] || [ "$UPSERT" = true ]; then
            local identifier_value
            identifier_value=$(echo "$json_record" | jq -r ".properties.$identifier_property")
            
            if [ "$identifier_value" != "null" ] && [ -n "$identifier_value" ]; then
                if existing_id=$(record_exists "$object_type" "$identifier_property" "$identifier_value"); then
                    if [ "$SKIP_DUPLICATES" = true ]; then
                        log_info "Skipping duplicate: $identifier_value"
                        SKIP_COUNT=$((SKIP_COUNT + 1))
                        continue
                    elif [ "$UPSERT" = true ]; then
                        # Update existing record
                        log_info "Updating existing record: $existing_id"
                        curl -s -X PATCH \
                            "https://api.hubapi.com/crm/v3/objects/$object_type/$existing_id" \
                            -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
                            -H "Content-Type: application/json" \
                            -d "$json_record" >/dev/null
                        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
                        continue
                    fi
                fi
            fi
        fi
        
        # Add to batch
        if [ "$batch_count" -eq 0 ]; then
            batch_data="[$json_record"
        else
            batch_data="$batch_data,$json_record"
        fi
        
        batch_count=$((batch_count + 1))
        
        # Process batch when full
        if [ "$batch_count" -eq "$BATCH_SIZE" ]; then
            batch_data="$batch_data]"
            process_batch "$object_type" "$batch_data" "$batch_num"
            
            # Reset for next batch
            batch_data="[]"
            batch_count=0
            batch_num=$((batch_num + 1))
            
            # Rate limiting delay
            sleep "$RATE_LIMIT_DELAY"
        fi
    done
    
    # Process remaining records
    if [ "$batch_count" -gt 0 ]; then
        batch_data="$batch_data]"
        process_batch "$object_type" "$batch_data" "$batch_num"
    fi
}

# Print final summary
print_summary() {
    echo
    log_info "=== Import Summary ==="
    log_info "Total records: $TOTAL_RECORDS"
    log_success "Successfully imported: $SUCCESS_COUNT"
    log_error "Errors: $ERROR_COUNT"
    log_warning "Skipped: $SKIP_COUNT"
    
    if [ "$ERROR_COUNT" -eq 0 ]; then
        log_success "Import completed successfully!"
    else
        log_warning "Import completed with errors"
        exit 1
    fi
}

# Main function
main() {
    parse_args "$@"
    validate_environment
    validate_csv "$CSV_FILE"
    
    if [ "$DRY_RUN" = true ]; then
        log_info "DRY RUN MODE - No data will be imported"
    fi
    
    import_data "$CSV_FILE" "$OBJECT_TYPE"
    print_summary
}

# Run main function
main "$@"