#!/bin/bash
# Turing Pyramid — Main Cycle Runner
# WORKSPACE is REQUIRED - no silent fallback
if [[ -z "$WORKSPACE" ]]; then
    echo "❌ ERROR: WORKSPACE environment variable not set" >&2
    echo "   Set it explicitly: export WORKSPACE=/path/to/workspace" >&2
    exit 1
fi

# Called on each heartbeat to evaluate and act on needs

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="$SKILL_DIR/assets/needs-config.json"

# Calculate max_tension dynamically from config
# max_tension = max_importance × max_deprivation(3)
MAX_IMPORTANCE=$(jq '[.needs[].importance] | max' "$CONFIG_FILE")
MAX_TENSION=$((MAX_IMPORTANCE * 3))
STATE_FILE="$SKILL_DIR/assets/needs-state.json"
SCRIPTS_DIR="$SKILL_DIR/scripts"
WORKSPACE="$WORKSPACE"
MEMORY_DIR="$WORKSPACE/memory"
LOGS_DIR="$WORKSPACE/memory/logs"

# Check initialization
if [[ ! -f "$STATE_FILE" ]]; then
    echo "❌ Turing Pyramid not initialized. Run: $SCRIPTS_DIR/init.sh"
    exit 1
fi

# Acquire exclusive lock on state file to prevent race conditions
exec 200>"$STATE_FILE.lock"
if ! flock -n 200; then
    echo "⏳ Another cycle is running, waiting..." >&2
    flock 200
fi

NOW=$(date +%s)
NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TODAY=$(date +%Y-%m-%d)

# Bootstrap mode: process ALL needs
if [[ "$1" == "--bootstrap" ]]; then
    MAX_ACTIONS=10
    echo "🚀 BOOTSTRAP MODE — processing all needs"
else
    MAX_ACTIONS=$(jq -r '.settings.max_actions_per_cycle // 3' "$CONFIG_FILE")
fi

# No-scans mode for testing
SKIP_SCANS=false
if [[ "$1" == "--no-scans" || "$2" == "--no-scans" ]]; then
    SKIP_SCANS=true
    echo "⚠️  TEST MODE — skipping event scans"
fi

# Calculate tension for all needs
declare -A TENSIONS
declare -A SATISFACTIONS
declare -A DEPRIVATIONS

calculate_tensions() {
    local needs=$(jq -r '.needs | keys[]' "$CONFIG_FILE")
    
    for need in $needs; do
        local importance=$(jq -r ".needs.\"$need\".importance" "$CONFIG_FILE")
        local decay_rate=$(jq -r ".needs.\"$need\".decay_rate_hours" "$CONFIG_FILE")
        
        # Read current satisfaction from state (float, default 2.0)
        local current_sat=$(jq -r --arg n "$need" '.[$n].satisfaction // 2.0' "$STATE_FILE")
        
        # Read last decay check time (when we last applied decay)
        local last_decay=$(jq -r --arg n "$need" '.[$n].last_decay_check // "1970-01-01T00:00:00Z"' "$STATE_FILE")
        local last_decay_epoch=$(date -d "$last_decay" +%s 2>/dev/null || echo 0)
        
        # Calculate hours since last decay check
        local hours_since_decay=$(echo "scale=4; ($NOW - $last_decay_epoch) / 3600" | bc -l)
        
        # Calculate decay delta: lose 1 satisfaction per decay_rate hours
        # Apply day/night multiplier if enabled
        local decay_multiplier=$("$SCRIPTS_DIR/get-decay-multiplier.sh" 2>/dev/null || echo "1.0")
        local decay_delta=$(echo "scale=4; ($hours_since_decay / $decay_rate) * $decay_multiplier" | bc -l)
        
        # Apply decay to current satisfaction
        local decayed_sat=$(echo "scale=2; $current_sat - $decay_delta" | bc -l)
        
        # Clamp to 0-3 range
        if (( $(echo "$decayed_sat < 0" | bc -l) )); then
            decayed_sat="0.00"
        fi
        if (( $(echo "$decayed_sat > 3" | bc -l) )); then
            decayed_sat="3.00"
        fi
        
        # Run event scan if exists (can only worsen)
        local scan_script="$SCRIPTS_DIR/scan_${need}.sh"
        local event_satisfaction=""
        if [[ "$SKIP_SCANS" != "true" && -x "$scan_script" ]]; then
            event_satisfaction=$("$scan_script" 2>/dev/null)
        fi
        
        # Event scan can override (take worst)
        local satisfaction=$decayed_sat
        if [[ -n "$event_satisfaction" && "$event_satisfaction" =~ ^[0-3]$ ]]; then
            if (( $(echo "$event_satisfaction < $satisfaction" | bc -l) )); then
                satisfaction=$event_satisfaction
            fi
        fi
        
        # Round satisfaction for integer deprivation/tension calc
        local sat_int=$(printf "%.0f" "$satisfaction")
        local deprivation=$(( 3 - sat_int ))
        [[ $deprivation -lt 0 ]] && deprivation=0
        local tension=$(( importance * deprivation ))
        
        TENSIONS[$need]=$tension
        SATISFACTIONS[$need]=$satisfaction  # Keep float for display
        DEPRIVATIONS[$need]=$deprivation
        
        # Update state with decayed satisfaction and decay check time
        jq --arg need "$need" --argjson sat "$satisfaction" --arg now "$NOW_ISO" '
            .[$need].satisfaction = $sat |
            .[$need].last_decay_check = $now
        ' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
    done
}

