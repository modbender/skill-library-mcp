#!/bin/bash
# test.sh — Basic end-to-end test for the linux-desktop skill
# Verifies that tools are installed and core functions work
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0
SKIP=0

pass() {
    echo "  PASS: $1"
    PASS=$((PASS + 1))
}

fail() {
    echo "  FAIL: $1"
    FAIL=$((FAIL + 1))
}

skip() {
    echo "  SKIP: $1"
    SKIP=$((SKIP + 1))
}

echo "=== linux-desktop skill tests ==="
echo ""

# --- Test 1: Check required commands ---
echo "[1/5] Checking required commands..."
for cmd in xdotool wmctrl scrot xwininfo; do
    if command -v "$cmd" &>/dev/null; then
        pass "$cmd is installed"
    else
        fail "$cmd is NOT installed (run: bash install.sh)"
    fi
done

# --- Test 2: Check DISPLAY ---
echo ""
echo "[2/5] Checking DISPLAY variable..."
if [ -n "$DISPLAY" ]; then
    pass "DISPLAY is set to '$DISPLAY'"
else
    fail "DISPLAY is not set"
    echo ""
    echo "Cannot run remaining tests without DISPLAY. Set it with: export DISPLAY=:0"
    echo ""
    echo "Results: $PASS passed, $FAIL failed, $SKIP skipped"
    exit 1
fi

# --- Test 3: Take a screenshot ---
echo ""
echo "[3/5] Testing screenshot capture..."
SCREENSHOT=$("$SCRIPT_DIR/capture.sh" --json 2>/dev/null)
if echo "$SCREENSHOT" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['success']" 2>/dev/null; then
    SHOT_PATH=$(echo "$SCREENSHOT" | python3 -c "import sys,json; print(json.load(sys.stdin)['output'])")
    if [ -f "$SHOT_PATH" ]; then
        pass "Screenshot captured: $SHOT_PATH"
        # Clean up
        rm -f "$SHOT_PATH"
    else
        fail "Screenshot file not found at reported path"
    fi
else
    fail "capture.sh returned failure"
fi

# --- Test 4: List windows ---
echo ""
echo "[4/5] Testing window listing..."
WINDOWS=$("$SCRIPT_DIR/inspect.sh" 2>/dev/null)
if echo "$WINDOWS" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['success']" 2>/dev/null; then
    WIN_COUNT=$(echo "$WINDOWS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['windows']))")
    pass "Found $WIN_COUNT open windows"
else
    fail "inspect.sh returned failure"
fi

# --- Test 5: Script syntax checks ---
echo ""
echo "[5/5] Checking script syntax..."
for script in capture.sh inspect.sh click.sh type.sh hotkey.sh scroll.sh window.sh; do
    if bash -n "$SCRIPT_DIR/$script" 2>/dev/null; then
        pass "$script syntax OK"
    else
        fail "$script has syntax errors"
    fi
done

# --- Summary ---
echo ""
echo "=== Results ==="
echo "  $PASS passed, $FAIL failed, $SKIP skipped"

if [ "$FAIL" -gt 0 ]; then
    echo ""
    echo "Some tests failed. Run 'bash install.sh' to install missing dependencies."
    exit 1
else
    echo ""
    echo "All tests passed!"
    exit 0
fi
