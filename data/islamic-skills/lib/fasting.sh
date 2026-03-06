#!/bin/bash

# Fasting Times Module

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/prayer.sh"

# Handle Fasting Command
handle_fasting() {
    local show_today=false
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --today) show_today=true; shift ;;
            *) shift ;;
        esac
    done
    
    if [ "$show_today" = true ]; then
        local data=$(get_prayer_times)
        if [ $? -ne 0 ]; then
            echo "Could not retrieve fasting times."
            return 1
        fi
        
        local date_readable=$(json_get "$data" "data.date.readable")
        local imsak=$(json_get "$data" "data.timings.Imsak")
        local maghrib=$(json_get "$data" "data.timings.Maghrib")
        
        print_header "Fasting Schedule for $date_readable"
        print_kv "Imsak (Stop Eating)" "$imsak"
        print_kv "Maghrib (Break Fast)" "$maghrib"
        echo ""
    else
        echo "Usage: fasting --today"
    fi
}
