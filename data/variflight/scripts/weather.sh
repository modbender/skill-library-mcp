#!/bin/bash
# Get airport weather forecast
# Usage: weather.sh [--api-key KEY] <airport_code>

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

AIRPORT="$1"

if [[ -z "$AIRPORT" ]]; then
    echo "Usage: weather.sh [--api-key KEY] <airport_code>"
    echo "Example: weather.sh PEK"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
$SCRIPT_DIR/variflight.sh $API_KEY_ARG futureAirportWeather code="$AIRPORT" type="1"
