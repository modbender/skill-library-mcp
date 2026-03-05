#!/usr/bin/env bash
#
# Backup and restore script for zotero-cli configuration and notes
#

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
BACKUP_DIR="$HOME/.zotero-cli-backups"
CONFIG_FILE="$HOME/.config/zotcli/config.ini"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Print header
print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}  Zotero-CLI Backup & Restore       ${NC}"
    echo -e "${BLUE}======================================${NC}"
    echo ""
}

# Print section
print_section() {
    echo -e "${GREEN}▶ $1${NC}"
    echo ""
}

# Print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_section "Checking Prerequisites"

    # Check if config exists
    if [ ! -f "$CONFIG_FILE" ]; then
        print_error "Configuration file not found: $CONFIG_FILE"
        echo "Please run 'zotcli configure' first."
        return 1
    else
        print_success "Configuration file found"
    fi

    # Create backup directory
    if [ ! -d "$BACKUP_DIR" ]; then
        echo "Creating backup directory: $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
        print_success "Backup directory created"
    else
        print_success "Backup directory exists"
    fi
    echo ""
}

# Backup configuration
backup_config() {
    print_section "Backing Up Configuration"

    backup_file="$BACKUP_DIR/config_$TIMESTAMP.ini"
    
    if [ -f "$CONFIG_FILE" ]; then
        cp "$CONFIG_FILE" "$backup_file"
        print_success "Configuration backed up to: $backup_file"
        
        # Compress old backups (keep last 5 uncompressed)
        cd "$BACKUP_DIR"
        ls -t config_*.ini 2>/dev/null | tail -n +6 | xargs -r gzip
        print_success "Old backups compressed"
        
        # List current backups
        echo ""
        echo "Current backups:"
        ls -lh "$BACKUP_DIR"/config_*.ini 2>/dev/null || ls -lh "$BACKUP_DIR"/config_*.ini.gz 2>/dev/null
    else
        print_error "No configuration file to backup"
    fi
    echo ""
}

# Backup notes and library data
backup_library_data() {
    print_section "Backing Up Library Data"

    # Get current item count
    echo "Attempting to retrieve library data..."
    
    # Create a backup file with all items
    backup_file="$BACKUP_DIR/library_$TIMESTAMP.json"
    
    # Try to query the library (this requires zotcli to be configured)
    if command -v zotcli &> /dev/null; then
        print_success "zotcli found, attempting to export library..."
        
        # Export all items (this may take time)
        echo "Note: This may take a while for large libraries..."
        
        # Try to export to a text file (zotero-cli doesn't have built-in export, 
        # but we can capture the query output)
        output_file="$BACKUP_DIR/library_list_$TIMESTAMP.txt"
        zotcli query "*" > "$output_file" 2>&1 || true
        
        if [ -s "$output_file" ]; then
            print_success "Library list exported to: $output_file"
        else
            print_warning "Library may be empty or query failed"
        fi
    else
        print_warning "zotcli not found, skipping library export"
    fi
    echo ""
}

# Backup custom scripts and queries
backup_custom_content() {
    print_section "Backing Up Custom Content"

    # Backup scripts directory if it exists
    if [ -d "$HOME/.config/zotcli/scripts" ]; then
        backup_dir="$BACKUP_DIR/scripts_$TIMESTAMP"
        cp -r "$HOME/.config/zotcli/scripts" "$backup_dir"
        print_success "Custom scripts backed up to: $backup_dir"
    else
        print_warning "No custom scripts found"
    fi

    # Backup query files if they exist in common locations
    query_locations=(
        "$HOME/.config/zotcli/queries"
        "$HOME/zotero-queries"
        "./queries.txt"
    )

    for location in "${query_locations[@]}"; do
        if [ -f "$location" ]; then
            backup_file="$BACKUP_DIR/queries_$TIMESTAMP.txt"
            cp "$location" "$backup_file"
            print_success "Query file backed up: $backup_file"
        fi
    done
    echo ""
}

# Run full backup
run_backup() {
    print_section "Starting Full Backup"
    echo ""
    
    if check_prerequisites; then
        backup_config
        backup_library_data
        backup_custom_content
        
        print_section "Backup Complete"
        print_success "Backup completed successfully"
        echo ""
        echo "Backup location: $BACKUP_DIR"
        echo "Backup timestamp: $TIMESTAMP"
        echo ""
        echo "To restore from this backup, use:"
        echo "  $0 restore --date $TIMESTAMP"
        echo ""
    else
        print_error "Backup failed. See errors above."
        return 1
    fi
}

