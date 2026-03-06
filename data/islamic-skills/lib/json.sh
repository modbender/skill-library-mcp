#!/bin/bash

# Check if jq is available
HAS_JQ=false
if command -v jq >/dev/null 2>&1; then
    HAS_JQ=true
fi

# Log warning if jq is missing
if [ "$HAS_JQ" = false ]; then
    echo "Warning: jq not found. Using pure bash JSON parser (slower/limited)." >&2
fi

# Function to clean JSON string for parsing (remove newlines/extra spaces outside quotes)
# This is expensive in pure bash, so we only do minimal cleanup
clean_json() {
    echo "$1" | tr -d '\n' | sed 's/:[[:space:]]*/:/g'
}

# Get value from JSON using dot notation
# Usage: json_get "$json_content" "key1.key2"
json_get() {
    local json="$1"
    local key="$2"

    if [ "$HAS_JQ" = true ]; then
        echo "$json" | jq -r ".$key // empty"
    else
        # Pure bash fallback
        # This is a simplified parser and might fail on complex nested structures or keys with special chars
        
        # Split key by dot
        local current_json="$json"
        local IFS='.'
        read -ra KEYS <<< "$key"
        
        for k in "${KEYS[@]}"; do
            # Extract content for key 'k'
            # 1. Match "k": ...
            # 2. handle string "k": "value"
            # 3. handle number/bool "k": 123
            # 4. handle object "k": { ... }
            # 5. handle array "k": [ ... ]
            
            # Simple extraction for now - relying on grep/sed
            # This is fragile but works for well-formed API responses
            
            # Try to match string value
            local val=$(echo "$current_json" | grep -o "\"$k\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | head -n1 | sed -E 's/.*: *"([^"]*)".*/\1/')
            
            if [ -z "$val" ]; then
                # Try number/boolean/null
                val=$(echo "$current_json" | grep -o "\"$k\"[[:space:]]*:[[:space:]]*[a-zA-Z0-9\.-]*" | head -n1 | sed -E 's/.*: *//')
            fi
            
            if [ -z "$val" ]; then
                # Try object or array - getting the block is hard with regex
                # We'll use a crude bracket counter approach if we must, but for specific keys it's better to rely on structure
                
                # Crude extraction of object/array content
                # Find start of key
                local rest=$(echo "$current_json" | sed -n "s/.*\"$k\"[[:space:]]*:[[:space:]]*//p")
                if [ -z "$rest" ]; then return 1; fi
                
                local first_char="${rest:0:1}"
                if [ "$first_char" == "{" ]; then
                     # Extract balanced {}
                     val=$(echo "$rest" | awk '
                        BEGIN {count=0; started=0}
                        {
                            for(i=1;i<=length($0);i++) {
                                c=substr($0,i,1);
                                if(c=="{") {count++; started=1}
                                if(c=="}") {count--}
                                printf "%s", c
                                if(started && count==0) exit
                            }
                        }
                     ')
                elif [ "$first_char" == "[" ]; then
                     # Extract balanced []
                     val=$(echo "$rest" | awk '
                        BEGIN {count=0; started=0}
                        {
                            for(i=1;i<=length($0);i++) {
                                c=substr($0,i,1);
                                if(c=="[") {count++; started=1}
                                if(c=="]") {count--}
                                printf "%s", c
                                if(started && count==0) exit
                            }
                        }
                     ')
                else
                    return 1
                fi
            fi
            
            current_json="$val"
            if [ -z "$current_json" ]; then return 1; fi
        done
        
        # Remove quotes if it's a string
        echo "$current_json" | sed -E 's/^"(.*)"$/\1/'
    fi
}

# Get array length
# Usage: json_array_length "$json_content" "key.to.array"
json_array_length() {
    local json="$1"
    local key="$2"
    
    if [ "$HAS_JQ" = true ]; then
        echo "$json" | jq ".$key | length"
    else
        local arr_content=$(json_get "$json" "$key")
        if [ -z "$arr_content" ]; then echo 0; return; fi
        
        # Count objects "{...}" or items in array
        # This is tricky. Simplified: count occurrences of "{" at top level?
        # Better: use a loop to extract elements
        
        # Assume array of objects for now as that's what we mostly deal with (matches, ayahs)
        # We can count "{" that are directly inside the array? No, too risky.
        
        # Let's just return a placeholder or try to parse
        # For our use case (top 3 matches), we can just extract them one by one
        
        # Fallback: Count non-nested "}," ?
        echo "$arr_content" | grep -o "}," | wc -l | awk '{print $1 + 1}'
        # This is very approximate
    fi
}

# Extract element from array by index
# Usage: json_array_get "$json_content" "key.to.array" index
json_array_get() {
    local json="$1"
    local key="$2"
    local index="$3"
    
    if [ "$HAS_JQ" = true ]; then
        echo "$json" | jq -r ".$key[$index]"
    else
        local arr_content=$(json_get "$json" "$key")
        # Remove outer []
        arr_content="${arr_content:1:${#arr_content}-2}"
        
        # Split by "}, {" or similar boundaries
        # This is extremely hard in pure bash for arbitrary JSON
        
        # Simplified: Use awk to find the Nth object
        echo "$arr_content" | awk -v n="$((index+1))" '
            BEGIN {count=0; nesting=0; start_idx=0}
            {
                raw=$0
                len=length(raw)
                for(i=1; i<=len; i++) {
                    c=substr(raw,i,1)
                    if(nesting==0 && c=="{") {
                        count++
                        if(count==n) start_idx=i
                    }
                    if(c=="{") nesting++
                    if(c=="}") nesting--
                    
                    if(count==n && start_idx>0) {
                        printf "%s", c
                    }
                    
                    if(count==n && nesting==0 && c=="}") exit
                }
            }
        '
    fi
}
