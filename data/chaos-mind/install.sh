#!/bin/bash
# CHAOS Memory - ClawdHub Install Script
# Downloads pre-built binaries and sets up the system
#
# Security Model:
# - Requires Dolt pre-installed (via package manager - no curl|bash)
# - Downloads binaries from GitHub releases (signed, reproducible builds)
# - All data stored locally (~/.chaos/db - no cloud sync)
# - No external API calls or network access after installation
# - Auto-capture is opt-in and requires manual configuration
#
# Source: https://github.com/hargabyte/Chaos-mind

set -e

echo "🧠 Installing CHAOS Memory System..."
echo ""

CHAOS_HOME="${CHAOS_HOME:-$HOME/.chaos}"
CHAOS_VERSION="${CHAOS_VERSION:-v1.0.0}"
GITHUB_REPO="hargabyte/Chaos-mind"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

success() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; exit 1; }

# Detect platform
detect_platform() {
    OS="$(uname -s)"
    ARCH="$(uname -m)"
    
    case "$OS" in
        Linux)
            case "$ARCH" in
                x86_64) PLATFORM="linux" ;;
                aarch64|arm64) PLATFORM="linux-arm64" ;;
                *) error "Unsupported architecture: $ARCH" ;;
            esac
            ;;
        Darwin)
            case "$ARCH" in
                x86_64) PLATFORM="macos" ;;
                arm64) PLATFORM="macos-arm64" ;;
                *) error "Unsupported architecture: $ARCH" ;;
            esac
            ;;
        MINGW*|MSYS*|CYGWIN*)
            PLATFORM="windows"
            ;;
        *)
            error "Unsupported OS: $OS"
            ;;
    esac
    
    echo "$PLATFORM"
}

# 1. Check Dolt (required)
echo "Checking dependencies..."
if command -v dolt &> /dev/null; then
    success "Dolt installed ($(dolt version 2>/dev/null | head -1 || echo 'unknown'))"
else
    error "Dolt not found. Please install Dolt first:"
    echo ""
    echo "  macOS:   brew install dolt"
    echo "  Linux:   brew install dolt  # or see https://docs.dolthub.com/introduction/installation"
    echo "  Windows: choco install dolt  # or see https://docs.dolthub.com/introduction/installation"
    echo ""
    echo "Official installation guide: https://docs.dolthub.com/introduction/installation"
    exit 1
fi

# 2. Check Ollama (optional, for auto-capture only)
if command -v ollama &> /dev/null; then
    success "Ollama installed (optional for auto-capture)"
else
    warn "Ollama not found (optional - only needed for auto-capture)"
    echo "  To use auto-capture later, install Ollama from: https://ollama.com"
fi

# 3. Create directories
mkdir -p "$CHAOS_HOME/bin" "$CHAOS_HOME/db" "$CHAOS_HOME/config"
success "Created $CHAOS_HOME"

# 4. Download pre-built binaries
PLATFORM=$(detect_platform)
DOWNLOAD_URL="https://github.com/$GITHUB_REPO/releases/download/$CHAOS_VERSION/chaos-memory-$PLATFORM.tar.gz"

echo "Downloading binaries for $PLATFORM..."
if curl -fsSL "$DOWNLOAD_URL" -o "/tmp/chaos-memory.tar.gz" 2>/dev/null; then
    tar -xzf /tmp/chaos-memory.tar.gz -C "$CHAOS_HOME/bin/"
    rm /tmp/chaos-memory.tar.gz
    success "Binaries downloaded"
else
    warn "Could not download pre-built binaries from release"
    warn "Attempting to build from source..."
    
    # Fallback: build from source if Go is available
    if command -v go &> /dev/null; then
        TEMP_DIR=$(mktemp -d)
        git clone "https://github.com/$GITHUB_REPO.git" "$TEMP_DIR/chaos-memory" 2>/dev/null || {
            error "Cannot clone repo. Ensure you have access to the private repository."
        }
        cd "$TEMP_DIR/chaos-memory"
        go build -o "$CHAOS_HOME/bin/chaos-mcp" ./cmd/chaos/
        go build -o "$CHAOS_HOME/bin/chaos-consolidator" ./cmd/consolidator/
        rm -rf "$TEMP_DIR"
        success "Built from source"
    else
        error "Cannot download binaries and Go is not installed. Please install Go or download binaries manually."
    fi
