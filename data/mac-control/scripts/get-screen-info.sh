#!/bin/bash
# Get screen resolution and scale factor
# Outputs: physical resolution, logical resolution, and scale factor

echo "=== Display Info ==="
system_profiler SPDisplaysDataType 2>/dev/null | grep -E "Display Type|Resolution|Retina|Main Display"

echo ""
echo "=== Logical Screen Size (what apps see) ==="
# Get logical resolution via system_profiler or defaults
osascript -e 'tell application "Finder" to get bounds of window of desktop' 2>/dev/null || \
    system_profiler SPDisplaysDataType 2>/dev/null | grep "UI Looks like"

echo ""
echo "=== Quick Reference ==="
# Parse physical resolution
PHYSICAL=$(system_profiler SPDisplaysDataType 2>/dev/null | grep "Resolution:" | head -1 | sed 's/.*: //')
echo "Physical: $PHYSICAL"

# Determine scale factor
if echo "$PHYSICAL" | grep -q "3840"; then
    echo "Likely scale: 2x (divide screenshot coords by 2 for cliclick)"
elif echo "$PHYSICAL" | grep -q "2560"; then
    echo "Likely scale: 2x (divide screenshot coords by 2 for cliclick)"
elif echo "$PHYSICAL" | grep -q "5120"; then
    echo "Likely scale: 2x (divide screenshot coords by 2 for cliclick)"
else
    echo "Scale: Check 'UI Looks like' vs 'Resolution' to determine"
fi
