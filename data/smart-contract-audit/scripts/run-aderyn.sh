#!/usr/bin/env bash
set -uo pipefail

TARGET="${1:-.}"
OUTPUT_DIR="${2:-audit-output}"
mkdir -p "$OUTPUT_DIR"

echo "🔍 Running Aderyn on: $TARGET"

# Source cargo env if needed
[ -f "$HOME/.cargo/env" ] && source "$HOME/.cargo/env"

if ! command -v aderyn &>/dev/null; then
    echo "❌ Aderyn not found. Run install-tools.sh first."
    exit 1
fi

# --- Framework Detection ---
if [ -f "$TARGET/foundry.toml" ]; then
    echo "📦 Detected Foundry project — building with forge first..."
    (cd "$TARGET" && forge build 2>/dev/null) || echo "⚠️  forge build failed"
elif [ -f "$TARGET/hardhat.config.js" ] || [ -f "$TARGET/hardhat.config.ts" ]; then
    echo "📦 Detected Hardhat project — compiling first..."
    (cd "$TARGET" && npx hardhat compile 2>/dev/null) || echo "⚠️  hardhat compile failed"
fi

# --- Run aderyn ---
# Aderyn auto-detects foundry.toml; for hardhat it needs the root dir
aderyn "$TARGET" --output "$OUTPUT_DIR/aderyn-report.md" 2>"$OUTPUT_DIR/aderyn-stderr.log" || true

if [ -f "$OUTPUT_DIR/aderyn-report.md" ]; then
    echo "✅ Aderyn report: $OUTPUT_DIR/aderyn-report.md"
    # Count findings
    HIGH=$(grep -c '### \[H-' "$OUTPUT_DIR/aderyn-report.md" 2>/dev/null || echo 0)
    LOW=$(grep -c '### \[L-' "$OUTPUT_DIR/aderyn-report.md" 2>/dev/null || echo 0)
    echo "   High: $HIGH | Low: $LOW"
else
    echo "⚠️  Aderyn produced no output. Check $OUTPUT_DIR/aderyn-stderr.log"
fi
