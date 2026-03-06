#!/bin/bash
# Quick test for Signet Guardian CLI
# Uses project's references/ by setting OPENCLAW_SKILL_DIR to script dir.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
export OPENCLAW_SKILL_DIR="$SCRIPT_DIR"
export OPENCLAW_BASE_DIR="$SCRIPT_DIR"

echo "=== Policy (show) ==="
npx -y tsx scripts/signet-cli.ts signet-policy --show

echo ""
echo "=== Preflight: small amount (expect ALLOW) ==="
npx -y tsx scripts/signet-cli.ts signet-preflight --amount 3 --currency GBP --payee "test.com" --purpose "Test" || true

echo ""
echo "=== Preflight: above per-tx limit (expect DENY) ==="
npx -y tsx scripts/signet-cli.ts signet-preflight --amount 25 --currency GBP --payee "test.com" --purpose "Test" 2>/dev/null && echo "UNEXPECTED ALLOW" || echo "Got DENY (ok)"

echo ""
echo "=== Preflight: above confirmation threshold (expect CONFIRM_REQUIRED) ==="
npx -y tsx scripts/signet-cli.ts signet-preflight --amount 10 --currency GBP --payee "test.com" --purpose "Test" || true

echo ""
echo "=== Record a payment ==="
npx -y tsx scripts/signet-cli.ts signet-record --amount 3 --currency GBP --payee "test.com" --purpose "Test" --idempotency-key "test-$(date +%s)"

echo ""
echo "=== Report (month) ==="
npx -y tsx scripts/signet-cli.ts signet-report --period month

echo ""
echo "=== Done ==="
