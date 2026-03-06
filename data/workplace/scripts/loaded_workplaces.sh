#!/usr/bin/env bash
set -euo pipefail

# loaded_workplaces.sh — Manage loaded/open workplaces
# Usage:
#   loaded_workplaces.sh list                          — List all loaded workplaces
#   loaded_workplaces.sh load <path|uuid>              — Load a workplace (must be registered)
#   loaded_workplaces.sh unload <name|uuid>            — Unload a workplace
#   loaded_workplaces.sh status                        — Summary of loaded workplaces
#
# Loaded workplaces are tracked in ~/.openclaw/workspace/.workplaces/loaded.json
# They represent workplaces that are currently "open" and available for quick access,
# agent orchestration, and cross-workspace operations.

REGISTRY_DIR="$HOME/.openclaw/workspace/.workplaces"
REGISTRY="$REGISTRY_DIR/registry.json"
LOADED="$REGISTRY_DIR/loaded.json"

# Ensure files exist
mkdir -p "$REGISTRY_DIR"
[[ -f "$REGISTRY" ]] || echo "[]" > "$REGISTRY"
[[ -f "$LOADED" ]] || echo "[]" > "$LOADED"

ACTION="${1:-list}"
shift || true

case "$ACTION" in
  list)
    COUNT=$(jq 'length' "$LOADED")
    if [[ "$COUNT" == "0" ]]; then
      echo "No workplaces currently loaded."
      exit 0
    fi
    echo "📂 Loaded workplaces ($COUNT):"
    echo ""
    jq -r '.[] | "  • \(.name) (\(.uuid | .[0:8])...)\n    Path: \(.path)\n    Loaded: \(.loadedAt)\n"' "$LOADED"
    ;;

  load)
    TARGET="${1:-}"
    if [[ -z "$TARGET" ]]; then
      echo "Usage: loaded_workplaces.sh load <path|uuid|name>"
      exit 1
    fi

    # Resolve target — try as path first, then uuid, then name
    RESOLVED=""
    if [[ -d "$TARGET" ]]; then
      TARGET_PATH="$(cd "$TARGET" && pwd)"
      RESOLVED=$(jq -r --arg p "$TARGET_PATH" '.[] | select(.path == $p) | @json' "$REGISTRY" 2>/dev/null | head -1)
    fi
    if [[ -z "$RESOLVED" ]]; then
      RESOLVED=$(jq -r --arg t "$TARGET" '.[] | select(.uuid == $t or (.uuid | startswith($t)) or .name == $t) | @json' "$REGISTRY" 2>/dev/null | head -1)
    fi

    if [[ -z "$RESOLVED" ]]; then
      echo "❌ Workplace not found in registry: $TARGET"
      echo "   Run 'workplace init <path>' or 'workplace scan <path> --register' first."
      exit 1
    fi

    WP_UUID=$(echo "$RESOLVED" | jq -r '.uuid')
    WP_NAME=$(echo "$RESOLVED" | jq -r '.name')
    WP_PATH=$(echo "$RESOLVED" | jq -r '.path')

    # Check if already loaded
    ALREADY=$(jq --arg u "$WP_UUID" '[.[] | select(.uuid == $u)] | length' "$LOADED")
    if [[ "$ALREADY" != "0" ]]; then
      echo "⚠️  $WP_NAME is already loaded."
      exit 0
    fi

    # Check that .workplace/config.json exists
    if [[ ! -f "$WP_PATH/.workplace/config.json" ]]; then
      echo "❌ No .workplace/ found at $WP_PATH"
      echo "   Initialize it first: workplace init $WP_PATH"
      exit 1
    fi

    # Add to loaded.json
    NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    jq --arg uuid "$WP_UUID" \
       --arg name "$WP_NAME" \
       --arg path "$WP_PATH" \
       --arg now "$NOW" \
       '. += [{
         "uuid": $uuid,
         "name": $name,
         "path": $path,
         "loadedAt": $now,
         "source": "manual"
       }]' "$LOADED" > "$LOADED.tmp" && mv "$LOADED.tmp" "$LOADED"

    echo "✅ Loaded: $WP_NAME"
    echo "   UUID: $WP_UUID"
    echo "   Path: $WP_PATH"
    ;;

  unload)
    TARGET="${1:-}"
    if [[ -z "$TARGET" ]]; then
      echo "Usage: loaded_workplaces.sh unload <name|uuid>"
      exit 1
    fi

    # Find in loaded.json
    MATCH=$(jq -r --arg t "$TARGET" '.[] | select(.uuid == $t or (.uuid | startswith($t)) or .name == $t) | .uuid' "$LOADED" | head -1)

    if [[ -z "$MATCH" ]]; then
      echo "❌ Not found in loaded workplaces: $TARGET"
      exit 1
    fi

    WP_NAME=$(jq -r --arg u "$MATCH" '.[] | select(.uuid == $u) | .name' "$LOADED")

    jq --arg u "$MATCH" '[.[] | select(.uuid != $u)]' "$LOADED" > "$LOADED.tmp" && mv "$LOADED.tmp" "$LOADED"

    echo "✅ Unloaded: $WP_NAME ($MATCH)"
    ;;

  status)
    COUNT=$(jq 'length' "$LOADED")
    echo "📊 Loaded Workplaces: $COUNT"
    echo ""
    if [[ "$COUNT" != "0" ]]; then
      jq -r '.[] | "  \(.name) — \(.path)"' "$LOADED"
    fi

    # Show current active
    if [[ -f "$REGISTRY_DIR/current.json" ]]; then
      CURRENT_UUID=$(jq -r '.uuid' "$REGISTRY_DIR/current.json")
      CURRENT_NAME=$(jq -r --arg u "$CURRENT_UUID" '.[] | select(.uuid == $u) | .name // "unknown"' "$REGISTRY")
      echo ""
      echo "  Active: $CURRENT_NAME ($CURRENT_UUID)"
    fi
    ;;

  *)
    echo "Usage: loaded_workplaces.sh <list|load|unload|status>"
    exit 1
    ;;
esac
