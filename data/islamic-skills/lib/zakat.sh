#!/bin/bash

# Zakat Module

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.sh"
source "${SCRIPT_DIR}/api.sh"
source "${SCRIPT_DIR}/cache.sh"
source "${SCRIPT_DIR}/format.sh"

# Get Zakat Data
# Usage: get_zakat_data "currency"
get_zakat_data() {
    local currency="$1"
    load_config
    
    local api_key="$ZAKAT_API_KEY"
    if [ -z "$api_key" ]; then
        echo "Error: Missing API Key. Please get one from https://islamicapi.com/" >&2
        return 1
    fi
    
    local cache_key="zakat_${currency}_$(date +%Y-%m-%d)"
    if cache_exists "$cache_key"; then
        cache_read "$cache_key"
        return 0
    fi
    
    local url="https://islamicapi.com/api/v1/zakat-nisab?api_key=${api_key}&currency=${currency}&standard=common&unit=g"
    
    local response=$(api_call "$url")
    if [ $? -eq 0 ] && [ ! -z "$response" ]; then
        cache_write "$cache_key" "$response"
        echo "$response"
    else
        return 1
    fi
}

# Handle Zakat Command
# Usage: handle_zakat [args...]
handle_zakat() {
    load_config
    local show_nisab=false
    local currency="$ZAKAT_CURRENCY"
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --nisab) show_nisab=true; shift ;;
            --currency) currency="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    
    if [ "$show_nisab" = true ]; then
        local data=$(get_zakat_data "$currency")
        if [ $? -ne 0 ]; then
            echo "Could not retrieve Zakat data."
            return 1
        fi
        
        # Check for error in response
        local err=$(json_get "$data" "error")
        if [ ! -z "$err" ] && [ "$err" != "null" ]; then
             echo "Error: $err"
             return 1
        fi
        
        local gold_price=$(json_get "$data" "data.nisab_thresholds.gold.unit_price")
        local gold_nisab=$(json_get "$data" "data.nisab_thresholds.gold.nisab_amount")
        local silver_price=$(json_get "$data" "data.nisab_thresholds.silver.unit_price")
        local silver_nisab=$(json_get "$data" "data.nisab_thresholds.silver.nisab_amount")
        
        # Format numbers? Pure bash printf can do basic floats
        
        print_header "Zakat Nisab (${currency})"
        printf "Gold (1g)         : %.2f\n" "$gold_price"
        printf "Gold Nisab (85g)  : %.2f\n" "$gold_nisab"
        print_separator
        printf "Silver (1g)       : %.2f\n" "$silver_price"
        printf "Silver Nisab (595g): %.2f\n" "$silver_nisab"
        echo ""
    else
        echo "Usage: zakat --nisab [--currency IDR]"
    fi
}
