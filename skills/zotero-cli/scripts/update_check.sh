#!/usr/bin/env bash
#
# Update check and management script for zotero-cli
#

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# GitHub repository
REPO="jbaiter/zotero-cli"
REPO_URL="https://github.com/$REPO"
PYPI_URL="https://pypi.org/pypi/zotero-cli/json"

# Print header
print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}  Zotero-CLI Update Manager          ${NC}"
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

# Check command availability
check_command() {
    if command -v "$1" &> /dev/null; then
        true
    else
        false
    fi
}

# Get current version
get_current_version() {
    if check_command zotcli; then
        zotcli --version 2>&1 | grep -oP '\d+\.\d+\.\d+' || echo "unknown"
    else
        echo "not installed"
    fi
}

# Get latest version from PyPI
get_pypi_version() {
    if check_command curl; then
        curl -s "$PYPI_URL" | grep -oP '"version":\s*"\K[^"]+' | head -1
    elif check_command wget; then
        wget -qO- "$PYPI_URL" | grep -oP '"version":\s*"\K[^"]+' | head -1
    else
        echo "unable to fetch"
    fi
}

# Get latest version from GitHub
get_github_version() {
    if check_command curl; then
        curl -s "https://api.github.com/repos/$REPO/releases/latest" | grep -oP '"tag_name":\s*"\K[^"]+' | sed 's/^v//'
    elif check_command wget; then
        wget -qO- "https://api.github.com/repos/$REPO/releases/latest" | grep -oP '"tag_name":\s*"\K[^"]+' | sed 's/^v//'
    else
        echo "unable to fetch"
    fi
}

# Compare versions
compare_versions() {
    local current="$1"
    local latest="$2"
    
    if [[ "$current" == "not installed" ]] || [[ "$current" == "unknown" ]]; then
        echo "install"
    elif [[ "$latest" == "unable to fetch" ]]; then
        echo "unknown"
    else
        if [ "$current" == "$latest" ]; then
            echo "up-to-date"
        else
            # Simple version comparison (assumes semantic versioning)
            IFS='.' read -ra CURR <<< "$current"
            IFS='.' read -ra LAT <<< "$latest"
            
            for i in 0 1 2; do
                if [ "${CURR[$i]:-0}" -lt "${LAT[$i]:-0}" ]; then
                    echo "update-available"
                    return
                elif [ "${CURR[$i]:-0}" -gt "${LAT[$i]:-0}" ]; then
                    echo "newer"
                    return
                fi
            done
            echo "up-to-date"
        fi
    fi
}

# Check for updates
check_updates() {
    print_section "Checking for Updates"
    echo ""
    
    # Get versions
    current_version=$(get_current_version)
    pypi_version=$(get_pypi_version)
    github_version=$(get_github_version)
    
    echo "Current version:  $current_version"
    echo "PyPI version:     $pypi_version"
    echo "GitHub version:   $github_version"
    echo ""
    
    # Determine which latest version to use
    if [[ "$github_version" == "unable to fetch" ]]; then
        latest_version="$pypi_version"
        
    elif [[ "$pypi_version" == "unable to fetch" ]]; then
        latest_version="$github_version"
    else
        # Use the newer of pypi or github
        latest_version="$github_version"
        
        # Compare pypi vs github
        if compare_versions "$github_version" "$pypi_version" &> /dev/null; then
            if [ $? -eq 1 ]; then
                latest_version="$pypi_version"
            fi
        fi
    fi
    
    # Compare current vs latest
    if [[ "$latest_version" == "unable to fetch" ]]; then
        print_warning "unable to determine latest version"
        print_warning "Please check $REPO_URL manually"
        return 1
    fi
    
    status=$(compare_versions "$current_version" "$latest_version")
    
    echo "Latest version:   $latest_version"
    echo ""
    
    case "$status" in
        "up-to-date")
            print_success "You are running the latest version!"
            ;;
        "update-available")
            print_warning "A new version is available!"
            echo ""
            echo "Current:  $current_version"
            echo "Latest:   $latest_version"
            echo ""
            
            # Check installation method
            if check_command pipx; then
                echo "To update, run:"
                echo "  pipx upgrade zotero-cli"
            else
                echo "To update, run:"
                echo "  pip install --upgrade zotero-cli"
                echo "  Or:"
                echo "  pip install --upgrade --user zotero-cli"
            fi
            ;;
        "newer")
            print_warning "You are running a newer version than the latest release"
            print_warning "This might be a development or pre-release version"
            ;;
        "install")
            print_warning "zotero-cli is not installed"
            echo ""
            echo "To install, run:"
            echo "  pipx install zotero-cli"
            echo "  Or:"
            echo "  pip install --user zotero-cli"
            ;;
        *)
            print_warning "Unable to compare versions"
            ;;
    esac
    echo ""
}

