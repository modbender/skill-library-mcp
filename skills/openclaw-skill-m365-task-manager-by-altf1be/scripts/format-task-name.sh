#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <date> <short-action>"
  exit 1
fi

date="$1"
action="$2"
slug=$(echo "$action" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')
echo "${date}-${slug}"
