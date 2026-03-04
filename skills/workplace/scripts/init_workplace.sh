#!/usr/bin/env bash
set -euo pipefail

# init_workplace.sh — Initialize a .workplace/ directory in a project folder
# Usage: init_workplace.sh <path> [--name <name>] [--desc <description>]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATES="$SKILL_DIR/assets/templates"
REGISTRY_DIR="$HOME/.openclaw/workspace/.workplaces"

# --- Parse args ---
TARGET_PATH=""
WP_NAME=""
WP_DESC=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) WP_NAME="$2"; shift 2 ;;
    --desc) WP_DESC="$2"; shift 2 ;;
    *) TARGET_PATH="$1"; shift ;;
  esac
done

if [[ -z "$TARGET_PATH" ]]; then
  echo "Usage: init_workplace.sh <path> [--name <name>] [--desc <description>]"
  exit 1
fi

TARGET_PATH="$(cd "$TARGET_PATH" 2>/dev/null && pwd || echo "$TARGET_PATH")"

# Create target if it doesn't exist
mkdir -p "$TARGET_PATH"
TARGET_PATH="$(cd "$TARGET_PATH" && pwd)"

# Check if already initialized
if [[ -d "$TARGET_PATH/.workplace" ]]; then
  echo "⚠️  Workplace already initialized at $TARGET_PATH/.workplace"
  echo "    UUID: $(jq -r '.uuid' "$TARGET_PATH/.workplace/config.json" 2>/dev/null || echo 'unknown')"
  exit 0
fi

# --- Check if target has .git or is a parent folder ---
HAS_GIT=false
IS_PARENT=false
CHILD_DIRS=()

if [[ -d "$TARGET_PATH/.git" || -f "$TARGET_PATH/.git" ]]; then
  HAS_GIT=true
fi

