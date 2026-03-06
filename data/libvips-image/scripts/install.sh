#!/usr/bin/env bash
#
# libvips-image skill installer (IMPROVED VERSION)
# Supports macOS, Linux (Ubuntu/Debian, Fedora/RHEL, Arch), and Docker
# Fixes for: Python dev headers, build tools, error handling, automation support
#

set -e

# Configuration
VERBOSE=${VERBOSE:-0}
AUTO_MODE=${AUTO_MODE:-0}
SKIP_SUDO=${SKIP_SUDO:-0}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }
debug() { [ "$VERBOSE" -eq 1 ] && echo -e "${BLUE}[DEBUG]${NC} $1"; }

# Detect OS and environment
detect_os() {
    case "$(uname -s)" in
        Darwin*)  OS="macos" ;;
        Linux*)   OS="linux" ;;
        MINGW*|MSYS*|CYGWIN*) OS="windows" ;;
        *)        error "Unsupported OS: $(uname -s)" ;;
    esac

    # Detect Linux distribution
    if [ "$OS" = "linux" ]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            DISTRO="$ID"
        elif [ -f /etc/debian_version ]; then
            DISTRO="debian"
        elif [ -f /etc/redhat-release ]; then
            DISTRO="rhel"
        else
            DISTRO="unknown"
        fi
    fi

    # Detect Docker environment
    if [ -f /.dockerenv ]; then
        info "Docker environment detected"
        SKIP_SUDO=1
    fi

    # Detect Apple Silicon
    if [ "$OS" = "macos" ] && [ "$(uname -m)" = "arm64" ]; then
        info "Apple Silicon (M1/M2) detected"
        APPLE_SILICON=1
    fi

    info "Detected: OS=$OS${DISTRO:+, Distro=$DISTRO}${APPLE_SILICON:+, Apple Silicon=yes}"
}

# Helper to check if command exists
has_cmd() { command -v "$1" &>/dev/null; }

# Helper to run commands with optional sudo
run_cmd() {
    local cmd="$1"
    if [ "$SKIP_SUDO" -eq 1 ]; then
        debug "Running (no sudo): $cmd"
        eval "$cmd"
    else
        debug "Running (with sudo): $cmd"
        sudo bash -c "$cmd"
    fi
}

# Install libvips system library
install_libvips() {
    info "Installing libvips system library..."

    case "$OS" in
        macos)
            install_libvips_macos
            ;;
        linux)
            install_libvips_linux
            ;;
        windows)
            warn "Windows detected. Please install libvips manually:"
            warn "1. Download from https://github.com/libvips/libvips/releases"
            warn "2. Extract and add bin/ to your PATH"
            warn "3. Then run this script again"
            ;;
    esac

    # Verify installation
    if has_cmd vips; then
        success "libvips installed: $(vips --version 2>/dev/null | head -1)"
    else
        for vips_path in /opt/homebrew/bin/vips /usr/local/bin/vips /usr/bin/vips; do
            if [ -x "$vips_path" ]; then
                success "libvips found at: $vips_path"
                return 0
            fi
        done
        warn "libvips command not found in PATH, but library may still be usable"
    fi
}

install_libvips_macos() {
    if ! has_cmd brew; then
        if [ -x /opt/homebrew/bin/brew ]; then
            BREW=/opt/homebrew/bin/brew
        elif [ -x /usr/local/bin/brew ]; then
            BREW=/usr/local/bin/brew
        else
            error "Homebrew not found. Install from https://brew.sh"
        fi
    else
        BREW=brew
    fi

    debug "Using Homebrew: $BREW"
    
    if ! $BREW install vips; then
        error "Failed to install libvips via Homebrew"
    fi
}

