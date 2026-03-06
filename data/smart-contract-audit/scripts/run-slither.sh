#!/usr/bin/env bash
set -uo pipefail

TARGET="${1:-.}"
OUTPUT_DIR="${2:-audit-output}"
mkdir -p "$OUTPUT_DIR"

echo "🔍 Running Slither on: $TARGET"

if ! command -v slither &>/dev/null; then
    echo "❌ Slither not found. Run install-tools.sh first."
    exit 1
fi

# --- Framework Detection ---
FRAMEWORK="raw"
SLITHER_FLAGS=""
if [ -f "$TARGET/foundry.toml" ]; then
    FRAMEWORK="foundry"
    echo "📦 Detected Foundry project — building with forge first..."
    (cd "$TARGET" && forge build 2>/dev/null) || echo "⚠️  forge build failed, slither may still work with existing artifacts"
elif [ -f "$TARGET/hardhat.config.js" ] || [ -f "$TARGET/hardhat.config.ts" ]; then
    FRAMEWORK="hardhat"
    echo "📦 Detected Hardhat project — compiling with hardhat first..."
    (cd "$TARGET" && npx hardhat compile 2>/dev/null) || echo "⚠️  hardhat compile failed"
    # Slither auto-detects Hardhat from hardhat.config — no flag needed
    SLITHER_FLAGS=""
fi

echo "   Framework: $FRAMEWORK"

# --- Detect and set solc version (skip for hardhat — it manages its own compiler) ---
if [ "$FRAMEWORK" != "hardhat" ]; then
    # For foundry/raw projects, detect version from source and set via solc-select
    # Look in src/ or contracts/ first to avoid picking up dependency pragmas
    SOLC_VERSION=""
    for dir in "$TARGET/src" "$TARGET/contracts" "$TARGET"; do
        if [ -d "$dir" ]; then
            SOLC_VERSION=$(grep -roh 'pragma solidity [^;]*' "$dir" --include="*.sol" 2>/dev/null | sort -V | tail -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
            [ -n "$SOLC_VERSION" ] && break
        fi
    done
    if [ -n "$SOLC_VERSION" ]; then
        echo "📌 Detected Solidity version: $SOLC_VERSION"
        if command -v solc-select &>/dev/null; then
            solc-select install "$SOLC_VERSION" 2>/dev/null || true
            solc-select use "$SOLC_VERSION" 2>/dev/null || true
        fi
    fi
fi

# --- Run slither ---
echo "🔍 Running slither analysis..."
slither "$TARGET" $SLITHER_FLAGS --json "$OUTPUT_DIR/slither-output.json" 2>"$OUTPUT_DIR/slither-stderr.log" || true

# Also generate human summary
slither "$TARGET" $SLITHER_FLAGS --print human-summary 2>/dev/null > "$OUTPUT_DIR/slither-summary.txt" || true

if [ -f "$OUTPUT_DIR/slither-output.json" ]; then
    echo "✅ Slither output: $OUTPUT_DIR/slither-output.json"
    HIGH=$(grep -c '"impact": "High"' "$OUTPUT_DIR/slither-output.json" 2>/dev/null || echo 0)
    MED=$(grep -c '"impact": "Medium"' "$OUTPUT_DIR/slither-output.json" 2>/dev/null || echo 0)
    LOW=$(grep -c '"impact": "Low"' "$OUTPUT_DIR/slither-output.json" 2>/dev/null || echo 0)
    echo "   High: $HIGH | Medium: $MED | Low: $LOW"
else
    echo "⚠️  Slither produced no output. Check $OUTPUT_DIR/slither-stderr.log"
fi
