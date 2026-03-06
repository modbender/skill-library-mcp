#!/bin/bash
#
# Mac Disk Cleanup Script
# Safely analyzes and cleans common disk space hogs on macOS
# Suitable for everyday Mac users

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track space freed
SPACE_FREED=0

print_header() {
    echo ""
    echo "========================================"
    echo "  Mac Disk Cleanup Tool"
    echo "========================================"
    echo ""
}

print_section() {
    echo ""
    echo -e "${BLUE}$1${NC}"
    echo "----------------------------------------"
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS
check_macos() {
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This script is designed for macOS only."
        exit 1
    fi
}

# Analyze disk usage
analyze_disk() {
    print_section "📊 Disk Usage Overview"
    
    df -h / | grep -E "^/dev" | awk '{printf "Total: %s  Used: %s  Available: %s  (%s used)\n", $2, $3, $4, $5}'
    echo ""
    
    # Check main space hogs in home directory
    print_info "Top space consumers in your home directory:"
    du -h -d 1 ~ 2>/dev/null | sort -hr | head -15
}

# Find common large items
find_large_items() {
    print_section "🔍 Finding Large Items"
    
    # iOS Simulators
    local simulators_size=0
    if command -v xcrun &> /dev/null; then
        simulators_size=$(find ~/Library/Developer/CoreSimulator/Devices -maxdepth 0 -exec du -sm {} \; 2>/dev/null | awk '{print $1}' || echo "0")
        if [[ $simulators_size -gt 0 ]]; then
            print_warning "iOS Simulators: ~${simulators_size}MB ($(xcrun simctl list devices 2>/dev/null | grep -c "(Booted)\|(Shutdown)" || echo "0") devices)"
        fi
    fi
    
    # iOS Backups
    local ios_backups=~/Library/Application\ Support/MobileSync/Backup
    if [[ -d "$ios_backups" ]]; then
        local backup_size=$(du -sm "$ios_backups" 2>/dev/null | awk '{print $1}' || echo "0")
        if [[ $backup_size -gt 0 ]]; then
            print_warning "iOS Device Backups: ~${backup_size}MB"
        fi
    fi
    
    # Xcode Derived Data
    local derived_data=~/Library/Developer/Xcode/DerivedData
    if [[ -d "$derived_data" ]]; then
        local dd_size=$(du -sm "$derived_data" 2>/dev/null | awk '{print $1}' || echo "0")
        if [[ $dd_size -gt 100 ]]; then
            print_warning "Xcode Derived Data: ~${dd_size}MB"
        fi
    fi
    
    # User Caches
    local cache_size=$(du -sm ~/Library/Caches 2>/dev/null | awk '{print $1}' || echo "0")
    if [[ $cache_size -gt 500 ]]; then
        print_warning "User Caches: ~${cache_size}MB"
    fi
    
    # Downloads folder
    local downloads_size=$(du -sm ~/Downloads 2>/dev/null | awk '{print $1}' || echo "0")
    if [[ $downloads_size -gt 1000 ]]; then
        print_warning "Downloads folder: ~${downloads_size}MB"
    fi
    
    # Trash
    local trash_size=$(du -sm ~/.Trash 2>/dev/null | awk '{print $1}' || echo "0")
    if [[ $trash_size -gt 0 ]]; then
        print_warning "Trash: ~${trash_size}MB"
    fi
}

# Clean user caches
clean_caches() {
    print_section "🧹 Cleaning User Caches"
    
    local cache_size=$(du -sm ~/Library/Caches 2>/dev/null | awk '{print $1}' || echo "0")
    
    if [[ $cache_size -gt 100 ]]; then
        print_info "Clearing user caches (~${cache_size}MB)..."
        rm -rf ~/Library/Caches/*
        SPACE_FREED=$((SPACE_FREED + cache_size))
        print_info "Caches cleared."
    else
        print_info "Caches are already small (${cache_size}MB), skipping."
    fi
}

# Clean Xcode derived data
clean_xcode() {
    print_section "🛠️ Cleaning Xcode Data"
    
    if [[ -d ~/Library/Developer/Xcode/DerivedData ]]; then
        local dd_size=$(du -sm ~/Library/Developer/Xcode/DerivedData 2>/dev/null | awk '{print $1}' || echo "0")
        
        if [[ $dd_size -gt 100 ]]; then
            print_info "Clearing Xcode Derived Data (~${dd_size}MB)..."
            rm -rf ~/Library/Developer/Xcode/DerivedData/*
            rm -rf ~/Library/Developer/Xcode/iOS\ DeviceSupport/* 2>/dev/null || true
            SPACE_FREED=$((SPACE_FREED + dd_size))
            print_info "Xcode data cleared."
        else
            print_info "Xcode Derived Data is small (${dd_size}MB), skipping."
        fi
    else
        print_info "Xcode not detected, skipping."
    fi
}

# Clean iOS simulators (unavailable ones)
clean_simulators() {
    print_section "📱 Cleaning iOS Simulators"
    
    if ! command -v xcrun &> /dev/null; then
        print_info "Xcode command line tools not found, skipping simulators."
        return
    fi
    
    # Count simulators before
    local before_count=$(xcrun simctl list devices 2>/dev/null | grep -c "(Shutdown)" || echo "0")
    
    print_info "Removing unavailable iOS simulators..."
    xcrun simctl delete unavailable 2>/dev/null || true
    
    # Count after
    local after_count=$(xcrun simctl list devices 2>/dev/null | grep -c "(Shutdown)" || echo "0")
    local removed=$((before_count - after_count))
    
    if [[ $removed -gt 0 ]]; then
        print_info "Removed $removed unavailable simulator(s)."
    else
        print_info "No unavailable simulators found."
    fi
}

# Empty trash
empty_trash() {
    print_section "🗑️ Emptying Trash"
    
    local trash_size=$(du -sm ~/.Trash 2>/dev/null | awk '{print $1}' || echo "0")
    
    if [[ $trash_size -gt 0 ]]; then
        print_info "Emptying trash (~${trash_size}MB)..."
        osascript -e 'tell application "Finder" to empty trash' 2>/dev/null || rm -rf ~/.Trash/*
        SPACE_FREED=$((SPACE_FREED + trash_size))
        print_info "Trash emptied."
    else
        print_info "Trash is already empty."
    fi
}

# Clean system logs (safely)
clean_logs() {
    print_section "📋 Cleaning System Logs"
    
    local log_size=$(sudo du -sm /var/log 2>/dev/null | awk '{print $1}' || echo "0")
    
    if [[ $log_size -gt 500 ]]; then
        print_info "System logs are large (~${log_size}MB)."
        print_warning "Cleaning old logs requires sudo. Only removing logs older than 7 days..."
        
        sudo find /var/log -name "*.log.*" -mtime +7 -delete 2>/dev/null || true
        sudo find /var/log -name "*.gz" -mtime +30 -delete 2>/dev/null || true
        
        local new_log_size=$(sudo du -sm /var/log 2>/dev/null | awk '{print $1}' || echo "0")
        local freed=$((log_size - new_log_size))
        SPACE_FREED=$((SPACE_FREED + freed))
        print_info "Cleaned ~${freed}MB of old logs."
    else
        print_info "System logs are small (${log_size}MB), skipping."
    fi
}

# Clean browser caches
clean_browser_caches() {
    print_section "🌐 Cleaning Browser Caches"
    
    local browser_cache=0
    
    # Chrome
    if [[ -d ~/Library/Caches/Google/Chrome ]]; then
        local chrome_size=$(du -sm ~/Library/Caches/Google/Chrome 2>/dev/null | awk '{print $1}' || echo "0")
        rm -rf ~/Library/Caches/Google/Chrome/Default/Cache/* 2>/dev/null || true
        browser_cache=$((browser_cache + chrome_size))
    fi
    
    # Safari
    if [[ -d ~/Library/Caches/com.apple.Safari ]]; then
        rm -rf ~/Library/Caches/com.apple.Safari/Cache.db 2>/dev/null || true
    fi
    
    # Firefox
    if [[ -d ~/Library/Caches/Firefox ]]; then
        rm -rf ~/Library/Caches/Firefox/Profiles/*/cache2/* 2>/dev/null || true
    fi
    
    if [[ $browser_cache -gt 0 ]]; then
        print_info "Cleared browser caches (~${browser_cache}MB)."
        SPACE_FREED=$((SPACE_FREED + browser_cache))
    else
        print_info "Browser caches are small or not found."
    fi
}

# Show final summary
show_summary() {
    print_section "✅ Cleanup Complete"
    
    if [[ $SPACE_FREED -gt 0 ]]; then
        print_info "Estimated space freed: ~${SPACE_FREED}MB (~$((SPACE_FREED / 1024))GB)"
    else
        print_info "No significant space was freed (everything was already clean)."
    fi
    
    echo ""
    print_info "Current disk status:"
    df -h / | grep -E "^/dev" | awk '{printf "Total: %s  Used: %s  Available: %s  (%s used)\n", $2, $3, $4, $5}'
    
    echo ""
    echo "💡 Tips for ongoing maintenance:"
    echo "   - Empty Downloads folder regularly"
    echo "   - Review iOS device backups in Finder"
    echo "   - Delete old Xcode archives: ~/Library/Developer/Xcode/Archives"
    echo "   - Check Parallels VMs if you use Windows"
}

# Main execution
main() {
    print_header
    check_macos
    
    # Parse arguments
    local MODE="${1:-analyze}"
    
    case "$MODE" in
        analyze)
            analyze_disk
            find_large_items
            echo ""
            print_info "Run with 'clean' argument to perform cleanup:"
            echo "   $0 clean"
            ;;
        clean)
            print_warning "This will clean temporary files and caches."
            read -p "Continue? (y/N): " confirm
            if [[ $confirm != [yY] ]]; then
                print_info "Cleanup cancelled."
                exit 0
            fi
            
            clean_caches
            clean_xcode
            clean_simulators
            clean_browser_caches
            clean_logs
            empty_trash
            show_summary
            ;;
        *)
            echo "Usage: $0 [analyze|clean]"
            echo ""
            echo "  analyze  - Show disk usage and large items (default)"
            echo "  clean    - Perform safe cleanup"
            exit 1
            ;;
    esac
}

main "$@"
