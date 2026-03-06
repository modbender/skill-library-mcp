#!/usr/bin/env bash
set -euo pipefail

# scan_workplaces.sh — Find all .git directories under a root path
# Usage: scan_workplaces.sh [path] [--max-depth N] [--register]
# Output: JSON array of discovered workplaces

REGISTRY_DIR="$HOME/.openclaw/workspace/.workplaces"
SCAN_PATH="."
MAX_DEPTH=5
DO_REGISTER=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --max-depth) MAX_DEPTH="$2"; shift 2 ;;
    --register) DO_REGISTER=true; shift ;;
    *) SCAN_PATH="$1"; shift ;;
  esac
done

SCAN_PATH="$(cd "$SCAN_PATH" 2>/dev/null && pwd || echo "$SCAN_PATH")"

# Ignore patterns for find
PRUNE_DIRS="node_modules|vendor|\.next|dist|build|target|__pycache__|\.venv"

# Find all .git directories
RESULTS="[]"

while IFS= read -r git_dir; do
  WP_PATH="$(dirname "$git_dir")"
  WP_NAME="$(basename "$WP_PATH")"
  HAS_WORKPLACE=false
  WP_UUID=""

  if [[ -d "$WP_PATH/.workplace" ]]; then
    HAS_WORKPLACE=true
    WP_UUID="$(jq -r '.uuid // empty' "$WP_PATH/.workplace/config.json" 2>/dev/null || true)"
  fi

  # Check for submodules
  IS_SUBMODULE=false
  if [[ -f "$git_dir" ]]; then
    # .git is a file (gitdir pointer) = submodule
    IS_SUBMODULE=true
  fi

  RESULTS="$(echo "$RESULTS" | jq --arg path "$WP_PATH" \
    --arg name "$WP_NAME" \
    --argjson hasWorkplace "$HAS_WORKPLACE" \
    --argjson isSubmodule "$IS_SUBMODULE" \
    --arg uuid "$WP_UUID" \
    '. += [{
      "path": $path,
      "name": $name,
      "hasWorkplace": $hasWorkplace,
      "isSubmodule": $isSubmodule,
      "uuid": (if $uuid == "" then null else $uuid end)
    }]')"
done < <(find "$SCAN_PATH" -maxdepth "$MAX_DEPTH" \
  -name ".git" \
  -not -path "*/node_modules/*" \
  -not -path "*/vendor/*" \
  -not -path "*/.next/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" \
  -not -path "*/target/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/.venv/*" \
  2>/dev/null | sort)

# Output
echo "$RESULTS" | jq '.'

# Summary
COUNT=$(echo "$RESULTS" | jq 'length')
INIT_COUNT=$(echo "$RESULTS" | jq '[.[] | select(.hasWorkplace)] | length')
NEW_COUNT=$(echo "$RESULTS" | jq '[.[] | select(.hasWorkplace | not)] | length')
SUB_COUNT=$(echo "$RESULTS" | jq '[.[] | select(.isSubmodule)] | length')

echo "" >&2
echo "📊 Found $COUNT workplaces ($INIT_COUNT initialized, $NEW_COUNT new, $SUB_COUNT submodules)" >&2

# Register if requested
if [[ "$DO_REGISTER" == true ]]; then
  mkdir -p "$REGISTRY_DIR"
  if [[ ! -f "$REGISTRY_DIR/registry.json" ]]; then
    echo "[]" > "$REGISTRY_DIR/registry.json"
  fi

  REGISTERED=0
  echo "$RESULTS" | jq -c '.[] | select(.hasWorkplace)' | while IFS= read -r wp; do
    UUID="$(echo "$wp" | jq -r '.uuid')"
    # Check if already registered
    EXISTS="$(jq --arg uuid "$UUID" '[.[] | select(.uuid == $uuid)] | length' "$REGISTRY_DIR/registry.json")"
    if [[ "$EXISTS" == "0" && "$UUID" != "null" ]]; then
      WP_PATH="$(echo "$wp" | jq -r '.path')"
      WP_NAME="$(echo "$wp" | jq -r '.name')"
      WP_HOSTNAME="$(hostname -s 2>/dev/null || hostname)"
      WP_NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      jq --arg uuid "$UUID" \
         --arg name "$WP_NAME" \
         --arg path "$WP_PATH" \
         --arg hostname "$WP_HOSTNAME" \
         --arg now "$WP_NOW" \
         '. += [{
           "uuid": $uuid,
           "name": $name,
           "path": $path,
           "hostname": $hostname,
           "created": $now,
           "parent": null,
           "linked": [],
           "lastActive": $now
         }]' "$REGISTRY_DIR/registry.json" > "$REGISTRY_DIR/registry.tmp" \
        && mv "$REGISTRY_DIR/registry.tmp" "$REGISTRY_DIR/registry.json"
      REGISTERED=$((REGISTERED + 1))
      echo "  ✅ Registered: $WP_NAME ($UUID)" >&2
    fi
  done
fi