if [[ "$HAS_GIT" == false ]]; then
  # No .git — check if subdirs have .git (making this a parent workspace)
  for subdir in "$TARGET_PATH"/*/; do
    subdir="$(cd "$subdir" 2>/dev/null && pwd || true)"
    [[ -z "$subdir" ]] && continue
    if [[ -d "$subdir/.git" || -f "$subdir/.git" ]]; then
      IS_PARENT=true
      CHILD_DIRS+=("$subdir")
    fi
  done

  if [[ "$IS_PARENT" == true ]]; then
    echo "📂 No .git found at $TARGET_PATH"
    echo "   Detected as parent workspace with ${#CHILD_DIRS[@]} child repo(s):"
    for cd in "${CHILD_DIRS[@]}"; do
      echo "   - $(basename "$cd")"
    done
    echo ""
  fi
fi

# --- Generate values ---
WP_UUID="$(uuidgen | tr '[:upper:]' '[:lower:]')"
WP_HOSTNAME="$(hostname -s 2>/dev/null || hostname)"
WP_CREATED="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [[ -z "$WP_NAME" ]]; then
  WP_NAME="$(basename "$TARGET_PATH")"
fi

# --- Detect parent workplace ---
PARENT_UUID=""
PARENT_DIR="$(dirname "$TARGET_PATH")"
while [[ "$PARENT_DIR" != "/" ]]; do
  if [[ -f "$PARENT_DIR/.workplace/config.json" ]]; then
    PARENT_UUID="$(jq -r '.uuid' "$PARENT_DIR/.workplace/config.json" 2>/dev/null || true)"
    break
  fi
  PARENT_DIR="$(dirname "$PARENT_DIR")"
done

# --- Create .workplace structure ---
WP_DIR="$TARGET_PATH/.workplace"
mkdir -p "$WP_DIR"/{agents,memory,skills,deploy}

# Config
sed -e "s|__UUID__|$WP_UUID|g" \
    -e "s|__NAME__|$WP_NAME|g" \
    -e "s|__PATH__|$TARGET_PATH|g" \
    -e "s|__HOSTNAME__|$WP_HOSTNAME|g" \
    -e "s|__CREATED__|$WP_CREATED|g" \
    "$TEMPLATES/config.json" > "$WP_DIR/config.json"

# Set description if provided
if [[ -n "$WP_DESC" ]]; then
  jq --arg desc "$WP_DESC" '.description = $desc' "$WP_DIR/config.json" > "$WP_DIR/config.tmp" \
    && mv "$WP_DIR/config.tmp" "$WP_DIR/config.json"
fi

# Set parent if found
if [[ -n "$PARENT_UUID" ]]; then
  jq --arg parent "$PARENT_UUID" '.parent = $parent' "$WP_DIR/config.json" > "$WP_DIR/config.tmp" \
    && mv "$WP_DIR/config.tmp" "$WP_DIR/config.json"
fi

# Mark as parent workspace if no .git but has children
if [[ "$IS_PARENT" == true ]]; then
  jq '.type = "parent"' "$WP_DIR/config.json" > "$WP_DIR/config.tmp" \
    && mv "$WP_DIR/config.tmp" "$WP_DIR/config.json"
fi

# Kernel agent
cp "$TEMPLATES/kernel.md" "$WP_DIR/agents/kernel.md"

# Deploy templates
cp "$TEMPLATES/deploy/dev.md" "$WP_DIR/deploy/dev.md"
cp "$TEMPLATES/deploy/main.md" "$WP_DIR/deploy/main.md"
cp "$TEMPLATES/deploy/pre.md" "$WP_DIR/deploy/pre.md"

# Empty chat.md
touch "$WP_DIR/chat.md"

# Initial process-status.json
cat > "$WP_DIR/process-status.json" << 'EOF'
{}
EOF

# --- Scan structure ---
IGNORE_PATTERN='node_modules|vendor|\.next|dist|build|target|__pycache__|\.venv|\.git|\.workplace'

generate_structure() {
  local dir="$1"
  local prefix="$2"
  find "$dir" -maxdepth 1 -mindepth 1 -not -name '.*' 2>/dev/null | sort | while read -r entry; do
    local name="$(basename "$entry")"
    # Skip ignored patterns
    if echo "$name" | grep -qE "^($IGNORE_PATTERN)$"; then
      continue
    fi
    if [[ -d "$entry" ]]; then
      echo "{\"path\":\"${prefix}${name}/\",\"type\":\"dir\"}"
      generate_structure "$entry" "${prefix}${name}/"
    else
      echo "{\"path\":\"${prefix}${name}\",\"type\":\"file\"}"
    fi
  done
}

echo "[" > "$WP_DIR/structure.json"
generate_structure "$TARGET_PATH" "" | paste -sd',' - >> "$WP_DIR/structure.json"
echo "]" >> "$WP_DIR/structure.json"

# Fix JSON (handle empty case)
if [[ "$(wc -l < "$WP_DIR/structure.json")" -le 2 ]]; then
  echo "[]" > "$WP_DIR/structure.json"
fi

# --- Generate full-tree.md ---
# Workspace-level view: list this workplace and its linked/parent workplaces (no file trees)
{
  echo "# Full Workspace Tree"
  echo ""
  echo "## Host: $WP_HOSTNAME"
  echo ""
  echo "### $WP_NAME ($WP_UUID)"
  echo "\`$TARGET_PATH\`"

  # Parent workplace
  if [[ -n "$PARENT_UUID" ]]; then
    PARENT_NAME="$(jq -r '.name // "unknown"' "$PARENT_DIR/.workplace/config.json" 2>/dev/null || echo "unknown")"
    echo ""
    echo "**Parent:** $PARENT_NAME ($PARENT_UUID)"
    echo "\`$PARENT_DIR\`"
  fi

  # Linked workplaces (read from registry)
  if [[ -f "$REGISTRY_DIR/registry.json" ]]; then
    # Get linked UUIDs from config (if config already written)
    if [[ -f "$WP_DIR/config.json" ]]; then
      LINKED_UUIDS="$(jq -r '.linked[]? // empty' "$WP_DIR/config.json" 2>/dev/null)"
      if [[ -n "$LINKED_UUIDS" ]]; then
        echo ""
        echo "**Linked:**"
        echo "$LINKED_UUIDS" | while IFS= read -r luuid; do
          LNAME="$(jq -r --arg u "$luuid" '.[] | select(.uuid == $u) | .name // "unknown"' "$REGISTRY_DIR/registry.json" 2>/dev/null)"
          LPATH="$(jq -r --arg u "$luuid" '.[] | select(.uuid == $u) | .path // "unknown"' "$REGISTRY_DIR/registry.json" 2>/dev/null)"
          echo "- $LNAME ($luuid) \`$LPATH\`"
        done
      fi
    fi
  fi

  # Sibling workplaces (other .workplace dirs in the same parent directory)
  SIBLINGS_DIR="$(dirname "$TARGET_PATH")"
  FOUND_SIBLINGS=false
  for sibling in "$SIBLINGS_DIR"/*/; do
    sibling="$(cd "$sibling" 2>/dev/null && pwd || true)"
    [[ -z "$sibling" ]] && continue
    [[ "$sibling" == "$TARGET_PATH" ]] && continue
    if [[ -f "$sibling/.workplace/config.json" ]]; then
      if [[ "$FOUND_SIBLINGS" == false ]]; then
        echo ""
        echo "**Siblings:**"
        FOUND_SIBLINGS=true
      fi
      SNAME="$(jq -r '.name // "unknown"' "$sibling/.workplace/config.json" 2>/dev/null)"
      SUUID="$(jq -r '.uuid // "unknown"' "$sibling/.workplace/config.json" 2>/dev/null)"
      echo "- $SNAME ($SUUID) \`$sibling\`"
    fi
  done
} > "$WP_DIR/full-tree.md"

