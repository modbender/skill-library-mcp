#!/bin/bash
# Search flight by flight number
# Usage: flight.sh [--api-key KEY] <fnum> <date> [dep] [arr]

API_KEY_ARG=""

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

FNUM="$1"
DATE="$2"
DEP="${3:-}"
ARR="${4:-}"

if [[ -z "$FNUM" || -z "$DATE" ]]; then
    echo "Usage: flight.sh [--api-key KEY] <flight_number> <YYYY-MM-DD> [dep_airport] [arr_airport]"
    echo "Example: flight.sh MU2157 2025-02-15"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PARAMS="fnum=$FNUM date=$DATE"
[[ -n "$DEP" ]] && PARAMS="$PARAMS dep=$DEP"
[[ -n "$ARR" ]] && PARAMS="$PARAMS arr=$ARR"

$SCRIPT_DIR/variflight.sh $API_KEY_ARG flight $PARAMS
