#!/bin/bash
# claudemem universal installer
# Usage: curl -fsSL https://raw.githubusercontent.com/zelinewang/claudemem/main/skills/claudemem/scripts/install.sh | bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

REPO="zelinewang/claudemem"
GITHUB_RELEASES="https://github.com/${REPO}/releases/latest/download"

detect_os() {
    case "$(uname -s)" in
        Darwin) echo "darwin" ;;
        Linux)  echo "linux" ;;
        MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
        *) echo "unknown" ;;
    esac
}

detect_arch() {
    case "$(uname -m)" in
        x86_64|amd64) echo "amd64" ;;
        arm64|aarch64) echo "arm64" ;;
        *) echo "unknown" ;;
    esac
}

find_install_dir() {
    if [ -d "$HOME/.local/bin" ] || mkdir -p "$HOME/.local/bin" 2>/dev/null; then
        echo "$HOME/.local/bin"
    elif [ -w "/usr/local/bin" ]; then
        echo "/usr/local/bin"
    else
        mkdir -p "$HOME/bin" 2>/dev/null
        echo "$HOME/bin"
    fi
}

OS=$(detect_os)
ARCH=$(detect_arch)
INSTALL_DIR=$(find_install_dir)

echo -e "${BLUE}╔════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   claudemem Universal Installer    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}→ Detected system: ${OS}/${ARCH}${NC}"
echo -e "${BLUE}→ Install directory: ${INSTALL_DIR}${NC}"

if [ "$OS" = "unknown" ] || [ "$ARCH" = "unknown" ]; then
    echo -e "${RED}✗ Unsupported platform: $(uname -s)/$(uname -m)${NC}"
    exit 1
fi

# Try downloading pre-built binary
BINARY_NAME="claudemem-${OS}-${ARCH}"
DOWNLOAD_URL="${GITHUB_RELEASES}/${BINARY_NAME}"

echo ""
echo -e "${BLUE}→ Downloading pre-built binary from GitHub...${NC}"
if curl -fsSL -o "${INSTALL_DIR}/claudemem" "${DOWNLOAD_URL}" 2>/dev/null; then
    chmod +x "${INSTALL_DIR}/claudemem"
    echo -e "${GREEN}✓ Installed claudemem to ${INSTALL_DIR}/claudemem${NC}"
else
    echo -e "${BLUE}→ Pre-built binary not available. Trying go install...${NC}"

    if command -v go &>/dev/null; then
        GOBIN="${INSTALL_DIR}" go install "github.com/${REPO}@latest"
        echo -e "${GREEN}✓ Installed via go install${NC}"
    elif [ -f "$HOME/.local/go/bin/go" ]; then
        GOBIN="${INSTALL_DIR}" "$HOME/.local/go/bin/go" install "github.com/${REPO}@latest"
        echo -e "${GREEN}✓ Installed via go install (local Go)${NC}"
    else
        echo -e "${RED}✗ Could not install: no pre-built binary and Go not found${NC}"
        echo "  Install Go from https://go.dev/dl/ then try again"
        exit 1
    fi
fi

# Verify installation
echo ""
if [ -x "${INSTALL_DIR}/claudemem" ]; then
    echo -e "${GREEN}✓ Installation complete!${NC}"

    # Check if in PATH
    if ! command -v claudemem &>/dev/null; then
        echo ""
        echo -e "${BLUE}→ Add to PATH if not already:${NC}"
        echo "  export PATH=\"${INSTALL_DIR}:\$PATH\""
    fi

    echo ""
    "${INSTALL_DIR}/claudemem" --version 2>/dev/null || true
else
    echo -e "${RED}✗ Installation verification failed${NC}"
    exit 1
fi

# Migration suggestions
echo ""
if [ -d "$HOME/.braindump" ]; then
    echo -e "${BLUE}→ Found ~/.braindump/ — import with:${NC}"
    echo "  claudemem migrate braindump"
fi
if [ -d "$HOME/.claude-done" ]; then
    echo -e "${BLUE}→ Found ~/.claude-done/ — import with:${NC}"
    echo "  claudemem migrate claude-done"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       Ready to use claudemem!      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════╝${NC}"
echo ""
echo "  claudemem note add test --title \"Hello\" --content \"World\""
echo "  claudemem search \"hello\""
echo "  claudemem stats"
