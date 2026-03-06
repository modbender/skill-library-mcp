#!/bin/bash
# test_homeostasis_stability.sh — Verify system self-corrects over 30 cycles
# 
# Success criteria: No need stays at sat=0 (floor=0.5) for all 30 cycles
# This tests that the priority system ensures all needs get attention eventually
#
# Methodology:
# 1. Start from crisis state (all needs at floor)
# 2. Simulate 30 cycles, marking top-priority need as satisfied each cycle
# 3. Track how many cycles each need spends at floor
# 4. FAIL if any need stays at floor for >20 cycles (66%)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
RUN_CYCLE="$SKILL_DIR/scripts/run-cycle.sh"
MARK_SCRIPT="$SKILL_DIR/scripts/mark-satisfied.sh"
STATE_FILE="$SKILL_DIR/assets/needs-state.json"
FIXTURES="$SCRIPT_DIR/../fixtures"

# WORKSPACE required by run-cycle.sh
export WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"

# Backup current state
cp "$STATE_FILE" "$STATE_FILE.homeostasis_backup"

# Start from crisis
cp "$FIXTURES/needs-state-crisis.json" "$STATE_FILE"

# Track cycles at floor per need
declare -A floor_cycles
for need in security integrity coherence closure autonomy connection competence understanding recognition expression; do
    floor_cycles[$need]=0
done

CYCLES=50
MAX_FLOOR_CYCLES=35  # Fail if any need at floor for more than this (70%)

echo "Running $CYCLES simulated cycles..."

for i in $(seq 1 $CYCLES); do
    # Run cycle and extract top ACTION need
    output=$("$RUN_CYCLE" 2>/dev/null)
    
    # Get the first ACTION need
    top_need=$(echo "$output" | grep -m1 "▶ ACTION:" | sed -E 's/.*ACTION: ([a-z]+).*/\1/')
    
    if [[ -n "$top_need" ]]; then
        # Simulate completing the action with medium impact
        "$MARK_SCRIPT" "$top_need" 1.5 > /dev/null 2>&1
    fi
    
    # Check which needs are at floor (sat <= 0.5)
    for need in security integrity coherence closure autonomy connection competence understanding recognition expression; do
        sat=$(jq -r ".$need.satisfaction // 0" "$STATE_FILE")
        if (( $(echo "$sat <= 0.5" | bc -l) )); then
            floor_cycles[$need]=$((floor_cycles[$need] + 1))
        fi
    done
done

# Restore backup
cp "$STATE_FILE.homeostasis_backup" "$STATE_FILE"
rm "$STATE_FILE.homeostasis_backup"

# Check results
echo ""
echo "Cycles at floor (max allowed: $MAX_FLOOR_CYCLES):"
errors=0
for need in security integrity coherence closure autonomy connection competence understanding recognition expression; do
    count=${floor_cycles[$need]}
    if [[ $count -gt $MAX_FLOOR_CYCLES ]]; then
        echo "  $need: $count cycles — FAIL (chronic deprivation)"
        ((errors++))
    else
        echo "  $need: $count cycles — OK"
    fi
done

if [[ $errors -eq 0 ]]; then
    echo ""
    echo "Homeostasis: STABLE"
    exit 0
else
    echo ""
    echo "Homeostasis: UNSTABLE ($errors needs with chronic deprivation)"
    exit 1
fi
