#!/bin/bash
set -e

echo "Installing Speak-Turbo..."

# Cleanup on failure
trap 'echo "Install failed." >&2' ERR

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install Python dependencies
# Version bounds match pyproject.toml [project.dependencies] — Keep in sync
echo "→ Installing Python dependencies..."
pip install --quiet "pocket-tts>=0.1.0,<1.0" "uvicorn>=0.20.0,<1.0" "fastapi>=0.100.0,<1.0" "python-dateutil>=2.7,<3.0"

# Create bin directory
mkdir -p ~/.local/bin

# Build Rust CLI from local source, or fall back to Python wrapper
if command -v cargo &> /dev/null && [ -d "$SCRIPT_DIR/speakturbo-cli" ]; then
    echo "→ Building Rust CLI from local source..."
    cd "$SCRIPT_DIR/speakturbo-cli"
    cargo build --release --quiet
    cp target/release/speakturbo ~/.local/bin/
else
    echo "→ Rust or local source not found. Installing Python CLI wrapper..."
    cat > ~/.local/bin/speakturbo << 'EOF'
#!/bin/bash
# Fallback wrapper - runs Python CLI
python -m speakturbo.cli "$@"
EOF
    chmod +x ~/.local/bin/speakturbo
fi

# Install Python package
echo "→ Installing daemon..."
if [ -d "$SCRIPT_DIR/speakturbo" ]; then
    pip install --quiet -e "$SCRIPT_DIR"
fi

# Add to PATH if needed
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo ""
    echo "Add to your shell profile:"
    echo '  export PATH="$HOME/.local/bin:$PATH"'
    echo ""
fi

echo "✓ Speak-Turbo installed!"
echo ""
echo "Test it:"
echo "  speakturbo \"Hello world\""
