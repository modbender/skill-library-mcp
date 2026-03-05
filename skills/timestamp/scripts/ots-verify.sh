#!/usr/bin/env bash
# Verify OpenTimestamps proofs
# Usage: ots-verify.sh [file1.ots] [file2.ots] ...
# Without args: verifies all .ots files in workspace
set -euo pipefail

OTS="${OTS_BIN:-ots}"
WORKSPACE="${WORKSPACE:-$(cd "$(dirname "$0")/../../.." && pwd)}"

files=("$@")

# If no args, find all .ots files in workspace
if [ ${#files[@]} -eq 0 ]; then
    mapfile -t files < <(find "$WORKSPACE" -name "*.ots" -not -path "*/.git/*" -not -path "*/node_modules/*" 2>/dev/null)
    if [ ${#files[@]} -eq 0 ]; then
        echo "No .ots files found in $WORKSPACE"
        exit 0
    fi
    echo "Found ${#files[@]} proof(s) to verify"
    echo ""
fi

confirmed=0
pending=0
failed=0
set +e

for ots_file in "${files[@]}"; do
    if [ ! -f "$ots_file" ]; then
        echo "SKIP: $ots_file (not found)"
        continue
    fi

    echo "VERIFY: $ots_file"
    output=$($OTS verify "$ots_file" 2>&1) || true

    if echo "$output" | grep -q "Success!"; then
        echo "  ✓ $output"
        ((confirmed++))
    elif echo "$output" | grep -q "Pending"; then
        echo "  ⏳ Pending Bitcoin confirmation"
        ((pending++))
    else
        echo "  ✗ $output"
        ((failed++))
    fi
done

echo ""
echo "Results: $confirmed confirmed, $pending pending, $failed failed"