# --- Register in central registry ---
mkdir -p "$REGISTRY_DIR"

if [[ ! -f "$REGISTRY_DIR/registry.json" ]]; then
  echo "[]" > "$REGISTRY_DIR/registry.json"
fi

# Add to registry
jq --arg uuid "$WP_UUID" \
   --arg name "$WP_NAME" \
   --arg path "$TARGET_PATH" \
   --arg hostname "$WP_HOSTNAME" \
   --arg created "$WP_CREATED" \
   --arg parent "$PARENT_UUID" \
   '. += [{
     "uuid": $uuid,
     "name": $name,
     "path": $path,
     "hostname": $hostname,
     "created": $created,
     "parent": (if $parent == "" then null else $parent end),
     "linked": [],
     "lastActive": $created
   }]' "$REGISTRY_DIR/registry.json" > "$REGISTRY_DIR/registry.tmp" \
  && mv "$REGISTRY_DIR/registry.tmp" "$REGISTRY_DIR/registry.json"

# Set as current
cat > "$REGISTRY_DIR/current.json" << EOF
{"uuid":"$WP_UUID","path":"$TARGET_PATH"}
EOF

# --- Summary ---
echo ""
echo "✅ Workplace initialized!"
echo "   Name:     $WP_NAME"
echo "   UUID:     $WP_UUID"
echo "   Path:     $TARGET_PATH"
echo "   Hostname: $WP_HOSTNAME"
if [[ -n "$PARENT_UUID" ]]; then
  echo "   Parent:   $PARENT_UUID"
fi
echo ""
echo "   .workplace/"
echo "   ├── config.json"
echo "   ├── agents/kernel.md"
echo "   ├── memory/"
echo "   ├── skills/"
echo "   ├── deploy/{dev,main,pre}.md"
echo "   ├── chat.md"
echo "   ├── structure.json"
echo "   ├── full-tree.md"
echo "   └── process-status.json"

