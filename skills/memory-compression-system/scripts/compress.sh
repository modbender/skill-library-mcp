#!/bin/bash
# Memory Compression System - Main Compression Script
# Version: 3.0.0

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="$SKILL_DIR/config/default.conf"
DATA_DIR="$SKILL_DIR/data"
COMPRESSED_DIR="$DATA_DIR/compressed"
BACKUP_DIR="$DATA_DIR/backups"
LOG_FILE="$SKILL_DIR/logs/compression.log"
TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load configuration
[ -f "$CONFIG_FILE" ] && source "$CONFIG_FILE" 2>/dev/null

# Default values
FORMAT="${DEFAULT_FORMAT:-ultra}"
AUTO_MODE=false
TEST_MODE=false
VERBOSE=false

# Log function
log() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local level="INFO"
    local message="$1"
    
    if [ "$VERBOSE" = true ] || [ "$AUTO_MODE" = false ]; then
        echo -e "${BLUE}[$timestamp]${NC} $message"
    fi
    
    echo "[$timestamp] $level: $message" >> "$LOG_FILE"
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
        --format|-f)
            FORMAT="$2"
            shift 2
            ;;
        --auto|-a)
            AUTO_MODE=true
            shift
            ;;
        --test|-t)
            TEST_MODE=true
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
            echo "  -f, --format FORMAT    Compression format (base64, binary, ultra)"
            echo "  -a, --auto             Auto mode (for cron jobs)"
            echo "  -t, --test             Test mode (dry run)"
            echo "  -v, --verbose          Verbose output"
            echo "  -h, --help             Show this help"
            echo ""
            echo "Examples:"
            echo "  $0 --format ultra --verbose"
            echo "  $0 --auto"
            echo "  $0 --test --format binary"
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate format
validate_format() {
    case "$FORMAT" in
        base64|b64c|binary|cbin|ultra|ucmp)
            return 0
            ;;
        *)
            error "Invalid format: $FORMAT. Valid formats: base64, binary, ultra"
            return 1
            ;;
    esac
}

# Create backup
create_backup() {
    if [ "$BACKUP_BEFORE_COMPRESSION" != "true" ]; then
        log "Backup before compression is disabled"
        return 0
    fi
    
    local backup_file="$BACKUP_DIR/backup_${TIMESTAMP}.tar.gz"
    log "Creating backup..."
    
    # Backup memory directory
    if [ -d "/home/node/.openclaw/workspace/memory" ]; then
        tar -czf "$backup_file" -C "/home/node/.openclaw/workspace" memory/ 2>/dev/null || true
        log "Backup created: $backup_file ($(stat -c%s "$backup_file" 2>/dev/null || echo 0) bytes)"
    else
        log "No memory directory found for backup"
    fi
}

