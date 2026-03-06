#!/bin/bash

# Scheduler Module (Cron Generation)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/prayer.sh"

# Handle Sync Command
handle_sync() {
    # We need prayer times for today
    local data=$(get_prayer_times)
    
    if [ -z "$data" ]; then
        echo "Sync failed: No data."
        return 1
    fi
    
    local today_str=$(date "+%Y-%m-%d")
    
    # Prayers to schedule
    local prayers=("Fajr" "Dhuhr" "Asr" "Maghrib" "Isha")
    
    for prayer in "${prayers[@]}"; do
        local time_str=$(json_get "$data" "data.timings.$prayer")
        # Remove (WIB) etc
        time_str=$(echo "$time_str" | cut -d' ' -f1)
        
        # Check if time is in future
        local prayer_ts=$(date -d "$today_str $time_str" +%s 2>/dev/null)
        local now_ts=$(date +%s)
        
        # If date parsing failed (Alpine busybox date is limited), try another way or skip check
        # Busybox date often doesn't support -d with complex formats.
        # But we format today_str as YYYY-MM-DD and time_str is HH:MM, which usually works.
        
        if [ -z "$prayer_ts" ]; then
            # Try without date part if only time supported? No, busybox supports -d
            # If failed, assume schedule it anyway
            prayer_ts=$((now_ts + 100)) # dummy
        fi
        
        if [ "$prayer_ts" -gt "$now_ts" ]; then
            # Construct JSON job object
            # We construct it manually string building to avoid heavy dependencies
            local iso_time="${today_str}T${time_str}:00"
            
            # Simple JSON construction
            local prayer_lower=$(echo "$prayer" | tr '[:upper:]' '[:lower:]')
            local job="{\"name\": \"prayer-${prayer_lower}-${today_str}\", \"schedule\": {\"kind\": \"at\", \"at\": \"${iso_time}\"}, \"payload\": {\"kind\": \"systemEvent\", \"text\": \"It is time for ${prayer} prayer.\"}, \"sessionTarget\": \"main\"}"
            
            echo "CRON_ADD: $job"
        fi
    done
    
    echo "Sync complete. Parse lines starting with CRON_ADD to schedule."
}