install_libvips_linux() {
    case "$DISTRO" in
        ubuntu|debian|pop|linuxmint)
            debug "Installing for Ubuntu/Debian"
            run_cmd "apt-get update"
            # FIX 1: Added python3-dev and build-essential
            run_cmd "apt-get install -y libvips-dev libvips-tools python3-dev build-essential"
            ;;
        fedora|rhel|centos|rocky|alma)
            debug "Installing for Fedora/RHEL"
            run_cmd "dnf groupinstall -y 'Development Tools'" || \
            run_cmd "yum groupinstall -y 'Development Tools'"
            run_cmd "dnf install -y vips-devel vips-tools" || \
            run_cmd "yum install -y vips-devel vips-tools"
            ;;
        arch|manjaro|endeavouros)
            debug "Installing for Arch Linux"
            run_cmd "pacman -S --noconfirm libvips base-devel"
            ;;
        alpine)
            debug "Installing for Alpine Linux"
            run_cmd "apk add vips-dev vips-tools build-base python3-dev"
            ;;
        *)
            warn "Unknown distro: $DISTRO"
            warn "Attempting to install with available package managers..."
            
            if has_cmd apt-get; then
                run_cmd "apt-get update && apt-get install -y libvips-dev python3-dev build-essential"
            elif has_cmd dnf; then
                run_cmd "dnf groupinstall -y 'Development Tools' && dnf install -y vips-devel"
            elif has_cmd yum; then
                run_cmd "yum groupinstall -y 'Development Tools' && yum install -y vips-devel"
            elif has_cmd pacman; then
                run_cmd "pacman -S --noconfirm libvips base-devel"
            else
                error "Cannot determine package manager. Install libvips manually."
            fi
            ;;
    esac
}

# Install Python package using uv (preferred) or pip
install_pyvips() {
    info "Installing pyvips Python package..."

    # Try uv first (preferred)
    if has_cmd uv; then
        debug "Found uv package manager"
        if uv pip install pyvips; then
            success "pyvips installed via uv"
            return 0
        fi
    fi

    # Check for uv in common locations
    for uv_path in ~/.cargo/bin/uv ~/.local/bin/uv /opt/homebrew/bin/uv /usr/local/bin/uv; do
        if [ -x "$uv_path" ]; then
            debug "Found uv at: $uv_path"
            if "$uv_path" pip install pyvips; then
                success "pyvips installed via uv"
                return 0
            fi
        fi
    done

    # Offer to install uv (with auto mode support)
    if [ "$AUTO_MODE" -eq 0 ]; then
        warn "uv not found. uv is recommended for faster, more reliable package management."
        echo -n "Install uv now? [Y/n] "
        read -r response
        if [[ "$response" =~ ^[Nn]$ ]]; then
            info "Skipping uv installation, falling back to pip..."
        else
            install_uv
        fi
    else
        info "Auto mode: Skipping uv installation, using pip..."
    fi

    # Fallback to pip
    install_pyvips_pip
}

install_uv() {
    info "Installing uv..."
    if has_cmd curl; then
        debug "Using curl to install uv"
        curl -LsSf https://astral.sh/uv/install.sh | sh
    elif has_cmd wget; then
        debug "Using wget to install uv"
        wget -qO- https://astral.sh/uv/install.sh | sh
    else
        error "Neither curl nor wget found. Install uv manually: https://docs.astral.sh/uv/"
    fi

    # Source the new PATH
    export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

    if has_cmd uv; then
        if uv pip install pyvips; then
            success "pyvips installed via uv"
            return 0
        fi
    fi
}

install_pyvips_pip() {
    info "Installing pyvips via pip..."

    # FIX 2: Use array instead of escaped strings for pip commands
    declare -a pip_commands=("pip3" "pip" "python3 -m pip" "python -m pip")
    
    for pip_cmd in "${pip_commands[@]}"; do
        if $pip_cmd --version &>/dev/null; then
            debug "Found pip: $pip_cmd"
            
            # FIX 3: Use --user for user installation (safer than sudo)
            if [ "$SKIP_SUDO" -eq 1 ]; then
                # Docker/container environment: install system-wide
                if $pip_cmd install pyvips; then
                    success "pyvips installed via $pip_cmd"
                    return 0
                fi
            else
                # Regular environment: prefer user installation
                if $pip_cmd install --user pyvips; then
                    success "pyvips installed via $pip_cmd (user)"
                    return 0
                fi
                
                # Fallback to system installation if user install fails
                warn "User installation failed, trying system-wide installation..."
                if sudo $pip_cmd install pyvips; then
                    success "pyvips installed via $pip_cmd (system)"
                    return 0
                fi
            fi
        fi
    done

    error "No suitable pip found. Please install Python with pip."
}