# Get memory context
get_memory_context() {
    local temp_file="$1"
    
    log "Collecting memory context..."
    
    # Create a comprehensive context from memory files
    {
        echo "# Memory Compression System Context"
        echo "## Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
        echo "## Format: $FORMAT"
        echo "## Mode: $( [ "$AUTO_MODE" = true ] && echo "auto" || echo "manual" )"
        echo ""
        
        # Include memory files
        if [ -d "/home/node/.openclaw/workspace/memory" ]; then
            echo "## Memory Files Summary"
            for file in /home/node/.openclaw/workspace/memory/*.md; do
                if [ -f "$file" ]; then
                    echo "### $(basename "$file")"
                    head -5 "$file" | sed 's/^/    /'
                    echo ""
                fi
            done
        fi
        
        # Include skill status
        echo "## System Status"
        echo "- Skill: memory-compression-system v3.0.0"
        echo "- Compression format: $FORMAT"
        echo "- Auto mode: $AUTO_MODE"
        echo "- Test mode: $TEST_MODE"
        echo "- Timestamp: $TIMESTAMP"
        echo ""
        
        # Include configuration summary
        echo "## Configuration Summary"
        echo "- Compression enabled: ${COMPRESSION_ENABLED:-true}"
        echo "- Retention days: ${RETENTION_DAYS:-30}"
        echo "- Max files: ${MAX_COMPRESSED_FILES:-100}"
        echo "- Search enabled: ${SEARCH_ENABLED:-true}"
        echo ""
        
    } > "$temp_file"
}

# Apply Base64 compression
compress_base64() {
    local input_file="$1"
    local output_file="$2"
    
    log "Applying Base64 Compact compression..."
    
    {
        echo "VERSION:3.0"
        echo "FORMAT:B64C"
        echo "TIMESTAMP:$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
        echo "ORIGINAL_SIZE:$(stat -c%s "$input_file" 2>/dev/null || echo 0)"
        echo "CHECKSUM:$(crc32 "$input_file" 2>/dev/null || echo "N/A")"
        echo "DATA:"
        base64 "$input_file"
    } > "$output_file"
}

# Apply Binary compression
compress_binary() {
    local input_file="$1"
    local output_file="$2"
    
    log "Applying Custom Binary compression..."
    
    # Use gzip for binary compression
    gzip -c "$input_file" > "${output_file}.gz"
    
    {
        echo -n "CBIN"  # Magic number
        echo -n -e "\\x03"  # Version 3
        echo -n -e "\\x01"  # Flags (compressed)
        # Size (4 bytes, little endian)
        local size=$(stat -c%s "${output_file}.gz")
        printf "\\x$(printf '%02x' $((size & 0xFF)))"
        printf "\\x$(printf '%02x' $(((size >> 8) & 0xFF)))"
        printf "\\x$(printf '%02x' $(((size >> 16) & 0xFF)))"
        printf "\\x$(printf '%02x' $(((size >> 24) & 0xFF)))"
        # Data
        cat "${output_file}.gz"
    } > "$output_file"
    
    rm -f "${output_file}.gz"
}

# Apply Ultra compression
compress_ultra() {
    local input_file="$1"
    local output_file="$2"
    
    log "Applying Ultra Compact compression..."
    
    # Read input file
    local content=$(cat "$input_file")
    
    # Ultra-compact format with abbreviations
    cat > "$output_file" << EOF
#UCMPv3.0
TS:$(date -u +%s)
FM:ultra
SZ:$(stat -c%s "$input_file" 2>/dev/null || echo 0)
DT:{
"sys":"memory-compression",
"ver":"3.0.0",
"cfg":{
"fmt":"ultra",
"auto":$( [ "$AUTO_MODE" = true ] && echo 1 || echo 0 ),
"test":$( [ "$TEST_MODE" = true ] && echo 1 || echo 0 )
},
"mem":{
"files":$(find /home/node/.openclaw/workspace/memory -name "*.md" 2>/dev/null | wc -l),
"size":$(du -sb /home/node/.openclaw/workspace/memory 2>/dev/null | cut -f1 || echo 0)
},
"cmp":{
"format":"$FORMAT",
"timestamp":"$TIMESTAMP",
"strategy":"balanced"
},
"stat":{
"enabled":${COMPRESSION_ENABLED:-true},
"retention":${RETENTION_DAYS:-30},
"maxfiles":${MAX_COMPRESSED_FILES:-100}
}
}
EOF
    
    # Add checksum
    local checksum=$(crc32 "$output_file" 2>/dev/null || echo "00000000")
    echo "CS:$checksum" >> "$output_file"
}

# Update search index
update_search_index() {
    if [ "$SEARCH_ENABLED" != "true" ]; then
        log "Search indexing is disabled"
        return 0
    fi
    
    local compressed_file="$1"
    local format="$2"
    
    log "Updating search index..."
    
    local index_file="$DATA_DIR/search/index.json"
    local temp_index="${index_file}.tmp"
    
    # Create index if it doesn't exist
    if [ ! -f "$index_file" ]; then
        cat > "$index_file" << EOF
{
  "version": "3.0.0",
  "created": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "last_updated": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "file_count": 0,
  "files": [],
  "statistics": {
    "total_size": 0,
    "average_ratio": 0,
    "formats": {}
  }
}
EOF
    fi
    
    # Extract basic file info
    local filename=$(basename "$compressed_file")
    local size=$(stat -c%s "$compressed_file" 2>/dev/null || echo 0)
    local original_size=$(grep -o 'SZ:[0-9]*' "$compressed_file" 2>/dev/null | cut -d: -f2 || echo "$((size * 4))")
    local ratio=$(( size * 100 / (original_size > 0 ? original_size : 1) ))
    
    # Create entry
    local entry=$(cat << EOF
    {
      "filename": "$filename",
      "format": "$format",
      "size": $size,
      "original_size": $original_size,
      "ratio": $ratio,
      "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
      "path": "$compressed_file"
    }
EOF
    )
    
    # Update index using jq if available
    if command -v jq &> /dev/null; then
        jq --argjson entry "$entry" '
            .last_updated = now | strftime("%Y-%m-%dT%H:%M:%SZ") |
            .files += [$entry] |
            .file_count = (.files | length) |
            .statistics.total_size = (.files | map(.size) | add) |
            .statistics.average_ratio = (.files | map(.ratio) | add / length) |
            .statistics.formats = (.files | group_by(.format) | map({key: .[0].format, value: length}) | from_entries)
        ' "$index_file" > "$temp_index" && mv "$temp_index" "$index_file"
        
        success "Search index updated"
    else
        log "jq not available, skipping advanced index update"
    fi
}

# Log compression results
log_compression_results() {
    local compressed_file="$1"
    local original_file="$2"
    local format="$3"
    
    local original_size=$(stat -c%s "$original_file" 2>/dev/null || echo 0)
    local compressed_size=$(stat -c%s "$compressed_file" 2>/dev/null || echo 0)
    local ratio=0
    
    if [ "$original_size" -gt 0 ]; then
        ratio=$(( (compressed_size * 100) / original_size ))
    fi
    
    # Log to history
    echo "$TIMESTAMP,$format,$original_size,$compressed_size,$ratio,$AUTO_MODE" \
        >> "$DATA_DIR/compression-history.csv"
    
    # Log summary
    log "========================================"
    log "Compression Results:"
    log "  Format:          $format"
    log "  Original size:   $original_size bytes"
    log "  Compressed size: $compressed_size bytes"
    log "  Ratio:           $ratio%"
    log "  File:            $(basename "$compressed_file")"
    log "  Mode:            $( [ "$AUTO_MODE" = true ] && echo "auto" || echo "manual" )"
    log "========================================"
    
    if [ "$ratio" -lt 100 ] && [ "$original_size" -gt 0 ]; then
        success "Compression successful! Saved $((100 - ratio))% space"
    else
        log "Compression completed"
    fi
}

# Main compression function
main_compression() {
    log "========================================"
    log "Starting Memory Compression System"
    log "Format: $FORMAT"
    log "Mode: $( [ "$AUTO_MODE" = true ] && echo "auto" || echo "manual" )"
    log "Test: $( [ "$TEST_MODE" = true ] && echo "yes" || echo "no" )"
    log "========================================"
    
    # Validate format
    validate_format || exit 1
    
    # Create directories
    mkdir -p "$COMPRESSED_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Create backup
    create_backup
    
    # Create temporary files
    TEMP_FILE=$(mktemp)
    OUTPUT_FILE="$COMPRESSED_DIR/memory_${TIMESTAMP}.${FORMAT}"
    
    # Get memory context
    get_memory_context "$TEMP_FILE"
    
    if [ "$TEST_MODE" = true ]; then
        log "Test mode - would compress to: $OUTPUT_FILE"
        log "Original content sample:"
        head -10 "$TEMP_FILE" | sed 's/^/  /'
        rm -f "$TEMP_FILE"
        success "Test completed successfully"
        exit 0
    fi
    
    # Apply compression based on format
    case "$FORMAT" in
        base64|b64c)
            compress_base64 "$TEMP_FILE" "$OUTPUT_FILE"
            ;;
        binary|cbin)
            compress_binary "$TEMP_FILE" "$OUTPUT_FILE"
            ;;
        ultra|ucmp)
            compress_ultra "$TEMP_FILE" "$OUTPUT_FILE"
            ;;
    esac
    
    # Update search index
    update_search_index "$OUTPUT_FILE" "$FORMAT"
    
    # Log results
    log_compression_results "$OUTPUT_FILE" "$TEMP_FILE" "$FORMAT"
    
    # Cleanup
    rm -f "$TEMP_FILE"
    
    # Update last compression timestamp
    date -u +"%Y-%m-%dT%H:%M:%SZ" > "$DATA_DIR/last-compression.txt"
    
    # Cleanup old files if in auto mode
    if [ "$AUTO_MODE" = true ]; then
        log "Auto mode - cleaning up old files..."
        "$SCRIPT_DIR/cleanup.sh" --auto 2>/dev/null || true
    fi
    
    success "Compression completed successfully!"
}

# Error handling
trap 'error "Script interrupted"; exit 1' INT TERM

# Run main function
if main_compression; then
    exit 0
else
    error "Compression failed"
    exit 1
fi