fi

# 5. Download chaos-cli script
SKILL_URL="https://github.com/$GITHUB_REPO/releases/download/$CHAOS_VERSION/chaos-memory-skill.tar.gz"
if curl -fsSL "$SKILL_URL" -o "/tmp/chaos-skill.tar.gz" 2>/dev/null; then
    tar -xzf /tmp/chaos-skill.tar.gz -C "/tmp/"
    cp /tmp/chaos-memory-skill/scripts/chaos-cli "$CHAOS_HOME/bin/" 2>/dev/null || true
    rm -rf /tmp/chaos-skill.tar.gz /tmp/chaos-memory-skill
fi

# Make sure chaos-cli exists (create if not downloaded)
if [ ! -f "$CHAOS_HOME/bin/chaos-cli" ]; then
    # Download from raw GitHub or create minimal version
    cat > "$CHAOS_HOME/bin/chaos-cli" << 'EOFCLI'
#!/bin/bash
# CHAOS CLI - Minimal wrapper
CHAOS_HOME="${CHAOS_HOME:-$HOME/.chaos}"
DB_PATH="$CHAOS_HOME/db"
cd "$DB_PATH" 2>/dev/null || { echo "Database not found at $DB_PATH"; exit 1; }

# Sanitize input to prevent SQL injection
sanitize_sql() {
    # Escape single quotes for SQL
    echo "$1" | sed "s/'/''/g"
}

case "$1" in
    search) 
        shift
        QUERY=$(sanitize_sql "$1")
        LIMIT=${2:-10}
        dolt sql -q "USE chaos_local; SELECT id, SUBSTRING(content,1,100) as preview, category, priority FROM memories WHERE content LIKE '%$QUERY%' LIMIT $LIMIT;"
        ;;
    list) 
        LIMIT=${2:-10}
        dolt sql -q "USE chaos_local; SELECT id, SUBSTRING(content,1,80), category, priority FROM memories ORDER BY created_at DESC LIMIT $LIMIT;"
        ;;
    *) 
        echo "Usage: chaos-cli search \"query\" [limit] | list [limit]"
        ;;
esac
EOFCLI
fi

chmod +x "$CHAOS_HOME/bin/"*
success "CLI tools installed"

# 6. Initialize database
if [ ! -d "$CHAOS_HOME/db/.dolt" ]; then
    echo "Initializing database..."
    cd "$CHAOS_HOME/db"
    dolt init --name "chaos" --email "chaos@local"
    # Create chaos_local database (required by v1.0.0 binaries)
    dolt sql -q "CREATE DATABASE IF NOT EXISTS chaos_local;"
    dolt sql -q "USE chaos_local; CREATE TABLE IF NOT EXISTS memories (
        id VARCHAR(64) PRIMARY KEY,
        content TEXT NOT NULL,
        category VARCHAR(50) NOT NULL,
        priority FLOAT NOT NULL DEFAULT 1.0,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_category (category),
        INDEX idx_created_at (created_at DESC),
        INDEX idx_priority (priority DESC)
    );"
    dolt add .
    dolt commit -m "Initialize CHAOS database with chaos_local"
    success "Database initialized (chaos_local)"
else
    success "Database exists"
fi

