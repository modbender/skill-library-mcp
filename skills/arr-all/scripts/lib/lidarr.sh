#!/bin/bash

# Lidarr library functions

lidarr_search() {
    local query="$1"
    
    encoded_query=$(echo "$query" | jq -sRr @uri)
    response=$(api_request "lidarr" "GET" "/api/v1/artist/lookup?term=$encoded_query")
    
    echo "$response" | jq -r '
      to_entries | .[] | 
      "\(.key + 1). [\(.value.artistName)](https://musicbrainz.org/artist/\(.value.foreignArtistId))" +
      (if .value.disambiguation then " (\(.value.disambiguation))" else "" end) +
      " - ID: \(.value.foreignArtistId)"
    '
}

lidarr_exists() {
    local artistId="$1"
    
    # lidarr "exists" check usually checks by foreignArtistId (MBID)
    # first get all artists? No, that's heavy.
    # use /api/v1/artist endpoint? It returns all artists.
    # There is no direct lookup by foreignId easily without fetching all or using lookups.
    
    # Optimally: fetch all artists is standard for Lidarr scripts unfortunately as there's no efficient "get by foreign id" 
    # except via lookup, but lookup returns external data, not internal library state.
    
    # Actually, we can just get /api/v1/artist and filter with jq.
    
    response=$(api_request "lidarr" "GET" "/api/v1/artist")
    existing=$(echo "$response" | jq --arg fid "$artistId" '[.[] | select(.foreignArtistId == $fid)]')
    
    if [ "$existing" = "[]" ]; then
        return 1
    else
        echo "$existing" | jq -r '.[0] | "Found: \(.artistName) - Albums: \(.statistics.albumCount) - Monitored: \(.monitored)"'
        return 0
    fi
}