# Get top N needs by tension
get_top_needs() {
    local n=$1
    for need in "${!TENSIONS[@]}"; do
        echo "${TENSIONS[$need]} $need"
    done | sort -rn | head -n "$n" | awk '{print $2}'
}

# Probability-based action decision
# Returns 0 (true) if should take action, 1 (false) for non-action
# v1.13.0: 6-level action probability with tension bonus
roll_action() {
    local sat=$1
    local tension=$2
    
    # Round float satisfaction to nearest 0.5 for lookup
    # Formula: round(sat * 2) / 2
    local doubled=$(echo "$sat * 2" | bc -l)
    local rounded_int=$(printf "%.0f" "$doubled")
    local sat_rounded=$(echo "scale=1; $rounded_int / 2" | bc -l)
    # Normalize format (.5 → 0.5)
    [[ "$sat_rounded" == .* ]] && sat_rounded="0$sat_rounded"
    # Clamp to valid range [0.5, 3.0]
    if (( $(echo "$sat_rounded < 0.5" | bc -l) )); then sat_rounded="0.5"; fi
    if (( $(echo "$sat_rounded > 3.0" | bc -l) )); then sat_rounded="3.0"; fi
    
    # Base chance by satisfaction level — read from config
    local config_key="sat_$sat_rounded"
    local base_chance=$(jq -r ".action_probability.\"$config_key\" // 50" "$CONFIG_FILE")
    # Validate it's a number, fallback to 50
    [[ ! "$base_chance" =~ ^[0-9]+$ ]] && base_chance=50
    
    # sat=3.0 always skip (no action needed)
    if [[ "$base_chance" -eq 0 ]]; then
        return 1
    fi
    
    # Tension bonus: scales 0-50% based on tension
    # MAX_TENSION = max_importance × max_deprivation(3), calculated from config
    # This preserves importance weighting: higher importance = bigger bonus at same sat
    local max_bonus=50
    local bonus=$(( (tension * max_bonus) / MAX_TENSION ))
    
    # Final chance (capped at 100)
    local final_chance=$((base_chance + bonus))
    [[ $final_chance -gt 100 ]] && final_chance=100
    
    local roll=$((RANDOM % 100))
    [[ $roll -lt $final_chance ]]
}

