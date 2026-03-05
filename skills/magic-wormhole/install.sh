#!/bin/bash
#
# Magic Wormhole Skill Installation Script
# Installs magic-wormhole CLI and verifies setup for OpenClaw
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_wormhole() {
    if command -v wormhole &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Detect package manager
detect_package_manager() {
    if command -v apt &> /dev/null; then
        echo "apt"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v zypper &> /dev/null; then
        echo "zypper"
    elif command -v brew &> /dev/null; then
        echo "brew"
    elif command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
        echo "pip"
    else
        echo "unknown"
    fi
}

# Install using detected package manager
install_wormhole() {
    local pkg_manager=$1

    print_status "Installing magic-wormhole using $pkg_manager..."

    case $pkg_manager in
        apt)
            sudo apt update
            sudo apt install -y magic-wormhole
            ;;
        dnf)
            sudo dnf install -y magic-wormhole
            ;;
        zypper)
            sudo zypper install -y python-magic-wormhole
            ;;
        brew)
            brew install magic-wormhole
            ;;
        pip)
            # Use pip3 if available, otherwise pip
            if command -v pip3 &> /dev/null; then
                pip3 install --user magic-wormhole
            else
                pip install --user magic-wormhole
            fi

            # Add ~/.local/bin to PATH if not already present
            if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
                print_status "Adding ~/.local/bin to PATH..."
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
                export PATH="$HOME/.local/bin:$PATH"
            fi
            ;;
        *)
            print_error "Unknown package manager. Attempting pip installation..."
            if command -v pip3 &> /dev/null; then
                pip3 install --user magic-wormhole
            elif command -v pip &> /dev/null; then
                pip install --user magic-wormhole
            else
                print_error "pip not found. Please install Python and pip first."
                print_error "Visit: https://pip.pypa.io/en/stable/installation/"
                exit 1
            fi
            ;;
    esac
}

# Main installation process
main() {
    echo "========================================="
    echo "  Magic Wormhole Skill Installation"
    echo "========================================="
    echo ""

    # Check if already installed
    print_status "Checking for existing magic-wormhole installation..."
    if check_wormhole; then
        VERSION=$(wormhole --version 2>&1 | head -n1)
        print_success "magic-wormhole is already installed: $VERSION"
        echo ""

        # Ask if user wants to update
        read -p "Do you want to update to the latest version? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Updating magic-wormhole..."
            PKG_MANAGER=$(detect_package_manager)
            if [[ "$PKG_MANAGER" == "pip" ]]; then
                if command -v pip3 &> /dev/null; then
                    pip3 install --upgrade magic-wormhole
                else
                    pip install --upgrade magic-wormhole
                fi
            else
                print_status "Please update using your system package manager:"
                echo "  apt: sudo apt update && sudo apt upgrade magic-wormhole"
                echo "  dnf: sudo dnf upgrade magic-wormhole"
                echo "  brew: brew upgrade magic-wormhole"
            fi
            print_success "Update complete!"
        fi
    else
        print_status "magic-wormhole not found. Installing..."
        echo ""

        # Detect package manager and install
        PKG_MANAGER=$(detect_package_manager)
        print_status "Detected package manager: $PKG_MANAGER"

        install_wormhole "$PKG_MANAGER"
        print_success "Installation complete!"
        echo ""

        # Refresh PATH if we added ~/.local/bin
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]] && [[ -d "$HOME/.local/bin" ]]; then
            export PATH="$HOME/.local/bin:$PATH"
            print_status "PATH updated. You may need to run: source ~/.bashrc"
        fi
    fi

    # Verify installation
    echo ""
    print_status "Verifying installation..."
    if command -v wormhole &> /dev/null; then
        VERSION=$(wormhole --version 2>&1 | head -n1)
        print_success "Verification successful!"
        echo ""
        echo "  Command: wormhole"
        echo "  Version: $VERSION"
        echo "  Location: $(which wormhole)"
        echo ""

        # Test with a simple command
        print_status "Running quick test..."
        if wormhole --help &> /dev/null; then
            print_success "Test passed! magic-wormhole is ready to use."
        else
            print_error "Test failed. Please check installation."
            exit 1
        fi
    else
        print_error "Verification failed. wormhole command not found."
        print_error "Please add ~/.local/bin to your PATH or log out and log back in."
        exit 1
    fi

    # Installation summary
    echo ""
    echo "========================================="
    print_success "Installation Complete!"
    echo "========================================="
    echo ""
    echo "Quick Start:"
    echo "  Send text:    wormhole send --text \"your-secret\""
    echo "  Send file:    wormhole send filename.txt"
    echo "  Receive:      wormhole receive"
    echo ""
    echo "Documentation:"
    echo "  SKILL.md      - Complete skill documentation"
    echo "  README.md     - User guide and quick reference"
    echo "  examples/     - Usage examples"
    echo ""
    echo "For more information, visit:"
    echo "  https://github.com/magic-wormhole/magic-wormhole"
    echo ""
}

# Run main function
main
