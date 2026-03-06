#!/usr/bin/env bash
set -euo pipefail

# Print the Fly app name from fly.toml (if present)
# Usage: scripts/fly_app_from_toml.sh [path]

path="${1:-fly.toml}"

if [ ! -f "$path" ]; then
  echo "fly.toml not found: $path" >&2
  exit 1
fi

# naive parse: app = "name" OR app = 'name'
# Avoid using an interpreter (ruby/python) here; keep it as a simple shell parser.
# This assumes a single-line definition like: app = "my-app"
app=$(awk -F= '/^[[:space:]]*app[[:space:]]*=/{v=$2; gsub(/^[[:space:]]*/,"",v); gsub(/[[:space:]]*$/,"",v); gsub(/^"|"$/,"",v); gsub(/^\x27|\x27$/,"",v); print v; exit}' "$path")

if [ -z "$app" ]; then
  echo "Could not find app = \"...\" in $path" >&2
  exit 1
fi

echo "$app"
