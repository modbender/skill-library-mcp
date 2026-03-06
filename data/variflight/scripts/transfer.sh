#!/bin/bash
# Get flight transfer info
# Usage: transfer.sh [--api-key KEY] <depcity> <arrcity> <depdate>

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
DEPDATE="$3"

if [[ -z "$DEPCITY" || -z "$ARRCITY" || -z "$DEPDATE" ]]; then
    echo "Usage: transfer.sh [--api-key KEY] <depcity> <arrcity> <YYYY-MM-DD>"
    echo "Example: transfer.sh BJS SHA 2025-02-15"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
$SCRIPT_DIR/variflight.sh $API_KEY_ARG transfer depcity="$DEPCITY" arrcity="$ARRCITY" depdate="$DEPDATE"
