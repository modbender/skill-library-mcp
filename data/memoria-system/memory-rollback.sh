#!/bin/bash
# Memory Rollback Script
# Rolls back memory to a previous backup

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/config.json"

# Default values
MEMORY_PATH="./memory"
BACKUP_PATH="./backups"

# Load config if exists
if [[ -f "$CONFIG_FILE" ]]; then
    MEMORY_PATH=$(jq -r '.memory.base_path // "./memory"' "$CONFIG_FILE")
    BACKUP_PATH=$(jq -r '.backup.path // "./backups"' "$CONFIG_FILE")
fi

# Functions
list_backups() {
    echo "📋 Available backups:"
    echo ""
    
    if [[ ! -d "$BACKUP_PATH" ]]; then
        echo "❌ No backup directory found"
        return 1
    fi
    
    local count=0
    for backup in "$BACKUP_PATH"/backup_*; do
        if [[ -d "$backup" ]] || [[ -f "$backup" ]]; then
            local name=$(basename "$backup")
            local date_str=$(echo "$name" | sed 's/backup_//' | sed 's/\([0-9]\{4\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)_\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1-\2-\3 \4:\5:\6/')
            echo "  [$((++count))] $name ($date_str)"
        fi
    done
    
    if [[ $count -eq 0 ]]; then
        echo "  No backups found"
        return 1
    fi
    
    return 0
}

rollback() {
    local backup_name="$1"
    local force="${2:-false}"
    
    if [[ -z "$backup_name" ]]; then
        echo "❌ Error: Backup name required"
        list_backups
        exit 1
    fi
    
    # Find backup
    local backup_path=""
    if [[ -d "$BACKUP_PATH/$backup_name" ]]; then
        backup_path="$BACKUP_PATH/$backup_name"
    elif [[ -f "$BACKUP_PATH/${backup_name}.tar.gz" ]]; then
        backup_path="$BACKUP_PATH/${backup_name}.tar.gz"
    elif [[ -f "$BACKUP_PATH/$backup_name" ]]; then
        backup_path="$BACKUP_PATH/$backup_name"
    else
        echo "❌ Error: Backup not found: $backup_name"
        list_backups
        exit 1
    fi
    
    echo "🔄 Rolling back to: $backup_name"
    echo "   Source: $backup_path"
    echo "   Target: $MEMORY_PATH"
    
    # Confirm unless forced
    if [[ "$force" != true ]]; then
        read -p "⚠️  This will overwrite current memory. Continue? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ Rollback cancelled"
            exit 0
        fi
    fi
    
    # Create safety backup of current state
    local safety_backup="${BACKUP_PATH}/safety_$(date +%Y%m%d_%H%M%S)"
    echo "💾 Creating safety backup: $safety_backup"
    mkdir -p "$safety_backup"
    if [[ -d "$MEMORY_PATH" ]]; then
        cp -r "$MEMORY_PATH" "$safety_backup/" 2>/dev/null || true
    fi
    
    # Perform rollback
    rm -rf "$MEMORY_PATH"
    mkdir -p "$MEMORY_PATH"
    
    if [[ -d "$backup_path" ]]; then
        # Directory backup
        if [[ -f "$backup_path/memory.tar.gz" ]]; then
            tar -xzf "$backup_path/memory.tar.gz" -C "$(dirname "$MEMORY_PATH")"
        else
            cp -r "$backup_path/memory"/* "$MEMORY_PATH/" 2>/dev/null || cp -r "$backup_path"/* "$MEMORY_PATH/"
        fi
    elif [[ "$backup_path" == *.tar.gz ]]; then
        # Compressed backup
        tar -xzf "$backup_path" -C "$(dirname "$MEMORY_PATH")"
    fi
    
    echo "✅ Rollback complete!"
    echo "💡 Safety backup available at: $safety_backup"
}

# Main command handler
case "${1:-list}" in
    list)
        list_backups
        ;;
    rollback)
        rollback "$2" "$3"
        ;;
    *)
        echo "Usage: $0 {list|rollback BACKUP_NAME [--force]}"
        echo ""
        echo "Commands:"
        echo "  list                    List available backups"
        echo "  rollback BACKUP_NAME    Rollback to specified backup"
        echo ""
        echo "Options:"
        echo "  --force                 Skip confirmation prompt"
        exit 1
        ;;
esac