# Verify installation
verify_installation() {
    info "Verifying installation..."

    # Find Python
    PYTHON=""
    
    if has_cmd uv; then
        if uv run python -c "print('ok')" &>/dev/null; then
            PYTHON="uv run python"
        fi
    fi

    if [ -z "$PYTHON" ]; then
        for py in python3 python; do
            if has_cmd $py; then
                PYTHON="$py"
                break
            fi
        done
    fi

    if [ -z "$PYTHON" ]; then
        error "Python not found"
    fi

    debug "Using Python: $PYTHON"

    # Set library paths for macOS
    if [ "$OS" = "macos" ]; then
        VIPS_LIB_PATH=""
        for lib_path in /opt/homebrew/lib /usr/local/lib; do
            if [ -f "$lib_path/libvips.dylib" ] || [ -f "$lib_path/libvips.42.dylib" ]; then
                VIPS_LIB_PATH="$lib_path"
                break
            fi
        done

        if [ -n "$VIPS_LIB_PATH" ]; then
            export DYLD_LIBRARY_PATH="$VIPS_LIB_PATH:$DYLD_LIBRARY_PATH"
            debug "Set DYLD_LIBRARY_PATH=$VIPS_LIB_PATH"
        fi
    fi

    # FIX 4: Improved version extraction
    TEST_CMD="import pyvips; v = pyvips.version(); print(f'pyvips {pyvips.__version__}, libvips {v[0]}.{v[1]}.{v[2]}')"

    if $PYTHON -c "$TEST_CMD" 2>/dev/null; then
        success "Installation verified successfully!"
        return 0
    fi

    # If verification failed but libraries exist, show setup instructions
    if [ "$OS" = "macos" ] && [ -n "$VIPS_LIB_PATH" ]; then
        warn "pyvips installed but library linking may need configuration."
        warn ""
        warn "Option 1: Use uv run (recommended):"
        warn "  uv run python scripts/vips_tool.py --help"
        warn ""
        warn "Option 2: Set library path in your shell profile (~/.zshrc or ~/.bashrc):"
        warn "  export DYLD_LIBRARY_PATH=\"$VIPS_LIB_PATH:\$DYLD_LIBRARY_PATH\""
        warn ""
        success "Installation complete (library path configuration may be needed)"
        return 0
    fi

    error "pyvips import failed. Please check libvips installation."
}

# Print usage instructions
print_usage() {
    echo ""
    echo "=============================================="
    echo "  libvips-image skill installed successfully!"
    echo "=============================================="
    echo ""
    echo "Usage examples:"
    echo ""
    echo "  # Resize image"
    echo "  python scripts/vips_tool.py resize input.jpg output.jpg --width 800"
    echo ""
    echo "  # Convert to WebP"
    echo "  python scripts/vips_tool.py convert input.jpg output.webp --quality 85"
    echo ""
    echo "  # Create thumbnail"
    echo "  python scripts/vips_tool.py thumbnail input.jpg thumb.jpg --size 200"
    echo ""
    echo "  # Batch process"
    echo "  python scripts/vips_batch.py resize ./input ./output --width 800"
    echo ""
    echo "For more commands, run: python scripts/vips_tool.py --help"
    echo ""
    echo "Environment variables:"
    echo "  VERBOSE=1          Enable verbose output"
    echo "  AUTO_MODE=1        Skip interactive prompts"
    echo "  SKIP_SUDO=1        Don't use sudo (for Docker)"
    echo ""
}

# Main
main() {
    echo ""
    echo "========================================"
    echo "  libvips-image Skill Installer"
    echo "  (IMPROVED VERSION)"
    echo "========================================"
    echo ""

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --auto)
                AUTO_MODE=1
                shift
                ;;
            --verbose)
                VERBOSE=1
                shift
                ;;
            --skip-sudo)
                SKIP_SUDO=1
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --auto          Skip interactive prompts"
                echo "  --verbose       Enable verbose output"
                echo "  --skip-sudo     Don't use sudo (for Docker)"
                echo "  --help          Show this help message"
                exit 0
                ;;
            *)
                warn "Unknown option: $1"
                shift
                ;;
        esac
    done

    detect_os
    install_libvips
    install_pyvips
    verify_installation
    print_usage
    
    success "Installation complete!"
}

# Run main
main "$@"
