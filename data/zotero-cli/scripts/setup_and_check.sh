#!/usr/bin/env bash
#
# Quick setup and verification script for zotero-cli
# This script helps you get started quickly and verifies your installation
#

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}   Zotero-CLI Quick Setup & Check    ${NC}"
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

# Check Python installation
check_python() {
    print_section "Checking Python Installation"

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

        print_success "Python 3 found: version $PYTHON_VERSION"

        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
            print_error "Python 3.7+ is required. You have $PYTHON_VERSION"
            return 1
        else
            print_success "Python version is compatible"
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
    echo ""
}

# Check pip installation
check_pip() {
    print_section "Checking pip Installation"

    if command -v pip3 &> /dev/null; then
        PIP_VERSION=$(pip3 --version)
        print_success "pip found: $PIP_VERSION"
    else
        print_warning "pip3 not found. You may need to install it."
    fi

    if command -v pipx &> /dev/null; then
        PIPX_VERSION=$(pipx --version)
        print_success "pipx found: $PIPX_VERSION"
    else
        print_warning "pipx not found. It's recommended for PEP 668-compliant systems."
    fi
    echo ""
}

# Check zotero-cli installation
check_zotcli() {
    print_section "Checking zotero-cli Installation"

    if command -v zotcli &> /dev/null; then
        ZOTCLI_VERSION=$(zotcli --version 2>&1 || echo "unknown")
        print_success "zotcli found: version $ZOTCLI_VERSION"
        
        # Check which installation method was used
        WHICH_ZOTCLI=$(which zotcli)
        echo "Location: $WHICH_ZOTCLI"

        if [[ "$WHICH_ZOTCLI" == *".local/bin"* ]]; then
            print_success "Installed via user installation"
        elif [[ "$WHICH_ZOTCLI" == *"pipx"* ]]; then
            print_success "Installed via pipx (recommended for PEP 668 systems)"
        fi
        echo ""
        return 0
    else
        print_error "zotcli not found"
        echo ""
        return 1
    fi
}

# Check zotero-cli configuration
check_configuration() {
    print_section "Checking zotero-cli Configuration"

    if [ -f ~/.config/zotcli/config.ini ]; then
        print_success "Configuration file exists"
        
        # Check file permissions
        PERMS=$(stat -c "%a" ~/.config/zotcli/config.ini 2>/dev/null || stat -f "%OLp" ~/.config/zotcli/config.ini 2>/dev/null)
        echo "Permissions: $PERMS"
        
        if [ "$PERMS" == "600" ]; then
            print_success "Configuration file has secure permissions"
        else
            print_warning "Consider setting secure permissions: chmod 600 ~/.config/zotcli/config.ini"
        fi
    else
        print_warning "Configuration file not found. You need to run 'zotcli configure'"
    fi
    echo ""
}

# Check optional tools
check_optional_tools() {
    print_section "Checking Optional Tools"

    if command -v pandoc &> /dev/null; then
        PANDOC_VERSION=$(pandoc --version | head -1)
        print_success "pandoc found: $PANDOC_VERSION"
        print_success "Note format conversion will work correctly"
    else
        print_warning "pandoc not found. Install it for note format conversion."
    fi
    echo ""
}

# Test basic functionality
test_basic_functionality() {
    print_section "Testing Basic Functionality"

    echo "Running test query..."
    TEST_OUTPUT=$(zotcli query "test" 2>&1 || true)

    if [[ "$TEST_OUTPUT" == *"Error"* ]] || [[ "$TEST_OUTPUT" == *"error"* ]]; then
        print_error "Test query failed. This might indicate a configuration issue."
        echo "Error output: $TEST_OUTPUT"
        return 1
    else
        print_success "Test query successful"
        print_success "zotero-cli is properly configured"
    fi
    echo ""
}

