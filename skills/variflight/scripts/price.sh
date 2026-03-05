#!/bin/bash
# Get flight price by cities
# Usage: price.sh [--api-key KEY] <dep_city> <arr_city> <date>

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

DEPCITY="$1"
ARRCITY="$2"
DATE="$3"

if [[ -z "$DEPCITY" || -z "$ARRCITY" || -z "$DATE" ]]; then
    echo "Usage: price.sh [--api-key KEY] <dep_city_code> <arr_city_code> <YYYY-MM-DD>"
    echo "Example: price.sh HFE CAN 2025-02-15"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
$SCRIPT_DIR/variflight.sh $API_KEY_ARG getFlightPriceByCities dep_city="$DEPCITY" arr_city="$ARRCITY" dep_date="$DATE"
