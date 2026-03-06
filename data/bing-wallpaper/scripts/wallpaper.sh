#!/bin/bash

# Default parameters
ENCODING=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --encoding|-e)
      if [[ -n "$2" && ! "$2" =~ ^- ]]; then
        ENCODING="$2"
        shift 2
      else
        echo "Error: --encoding requires a value."
        exit 1
      fi
      ;;
    *)
      # If only one argument is provided without flag, use it as encoding
      if [[ $# -eq 1 && ! "$1" =~ ^- ]]; then
        ENCODING="$1"
        shift
      else
        echo "Unknown parameter: $1"
        echo "Usage: $0 [--encoding text|json|image|markdown]"
        exit 1
      fi
      ;;
  esac
done

# Validate encoding value if provided
if [[ -n "$ENCODING" ]]; then
  case $ENCODING in
    text|json|image|markdown)
      # Valid encoding
      ;;
    *)
      echo "Error: Unsupported encoding type '$ENCODING'."
      echo "Supported types are: text, json, image, markdown"
      exit 1
      ;;
  esac
fi

# Construct API URL
API_URL="https://60s.viki.moe/v2/bing"

if [[ -n "$ENCODING" ]]; then
  API_URL="${API_URL}?encoding=${ENCODING}"
fi

# Request API and output result
curl -s "$API_URL"