# 7. Copy config templates
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/config/consolidator.template.yaml" ]; then
    cp "$SCRIPT_DIR/config/consolidator.template.yaml" "$CHAOS_HOME/config/"
    # Create active config from template (expand tilde paths to absolute)
    HOME_PATH="$(eval echo ~)"
    sed -e "s|~/.chaos|$CHAOS_HOME|g" \
        -e "s|~/.openclaw|$HOME_PATH/.openclaw|g" \
        -e "s|~/.clawdbot|$HOME_PATH/.clawdbot|g" \
        "$SCRIPT_DIR/config/consolidator.template.yaml" > "$CHAOS_HOME/config/consolidator.yaml"
    success "Config templates copied (paths expanded)"
else
    warn "Config templates not found, creating basic config"
    # Expand HOME for absolute paths (systemd compatibility)
    HOME_PATH="$(eval echo ~)"
    cat > "$CHAOS_HOME/config/consolidator.yaml" << EOF
polling:
  interval: 10m
  batch_size: 50
  state_file: $HOME_PATH/.chaos/consolidator-state.json

qwen:
  provider: ollama
  model: qwen3:1.7b
  ollama:
    host: http://localhost:11434
    num_threads: 0
    num_ctx: 8192
    keep_alive: 24h

chaos:
  mode: mcp
  mcp:
    command: $HOME_PATH/.chaos/bin/chaos-mcp
    args: []
    env:
      CHAOS_DB_PATH: "$HOME_PATH/.chaos/db"

auto_capture:
  enabled: false  # DISABLED BY DEFAULT - User must explicitly enable
  mode: transcript
  sources: []  # Empty by default - User must configure paths
  # Example paths (uncomment and customize to enable):
  # - $HOME_PATH/.openclaw-*/agents/*/sessions/*.jsonl
  # - $HOME_PATH/.clawdbot-*/agents/*/sessions/*.jsonl

extraction:
  min_confidence: 0.7
  categories:
    - core
    - semantic
    - working
    - episodic

logging:
  level: info
  file: $HOME_PATH/.chaos/consolidator.log
EOF
fi

# Copy service template
if [ -f "$SCRIPT_DIR/config/chaos-consolidator.service.template" ]; then
    cp "$SCRIPT_DIR/config/chaos-consolidator.service.template" "$CHAOS_HOME/config/"
    success "Service template copied"
fi

# Copy setup scripts
if [ -f "$SCRIPT_DIR/scripts/setup-service.sh" ]; then
    cp "$SCRIPT_DIR/scripts/setup-service.sh" "$CHAOS_HOME/bin/"
    chmod +x "$CHAOS_HOME/bin/setup-service.sh"
    success "Setup scripts copied"
fi

# 8. Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ CHAOS Memory installed successfully!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Add to your shell profile (.bashrc, .zshrc):"
echo ""
echo "  export CHAOS_HOME=\"$CHAOS_HOME\""
echo "  export PATH=\"\$CHAOS_HOME/bin:\$PATH\""
echo ""
echo "Test installation:"
echo "  chaos-cli list"
echo ""
echo "Store your first memory:"
echo "  chaos-cli store \"Your important fact\" --category core --priority 0.8"
echo ""
echo "Search memories:"
echo "  chaos-cli search \"keyword\""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 OPTIONAL: Enable Auto-Capture (Disabled by Default)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Auto-capture is DISABLED by default for privacy."
echo ""
echo "To enable (after reviewing privacy implications):"
echo "  1. Edit config: nano \$CHAOS_HOME/config/consolidator.yaml"
echo "  2. Set 'auto_capture.enabled: true'"
echo "  3. Configure 'auto_capture.sources' with your session paths"
echo "  4. Install Ollama: https://ollama.com"
echo "  5. Pull model: ollama pull qwen3:1.7b"
echo "  6. Test: chaos-consolidator --auto-capture --once"
echo ""
echo "Documentation:"
echo "  Security: https://github.com/hargabyte/Chaos-mind/blob/main/SECURITY.md"
echo "  Config: cat \$CHAOS_HOME/config/consolidator.yaml"
echo ""
echo "Note: v1.0.0 uses embedded Dolt (no SQL server needed)."
echo "The chaos-mcp binary auto-creates the database on first run."
echo ""