# Update zotero-cli
update_zotcli() {
    print_section "Updating zotero-cli"
    echo ""
    
    # Check current installation method
    if check_command pipx; then
        print_success "Using pipx for update"
        
        echo "Running: pipx upgrade zotero-cli"
        pipx upgrade zotero-cli
        
        if [ $? -eq 0 ]; then
            print_success "Update successful!"
            new_version=$(get_current_version)
            echo "New version: $new_version"
        else
            print_error "Update failed"
            return 1
        fi
        
    elif check_command pip3; then
        print_warning "pipx not found, using pip"
        
        # Try to determine if it's a user install
        if zotcli &> /dev/null; then
            zotcli_path=$(which zotcli)
            
            if [[ "$zotcli_path" == *".local/bin"* ]]; then
                echo "Running: pip install --upgrade zotero-cli"
                pip install --upgrade zotero-cli
            else
                echo "Running: pip install --upgrade --user zotero-cli"
                pip install --upgrade --user zotero-cli
            fi
            
            if [ $? -eq 0 ]; then
                print_success "Update successful!"
                new_version=$(get_current_version)
                echo "New version: $new_version"
            else
                print_error "Update failed"
                return 1
            fi
        else
            print_error "zotero-cli installation not detected"
            return 1
        fi
        
    else
        print_error "Neither pipx nor pip found. Cannot update."
        return 1
    fi
    
    echo ""
}

# Show update history or changelog
show_changelog() {
    print_section "Show Changelog"
    echo ""
    
    if check_command curl; then
        echo "Opening GitHub releases page..."
        echo ""
        echo "Visit: $REPO_URL/releases"
        echo ""
        
        # Try to open in browser if available
        if check_command xdg-open; then
            xdg-open "$REPO_URL/releases" &> /dev/null &
        elif check_command open; then
            open "$REPO_URL/releases" &> /dev/null &
        else
            print_warning "Browser not detected. Please visit the URL manually."
        fi
    else
        print_warning "curl not found. Cannot fetch changelog."
        echo "Please visit $REPO_URL/releases manually."
    fi
    echo ""
}

# Install latest version
install_latest() {
    print_section "Installing Latest Version"
    echo ""
    
    # Check prerequisites
    if ! check_command python3; then
        print_error "Python 3 not found"
        return 1
    fi
    
    # Installation options
    echo "Choose installation method:"
    echo "  1. pipx (recommended for PEP 668-compliant systems)"
    echo "  2. pip --user (user installation)"
    echo ""
    read -p "Enter your choice (1-2): " choice
    
    case "$choice" in
        1)
            if ! check_command pipx; then
                print_warning "pipx not found, installing..."
                
                if check_command apt; then
                    sudo apt update && sudo apt install pipx -y
                    pipx ensurepath
                    export PATH="$HOME/.local/bin:$PATH"
                else
                    print_error "Cannot install pipx automatically"
                    echo "Please install pipx manually and try again."
                    return 1
                fi
            fi
            
            echo "Installing latest release via pipx..."
            pipx install zotero-cli
            ;;
        2)
            echo "Installing via pip --user..."
            pip install --user zotero-cli
            ;;
        *)
            print_error "Invalid choice"
            return 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        print_success "Installation successful!"
        echo ""
        print_success "Next steps:"
        echo "  1. Run 'zotcli configure'"
        echo "  2. Run '$(dirname "$0")/setup_and_check.sh' to verify"
        echo ""
    else
        print_error "Installation failed"
        return 1
    fi
    echo ""
}

# Print usage
usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  check          Check for available updates"
    echo "  update         Update to the latest version"
    echo "  changelog      Show changelog on GitHub"
    echo "  install        Install the latest version"
    echo ""
    echo "Examples:"
    echo "  $0 check"
    echo "  $0 update"
    echo "  $0 changelog"
    echo "  $0 install"
    echo ""
}

# Main execution
main() {
    print_header

    case "${1:-}" in
        check)
            check_updates
            ;;
        update)
            check_updates
            update_zotcli
            ;;
        changelog)
            show_changelog
            ;;
        install)
            install_latest
            ;;
        *)
            usage
            ;;
    esac
}

# Run main function
main "$@"
