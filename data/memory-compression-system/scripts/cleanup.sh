#!/bin/bash
# Memory Compression System - Cleanup Script
# Version: 3.0.0

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="$SKILL_DIR/config/default.conf"
DATA_DIR="$SKILL_DIR/data"
COMPRESSED_DIR="$DATA_DIR/compressed"
BACKUP_DIR="$DATA_DIR/backups"
LOG_FILE="$SKILL_DIR/logs/cleanup.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load configuration
[ -f "$CONFIG_FILE" ] && source "$CONFIG_FILE" 2>/dev/null

# Default values
RETENTION_DAYS="${RETENTION_DAYS:-30}"
MAX_FILES="${MAX_COMPRESSED_FILES:-100}"
AUTO_MODE=false
DRY_RUN=false
VERBOSE=false

# Log function
log() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local message="$1"
    
    if [ "$VERBOSE" = true ] || [ "$AUTO_MODE" = false ]; then
        echo -e "${BLUE}[$timestamp]${NC} $message"
    fi
    
    echo "[$timestamp] INFO: $message" >> "$LOG_FILE"
}

error() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local message="$1"
    
    echo -e "${RED}[$timestamp] ERROR:${NC} $message" >&2
    echo "[$timestamp] ERROR: $message" >> "$LOG_FILE"
    echo "[$timestamp] ERROR: $message" >> "$SKILL_DIR/logs/error.log"
}

success() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local message="$1"
    
    if [ "$VERBOSE" = true ] || [ "$AUTO_MODE" = false ]; then
        echo -e "${GREEN}[$timestamp] SUCCESS:${NC} $message"
    fi
    
    echo "[$timestamp] SUCCESS: $message" >> "$LOG_FILE"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --days|-d)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        --max-files|-m)
            MAX_FILES="$2"
            shift 2
            ;;
        --auto|-a)
            AUTO_MODE=true
            shift
            ;;
        --dry-run|-n)
            DRY_RUN=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -d, --days DAYS      Retention days (default: 30)"
            echo "  -m, --max-files NUM  Maximum files to keep (default: 100)"
            echo "  -a, --auto           Auto mode (for cron jobs)"
            echo "  -n, --dry-run        Dry run (don't delete files)"
            echo "  -v, --verbose        Verbose output"
            echo "  -h, --help           Show this help"
            echo ""
            echo "Examples:"
            echo "  $0 --days 7 --verbose"
            echo "  $0 --auto --max-files 50"
            echo "  $0 --dry-run --days 30"
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Calculate cutoff date
calculate_cutoff() {
    local days="$1"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        date -v-${days}d -u +"%Y%m%d"
    else
        # Linux
        date -d "$days days ago" -u +"%Y%m%d"
    fi
}

# Cleanup compressed files
cleanup_compressed_files() {
    local cutoff_date=$(calculate_cutoff "$RETENTION_DAYS")
    local deleted_count=0
    local kept_count=0
    
    log "Cleaning up compressed files older than $RETENTION_DAYS days (before $cutoff_date)..."
    
    if [ ! -d "$COMPRESSED_DIR" ]; then
        log "No compressed directory found: $COMPRESSED_DIR"
        return 0
    fi
    
    # Find and process files
    find "$COMPRESSED_DIR" -name "memory_*.ultra" -o -name "memory_*.binary" -o -name "memory_*.base64" | \
    while read -r file; do
        # Extract date from filename (memory_YYYYMMDD_HHMMSS.format)
        local filename=$(basename "$file")
        local filedate=$(echo "$filename" | grep -o 'memory_[0-9]\{8\}' | cut -d_ -f2)
        
        if [ -n "$filedate" ] && [ "$filedate" -lt "$cutoff_date" ]; then
            if [ "$DRY_RUN" = true ]; then
                log "Would delete: $filename (date: $filedate)"
            else
                log "Deleting: $filename (date: $filedate)"
                rm -f "$file"
            fi
            deleted_count=$((deleted_count + 1))
        else
            kept_count=$((kept_count + 1))
        fi
    done
    
    log "Compressed files cleanup: $deleted_count deleted, $kept_count kept"
}

# Cleanup old backups
cleanup_backups() {
    local backup_retention_days=$((RETENTION_DAYS * 2))  # Keep backups longer
    local cutoff_date=$(calculate_cutoff "$backup_retention_days")
    local deleted_count=0
    local kept_count=0
    
    log "Cleaning up backups older than $backup_retention_days days (before $cutoff_date)..."
    
    if [ ! -d "$BACKUP_DIR" ]; then
        log "No backup directory found: $BACKUP_DIR"
        return 0
    fi
    
    # Find and process backup files
    find "$BACKUP_DIR" -name "backup_*.tar.gz" | \
    while read -r file; do
        # Extract date from filename (backup_YYYYMMDD_HHMMSS.tar.gz)
        local filename=$(basename "$file")
        local filedate=$(echo "$filename" | grep -o 'backup_[0-9]\{8\}' | cut -d_ -f2)
        
        if [ -n "$filedate" ] && [ "$filedate" -lt "$cutoff_date" ]; then
            if [ "$DRY_RUN" = true ]; then
                log "Would delete backup: $filename (date: $filedate)"
            else
                log "Deleting backup: $filename (date: $filedate)"
                rm -f "$file"
            fi
            deleted_count=$((deleted_count + 1))
        else
            kept_count=$((kept_count + 1))
        fi
    done
    
    log "Backup cleanup: $deleted_count deleted, $kept_count kept"
}

