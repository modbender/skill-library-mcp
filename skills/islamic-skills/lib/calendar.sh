#!/bin/bash

# Calendar Module

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.sh"
source "${SCRIPT_DIR}/api.sh"
source "${SCRIPT_DIR}/cache.sh"
source "${SCRIPT_DIR}/format.sh"

# Get Calendar Data
# Usage: get_calendar_data "city" "country" "month" "year"
get_calendar_data() {
    local city="$1"
    local country="$2"
    local month="$3"
    local year="$4"
    
    load_config
    
    local cache_key="calendar_${city}_${month}_${year}"
    if cache_exists "$cache_key"; then
        cache_read "$cache_key"
        return 0
    fi
    
    # URL encode city/country
    local enc_city=$(url_encode "$city")
    local enc_country=$(url_encode "$country")
    
    local url="http://api.aladhan.com/v1/calendarByCity?city=${enc_city}&country=${enc_country}&method=${CALCULATION_METHOD}&school=${CALCULATION_SCHOOL}&month=${month}&year=${year}"
    
    local response=$(api_call "$url")
    if [ $? -eq 0 ] && [ ! -z "$response" ]; then
        cache_write "$cache_key" "$response"
        echo "$response"
    else
        return 1
    fi
}

# Handle Calendar Command
# Usage: handle_calendar [args...]
handle_calendar() {
    local city=""
    local country="Indonesia"
    local month=$(date "+%m")
    local year=$(date "+%Y")
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --city) city="$2"; shift 2 ;;
            --country) country="$2"; shift 2 ;;
            --month) month="$2"; shift 2 ;;
            --year) year="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    
    # If city not provided, try config
    if [ -z "$city" ]; then
        load_config
        # Extract city from "City, Country" or just "City"
        if [[ "$LOCATION_NAME" == *","* ]]; then
             city=$(echo "$LOCATION_NAME" | cut -d',' -f1 | xargs)
             country=$(echo "$LOCATION_NAME" | cut -d',' -f2 | xargs)
        else
             city="$LOCATION_NAME"
        fi
    fi
    
    if [ -z "$city" ]; then
        echo "Error: City is required. Use --city or set in config." >&2
        return 1
    fi
    
    local data=$(get_calendar_data "$city" "$country" "$month" "$year")
    if [ $? -ne 0 ]; then
        echo "Could not retrieve calendar for $city, $country."
        return 1
    fi
    
    print_header "Prayer Calendar for $month/$year - $city, $country"
    printf "%-12s %-8s %-8s %-8s %-8s %-8s\n" "Date" "Fajr" "Dhuhr" "Asr" "Maghrib" "Isha"
    print_separator
    
    if [ "$HAS_JQ" = true ]; then
        echo "$data" | jq -r '.data[] | "\(.date.gregorian.date) \(.timings.Fajr | sub(" .*";"")) \(.timings.Dhuhr | sub(" .*";"")) \(.timings.Asr | sub(" .*";"")) \(.timings.Maghrib | sub(" .*";"")) \(.timings.Isha | sub(" .*";""))"' | while read -r line; do
            read -r dt f d a m i <<< "$line"
            printf "%-12s %-8s %-8s %-8s %-8s %-8s\n" "$dt" "$f" "$d" "$a" "$m" "$i"
        done
    else
        # Fallback pure bash parsing using simple grep logic
        # This assumes standard JSON formatting from API
        local dates=$(echo "$data" | grep -o "\"date\":[[:space:]]*\"[0-9-]*\"" | cut -d'"' -f4)
        local fajrs=$(echo "$data" | grep -o "\"Fajr\":[[:space:]]*\"[^\"]*\"" | cut -d'"' -f4 | cut -d' ' -f1)
        # This naive grep fails if keys are not in reliable order or duplicated
        # Better: Iterate with loop if possible, or just warn
        
        echo "Pure bash table formatting is limited for complex data. Install jq for better output."
        # Attempt to display simplified or raw
    fi
    echo ""
}