# --- Auto-init children if parent workspace ---
if [[ "$IS_PARENT" == true && ${#CHILD_DIRS[@]} -gt 0 ]]; then
  echo ""
  echo "🔄 Initializing child workplaces..."
  echo ""

  CHILD_UUIDS=()

  for child_dir in "${CHILD_DIRS[@]}"; do
    CHILD_NAME="$(basename "$child_dir")"

    if [[ -d "$child_dir/.workplace" ]]; then
      echo "   ⚠️  $CHILD_NAME — already initialized"
      CHILD_UUID="$(jq -r '.uuid' "$child_dir/.workplace/config.json" 2>/dev/null || true)"
      CHILD_UUIDS+=("$CHILD_UUID")

      # Update parent reference if not set
      EXISTING_PARENT="$(jq -r '.parent // empty' "$child_dir/.workplace/config.json" 2>/dev/null || true)"
      if [[ -z "$EXISTING_PARENT" ]]; then
        jq --arg parent "$WP_UUID" '.parent = $parent' "$child_dir/.workplace/config.json" > "$child_dir/.workplace/config.tmp" \
          && mv "$child_dir/.workplace/config.tmp" "$child_dir/.workplace/config.json"
        echo "      → Set parent to $WP_NAME ($WP_UUID)"
      fi
    else
      # Init child — reuse this script recursively
      "$0" "$child_dir" --name "$CHILD_NAME"
      CHILD_UUID="$(jq -r '.uuid' "$child_dir/.workplace/config.json" 2>/dev/null || true)"
      CHILD_UUIDS+=("$CHILD_UUID")

      # Set parent reference on the child
      jq --arg parent "$WP_UUID" '.parent = $parent' "$child_dir/.workplace/config.json" > "$child_dir/.workplace/config.tmp" \
        && mv "$child_dir/.workplace/config.tmp" "$child_dir/.workplace/config.json"
    fi
  done

  # Cross-link all children with each other
  if [[ ${#CHILD_UUIDS[@]} -gt 1 ]]; then
    echo ""
    echo "🔗 Cross-linking ${#CHILD_UUIDS[@]} child workplaces..."

    for child_dir in "${CHILD_DIRS[@]}"; do
      if [[ ! -f "$child_dir/.workplace/config.json" ]]; then
        continue
      fi
      CHILD_UUID="$(jq -r '.uuid' "$child_dir/.workplace/config.json" 2>/dev/null)"

      for other_uuid in "${CHILD_UUIDS[@]}"; do
        if [[ "$other_uuid" != "$CHILD_UUID" && -n "$other_uuid" ]]; then
          # Add to linked if not already there
          ALREADY_LINKED="$(jq --arg u "$other_uuid" '[.linked[]? | select(. == $u)] | length' "$child_dir/.workplace/config.json" 2>/dev/null || echo "0")"
          if [[ "$ALREADY_LINKED" == "0" ]]; then
            jq --arg u "$other_uuid" '.linked += [$u]' "$child_dir/.workplace/config.json" > "$child_dir/.workplace/config.tmp" \
              && mv "$child_dir/.workplace/config.tmp" "$child_dir/.workplace/config.json"
          fi
        fi
      done
    done
    echo "   ✅ All children linked"
  fi

  # Add all children to parent's linked list
  for cuuid in "${CHILD_UUIDS[@]}"; do
    if [[ -n "$cuuid" ]]; then
      ALREADY_LINKED="$(jq --arg u "$cuuid" '[.linked[]? | select(. == $u)] | length' "$WP_DIR/config.json" 2>/dev/null || echo "0")"
      if [[ "$ALREADY_LINKED" == "0" ]]; then
        jq --arg u "$cuuid" '.linked += [$u]' "$WP_DIR/config.json" > "$WP_DIR/config.tmp" \
          && mv "$WP_DIR/config.tmp" "$WP_DIR/config.json"
      fi
    fi
  done

  # Regenerate full-tree.md for parent (now with children)
  {
    echo "# Full Workspace Tree"
    echo ""
    echo "## Host: $WP_HOSTNAME"
    echo ""
    echo "### $WP_NAME ($WP_UUID) [parent]"
    echo "\`$TARGET_PATH\`"
    echo ""
    echo "**Children:**"
    for child_dir in "${CHILD_DIRS[@]}"; do
      if [[ -f "$child_dir/.workplace/config.json" ]]; then
        CNAME="$(jq -r '.name // "unknown"' "$child_dir/.workplace/config.json" 2>/dev/null)"
        CUUID="$(jq -r '.uuid // "unknown"' "$child_dir/.workplace/config.json" 2>/dev/null)"
        echo "- $CNAME ($CUUID) \`$child_dir\`"
      fi
    done
  } > "$WP_DIR/full-tree.md"

  # Regenerate full-tree.md for each child (now with parent + siblings)
  for child_dir in "${CHILD_DIRS[@]}"; do
    if [[ ! -f "$child_dir/.workplace/config.json" ]]; then
      continue
    fi
    CNAME="$(jq -r '.name' "$child_dir/.workplace/config.json" 2>/dev/null)"
    CUUID="$(jq -r '.uuid' "$child_dir/.workplace/config.json" 2>/dev/null)"
    {
      echo "# Full Workspace Tree"
      echo ""
      echo "## Host: $WP_HOSTNAME"
      echo ""
      echo "### $CNAME ($CUUID)"
      echo "\`$child_dir\`"
      echo ""
      echo "**Parent:** $WP_NAME ($WP_UUID) \`$TARGET_PATH\`"

      # Siblings
      FOUND_SIBS=false
      for sib_dir in "${CHILD_DIRS[@]}"; do
        [[ "$sib_dir" == "$child_dir" ]] && continue
        if [[ -f "$sib_dir/.workplace/config.json" ]]; then
          if [[ "$FOUND_SIBS" == false ]]; then
            echo ""
            echo "**Siblings:**"
            FOUND_SIBS=true
          fi
          SNAME="$(jq -r '.name // "unknown"' "$sib_dir/.workplace/config.json" 2>/dev/null)"
          SUUID="$(jq -r '.uuid // "unknown"' "$sib_dir/.workplace/config.json" 2>/dev/null)"
          echo "- $SNAME ($SUUID) \`$sib_dir\`"
        fi
      done
    } > "$child_dir/.workplace/full-tree.md"
  done

  echo ""
  echo "✅ Parent workspace with ${#CHILD_DIRS[@]} children initialized and linked"

  # Set current back to parent
  cat > "$REGISTRY_DIR/current.json" << EOF
{"uuid":"$WP_UUID","path":"$TARGET_PATH"}
EOF
fi
