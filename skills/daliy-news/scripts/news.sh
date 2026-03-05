#!/bin/bash

# Default parameters
ENCODING=""
DATE_PARAM=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --encoding|-e)
      ENCODING="$2"
      shift 2
      ;;
    --date|-d)
      DATE_PARAM="$2"
      shift 2
      ;;
    *)
      # If only one argument is provided without flag, use it as date
      if [[ $# -eq 1 && ! "$1" =~ ^- ]]; then
        DATE_PARAM="$1"
        shift
      else
        echo "Unknown parameter: $1"
        echo "Usage: $0 [--encoding text|json|markdown|image|image-proxy] [--date YYYY-MM-DD]"
        exit 1
      fi
      ;;
  esac
done

# Validate encoding value if provided
if [[ -n "$ENCODING" ]]; then
  case $ENCODING in
    text|json|markdown|image|image-proxy)
      # Valid encoding
      ;;
    *)
      echo "Error: Unsupported encoding type '$ENCODING'."
      echo "Supported types are: text, json, markdown, image, image-proxy"
      exit 1
      ;;
  esac
fi

# Validate date format if provided
if [[ -n "$DATE_PARAM" ]]; then
  if ! [[ "$DATE_PARAM" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo "Error: Invalid date format '$DATE_PARAM'. Must be YYYY-MM-DD."
    exit 1
  fi
fi

# Construct API URL
API_URL="https://60s.viki.moe/v2/60s"
QUERY_STRING=""

if [[ -n "$ENCODING" ]]; then
  QUERY_STRING="encoding=${ENCODING}"
fi

if [[ -n "$DATE_PARAM" ]]; then
  if [[ -n "$QUERY_STRING" ]]; then
    QUERY_STRING="${QUERY_STRING}&date=${DATE_PARAM}"
  else
    QUERY_STRING="date=${DATE_PARAM}"
  fi
fi

if [[ -n "$QUERY_STRING" ]]; then
  API_URL="${API_URL}?${QUERY_STRING}"
fi

# Request API and output result
curl -s "$API_URL"
