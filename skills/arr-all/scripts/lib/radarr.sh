#!/bin/bash

# Radarr library functions

# Search validation
radarr_search() {
    local query="$1"
    
    encoded_query=$(echo "$query" | jq -sRr @uri)
    response=$(api_request "radarr" "GET" "/api/v3/movie/lookup?term=$encoded_query")
    
    echo "$response" | jq -r '
      to_entries | .[] | 
      "\(.key + 1). [\(.value.title) (\(.value.year))](https://themoviedb.org/movie/\(.value.tmdbId))" + 
      (if .value.collection.tmdbId then " [Collection: \(.value.collection.title)]" else "" end)
      + " - TMDB: \(.value.tmdbId)"
    '
}

radarr_exists() {
    local tmdbId="$1"
    response=$(api_request "radarr" "GET" "/api/v3/movie?tmdbId=$tmdbId")
    
    if [ "$response" = "[]" ]; then
        return 1
    else
        echo "$response" | jq -r '.[0] | "Found: \(.title) (\(.year)) - Monitored: \(.monitored)"'
        return 0
    fi
}

radarr_add() {
    local tmdbId="$1"
    local no_search="$2" # "true" or "false"
    
    # Get movie details
    movie=$(api_request "radarr" "GET" "/api/v3/movie/lookup/tmdb?tmdbId=$tmdbId")
    
    # Get root folder
    rootFolder=$(api_request "radarr" "GET" "/api/v3/rootfolder" | jq -r '.[0].path')
    
    # Get default quality profile
    # If DEFAULT_PROFILE is set in common.sh/config, use it, otherwise fetch first
    if [ -n "$DEFAULT_PROFILE" ]; then
        qualityProfile="$DEFAULT_PROFILE"
    else
        qualityProfile=$(api_request "radarr" "GET" "/api/v3/qualityprofile" | jq -r '.[0].id')
    fi
    
    searchFlag="true"
    if [ "$no_search" = "true" ]; then
        searchFlag="false"
    fi

    # Construct payload
    payload=$(echo "$movie" | jq --arg rf "$rootFolder" --argjson qp "$qualityProfile" --argjson search "$searchFlag" '
      . + {
        rootFolderPath: $rf,
        qualityProfileId: $qp,
        monitored: true,
        addOptions: {
          searchForMovie: $search
        }
      }
    ')
    
    result=$(api_request "radarr" "POST" "/api/v3/movie" "$payload")
    
    if echo "$result" | jq -e '.id' > /dev/null 2>&1; then
        title=$(echo "$result" | jq -r '.title')
        year=$(echo "$result" | jq -r '.year')
        log_success "Added: $title ($year)"
        echo "   Path: $rootFolder/$title ($year)"
        echo "   Monitored: Yes"
        if [ "$searchFlag" = "true" ]; then
            echo "   Search started"
        fi
        
        # Check for collection
        collectionTmdbId=$(echo "$result" | jq -r '.collection.tmdbId // empty')
        if [ -n "$collectionTmdbId" ]; then
             collectionName=$(echo "$result" | jq -r '.collection.title')
             echo "   This is part of a collection: $collectionName"
             echo "      To add all: arr-all movie add-collection $collectionTmdbId"
        fi
    else
        log_error "Failed to add movie"
        echo "$result" | jq -r '.message // .'
    fi
}

radarr_remove() {
    local tmdbId="$1"
    local delete_files="$2" # "true" or "false"
    
    # Get ID
    movie=$(api_request "radarr" "GET" "/api/v3/movie?tmdbId=$tmdbId")
    
    if [ "$movie" = "[]" ]; then
        log_error "Movie not found in library"
        return 1
    fi
    
    movieId=$(echo "$movie" | jq -r '.[0].id')
    title=$(echo "$movie" | jq -r '.[0].title')
    
    api_request "radarr" "DELETE" "/api/v3/movie/$movieId?deleteFiles=$delete_files"
    
    if [ "$delete_files" = "true" ]; then
        log_success "Removed: $title (files deleted)"
    else
        log_success "Removed: $title (files kept)"
    fi
}

radarr_config() {
    echo "=== Radarr Config ==="
    echo "Root Folders:"
    api_request "radarr" "GET" "/api/v3/rootfolder" | jq -r '.[] | "  - \(.path) (Free: \(.freeSpace / 1073741824 | floor) GB)"'
    
    echo "Quality Profiles:"
    api_request "radarr" "GET" "/api/v3/qualityprofile" | jq -r '.[] | "  - \(.id): \(.name)"'
}

radarr_add_collection() {
    local collectionTmdbId="$1"
    local no_search="$2"

    # We need to find the collection first to get its movies
    # This is tricky because Radarr doesn't have a direct "get collection by TMDB ID" endpoint that returns movies indiscriminately
    # But we can search for the movies in the collection
    
    # 1. We need the collection name or details. 
    # Use existing collection if monitored, or search?
    # The reference script used a hack by searching for a movie in the collection or using a user provided name.
    # A robust way: use `api/v3/collection` to see if we already have it.
    
    # For now, let's implement the simpler version: Look up via a movie in it? No, that's chicken/egg.
    # The reference script demanded a search term.
    # We can try to use the `GET /api/v3/movie` to see if ANY movie in that collection already exists, then grab collection info.
    
    # Better approach if we have just the ID:
    # 1. We can't query TMDB directly.
    # 2. We can try to list collections and see if it's there (but that only lists collections we have at least one movie for).
    
    # The spec says: arr-all movie add-collection <tmdbCollectionId>
    # If we don't have any movies from it, Radarr might not know about it.
    # But usually users add a movie, then see "Hey this is in a collection", then add the rest.
    # So we probably have the collection record in Radarr.
    
    collections=$(api_request "radarr" "GET" "/api/v3/collection")
    collection=$(echo "$collections" | jq --argjson tid "$collectionTmdbId" '.[] | select(.tmdbId == $tid)')
    
    if [ -z "$collection" ] || [ "$collection" = "null" ]; then
        log_error "Collection not found in Radarr. Add at least one movie from the collection first."
        return 1
    fi
    
    collectionTitle=$(echo "$collection" | jq -r '.title')
    log_info "Found collection: $collectionTitle"
    
    # Now we need to fetch all movies in this collection.
    # The /api/v3/collection/{id} endpoint should give us the movies?
    collectionId=$(echo "$collection" | jq -r '.id')
    fullCollection=$(api_request "radarr" "GET" "/api/v3/collection/$collectionId")
    
    # Wait, does the collection object contain the movies? 
    # Radarr API v3: GET /collection/{id} returns the collection details.
    # It does NOT list missing movies directly in the response usually, unless monitored?
    # Actually, we might need to search for the collection title to find the missing ones.
    
    # Let's clean the collection title (remove " Collection")
    searchTerm=$(echo "$collectionTitle" | sed 's/ Collection$//')
    
    log_info "Searching for movies in collection: $searchTerm"
    encoded_query=$(echo "$searchTerm" | jq -sRr @uri)
    allMovies=$(api_request "radarr" "GET" "/api/v3/movie/lookup?term=$encoded_query")
    
    # Filter by collectionId
    moviesToAdd=$(echo "$allMovies" | jq --argjson cid "$collectionTmdbId" '[.[] | select(.collection.tmdbId == $cid)]')
    count=$(echo "$moviesToAdd" | jq 'length')
    
    if [ "$count" = "0" ]; then
        log_error "No movies found for collection."
        return 1
    fi
    
    log_info "Found $count movies in collection."
    
    # Prepare common resources
    rootFolder=$(api_request "radarr" "GET" "/api/v3/rootfolder" | jq -r '.[0].path')
    if [ -n "$DEFAULT_PROFILE" ]; then
        qualityProfile="$DEFAULT_PROFILE"
    else
        qualityProfile=$(api_request "radarr" "GET" "/api/v3/qualityprofile" | jq -r '.[0].id')
    fi
    
    searchFlag="true"
    if [ "$no_search" = "true" ]; then searchFlag="false"; fi
    
    added=0
    skipped=0
    
    # Iterate and add
    # Note: Using a while loop with jq -c to handle spaces in json
    while read -r movie; do
        tmdbId=$(echo "$movie" | jq -r '.tmdbId')
        title=$(echo "$movie" | jq -r '.title')
        year=$(echo "$movie" | jq -r '.year')
        
        # Check if exists
        exists=$(api_request "radarr" "GET" "/api/v3/movie?tmdbId=$tmdbId")
        if [ "$exists" != "[]" ]; then
            echo "SKIP: $title ($year) - already in library"
            skipped=$((skipped + 1))
            continue
        fi
        
        # Add
        payload=$(echo "$movie" | jq --arg rf "$rootFolder" --argjson qp "$qualityProfile" --argjson search "$searchFlag" '
          . + {
            rootFolderPath: $rf,
            qualityProfileId: $qp,
            monitored: true,
            addOptions: {
              searchForMovie: $search
            }
          }
        ')
        
        res=$(api_request "radarr" "POST" "/api/v3/movie" "$payload")
        
        if echo "$res" | jq -e '.id' >/dev/null 2>&1; then
             echo "OK: $title ($year)"
             added=$((added + 1))
        else
             echo "FAIL: $title ($year) - $(echo "$res" | jq -r '.message // "failed"')"
        fi
    done < <(echo "$moviesToAdd" | jq -c '.[]')
    
    echo ""
    log_success "Collection processing complete. Added: $added | Skipped: $skipped"
    
    # Monitor collection
    updatePayload=$(echo "$fullCollection" | jq '. + {monitored: true, searchOnAdd: true}')
    api_request "radarr" "PUT" "/api/v3/collection/$collectionId" "$updatePayload" >/dev/null
    echo "Collection monitored."
}
