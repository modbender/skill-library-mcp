#!/bin/bash
# Memory Backup Script
# Creates incremental backups of the memory system

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/config.json"

# Default values
MEMORY_PATH="./memory"
BACKUP_PATH="./backups"
RETENTION_DAYS=30
COMPRESSION=true

# Load config if exists
if [[ -f "$CONFIG_FILE" ]]; then
    MEMORY_PATH=$(jq -r '.memory.base_path // "./memory"' "$CONFIG_FILE")
    BACKUP_PATH=$(jq -r '.backup.path // "./backups"' "$CONFIG_FILE")
    RETENTION_DAYS=$(jq -r '.backup.retention_days // 30' "$CONFIG_FILE")
    COMPRESSION=$(jq -r '.backup.compression // true' "$CONFIG_FILE")
fi

# Parse arguments
DRY_RUN=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --path)
            MEMORY_PATH="$2"
            shift 2
            ;;
        --output)
            BACKUP_PATH="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Create backup directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_PATH}/backup_${TIMESTAMP}"

if [[ "$DRY_RUN" == true ]]; then
    echo "[DRY RUN] Would create backup at: $BACKUP_DIR"
    exit 0
fi

mkdir -p "$BACKUP_DIR"

echo "📦 Creating memory backup..."
echo "   Source: $MEMORY_PATH"
echo "   Destination: $BACKUP_DIR"

# Check if memory directory exists
if [[ ! -d "$MEMORY_PATH" ]]; then
    echo "❌ Error: Memory directory not found: $MEMORY_PATH"
    exit 1
fi

# Create backup
if [[ "$COMPRESSION" == true ]]; then
    tar -czf "${BACKUP_DIR}/memory.tar.gz" -C "$(dirname "$MEMORY_PATH")" "$(basename "$MEMORY_PATH")"
    echo "✅ Compressed backup created: ${BACKUP_DIR}/memory.tar.gz"
else
    cp -r "$MEMORY_PATH" "$BACKUP_DIR/"
    echo "✅ Backup created: $BACKUP_DIR"
fi

# Save metadata
cat > "${BACKUP_DIR}/metadata.json" << EOF
{
    "timestamp": "$TIMESTAMP",
    "date_iso": "$(date -Iseconds)",
    "source_path": "$MEMORY_PATH",
    "compression": $COMPRESSION,
    "version": "1.0.0"
}
EOF

# Cleanup old backups
echo "🧹 Cleaning up old backups (retention: ${RETENTION_DAYS} days)..."
find "$BACKUP_PATH" -name "backup_*" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} + 2>/dev/null || true
find "$BACKUP_PATH" -name "backup_*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

BACKUP_COUNT=$(find "$BACKUP_PATH" -name "backup_*" -type d 2>/dev/null | wc -l)
echo "📊 Total backups: $BACKUP_COUNT"

echo "✅ Backup complete!"