lidarr_add() {
    local foreignArtistId="$1"
    local no_search="$2" # "true" or "false"
    local discography="$3" # "true" or "false"
    
    # Check if already exists first
    response=$(api_request "lidarr" "GET" "/api/v1/artist")
    existingArtist=$(echo "$response" | jq --arg fid "$foreignArtistId" '[.[] | select(.foreignArtistId == $fid)] | .[0]')
    
    if [ "$existingArtist" != "null" ] && [ -n "$existingArtist" ]; then
         artistName=$(echo "$existingArtist" | jq -r '.artistName')
         log_warn "Artist already exists: $artistName"
         
         # If not monitored, monitor it?
         if [ "$(echo "$existingArtist" | jq -r '.monitored')" != "true" ]; then
              artistId=$(echo "$existingArtist" | jq -r '.id')
              updated=$(echo "$existingArtist" | jq '.monitored = true')
              api_request "lidarr" "PUT" "/api/v1/artist/$artistId" "$updated" >/dev/null
              log_success "Updated to monitored."
         fi
         return 0
    fi

    # Lookup artist
    artist=$(api_request "lidarr" "GET" "/api/v1/artist/lookup?term=$foreignArtistId" | jq --arg fid "$foreignArtistId" '[.[] | select(.foreignArtistId == $fid)] | .[0]')
    
    if [ -z "$artist" ] || [ "$artist" = "null" ]; then
        log_error "Artist not found with ID: $foreignArtistId"
        return 1
    fi
    
    # Config
    rootFolder=$(api_request "lidarr" "GET" "/api/v1/rootfolder" | jq -r '.[0].path')
    
    if [ -n "$DEFAULT_PROFILE" ]; then
        qualityProfileId="$DEFAULT_PROFILE"
    else
        qualityProfileId=$(api_request "lidarr" "GET" "/api/v1/qualityprofile" | jq -r '.[0].id')
    fi
    
    metadataProfileId="$DEFAULT_METADATA_PROFILE"
    if [ -z "$metadataProfileId" ]; then
         # Default to first one
         metadataProfileId=$(api_request "lidarr" "GET" "/api/v1/metadataprofile" | jq -r '.[0].id')
    fi
    
    # Handle discography override
    if [ "$discography" = "true" ]; then
         # Try to find "All" or "Everything" or "Discography"
         mp=$(api_request "lidarr" "GET" "/api/v1/metadataprofile" | jq -r '.[] | select(.name | test("Discography|Everything|All"; "i")) | .id' | head -1)
         if [ -n "$mp" ]; then metadataProfileId="$mp"; fi
    fi

    searchFlag="true"
    if [ "$no_search" = "true" ]; then searchFlag="false"; fi
    
    # Build payload
    payload=$(echo "$artist" | jq --arg rf "$rootFolder" --argjson qp "$qualityProfileId" --argjson mp "$metadataProfileId" --argjson search "$searchFlag" '
      . + {
        rootFolderPath: $rf,
        qualityProfileId: $qp,
        metadataProfileId: $mp,
        monitored: true,
        addOptions: {
          searchForMissingAlbums: $search
        }
      }
    ')
    
    result=$(api_request "lidarr" "POST" "/api/v1/artist" "$payload")
    
    if echo "$result" | jq -e '.id' > /dev/null 2>&1; then
        artistName=$(echo "$result" | jq -r '.artistName')
        log_success "Added: $artistName"
        if [ "$searchFlag" = "true" ]; then
             echo "   Search started"
        fi
        echo "   Use 'arr-all music albums $(echo "$result" | jq -r '.id')' to list albums."
    else
        log_error "Failed to add artist"
        echo "$result" | jq -r '.message // .'
    fi
}

lidarr_remove() {
    local artistId="$1" # This expects internal integer ID usually
    local delete_files="$2"
    
    # Wait, arr-all uses external IDs for commands usually?
    # No, existing commands usually use the ID returned from search/exists.
    # But user might pass MBID.
    
    # Check if input looks like a UUID (MBID)
    if [[ "$artistId" =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]]; then
         # Resolve to internal ID
         response=$(api_request "lidarr" "GET" "/api/v1/artist")
         artist=$(echo "$response" | jq --arg fid "$artistId" '[.[] | select(.foreignArtistId == $fid)] | .[0]')
         
         if [ "$artist" = "null" ]; then
             log_error "Artist not found in library"
             return 1
         fi
         internalId=$(echo "$artist" | jq -r '.id')
         name=$(echo "$artist" | jq -r '.artistName')
    else
         # Assume internal ID
         internalId="$artistId"
         # Verify
         artist=$(api_request "lidarr" "GET" "/api/v1/artist/$internalId")
         if [ -z "$artist" ] || [ "$artist" = "null" ]; then
             log_error "Artist not found"
             return 1
         fi
         name=$(echo "$artist" | jq -r '.artistName')
    fi
    
    api_request "lidarr" "DELETE" "/api/v1/artist/$internalId?deleteFiles=$delete_files"
    
    if [ "$delete_files" = "true" ]; then
        log_success "Removed: $name (files deleted)"
    else
        log_success "Removed: $name (files kept)"
    fi
}

lidarr_albums() {
    local artistId="$1"
    
    # Resolve MBID if needed
    if [[ "$artistId" =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]]; then
         response=$(api_request "lidarr" "GET" "/api/v1/artist")
         artist=$(echo "$response" | jq --arg fid "$artistId" '[.[] | select(.foreignArtistId == $fid)] | .[0]')
         if [ "$artist" = "null" ]; then log_error "Artist not found"; return 1; fi
         internalId=$(echo "$artist" | jq -r '.id')
    else
         internalId="$artistId"
    fi
    
    echo "=== Albums ==="
    api_request "lidarr" "GET" "/api/v1/album?artistId=$internalId" | jq -r '
      sort_by(.releaseDate) | reverse | .[] |
      "\(.id): \(.title) (\(.releaseDate | split("T")[0])) - Monitored: \(.monitored)"
    '
}

lidarr_monitor_album() {
    local albumId="$1"
    local no_search="$2"
    
    album=$(api_request "lidarr" "GET" "/api/v1/album/$albumId")
    
    if [ -z "$album" ] || [ "$album" = "null" ]; then
        log_error "Album not found"
        return 1
    fi
    
    searchFlag="true"
    if [ "$no_search" = "true" ]; then searchFlag="false"; fi
    
    # Update
    payload=$(echo "$album" | jq --argjson search "$searchFlag" '
      .monitored = true |
      .addOptions = {searchForNewAlbum: $search}
    ')
    
    res=$(api_request "lidarr" "PUT" "/api/v1/album/$albumId" "$payload")
    
    if echo "$res" | jq -e '.id' >/dev/null 2>&1; then
        title=$(echo "$res" | jq -r '.title')
        log_success "Monitoring: $title"
    else
        log_error "Failed to update album"
    fi
}

lidarr_config() {
    echo "=== Lidarr Config ==="
    echo "Root Folders:"
    api_request "lidarr" "GET" "/api/v1/rootfolder" | jq -r '.[] | "  - \(.path)"'
    echo "Quality Profiles:"
    api_request "lidarr" "GET" "/api/v1/qualityprofile" | jq -r '.[] | "  - \(.id): \(.name)"'
    echo "Metadata Profiles:"
    api_request "lidarr" "GET" "/api/v1/metadataprofile" | jq -r '.[] | "  - \(.id): \(.name)"'
}
