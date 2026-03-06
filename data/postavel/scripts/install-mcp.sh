#!/bin/bash
# Postavel MCP Installer
# One-command setup for mcporter
# Run: curl -fsSL https://postavel.com/install-mcp | bash

set -e

echo "🚀 Postavel MCP Setup"
echo "===================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Step 1: Check if mcporter is already installed
print_info "Checking for mcporter..."

MCPORter_PATH=""

# Check common locations
if command -v mcporter &> /dev/null; then
    MCPORter_PATH=$(which mcporter)
    print_status "Found mcporter at: $MCPORter_PATH"
elif [ -f "/usr/local/bin/mcporter" ]; then
    MCPORter_PATH="/usr/local/bin/mcporter"
    print_status "Found mcporter at: $MCPORter_PATH"
elif [ -f "/opt/homebrew/bin/mcporter" ]; then
    MCPORter_PATH="/opt/homebrew/bin/mcporter"
    print_status "Found mcporter at: $MCPORter_PATH"
elif [ -f "$HOME/.local/bin/mcporter" ]; then
    MCPORter_PATH="$HOME/.local/bin/mcporter"
    print_status "Found mcporter at: $MCPORter_PATH"
else
    # Search in npm global locations
    NPM_PREFIX=$(npm config get prefix 2>/dev/null || echo "")
    if [ -n "$NPM_PREFIX" ] && [ -f "$NPM_PREFIX/bin/mcporter" ]; then
        MCPORter_PATH="$NPM_PREFIX/bin/mcporter"
        print_status "Found mcporter at: $MCPORter_PATH"
    fi
fi

# Step 2: Install if not found
if [ -z "$MCPORter_PATH" ]; then
    print_info "mcporter not found. Installing..."
    
    # Try Homebrew first
    if command -v brew &> /dev/null; then
        print_info "Installing via Homebrew..."
        brew install mcporter
        MCPORter_PATH=$(which mcporter)
    else
        # Fall back to npm
        print_info "Installing via npm..."
        npm install -g mcporter
        
        # Find it after npm install
        NPM_PREFIX=$(npm config get prefix)
        if [ -f "$NPM_PREFIX/bin/mcporter" ]; then
            MCPORter_PATH="$NPM_PREFIX/bin/mcporter"
        elif [ -f "$HOME/.local/bin/mcporter" ]; then
            MCPORter_PATH="$HOME/.local/bin/mcporter"
        fi
    fi
    
    # Verify installation
    if [ -z "$MCPORter_PATH" ] || [ ! -f "$MCPORter_PATH" ]; then
        print_error "Installation failed. Trying direct download..."
        
        # Direct download as last resort
        OS=$(uname -s)
        ARCH=$(uname -m)
        
        if [ "$OS" = "Darwin" ]; then
            if [ "$ARCH" = "arm64" ]; then
                URL="https://github.com/steipete/mcporter/releases/latest/download/mcporter-Darwin-arm64"
            else
                URL="https://github.com/steipete/mcporter/releases/latest/download/mcporter-Darwin-x86_64"
            fi
        else
            URL="https://github.com/steipete/mcporter/releases/latest/download/mcporter-Linux-x86_64"
        fi
        
        print_info "Downloading from: $URL"
        sudo curl -L -o /usr/local/bin/mcporter "$URL"
        sudo chmod +x /usr/local/bin/mcporter
        MCPORter_PATH="/usr/local/bin/mcporter"
    fi
    
    if [ -z "$MCPORter_PATH" ] || [ ! -f "$MCPORter_PATH" ]; then
        print_error "Failed to install mcporter. Please install manually:"
        echo "  brew install mcporter"
        echo "  or: npm install -g mcporter"
        exit 1
    fi
    
    print_status "mcporter installed at: $MCPORter_PATH"
fi

# Step 3: Create config directory
print_info "Creating configuration..."
mkdir -p "$HOME/.config/mcporter"

# Step 4: Write config file
cat > "$HOME/.config/mcporter/postavel.json" <<'EOF'
{
  "mcpServers": {
    "postavel": {
      "command": "mcporter",
      "args": [
        "--url", "https://postavel.com/mcp/postavel",
        "--oauth",
        "--name", "postavel"
      ]
    }
  }
}
EOF

print_status "Configuration created at ~/.config/mcporter/postavel.json"

# Step 5: Launch OAuth
print_info "Launching OAuth authentication..."
print_info "Your browser will open to log in to Postavel."
echo ""

"$MCPORter_PATH" --config "$HOME/.config/mcporter/postavel.json"

print_status "Setup complete! You can now use Postavel with your AI assistant."
echo ""
echo "Try saying: 'Schedule a Facebook post for tomorrow'"