# Roll for impact range based on satisfaction
# Returns: low, mid, high, or skip (for sat=3.0)
roll_impact_range() {
    local need=$1
    local sat=$2
    local roll=$((RANDOM % 100))
    
    # Round float satisfaction to nearest 0.5 for matrix lookup
    # Formula: round(sat * 2) / 2 → e.g., 1.3→1.5, 1.7→1.5, 2.1→2.0, 2.8→3.0
    local doubled=$(echo "$sat * 2" | bc -l)
    local rounded_int=$(printf "%.0f" "$doubled")
    local sat_rounded=$(echo "scale=1; $rounded_int / 2" | bc -l)
    # Normalize format (.5 → 0.5)
    [[ "$sat_rounded" == .* ]] && sat_rounded="0$sat_rounded"
    # Clamp to valid range [0.5, 3.0]
    if (( $(echo "$sat_rounded < 0.5" | bc -l) )); then sat_rounded="0.5"; fi
    if (( $(echo "$sat_rounded > 3.0" | bc -l) )); then sat_rounded="3.0"; fi
    
    # Get impact matrix probabilities
    local matrix_key="sat_$sat_rounded"
    local p_low p_mid p_high
    
    p_low=$(jq -r ".impact_matrix_default.\"$matrix_key\".low // 25" "$CONFIG_FILE")
    p_mid=$(jq -r ".impact_matrix_default.\"$matrix_key\".mid // 50" "$CONFIG_FILE")
    p_high=$(jq -r ".impact_matrix_default.\"$matrix_key\".high // 25" "$CONFIG_FILE")
    
    # If all zeros (sat=3.0), skip action
    if [[ $p_low -eq 0 && $p_mid -eq 0 && $p_high -eq 0 ]]; then
        echo "skip"
        return
    fi
    
    # Roll: 0-p_low = low, p_low-(p_low+p_mid) = mid, rest = high
    if [[ $roll -lt $p_low ]]; then
        echo "low"
    elif [[ $roll -lt $((p_low + p_mid)) ]]; then
        echo "mid"
    else
        echo "high"
    fi
}

# Get actions filtered by impact range (low/mid/high)
get_actions_by_range() {
    local need=$1
    local range=$2
    
    case $range in
        low)  jq -r ".needs.\"$need\".actions[] | select(.impact < 1.0) | .name" "$CONFIG_FILE" ;;
        mid)  jq -r ".needs.\"$need\".actions[] | select(.impact >= 1.0 and .impact < 2.0) | .name" "$CONFIG_FILE" ;;
        high) jq -r ".needs.\"$need\".actions[] | select(.impact >= 2.0) | .name" "$CONFIG_FILE" ;;
    esac
}

# Weighted random selection of action by impact range
select_weighted_action() {
    local need=$1
    local range=$2
    
    # Get actions with weights for this impact range
    local actions_json
    case $range in
        low)  actions_json=$(jq -c "[.needs.\"$need\".actions[] | select(.impact < 1.0)]" "$CONFIG_FILE") ;;
        mid)  actions_json=$(jq -c "[.needs.\"$need\".actions[] | select(.impact >= 1.0 and .impact < 2.0)]" "$CONFIG_FILE") ;;
        high) actions_json=$(jq -c "[.needs.\"$need\".actions[] | select(.impact >= 2.0)]" "$CONFIG_FILE") ;;
    esac
    
    local count=$(echo "$actions_json" | jq 'length')
    
    if [[ $count -eq 0 ]]; then
        echo ""
        return
    fi
    
    if [[ $count -eq 1 ]]; then
        echo "$actions_json" | jq -r '.[0].name'
        return
    fi
    
    # Calculate total weight
    local total_weight=$(echo "$actions_json" | jq '[.[].weight // 100] | add')
    local roll=$((RANDOM % total_weight))
    
    # Select based on cumulative weights
    local cumulative=0
    local selected=""
    
    for i in $(seq 0 $((count - 1))); do
        local weight=$(echo "$actions_json" | jq -r ".[$i].weight // 100")
        local name=$(echo "$actions_json" | jq -r ".[$i].name")
        cumulative=$((cumulative + weight))
        
        if [[ $roll -lt $cumulative ]]; then
            selected="$name"
            break
        fi
    done
    
    echo "$selected"
}

# Log non-action (noticed but deferred)
log_noticed() {
    local need=$1
    local sat=$2
    local tension=$3
    local timestamp=$(date +"%H:%M")
    
    # Append to today's memory with timestamp
    if [[ -d "$MEMORY_DIR" ]]; then
        echo "- [$timestamp] ○ noticed: $need (sat=$sat, tension=$tension) — non-action" >> "$LOGS_DIR/$TODAY-cycles.log"
    fi
}

