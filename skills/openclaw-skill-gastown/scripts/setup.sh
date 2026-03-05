#!/bin/bash
# Gastown Setup — installs Go, gt, bd, creates workspace, and verifies everything
set -e

echo "🏭 Gastown Setup"
echo ""

# Check for tmux
if ! command -v tmux &>/dev/null; then
    echo "❌ tmux not found. Install with: apt install tmux / brew install tmux"
    exit 1
fi
echo "✅ tmux $(tmux -V)"

# Check for claude
if ! command -v claude &>/dev/null; then
    echo "❌ claude CLI not found. Install from: https://claude.ai/code"
    exit 1
fi
echo "✅ claude CLI found"

# Install Go if needed
if ! command -v go &>/dev/null; then
    echo "📦 Installing Go..."
    ARCH=$(uname -m)
    case "$ARCH" in
        x86_64) GOARCH="amd64" ;;
        aarch64|arm64) GOARCH="arm64" ;;
        *) echo "❌ Unsupported arch: $ARCH"; exit 1 ;;
    esac
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    GO_VERSION="1.23.6"
    URL="https://go.dev/dl/go${GO_VERSION}.${OS}-${GOARCH}.tar.gz"
    
    mkdir -p "$HOME/local"
    wget -q "$URL" -O /tmp/go.tar.gz
    tar -C "$HOME/local" -xzf /tmp/go.tar.gz
    rm /tmp/go.tar.gz
    
    export PATH="$PATH:$HOME/local/go/bin:$HOME/go/bin"
    if ! grep -q 'local/go/bin' "$HOME/.bashrc" 2>/dev/null; then
        echo 'export PATH=$PATH:$HOME/local/go/bin:$HOME/go/bin' >> "$HOME/.bashrc"
    fi
    echo "✅ Go $(go version | awk '{print $3}')"
else
    export PATH="$PATH:$HOME/local/go/bin:$HOME/go/bin"
    echo "✅ Go $(go version | awk '{print $3}')"
fi

# Install gt if needed
if ! command -v gt &>/dev/null; then
    echo "📦 Installing Gas Town (gt)..."
    go install github.com/steveyegge/gastown/cmd/gt@latest 2>&1
    echo "✅ gt $(gt version 2>&1)"
else
    echo "✅ gt $(gt version 2>&1)"
fi

# Install bd if needed
if ! command -v bd &>/dev/null; then
    echo "📦 Installing Beads (bd)..."
    CGO_ENABLED=0 go install github.com/steveyegge/beads/cmd/bd@latest 2>&1
    echo "✅ bd $(bd version 2>&1)"
else
    echo "✅ bd $(bd version 2>&1)"
fi

# Create workspace if needed
if [ ! -d "$HOME/gt" ]; then
    echo ""
    echo "📦 Creating Gastown workspace..."
    gt install "$HOME/gt" --git
    echo "✅ Workspace created at ~/gt"
else
    echo "✅ Workspace exists at ~/gt"
fi

echo ""
echo "🎸 Gastown is ready!"
echo ""
echo "Next steps:"
echo "  cd ~/gt"
echo "  gt rig add <name> <repo-or-path> --branch main"
echo "  cd ~/gt/<name>/.beads && ln -s ../../.beads/formulas formulas"
echo "  gt doctor --fix"
echo "  gt up"
echo "  gt mail send mayor -s 'Task' -m 'Description'"
echo "  gt nudge mayor 'Check inbox'"