# Limit number of files
limit_file_count() {
    local max_files="$1"
    local current_count=0
    local deleted_count=0
    
    log "Limiting compressed files to maximum $max_files..."
    
    if [ ! -d "$COMPRESSED_DIR" ]; then
        log "No compressed directory found: $COMPRESSED_DIR"
        return 0
    fi
    
    # Count current files
    current_count=$(find "$COMPRESSED_DIR" -name "memory_*.ultra" -o -name "memory_*.binary" -o -name "memory_*.base64" | wc -l)
    
    if [ "$current_count" -le "$max_files" ]; then
        log "Current file count ($current_count) is within limit ($max_files)"
        return 0
    fi
    
    # Sort files by date (oldest first) and delete excess
    find "$COMPRESSED_DIR" -name "memory_*.ultra" -o -name "memory_*.binary" -o -name "memory_*.base64" | \
        sort | head -n $((current_count - max_files)) | \
    while read -r file; do
        if [ "$DRY_RUN" = true ]; then
            log "Would delete (excess): $(basename "$file")"
        else
            log "Deleting (excess): $(basename "$file")"
            rm -f "$file"
        fi
        deleted_count=$((deleted_count + 1))
    done
    
    log "File limit enforcement: $deleted_count excess files removed"
}

# Cleanup old logs
cleanup_logs() {
    local log_retention_days="${LOG_RETENTION_DAYS:-7}"
    local cutoff_date=$(calculate_cutoff "$log_retention_days")
    local deleted_count=0
    
    log "Cleaning up logs older than $log_retention_days days..."
    
    if [ ! -d "$SKILL_DIR/logs" ]; then
        log "No logs directory found: $SKILL_DIR/logs"
        return 0
    fi
    
    # Find and process log files
    find "$SKILL_DIR/logs" -name "*.log" -type f | \
    while read -r file; do
        # Check file modification time
        local filedate=$(date -r "$file" -u +"%Y%m%d" 2>/dev/null || echo "")
        
        if [ -n "$filedate" ] && [ "$filedate" -lt "$cutoff_date" ]; then
            if [ "$DRY_RUN" = true ]; then
                log "Would delete log: $(basename "$file") (date: $filedate)"
            else
                log "Deleting log: $(basename "$file") (date: $filedate)"
                rm -f "$file"
            fi
            deleted_count=$((deleted_count + 1))
        fi
    done
    
    # Rotate large log files
    find "$SKILL_DIR/logs" -name "*.log" -type f -size +10M 2>/dev/null | \
    while read -r file; do
        log "Rotating large log file: $(basename "$file")"
        if [ "$DRY_RUN" = false ]; then
            mv "$file" "${file}.$(date +%Y%m%d)"
            touch "$file"
        fi
    done
    
    log "Log cleanup: $deleted_count old logs removed"
}

# Update search index after cleanup
update_search_index() {
    if [ "$SEARCH_ENABLED" != "true" ]; then
        log "Search indexing is disabled, skipping index update"
        return 0
    fi
    
    log "Updating search index after cleanup..."
    
    local index_file="$DATA_DIR/search/index.json"
    
    if [ ! -f "$index_file" ]; then
        log "No search index found: $index_file"
        return 0
    fi
    
    if command -v jq &> /dev/null; then
        # Remove entries for deleted files
        local temp_index="${index_file}.tmp"
        
        # Get list of existing files
        local existing_files=$(find "$COMPRESSED_DIR" -name "memory_*.ultra" -o -name "memory_*.binary" -o -name "memory_*.base64" | xargs -I {} basename {} 2>/dev/null || echo "")
        
        # Filter index to only include existing files
        echo "$existing_files" | jq -R -s -c 'split("\n") | map(select(. != ""))' | \
        jq --argjson files "$(cat)" '
            .files = (.files | map(select(.filename as $f | $files | index($f) != null))) |
            .file_count = (.files | length) |
            .last_updated = now | strftime("%Y-%m-%dT%H:%M:%SZ") |
            .statistics.total_size = (.files | map(.size) | add) |
            .statistics.average_ratio = (.files | map(.ratio) | add / length) |
            .statistics.formats = (.files | group_by(.format) | map({key: .[0].format, value: length}) | from_entries)
        ' "$index_file" > "$temp_index" 2>/dev/null && mv "$temp_index" "$index_file"
        
        success "Search index updated after cleanup"
    else
        log "jq not available, skipping search index update"
    fi
}

# Main cleanup function
main_cleanup() {
    log "========================================"
    log "Starting Memory Compression System Cleanup"
    log "Retention days: $RETENTION_DAYS"
    log "Max files: $MAX_FILES"
    log "Mode: $( [ "$AUTO_MODE" = true ] && echo "auto" || echo "manual" )"
    log "Dry run: $( [ "$DRY_RUN" = true ] && echo "yes" || echo "no" )"
    log "========================================"
    
    # Create directories if they don't exist
    mkdir -p "$COMPRESSED_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Run cleanup tasks
    cleanup_compressed_files
    cleanup_backups
    limit_file_count "$MAX_FILES"
    cleanup_logs
    
    # Update search index
    update_search_index
    
    # Summary
    log "========================================"
    log "Cleanup completed successfully"
    log "========================================"
    
    success "Cleanup completed!"
}

# Error handling
trap 'error "Cleanup interrupted"; exit 1' INT TERM

# Run main function
if main_cleanup; then
    exit 0
else
    error "Cleanup failed"
    exit 1
fi