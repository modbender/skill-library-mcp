#!/bin/bash
# Initialize sync repository and configuration
# Safety features: backup, confirmation, selective operations

set -e

DEVICE_NAME=""
REPO_URL=""
FORCE=false
SYNC_FILES=""
SKIP_CONFIRM=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --device-name)
            DEVICE_NAME="$2"
            shift 2
            ;;
        --repo-url)
            REPO_URL="$2"
            shift 2
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --sync-files)
            SYNC_FILES="$2"
            shift 2
            ;;
        --skip-confirm)
            SKIP_CONFIRM=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ -z "$DEVICE_NAME" ]]; then
    echo "Usage: sync-init.sh --device-name <name> [options]"
    echo ""
    echo "Options:"
    echo "  --device-name   Device identifier (ubuntu, macmini, laptop, etc.)"
    echo "  --repo-url      Git repository URL (optional, can set later)"
    echo "  --sync-files    Space-separated list of files to sync"
    echo "  --force         Skip confirmation prompts (use with caution)"
    echo "  --skip-confirm  Skip individual confirmations"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$HOME/.openclaw/workspace"
SYNC_REPO="${SYNC_REPO:-$HOME/openclaw-sync}"
CONFIG_DIR="$HOME/.config/openclaw"

mkdir -p "$CONFIG_DIR"

# Default files to sync
if [[ -z "$SYNC_FILES" ]]; then
    SYNC_FILES="USER.md MEMORY.md SOUL.md skills/ memory/"
fi

# Safety: Check if already initialized
if [[ -d "$SYNC_REPO/.git" ]]; then
    echo "Sync repo already exists at $SYNC_REPO"
else
    # Clone or init repo
    if [[ -n "$REPO_URL" ]]; then
        echo "Cloning repository..."
        git clone "$REPO_URL" "$SYNC_REPO" 2>/dev/null || {
            mkdir -p "$SYNC_REPO"
            cd "$SYNC_REPO"
            git init
            git remote add origin "$REPO_URL"
        }
    else
        mkdir -p "$SYNC_REPO"
        cd "$SYNC_REPO"
        git init
        echo "Initialized empty repo. Please set remote:"
        echo "  cd $SYNC_REPO"
        echo "  git remote add origin <your-repo-url>"
    fi
fi

cd "$SYNC_REPO"

# Create .gitignore if not exists
if [[ ! -f ".gitignore" ]]; then
    cat > .gitignore << 'EOF'
logs/
temp/
*.log
.DS_Store
node_modules/
.sync-conflicts
.sync-conflict.log
*.backup.*
EOF
    echo "Created .gitignore"
fi

# Create default config
CONFIG_FILE="$CONFIG_DIR/sync-config.yaml"
if [[ ! -f "$CONFIG_FILE" ]]; then
    cat > "$CONFIG_FILE" << EOF
repo_url: "${REPO_URL:-git@github.com:YOURNAME/openclaw-sync.git}"
sync_interval_minutes: 5
device_name: "$DEVICE_NAME"
conflict_strategy: "notify"
auto_pull_on_start: true
auto_push_enabled: false

paths:
  sync:
$(echo "$SYNC_FILES" | tr ' ' '\n' | while read f; do echo "    - \"$f\""; done)
  ignore:
    - "logs/"
    - "temp/"
    - "*.log"
EOF
    echo "Created config: $CONFIG_FILE"
else
    # Update device_name in existing config
    sed -i "s/device_name:.*/device_name: \"$DEVICE_NAME\"/" "$CONFIG_FILE"
    echo "Updated device_name in config: $DEVICE_NAME"
fi

# Setup workspace symlink structure
echo "Setting up workspace links..."

