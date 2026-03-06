#!/bin/bash
# Dependency checker for deai-image skill
# Verifies all required tools are installed

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function check_command() {
    local cmd="$1"
    local package="$2"
    
    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $cmd"
        return 0
    else
        echo -e "${RED}✗${NC} $cmd ${YELLOW}(missing)${NC}"
        return 1
    fi
}

function check_python_module() {
    local module="$1"
    
    if python3 -c "import $module" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Python: $module"
        return 0
    else
        echo -e "${RED}✗${NC} Python: $module ${YELLOW}(missing)${NC}"
        return 1
    fi
}

function get_version() {
    local cmd="$1"
    
    case "$cmd" in
        magick)
            magick -version 2>/dev/null | head -n1 | awk '{print $3}'
            ;;
        exiftool)
            exiftool -ver 2>/dev/null
            ;;
        python3)
            python3 --version 2>/dev/null | awk '{print $2}'
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

function detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif [ "$(uname)" = "Darwin" ]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

function show_install_guide() {
    local os=$(detect_os)
    local missing_sys=("$@")
    
    echo ""
    echo -e "${BLUE}Installation Guide${NC}"
    echo "=================================================="
    
    case "$os" in
        ubuntu|debian)
            echo -e "${YELLOW}Debian/Ubuntu:${NC}"
            echo "sudo apt update"
            echo "sudo apt install -y imagemagick libimage-exiftool-perl python3 python3-pip"
            echo "pip3 install Pillow numpy"
            ;;
        fedora|rhel|centos)
            echo -e "${YELLOW}Fedora/RHEL/CentOS:${NC}"
            echo "sudo dnf install -y ImageMagick perl-Image-ExifTool python3-pip"
            echo "pip3 install Pillow numpy"
            ;;
        arch)
            echo -e "${YELLOW}Arch Linux:${NC}"
            echo "sudo pacman -S imagemagick perl-image-exiftool python python-pip"
            echo "pip install Pillow numpy"
            ;;
        macos)
            echo -e "${YELLOW}macOS (Homebrew):${NC}"
            echo "brew install imagemagick exiftool python3"
            echo "pip3 install Pillow numpy"
            ;;
        *)
            echo -e "${YELLOW}Generic Linux:${NC}"
            echo "Install the following packages using your package manager:"
            echo "  - ImageMagick (7.0+)"
            echo "  - ExifTool (perl-Image-ExifTool)"
            echo "  - Python 3.7+"
            echo ""
            echo "Then install Python packages:"
            echo "pip3 install Pillow numpy"
            ;;
    esac
    
    echo "=================================================="
}

function main() {
    echo ""
    echo "=================================================="
    echo "  AI Image De-Fingerprinting - Dependency Check"
    echo "=================================================="
    echo ""
    
    local all_good=true
    
    # System commands
    echo -e "${BLUE}System Commands:${NC}"
    check_command "magick" "imagemagick" || all_good=false
    if command -v magick &> /dev/null; then
        echo "  Version: $(get_version magick)"
    fi
    
    check_command "exiftool" "libimage-exiftool-perl" || all_good=false
    if command -v exiftool &> /dev/null; then
        echo "  Version: $(get_version exiftool)"
    fi
    
    check_command "python3" "python3" || all_good=false
    if command -v python3 &> /dev/null; then
        echo "  Version: $(get_version python3)"
    fi
    
    echo ""
    
    # Python modules (optional, only for deai.py)
    echo -e "${BLUE}Python Modules (for deai.py):${NC}"
    check_python_module "PIL" || all_good=false
    check_python_module "numpy" || all_good=false
    
    echo ""
    echo "=================================================="
    
    if [ "$all_good" = true ]; then
        echo -e "${GREEN}✓ All dependencies satisfied!${NC}"
        echo ""
        echo "You can use both versions:"
        echo "  • Python: python scripts/deai.py image.png"
        echo "  • Bash:   bash scripts/deai.sh image.png output.jpg"
        echo ""
    else
        echo -e "${RED}✗ Missing dependencies detected${NC}"
        show_install_guide
        echo ""
        echo -e "${YELLOW}Note:${NC} If Python modules are missing, you can still use:"
        echo "  bash scripts/deai.sh image.png output.jpg"
        echo ""
        exit 1
    fi
}

main
