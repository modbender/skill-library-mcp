#!/bin/bash

# Quran Module

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.sh"
source "${SCRIPT_DIR}/api.sh"
source "${SCRIPT_DIR}/cache.sh"
source "${SCRIPT_DIR}/format.sh"

# Constants
BASE_URL="http://api.alquran.cloud/v1"
ARABIC_EDITION="quran-uthmani"

# Language to edition mapping
get_translation_edition() {
    local lang="${1:-id}"
    case "$lang" in
        id) echo "id.indonesian" ;;
        en) echo "en.sahih" ;;
        ar) echo "quran-uthmani" ;; # Though not really a translation
        *) echo "en.sahih" ;;
    esac
}

# Fetch Ayah
# Usage: get_ayah "surah" "ayah"
get_ayah() {
    local surah="$1"
    local ayah="$2"
    load_config
    
    local edition=$(get_translation_edition "$QURAN_LANGUAGE")
    local cache_key="quran_ayah_${surah}_${ayah}_${QURAN_LANGUAGE}"
    
    if cache_exists "$cache_key"; then
        cache_read "$cache_key"
        return 0
    fi
    
    # Fetch Arabic
    local ar_url="${BASE_URL}/ayah/${surah}:${ayah}/${ARABIC_EDITION}"
    local ar_resp=$(api_call "$ar_url")
    
    if [ $? -ne 0 ] || [ -z "$ar_resp" ]; then return 1; fi
    
    # Fetch Translation
    local tr_url="${BASE_URL}/ayah/${surah}:${ayah}/${edition}"
    local tr_resp=$(api_call "$tr_url")
    
    if [ $? -ne 0 ] || [ -z "$tr_resp" ]; then return 1; fi
    
    # Combine (simple string concatenation approach for bash)
    # We create a synthetic JSON or just echo the data separated
    # Let's create a custom format for caching to avoid complex JSON merging
    
    # Extract values
    local ar_text=$(json_get "$ar_resp" "data.text")
    local tr_text=$(json_get "$tr_resp" "data.text")
    local surah_name=$(json_get "$ar_resp" "data.surah.englishName")
    local surah_num=$(json_get "$ar_resp" "data.surah.number")
    local ayah_num=$(json_get "$ar_resp" "data.numberInSurah")
    
    # Create simple JSON
    local combined
    if [ "$HAS_JQ" = true ]; then
        combined=$(jq -n \
                  --arg sn "$surah_name" \
                  --arg snum "$surah_num" \
                  --arg anum "$ayah_num" \
                  --arg ta "$ar_text" \
                  --arg tt "$tr_text" \
                  '{surah: $sn, surah_num: ($snum|tonumber), ayah_num: ($anum|tonumber), text_ar: $ta, text_tr: $tt}')
    else
        # Basic escaping for pure bash (simple quote replacement)
        ar_text=${ar_text//\"/\\\"}
        tr_text=${tr_text//\"/\\\"}
        combined="{\"surah\": \"$surah_name\", \"surah_num\": $surah_num, \"ayah_num\": $ayah_num, \"text_ar\": \"$ar_text\", \"text_tr\": \"$tr_text\"}"
    fi
    
    cache_write "$cache_key" "$combined"
    echo "$combined"
}

# Fetch Surah
# Usage: get_surah "surah_num"
get_surah() {
    local surah="$1"
    load_config
    
    local edition=$(get_translation_edition "$QURAN_LANGUAGE")
    local cache_key="quran_surah_${surah}_${QURAN_LANGUAGE}"
    
    if cache_exists "$cache_key"; then
        cache_read "$cache_key"
        return 0
    fi
    
    # Fetch Arabic
    local ar_url="${BASE_URL}/surah/${surah}/${ARABIC_EDITION}"
    local ar_resp=$(api_call "$ar_url")
    
    if [ $? -ne 0 ] || [ -z "$ar_resp" ]; then return 1; fi
    
    # Fetch Translation
    local tr_url="${BASE_URL}/surah/${surah}/${edition}"
    local tr_resp=$(api_call "$tr_url")
    
    if [ $? -ne 0 ] || [ -z "$tr_resp" ]; then return 1; fi
    
    # For full surah, we need to merge arrays.
    # If jq is available, use it
    if [ "$HAS_JQ" = true ]; then
        # Use jq to merge
        # This is complex one-liner.
        # Create a temp file for ar and tr
        local ar_file=$(mktemp)
        local tr_file=$(mktemp)
        echo "$ar_resp" > "$ar_file"
        echo "$tr_resp" > "$tr_file"
        
        local combined=$(jq -n --slurpfile ar "$ar_file" --slurpfile tr "$tr_file" '
            {
                surah: $ar[0].data.englishName,
                surah_num: $ar[0].data.number,
                ayahs: [range(0; ($ar[0].data.ayahs | length)) | {
                    number: $ar[0].data.ayahs[.].numberInSurah,
                    text_ar: $ar[0].data.ayahs[.].text,
                    text_tr: $tr[0].data.ayahs[.].text
                }]
            }
        ')
        rm "$ar_file" "$tr_file"
        cache_write "$cache_key" "$combined"
        echo "$combined"
    else
        # Pure bash fallback: Line by line processing?
        # This is extremely hard for full surah without jq.
        # We will cheat: Just store raw responses in a way format can handle
        # Or just store the Translation response but missing Arabic text? No.
        
        echo "Error: Reading full Surah requires 'jq' installed on the system." >&2
        return 1
    fi
}

# Search Quran
# Usage: search_quran "keyword"
search_quran() {
    local keyword="$1"
    load_config
    
    local edition=$(get_translation_edition "$QURAN_LANGUAGE")
    # No caching for search usually
    
    local enc_keyword=$(url_encode "$keyword")
    local url="${BASE_URL}/search/${enc_keyword}/all/${edition}"
    
    local response=$(api_call "$url")
    if [ -z "$response" ]; then return 1; fi
    
    # Limit to top 3 results to fetch details
    # We need to extract surah number and ayah number for top 3 matches
    
    if [ "$HAS_JQ" = true ]; then
        echo "$response" | jq -r '.data.matches[0:3] | .[] | "\(.surah.number):\(.numberInSurah)"'
    else
        # Fallback extraction
        # Matches structure: data.matches[].surah.number
        echo "$response" | grep -o "\"surah\":{[^}]*\"number\":[0-9]*" | head -n 3 | grep -o "\"number\":[0-9]*" | cut -d: -f2 > /tmp/quran_search_surahs
        # We also need ayah number
        # This is getting very messy in pure bash.
        
        # Simplified: regex for "numberInSurah":X ... "surah":{..."number":Y
        # But order differs.
        
        echo "Error: Search requires 'jq' installed." >&2
        return 1
    fi
}

# Handle Quran Command
handle_quran() {
    local search_kw=""
    local surah=""
    local ayah=""
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --search) search_kw="$2"; shift 2 ;;
            --surah) surah="$2"; shift 2 ;;
            --ayah) ayah="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    
    if [ ! -z "$search_kw" ]; then
        local matches=$(search_quran "$search_kw")
        if [ $? -ne 0 ] || [ -z "$matches" ]; then
            echo "No results found or error occurred."
            return 1
        fi
        
        print_header "Search results for '$search_kw'"
        
        # matches contains lines "SURAH:AYAH"
        while read -r match; do
            if [ -z "$match" ]; then continue; fi
            local s=$(echo "$match" | cut -d: -f1)
            local a=$(echo "$match" | cut -d: -f2)
            
            local ayah_data=$(get_ayah "$s" "$a")
            # Format
            local s_name=$(json_get "$ayah_data" "surah")
            local s_num=$(json_get "$ayah_data" "surah_num")
            local a_num=$(json_get "$ayah_data" "ayah_num")
            local ar=$(json_get "$ayah_data" "text_ar")
            local tr=$(json_get "$ayah_data" "text_tr")
            
            echo -e "=== $s_name ($s_num:$a_num) ===\n"
            echo -e "$ar\n"
            echo -e "$tr"
            print_separator
        done <<< "$matches"
        
    elif [ ! -z "$surah" ]; then
        if [ ! -z "$ayah" ]; then
            local data=$(get_ayah "$surah" "$ayah")
            if [ -z "$data" ]; then echo "Ayah not found."; return 1; fi
            
            local s_name=$(json_get "$data" "surah")
            local s_num=$(json_get "$data" "surah_num")
            local a_num=$(json_get "$data" "ayah_num")
            local ar=$(json_get "$data" "text_ar")
            local tr=$(json_get "$data" "text_tr")
            
            print_header "$s_name ($s_num:$a_num)"
            echo -e "$ar\n"
            echo -e "$tr"
            echo ""
        else
            local data=$(get_surah "$surah")
            if [ -z "$data" ]; then echo "Surah not found."; return 1; fi
            
            local s_name=$(json_get "$data" "surah")
            local s_num=$(json_get "$data" "surah_num")
            
            print_header "$s_name (Surah $s_num)"
            
            if [ "$HAS_JQ" = true ]; then
                echo "$data" | jq -r '.ayahs[] | "\(.number) \(.text_ar) \(.text_tr)"' | while read -r line; do
                     # This split is dangerous if text contains spaces (it does).
                     # Better to use jq to format entire block
                     :
                done
                # Direct JQ output
                echo "$data" | jq -r '.ayahs[] | "[\(.number)] \(.text_ar)\n\(.text_tr)\n"'
            else
                echo "Displaying full Surah requires jq."
            fi
        fi
    else
        echo "Usage: quran --search \"keyword\" | --surah NUMBER [--ayah NUMBER]"
    fi
}