# List available backups
list_backups() {
    print_section "Available Backups"
    echo ""
    
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A $BACKUP_DIR 2>/dev/null)" ]; then
        print_warning "No backups found in $BACKUP_DIR"
        return 1
    fi

    echo "Configuration backups:"
    ls -lh "$BACKUP_DIR"/config_*.ini 2>/dev/null || echo "  None"
    echo ""
    
    echo "Library data backups:"
    ls -lh "$BACKUP_DIR"/library_*.txt 2>/dev/null || echo "  None"
    echo ""
    
    echo "Custom content backups:"
    ls -lh "$BACKUP_DIR"/scripts_* 2>/dev/null || echo "  None"
    ls -lh "$BACKUP_DIR"/queries_*.txt 2>/dev/null || echo "  None"
    echo ""
}

# Restore backup
restore_backup() {
    local backup_date="$1"
    
    print_section "Restoring from Backup: $backup_date"
    echo ""
    
    if [ -z "$backup_date" ]; then
        print_error "Please specify a backup date (e.g., ./backup_restore.sh restore --date 20250109_100000)"
        return 1
    fi

    # Check if backup exists
    if [ ! -d "$BACKUP_DIR" ]; then
        print_error "Backup directory not found"
        return 1
    fi

    # Restore configuration
    config_backup="$BACKUP_DIR/config_$backup_date.ini"
    if [ -f "$config_backup" ]; then
        print_section "Restoring Configuration"
        
        # Backup current config before restoring
        current_backup="$BACKUP_DIR/config_before_restore_$TIMESTAMP.ini"
        [ -f "$CONFIG_FILE" ] && cp "$CONFIG_FILE" "$current_backup"
        print_success "Current configuration backed up to: $current_backup"
        
        # Restore
        cp "$config_backup" "$CONFIG_FILE"
        print_success "Configuration restored from: $config_backup"
        echo ""
    else
        print_warning "Configuration backup not found: $config_backup"
    fi

    # Restore library data if exists
    library_backup="$BACKUP_DIR/library_list_$backup_date.txt"
    if [ -f "$library_backup" ]; then
        print_section "Library Data"
        print_success "Library data found: $library_backup"
        print_warning "Note: Library data is for reference only."
        print_warning "To restore notes/items to Zotero, you may need to use the Zotero desktop application."
        echo ""
    fi

    # Restore custom scripts if exists
    scripts_backup="$BACKUP_DIR/scripts_$backup_date"
    if [ -d "$scripts_backup" ]; then
        print_section "Restoring Custom Scripts"
        mkdir -p "$HOME/.config/zotcli"
        cp -r "$scripts_backup" "$HOME/.config/zotcli/scripts"
        print_success "Custom scripts restored to: $HOME/.config/zotcli/scripts"
        echo ""
    fi

    # Restore queries if exists
    queries_backup="$BACKUP_DIR/queries_$backup_date.txt"
    if [ -f "$queries_backup" ]; then
        print_section "Restoring Query Files"
        cp "$queries_backup" "$HOME/queries_restored_$TIMESTAMP.txt"
        print_success "Query files restored to: $HOME/queries_restored_$TIMESTAMP.txt"
        echo ""
    fi

    print_section "Restore Complete"
    print_success "Backup restored successfully"
    echo ""
    print_warning "Please verify your zotero-cli configuration:"
    echo "  zotcli query \"test\""
    echo ""
}

# Clean old backups
clean_old_backups() {
    print_section "Cleaning Old Backups"
    echo ""
    
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A $BACKUP_DIR 2>/dev/null)" ]; then
        print_warning "No backups found"
        return 1
    fi

    # Ask for confirmation
    echo "This will delete backups older than 30 days."
    read -p "Continue? (y/n): " confirm

    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        return 0
    fi

    # Find and remove old backups
    old_backups=$(find "$BACKUP_DIR" -name "config_*" -mtime +30 -o -name "library_*" -mtime +30 2>/dev/null)

    if [ -n "$old_backups" ]; then
        echo "Removing old backups..."
        echo "$old_backups" | while read -r file; do
            rm -rf "$file"
            print_success "Removed: $file"
        done
        print_success "Cleanup complete"
    else
        print_success "No old backups to remove"
    fi
    echo ""
}

# Print usage
usage() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  backup              Run a full backup"
    echo "  list                List available backups"
    echo "  restore --date DATE Restore from a specific backup (format: YYYYMMDD_HHMMSS)"
    echo "  clean               Clean older backups (>30 days)"
    echo ""
    echo "Examples:"
    echo "  $0 backup"
    echo "  $0 list"
    echo "  $0 restore --date 20250109_100000"
    echo "  $0 clean"
    echo ""
    exit 1
}

# Main execution
main() {
    print_header

    case "${1:-}" in
        backup)
            run_backup
            ;;
        list)
            list_backups
            ;;
        restore)
            if [[ "${2:-}" == "--date" ]]; then
                restore_backup "${3:-}"
            else
                print_error "Missing --date parameter"
                usage
            fi
            ;;
        clean)
            clean_old_backups
            ;;
        *)
            usage
            ;;
    esac
}

# Run main function
main "$@"
