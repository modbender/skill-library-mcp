#!/usr/bin/env bash
# ZipTax Sales Tax Lookup Script
# Usage:
#   By address:    ./lookup.sh --address "200 Spectrum Center Dr Irvine CA 92618"
#   By lat/lng:    ./lookup.sh --lat 33.6525 --lng -117.7479
#   By postal:     ./lookup.sh --postalcode 92618
#   By postal+ver: ./lookup.sh --postalcode 92618 --version v20
#   Metrics:       ./lookup.sh --metrics
#
# Requires ZIPTAX_API_KEY environment variable.

set -euo pipefail

BASE_URL="https://api.zip-tax.com"
VERSION="v60"
ADDRESS=""
LAT=""
LNG=""
POSTALCODE=""
METRICS=false

usage() {
  echo "Usage: $0 [options]"
  echo "  --address <addr>     Full street address lookup (door-level)"
  echo "  --lat <lat>          Latitude (use with --lng)"
  echo "  --lng <lng>          Longitude (use with --lat)"
  echo "  --postalcode <zip>   Postal code lookup (returns all rates)"
  echo "  --version <v10-v60>  API version (default: v60)"
  echo "  --metrics            Show account usage metrics"
  echo ""
  echo "Requires ZIPTAX_API_KEY environment variable."
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --address)   ADDRESS="$2"; shift 2 ;;
    --lat)       LAT="$2"; shift 2 ;;
    --lng)       LNG="$2"; shift 2 ;;
    --postalcode) POSTALCODE="$2"; shift 2 ;;
    --version)   VERSION="$2"; shift 2 ;;
    --metrics)   METRICS=true; shift ;;
    -h|--help)   usage ;;
    *)           echo "Unknown option: $1"; usage ;;
  esac
done

if [[ -z "${ZIPTAX_API_KEY:-}" ]]; then
  echo "Error: ZIPTAX_API_KEY environment variable not set" >&2
  exit 1
fi

if $METRICS; then
  curl -s "${BASE_URL}/account/metrics?key=${ZIPTAX_API_KEY}" | python3 -m json.tool
  exit 0
fi

if [[ -n "$ADDRESS" ]]; then
  ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$ADDRESS'))")
  curl -s "${BASE_URL}/request/${VERSION}?address=${ENCODED}" \
    -H "X-API-KEY: ${ZIPTAX_API_KEY}" | python3 -m json.tool
elif [[ -n "$LAT" && -n "$LNG" ]]; then
  curl -s "${BASE_URL}/request/${VERSION}?lat=${LAT}&lng=${LNG}" \
    -H "X-API-KEY: ${ZIPTAX_API_KEY}" | python3 -m json.tool
elif [[ -n "$POSTALCODE" ]]; then
  curl -s "${BASE_URL}/request/${VERSION}?postalcode=${POSTALCODE}" \
    -H "X-API-KEY: ${ZIPTAX_API_KEY}" | python3 -m json.tool
else
  echo "Error: Provide --address, --lat/--lng, or --postalcode" >&2
  usage
fi
