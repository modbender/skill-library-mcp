#!/usr/bin/env bash
# Generate HTML form from JSON schema

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <schema.json> [output.html]"
  exit 1
fi

gatecrash-forms generate "$@"
