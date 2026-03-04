#!/bin/bash
# Search flights by departure and arrival
# Usage: flights.sh [--api-key KEY] <dep> <arr> <date> [depcity] [arrcity]

API_KEY_ARG=""

# Parse --api-key if present
while [[ $# -gt 0 ]]; do
    case "$1" in
        --api-key|-k)
            API_KEY_ARG="--api-key=$2"
            shift 2
            ;;
        --api-key=*)
            API_KEY_ARG="$1"
            shift
            ;;
        *)
            break
            ;;
    esac
done

DEP="$1"
ARR="$2"
DATE="$3"
DEPCITY="${4:-}"
ARRCITY="${5:-}"

if [[ -z "$DEP" || -z "$ARR" || -z "$DATE" ]]; then
    echo "Usage: flights.sh [--api-key KEY] <dep_airport> <arr_airport> <YYYY-MM-DD> [depcity] [arrcity]"
    echo "Example: flights.sh PEK SHA 2025-02-15"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PARAMS="dep=$DEP arr=$ARR date=$DATE"
[[ -n "$DEPCITY" ]] && PARAMS="$PARAMS depcity=$DEPCITY"
[[ -n "$ARRCITY" ]] && PARAMS="$PARAMS arrcity=$ARRCITY"

$SCRIPT_DIR/variflight.sh $API_KEY_ARG flights $PARAMS