# Log action taken
log_action() {
    local need=$1
    local sat=$2
    local tension=$3
    local timestamp=$(date +"%H:%M")
    
    # Append to today's memory with timestamp
    if [[ -d "$MEMORY_DIR" ]]; then
        echo "- [$timestamp] ▶ action: $need (sat=$sat, tension=$tension) — requires action" >> "$LOGS_DIR/$TODAY-cycles.log"
    fi
}

# Main execution
echo "🔺 Turing Pyramid — Cycle at $(date)"
echo "======================================"

# Apply cross-need deprivation effects first
if [[ -x "$SCRIPTS_DIR/apply-deprivation.sh" ]]; then
    "$SCRIPTS_DIR/apply-deprivation.sh"
fi

calculate_tensions

# Check if all satisfied
all_satisfied=true
for need in "${!TENSIONS[@]}"; do
    if [[ ${TENSIONS[$need]} -gt 0 ]]; then
        all_satisfied=false
        break
    fi
done

if $all_satisfied; then
    echo "✅ All needs satisfied. HEARTBEAT_OK"
    exit 0
fi

# Show current tensions
echo ""
echo "Current tensions:"
for need in "${!TENSIONS[@]}"; do
    if [[ ${TENSIONS[$need]} -gt 0 ]]; then
        echo "  $need: tension=${TENSIONS[$need]} (sat=${SATISFACTIONS[$need]}, dep=${DEPRIVATIONS[$need]})"
    fi
done | sort -t'=' -k2 -rn

# Select top needs
echo ""
echo "Selecting top $MAX_ACTIONS needs..."
top_needs=$(get_top_needs $MAX_ACTIONS)

echo ""
echo "📋 Decisions:"

action_count=0
noticed_count=0

for need in $top_needs; do
    if [[ ${TENSIONS[$need]} -gt 0 ]]; then
        sat=${SATISFACTIONS[$need]}
        tension=${TENSIONS[$need]}
        
        if roll_action $sat $tension; then
            # Roll for impact range first
            impact_range=$(roll_impact_range "$need" "$sat")
            
            # If sat=3.0, skip action (fully satisfied)
            if [[ "$impact_range" == "skip" ]]; then
                ((noticed_count++))
                echo ""
                echo "○ SATISFIED: $need (sat=$sat) — no action needed"
                continue
            fi
            
            # ACTION - weighted action selection
            ((action_count++))
            
            # Select specific action using weights within range
            selected_action=$(select_weighted_action "$need" "$impact_range")
            
            # Get actual impact value of selected action
            actual_impact=""
            if [[ -n "$selected_action" ]]; then
                actual_impact=$(jq -r ".needs.\"$need\".actions[] | select(.name == \"$selected_action\") | .impact" "$CONFIG_FILE")
            fi
            
            echo ""
            echo "▶ ACTION: $need (tension=$tension, sat=$sat)"
            echo "  Range $impact_range rolled → selected:"
            
            if [[ -n "$selected_action" ]]; then
                echo "    ★ $selected_action (impact: $actual_impact)"
            else
                # Fallback: show all actions if no weighted selection
                echo "  (no $impact_range actions, showing all):"
                jq -r ".needs.\"$need\".actions[] | \"    • \" + .name + \" (impact \" + (.impact|tostring) + \")\"" "$CONFIG_FILE"
            fi
            
            echo "  Then: mark-satisfied.sh $need $actual_impact"
            
            # Log to memory with selected action
            log_action "$need" "$sat" "$tension"
        else
            # NON-ACTION - noticed but deferred
            ((noticed_count++))
            echo ""
            echo "○ NOTICED: $need (tension=$tension, sat=$sat) — deferred"
            log_noticed "$need" "$sat" "$tension"
        fi
    fi
done

echo ""
echo "======================================"
echo "Summary: $action_count action(s), $noticed_count noticed"

if [[ $action_count -gt 0 ]]; then
    echo ""
    echo "After completing actions, update state with:"
    echo "  ./scripts/mark-satisfied.sh <need> [impact]"
fi
