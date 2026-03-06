#!/bin/bash

# Sonarr library functions

sonarr_search() {
    local query="$1"
    
    encoded_query=$(echo "$query" | jq -sRr @uri)
    response=$(api_request "sonarr" "GET" "/api/v3/series/lookup?term=$encoded_query")
    
    echo "$response" | jq -r '
      to_entries | .[:10] | .[] | 
      "\(.key + 1). [\(.value.title) (\(.value.year))](https://thetvdb.com/?tab=series&id=\(.value.tvdbId))"
    '
}

sonarr_exists() {
    local tvdbId="$1"
    response=$(api_request "sonarr" "GET" "/api/v3/series?tvdbId=$tvdbId")
    
    if [ "$response" = "[]" ]; then
        return 1
    else
        echo "$response" | jq -r '.[0] | "Found: \(.title) (\(.year)) - Seasons: \(.statistics.seasonCount) - Status: \(.status)"'
        return 0
    fi
}

sonarr_add() {
    local tvdbId="$1"
    local no_search="$2" # "true" or "false"
    local monitor_type="$3" # all, future, missing, existing, pilot, firstSeason, latest, monitorSpec (e.g. seasons:1,2)
    
    # Get series details
    # lookup by tvdbId needs "tvdb:" prefix for lookup endpoint usually, or just term
    series=$(api_request "sonarr" "GET" "/api/v3/series/lookup?term=tvdb:$tvdbId" | jq '.[0]')
    
    if [ "$series" = "null" ] || [ -z "$series" ]; then
        log_error "Show not found with TVDB ID: $tvdbId"
        return 1
    fi
    
    # Get root folder
    rootFolder=$(api_request "sonarr" "GET" "/api/v3/rootfolder" | jq -r '.[0].path')
    
    # Get default quality profile
    if [ -n "$DEFAULT_PROFILE" ]; then
        qualityProfile="$DEFAULT_PROFILE"
    else
        qualityProfile=$(api_request "sonarr" "GET" "/api/v3/qualityprofile" | jq -r '.[0].id')
    fi
    
    searchFlag="true"
    if [ "$no_search" = "true" ]; then searchFlag="false"; fi
    
    # Determine monitor status
    # Default is "all"
    monitor="all"
    if [ -n "$monitor_type" ]; then
        monitor="$monitor_type"
    elif [ -n "$DEFAULT_MONITOR" ]; then
        monitor="$DEFAULT_MONITOR"
    fi
    
    # TODO: Handle "seasons:1,2" complexity if we want to get fancy with specific season monitoring
    # For now, let's pass the monitor value directly if it's a standard one. 
    # Valid values for addOptions.monitor: all, future, missing, existing, pilot, firstSeason, latest, none
    
    # Construct payload
    payload=$(echo "$series" | jq --arg rf "$rootFolder" --argjson qp "$qualityProfile" --argjson search "$searchFlag" --arg mon "$monitor" '
      . + {
        rootFolderPath: $rf,
        qualityProfileId: $qp,
        monitored: true,
        seasonFolder: true,
        addOptions: {
          monitor: $mon,
          searchForMissingEpisodes: $search,
          searchForCutoffUnmetEpisodes: false
        }
      }
    ')
    
    result=$(api_request "sonarr" "POST" "/api/v3/series" "$payload")
    
    if echo "$result" | jq -e '.id' > /dev/null 2>&1; then
        title=$(echo "$result" | jq -r '.title')
        year=$(echo "$result" | jq -r '.year')
        seasons=$(echo "$result" | jq -r '.statistics.seasonCount // "?"')
        log_success "Added: $title ($year) - $seasons seasons"
        echo "   Path: $rootFolder/$title"
        echo "   Monitor: $monitor"
        if [ "$searchFlag" = "true" ]; then
            echo "   Search started"
        fi
    else
        log_error "Failed to add show"
        echo "$result" | jq -r '.message // .'
    fi
}

sonarr_remove() {
    local tvdbId="$1"
    local delete_files="$2"
    
    # Get ID
    series=$(api_request "sonarr" "GET" "/api/v3/series?tvdbId=$tvdbId")
    
    if [ "$series" = "[]" ]; then
        log_error "Show not found in library"
        return 1
    fi
    
    seriesId=$(echo "$series" | jq -r '.[0].id')
    title=$(echo "$series" | jq -r '.[0].title')
    
    api_request "sonarr" "DELETE" "/api/v3/series/$seriesId?deleteFiles=$delete_files"
    
    if [ "$delete_files" = "true" ]; then
        log_success "Removed: $title (files deleted)"
    else
        log_success "Removed: $title (files kept)"
    fi
}

sonarr_config() {
    echo "=== Sonarr Config ==="
    echo "Root Folders:"
    api_request "sonarr" "GET" "/api/v3/rootfolder" | jq -r '.[] | "  - \(.path) (Free: \(.freeSpace / 1073741824 | floor) GB)"'
    
    echo "Quality Profiles:"
    api_request "sonarr" "GET" "/api/v3/qualityprofile" | jq -r '.[] | "  - \(.id): \(.name)"'
}

sonarr_seasons() {
    local tvdbId="$1"
    
    series=$(api_request "sonarr" "GET" "/api/v3/series?tvdbId=$tvdbId")
    if [ "$series" = "[]" ]; then
        log_error "Show not found in library"
        return 1
    fi
    
    echo "Seasons for $(echo "$series" | jq -r '.[0].title'):"
    echo "$series" | jq -r '.[0].seasons[] | "  - Season \(.seasonNumber): \(.monitored | if . then "Requesting" else "Ignored" end) (Status: \(.statistics.episodeFileCount)/\(.statistics.totalEpisodeCount) eps)"'
}

sonarr_monitor_season() {
    local tvdbId="$1"
    local season="$2"
    local monitored="$3" # true/false
    
    series=$(api_request "sonarr" "GET" "/api/v3/series?tvdbId=$tvdbId")
    if [ "$series" = "[]" ]; then
        log_error "Show not found in library"
        return 1
    fi
    
    seriesId=$(echo "$series" | jq -r '.[0].id')
    
    # To update a season, we need to update the series object
    # This involves PUT to /api/v3/series/{id} with the modified seasons array
    
    # jq magic to toggle the monitored flag for the specific season
    updatedSeries=$(echo "$series" | jq --argjson sn "$season" --argjson mon "$monitored" '
      .[0] | .seasons |= map(if .seasonNumber == $sn then .monitored = $mon else . end)
    ')
    
    result=$(api_request "sonarr" "PUT" "/api/v3/series/$seriesId" "$updatedSeries")
    
    if echo "$result" | jq -e '.id' > /dev/null 2>&1; then
        state="Monitored"
        if [ "$monitored" = "false" ]; then state="Unmonitored"; fi
        log_success "Season $season is now: $state"
    else
        log_error "Failed to update season."
    fi
}