for item in $SYNC_FILES; do
    # Remove trailing slash for directory names
    item_name="${item%/}"
    
    # Check if sync repo has this file/dir
    if [[ ! -e "$SYNC_REPO/$item_name" ]]; then
        # Create empty file/dir in sync repo
        if [[ "$item" == */ ]]; then
            mkdir -p "$SYNC_REPO/$item_name"
        else
            touch "$SYNC_REPO/$item_name"
        fi
    fi
    
    # Check if workspace has this file/dir
    if [[ -e "$WORKSPACE_DIR/$item_name" ]]; then
        # If it's already a symlink, skip
        if [[ -L "$WORKSPACE_DIR/$item_name" ]]; then
            echo "  $item_name: already symlinked"
            continue
        fi
        
        # === SAFETY: Check before removing ===
        if [[ "$FORCE" != "true" && "$SKIP_CONFIRM" != "true" ]]; then
            echo ""
            echo "⚠️  File '$item_name' already exists in workspace."
            echo "    Size: $(du -sh "$WORKSPACE_DIR/$item_name" 2>/dev/null | cut -f1)"
            read -p "    Backup and replace with symlink? [y/N]: " confirm
            if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
                echo "    Skipped: $item_name"
                continue
            fi
        fi
        
        # Handle directory merge
        if [[ "$item" == */ ]] && [[ -d "$WORKSPACE_DIR/$item_name" ]]; then
            mkdir -p "$SYNC_REPO/$item_name"
            # Copy contents that don't exist in sync repo
            for subfile in "$WORKSPACE_DIR/$item_name"/*; do
                if [[ -e "$subfile" ]]; then
                    filename=$(basename "$subfile")
                    if [[ ! -e "$SYNC_REPO/$item_name/$filename" ]]; then
                        cp -r "$subfile" "$SYNC_REPO/$item_name/$filename"
                        echo "  $item_name/$filename: copied to sync repo"
                    fi
                fi
            done
        elif [[ -s "$WORKSPACE_DIR/$item_name" ]] && [[ ! -s "$SYNC_REPO/$item_name" ]]; then
            # Copy non-empty workspace file if sync repo file is empty
            cp "$WORKSPACE_DIR/$item_name" "$SYNC_REPO/$item_name"
            echo "  $item_name: copied to sync repo"
        elif [[ -s "$SYNC_REPO/$item_name" ]] && [[ -s "$WORKSPACE_DIR/$item_name" ]]; then
            # Both have content - backup workspace version
            backup_file="$WORKSPACE_DIR/$item_name.backup.$(date +%s)"
            cp "$WORKSPACE_DIR/$item_name" "$backup_file"
            echo "  $item_name: backed up to $(basename $backup_file)"
        fi
    fi
    
    # === SAFETY: Only remove what we've backed up ===
    if [[ -e "$WORKSPACE_DIR/$item_name" && ! -L "$WORKSPACE_DIR/$item_name" ]]; then
        # Remove original (already backed up above)
        rm -rf "$WORKSPACE_DIR/$item_name"
    fi
    
    # Create symlink
    ln -sf "$SYNC_REPO/$item_name" "$WORKSPACE_DIR/$item_name"
    echo "  $item_name: symlinked"
done

# Create device-specific memory file
mkdir -p "$SYNC_REPO/memory"
TODAY=$(date +%Y-%m-%d)
DEVICE_MEMORY="$SYNC_REPO/memory/${DEVICE_NAME}-${TODAY}.md"
if [[ ! -f "$DEVICE_MEMORY" ]]; then
    echo "# ${DEVICE_NAME} - ${TODAY}" > "$DEVICE_MEMORY"
    echo "" >> "$DEVICE_MEMORY"
    echo "Device: ${DEVICE_NAME}" >> "$DEVICE_MEMORY"
    echo "Started: $(date)" >> "$DEVICE_MEMORY"
    echo "Created initial memory file: memory/${DEVICE_NAME}-${TODAY}.md"
fi

# Ensure memory directory is symlinked if included in sync
if echo "$SYNC_FILES" | grep -q "memory"; then
    if [[ ! -L "$WORKSPACE_DIR/memory" ]]; then
        if [[ -d "$WORKSPACE_DIR/memory" && ! -L "$WORKSPACE_DIR/memory" ]]; then
            # === SAFETY: Backup first ===
            mv "$WORKSPACE_DIR/memory" "$WORKSPACE_DIR/memory.backup.$(date +%s)"
        fi
        ln -sf "$SYNC_REPO/memory" "$WORKSPACE_DIR/memory"
        echo "  memory: symlinked"
    fi
fi

echo ""
echo "✓ Sync initialized for device: $DEVICE_NAME"
echo "  Repo: $SYNC_REPO"
echo "  Config: $CONFIG_FILE"
echo "  Files: $SYNC_FILES"
echo ""
echo "Safety notes:"
echo "  - Auto-push is disabled by default"
echo "  - Run './scripts/sync-push.sh' manually when ready"
echo "  - Or enable auto-push in config: auto_push_enabled: true"
