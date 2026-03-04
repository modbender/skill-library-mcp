#!/bin/bash
# OPNsense Configuration Backup Script
# Creates timestamped backups of OPNsense configuration

# Configuration
OPNSENSE_HOST="${OPNSENSE_HOST:-192.168.1.1}"
OPNSENSE_PORT="${OPNSENSE_PORT:-443}"
OPNSENSE_KEY="${OPNSENSE_KEY:-}"
OPNSENSE_SECRET="${OPNSENSE_SECRET:-}"
OPNSENSE_INSECURE="${OPNSENSE_INSECURE:-false}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
KEEP_DAYS="${KEEP_DAYS:-30}"

# Load credentials from file if not set
if [[ -z "$OPNSENSE_KEY" && -f ~/.opnsense/credentials ]]; then
    source ~/.opnsense/credentials
fi

# Parse arguments
CONFIG_ONLY=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -k|--keep)
            KEEP_DAYS="$2"
            shift 2
            ;;
        -c|--config-only)
            CONFIG_ONLY=true
            shift
            ;;
        --insecure)
            OPNSENSE_INSECURE="true"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Set curl flags based on security preference
INSECURE_FLAG=""
if [[ "$OPNSENSE_INSECURE" == "true" ]]; then
    INSECURE_FLAG="-k"
fi

show_help() {
    cat << EOF
OPNsense Configuration Backup

Usage: $0 [options]

Options:
    -d, --dir <path>        Backup directory (default: ./backups)
    -k, --keep <days>       Keep backups for N days (default: 30)
    -c, --config-only       Only backup config.xml (not RRD)
    --insecure              Disable SSL certificate validation (NOT recommended)
    -h, --help              Show this help

Environment:
    OPNSENSE_KEY            API key
    OPNSENSE_SECRET         API secret
    OPNSENSE_INSECURE       Set to 'true' to disable SSL verification
    BACKUP_DIR              Backup directory
    KEEP_DAYS               Retention period

Security Note:
    By default, SSL certificate validation is ENABLED.
    Use --insecure only for development or self-signed certificates.

Examples:
    $0                          # Full backup with defaults
    $0 -d /mnt/backups/opnsense -k 90
    $0 --config-only            # Smaller backup without RRD data
    $0 --insecure               # For self-signed certificates
EOF
}

# Check credentials
if [[ -z "$OPNSENSE_KEY" || -z "$OPNSENSE_SECRET" ]]; then
    echo "Error: API credentials not configured"
    echo "Set OPNSENSE_KEY and OPNSENSE_SECRET environment variables"
    echo "Or create ~/.opnsense/credentials with:"
    echo "  OPNSENSE_KEY=your_key"
    echo "  OPNSENSE_SECRET=your_secret"
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/opnsense_backup_${TIMESTAMP}.xml"

echo "Creating OPNsense backup..."
echo "  Host: $OPNSENSE_HOST"
echo "  Destination: $BACKUP_FILE"
echo "  Config only: $CONFIG_ONLY"
echo "  SSL verification: $([ -z "$INSECURE_FLAG" ] && echo 'ENABLED' || echo 'DISABLED')"

# Download backup
if [[ "$CONFIG_ONLY" == true ]]; then
    curl -s $INSECURE_FLAG -u "${OPNSENSE_KEY}:${OPNSENSE_SECRET}" \
        "https://${OPNSENSE_HOST}:${OPNSENSE_PORT}/api/core/backup/backup" \
        -o "$BACKUP_FILE"
else
    # Full backup including RRD data
    curl -s $INSECURE_FLAG -u "${OPNSENSE_KEY}:${OPNSENSE_SECRET}" \
        "https://${OPNSENSE_HOST}:${OPNSENSE_PORT}/api/core/backup/backup?rrd=true" \
        -o "$BACKUP_FILE"
fi

# Verify backup
if [[ -f "$BACKUP_FILE" && -s "$BACKUP_FILE" ]]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "✓ Backup created successfully: $SIZE"
    
    # Show backup info
    if grep -q '<opnsense>' "$BACKUP_FILE" 2>/dev/null; then
        VERSION=$(grep -o '<version>[^<]*</version>' "$BACKUP_FILE" | head -1 | sed 's/<[^>]*>//g')
        echo "  Version: $VERSION"
    fi
else
    echo "✗ Backup failed"
    rm -f "$BACKUP_FILE"
    exit 1
fi

# Cleanup old backups
if [[ "$KEEP_DAYS" -gt 0 ]]; then
    echo "Cleaning up backups older than $KEEP_DAYS days..."
    find "$BACKUP_DIR" -name "opnsense_backup_*.xml" -mtime +$KEEP_DAYS -delete
fi

# List recent backups
echo ""
echo "Recent backups:"
ls -lh "$BACKUP_DIR"/opnsense_backup_*.xml 2>/dev/null | tail -5

echo ""
echo "Backup complete: $BACKUP_FILE"