# Offer installation
offer_installation() {
    print_section "Installation Options"

    echo "zotero-cli is not installed. Choose an installation method:"
    echo ""
    echo "1. pipx (Recommended for PEP 668-compliant systems)"
    echo "2. pip --user (User installation)"
    echo "3. manual (Manual instructions)"
    echo ""
    read -p "Enter your choice (1-3): " choice

    case $choice in
        1)
            if ! command -v pipx &> /dev/null; then
                echo ""
                print_warning "pipx is not installed. Installing pipx..."
                
                if command -v apt &> /dev/null; then
                    sudo apt update && sudo apt install pipx -y
                    pipx ensurepath
                    export PATH="$HOME/.local/bin:$PATH"
                elif command -v pacman &> /dev/null; then
                    sudo pacman -S pipx
                    pipx ensurepath
                    export PATH="$HOME/.local/bin:$PATH"
                elif command -v dnf &> /dev/null; then
                    sudo dnf install pipx
                    pipx ensurepath
                    export PATH="$HOME/.local/bin:$PATH"
                else
                    print_error "Unable to install pipx automatically. Please install it manually."
                    return 1
                fi
            fi

            echo ""
            echo "Installing zotero-cli via pipx..."
            pipx install zotero-cli
            ;;
        2)
            echo ""
            echo "Installing zotero-cli via pip --user..."
            pip3 install --user zotero-cli
            
            # Add to PATH if not already
            if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
                echo ""
                echo "Adding ~/.local/bin to PATH..."
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
                export PATH="$HOME/.local/bin:$PATH"
            fi
            ;;
        3)
            echo ""
            echo "Manual installation instructions:"
            echo ""
            echo "1. Using pipx:"
            echo "   pipx install zotero-cli"
            echo ""
            echo "2. Using pip with user installation:"
            echo "   pip install --user zotero-cli"
            echo ""
            echo "3. Or, install from GitHub for latest version:"
            echo "   pip install git+git://github.com/jbaiter/zotero-cli.git@master"
            echo ""
            echo "See INSTALL.md for detailed instructions."
            ;;
        *)
            print_error "Invalid choice"
            return 1
            ;;
    esac
    echo ""
}

# Offer configuration assistance
offer_configuration() {
    print_section "Configuration Assistance"

    if [ ! -f ~/.config/zotcli/config.ini ]; then
        print_warning "Configuration file not found"
        echo ""
        echo "Do you want to configure zotero-cli now?"
        echo "This will guide you through:"
        echo "  1. Setting up your Zotero userID"
        echo "  2. Generating an API key"
        echo ""
        read -p "Run configuration? (y/n): " config_choice

        if [[ "$config_choice" == "y" ]] || [[ "$config_choice" == "Y" ]]; then
            zotcli configure
            if [ $? -eq 0 ]; then
                print_success "Configuration successful!"
            else
                print_error "Configuration failed. Please check for errors above."
            fi
        fi
    else
        print_success "Configuration file already exists"
        echo ""
        echo "Do you want to reconfigure zotero-cli?"
        read -p "Reconfigure? (y/n): " reconfig_choice

        if [[ "$reconfig_choice" == "y" ]] || [[ "$reconfig_choice" == "Y" ]]; then
            zotcli configure
        fi
    fi
    echo ""
}

# Print next steps
print_next_steps() {
    print_section "Next Steps"

    echo "Congratulations! Your zotero-cli setup is complete."
    echo ""
    echo "Try these commands to get started:"
    echo ""
    echo "  zotcli query \"your topic\"              # Search your library"
    echo "  zotcli add-note \"paper query\"          # Add a note to a paper"
    echo "  zotcli read \"paper query\"              # Read a paper's PDF"
    echo ""
    echo "Use the helper scripts for enhanced functionality:"
    echo ""
    echo "  python scripts/quick_search.py \"topic\" --format table"
    echo "  python scripts/export_citations.py \"topic\" --format bib"
    echo "  ./scripts/batch_process.sh queries.txt --output results.txt"
    echo ""
    echo "For more information, see:"
    echo "  - SKILL.md        - Complete documentation"
    echo "  - INSTALL.md      - Installation guide"
    echo "  - EXAMPLES.md     - Usage examples"
    echo "  - scripts/README.md   - Helper scripts documentation"
    echo ""
}

# Main execution
main() {
    print_header

    # Check prerequisites
    check_python
    check_pip

    # Main flow
    if check_zotcli; then
        check_configuration
        check_optional_tools
        test_basic_functionality
        
        print_section "Setup Summary"
        print_success "zotero-cli is installed and configured!"
        echo ""
        read -p "Would you like to reconfigure? (y/n): " reconfig_question
        if [[ "$reconfig_question" == "y" ]] || [[ "$reconfig_question" == "Y" ]]; then
            offer_configuration
        fi
    else
        print_section "Setup Required"
        offer_installation
        offer_configuration
    fi

    # Next steps
    echo ""
    print_next_steps
}

# Run main function
main "$@"
