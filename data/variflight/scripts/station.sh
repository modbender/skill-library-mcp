#!/bin/bash
# Search train stations
# Usage: station.sh [--api-key KEY] <query>

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

QUERY="$1"

if [[ -z "$QUERY" ]]; then
    echo "Usage: station.sh [--api-key KEY] <query>"
    echo "Example: station.sh \"北京西\""
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
$SCRIPT_DIR/variflight.sh $API_KEY_ARG searchTrainStations query="$QUERY"
