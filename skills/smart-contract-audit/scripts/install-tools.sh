#!/usr/bin/env bash
set -euo pipefail

echo "=== Smart Contract Audit Tools Installer ==="

# --- Framework Detection ---
detect_framework() {
    local dir="${1:-.}"
    if [ -f "$dir/foundry.toml" ]; then
        echo "foundry"
    elif [ -f "$dir/hardhat.config.js" ] || [ -f "$dir/hardhat.config.ts" ]; then
        echo "hardhat"
    else
        echo "raw"
    fi
}

echo ""
echo "📋 Framework Detection Notes:"
echo "  - Foundry projects (foundry.toml): tools use forge build artifacts"
echo "  - Hardhat projects (hardhat.config.js/ts): tools use npx hardhat compile artifacts"
echo "  - Raw .sol files: tools analyze directly"
echo ""

# --- Forge check ---
if command -v forge &>/dev/null; then
    echo "✅ Forge already installed: $(forge --version 2>&1 | head -1)"
else
    echo "⚠️  Forge not found. Install via: curl -L https://foundry.paradigm.xyz | bash && foundryup"
fi

# --- Slither ---
if command -v slither &>/dev/null; then
    echo "✅ Slither already installed: $(slither --version 2>&1 | head -1)"
else
    echo "📦 Installing Slither..."
    pip3 install --break-system-packages slither-analyzer 2>/dev/null || pip3 install slither-analyzer
fi

# --- solc-select ---
if command -v solc-select &>/dev/null; then
    echo "✅ solc-select already installed"
else
    echo "📦 Installing solc-select..."
    pip3 install --break-system-packages solc-select 2>/dev/null || pip3 install solc-select
fi

# --- Aderyn ---
if command -v aderyn &>/dev/null; then
    echo "✅ Aderyn already installed: $(aderyn --version 2>&1 | head -1)"
else
    echo "📦 Installing Aderyn..."
    if command -v cargo &>/dev/null; then
        cargo install aderyn
    elif [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
        cargo install aderyn
    else
        echo "⚠️  Rust/cargo not found. Install Rust first:"
        echo "   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y"
        echo "   source ~/.cargo/env && cargo install aderyn"
    fi
fi

echo ""
echo "=== Installation Complete ==="
echo "Verify with:"
echo "  slither --version"
echo "  aderyn --version"
