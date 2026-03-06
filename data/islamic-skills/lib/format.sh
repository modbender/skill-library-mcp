#!/bin/bash

# Output Formatting

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Print header
print_header() {
    local title="$1"
    echo -e "\n${BOLD}${BLUE}=== $title ===${NC}\n"
}

# Print key-value pair
print_kv() {
    local key="$1"
    local value="$2"
    printf "%-20s : %s\n" "$key" "$value"
}

# Print table row
print_row() {
    local fmt="$1"
    shift
    printf "$fmt\n" "$@"
}

# Print separator
print_separator() {
    echo "------------------------------------------------------------"
}
