#!/bin/bash
# Search train tickets
# Usage: train.sh [--api-key KEY] <from_city> <to_city> <date>

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

FROM="$1"
TO="$2"
DATE="$3"

if [[ -z "$FROM" || -z "$TO" || -z "$DATE" ]]; then
    echo "Usage: train.sh [--api-key KEY] <from_city> <to_city> <YYYY-MM-DD>"
    echo "Example: train.sh \"上海\" \"合肥\" 2025-02-15"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
$SCRIPT_DIR/variflight.sh $API_KEY_ARG trainStanTicket cdep="$FROM" carr="$TO" date="$DATE"
