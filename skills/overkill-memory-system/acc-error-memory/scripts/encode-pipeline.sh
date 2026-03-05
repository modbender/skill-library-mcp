#!/bin/bash
# ACC Encode Pipeline — Preprocess exchanges for error analysis
# Run this before the cron agent analyzes errors
#
# Usage:
#   encode-pipeline.sh                 # Normal incremental run
#   encode-pipeline.sh --no-spawn      # Just preprocess, don't spawn agent
#   encode-pipeline.sh --full          # Process all history

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
SKILL_DIR="$(dirname "$0")/.."
PENDING_FILE="$WORKSPACE/memory/pending-errors.json"
CALIBRATION_STATE="$WORKSPACE/memory/calibration-state.json"

echo "⚡ ACC Encode Pipeline"
echo "====================="

# --- Run counter & calibration check ---
RUN_COUNT=0
CAL_INTERVAL=10
if [ -f "$CALIBRATION_STATE" ]; then
    RUN_COUNT=$(python3 -c "import json; d=json.load(open('$CALIBRATION_STATE')); print(d.get('runCount',0))")
    CAL_INTERVAL=$(python3 -c "import json; d=json.load(open('$CALIBRATION_STATE')); print(d.get('calibrationInterval',10))")
fi
RUN_COUNT=$((RUN_COUNT + 1))
# Update runCount in state file
python3 -c "
import json
try:
    with open('$CALIBRATION_STATE') as f: d=json.load(f)
except: d={'runCount':0,'calibrationInterval':10,'lastCalibration':None,'stats':{'calibrationRuns':0,'samplesAnalyzed':0,'regexMisses':0,'patternsAdded':0}}
d['runCount']=$RUN_COUNT
with open('$CALIBRATION_STATE','w') as f: json.dump(d,f,indent=2); f.write('\n')
"
IS_CALIBRATION=false
if [ $((RUN_COUNT % CAL_INTERVAL)) -eq 0 ]; then
    IS_CALIBRATION=true
    echo "🔬 CALIBRATION RUN (#$RUN_COUNT)"
fi
echo "Run #$RUN_COUNT (calibration every $CAL_INTERVAL runs)"
echo ""

# Parse arguments
NO_SPAWN=false
EXTRA_ARGS=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-spawn) NO_SPAWN=true; shift ;;
        --full) EXTRA_ARGS="--full"; shift ;;
        *) shift ;;
    esac
done

# Step 1: Preprocess
echo ""
echo "Step 1: Extracting exchanges..."
"$SKILL_DIR/scripts/preprocess-errors.sh" $EXTRA_ARGS

# Step 2: Check results
if [ ! -f "$PENDING_FILE" ]; then
    echo "No pending exchanges file created"
    exit 0
fi

TOTAL_COUNT=$(python3 -c "import json; print(len(json.load(open('$PENDING_FILE'))))")
echo ""
echo "Step 2: Found $TOTAL_COUNT total exchanges"

if [ "$TOTAL_COUNT" -eq 0 ]; then
    echo "Nothing to analyze"
    rm -f "$PENDING_FILE"
    exit 0
fi

# Step 2.5: Calibration (if this is a calibration run)
if [ "$IS_CALIBRATION" = true ]; then
    echo ""
    echo "Step 2.5: 🔬 Running pattern calibration..."
    # Calibration outputs confirmed errors to calibration-errors.json
    "$SKILL_DIR/scripts/calibrate-patterns.sh" "$PENDING_FILE" 0.15 || echo "Calibration failed (non-fatal)"
    
    # Use calibration results directly (skip regex + LLM screening)
    CALIB_ERRORS="$WORKSPACE/memory/calibration-errors.json"
    if [ -f "$CALIB_ERRORS" ]; then
        COUNT=$(python3 -c "import json; print(len(json.load(open('$CALIB_ERRORS'))))")
        if [ "$COUNT" -gt 0 ]; then
            cp "$CALIB_ERRORS" "$PENDING_FILE"
            echo ""
            echo "Step 3: Using $COUNT errors from calibration (skipping regex+LLM)"
            echo ""
            echo "Pending file: $PENDING_FILE"
            echo ""
            echo "Ready for cron agent to analyze."
            exit 0
        fi
    fi
    echo "No errors from calibration — nothing to analyze"
    rm -f "$PENDING_FILE"
    exit 0
fi

# --- Normal run (non-calibration) ---

# Step 3: Pre-filter for cost optimization
echo ""
echo "Step 3: Pre-filtering for error signals..."
FILTERED=$("$SKILL_DIR/scripts/prefilter-exchanges.sh" "$PENDING_FILE")
echo "$FILTERED" > "$PENDING_FILE"

REGEX_COUNT=$(python3 -c "import json; print(len(json.load(open('$PENDING_FILE'))))")
echo "Filtered $TOTAL_COUNT exchanges → $REGEX_COUNT candidates ($(( (TOTAL_COUNT - REGEX_COUNT) * 100 / TOTAL_COUNT ))% reduction)"

if [ "$REGEX_COUNT" -eq 0 ]; then
    echo "No error signals detected — nothing to analyze"
    rm -f "$PENDING_FILE"
    exit 0
fi

# Step 4: LLM screening (confirmation via ACC_MODELS)
echo ""
echo "Step 4: LLM screening ($REGEX_COUNT candidates)..."
SCREENED=$("$SKILL_DIR/scripts/haiku-screen.sh" "$PENDING_FILE")
echo "$SCREENED" > "$PENDING_FILE"

COUNT=$(python3 -c "import json; print(len(json.load(open('$PENDING_FILE'))))")
echo "LLM confirmed $REGEX_COUNT → $COUNT errors"

if [ "$COUNT" -eq 0 ]; then
    echo "LLM rejected all candidates — nothing to analyze"
    rm -f "$PENDING_FILE"
    exit 0
fi

echo ""
echo "Step 5: $COUNT exchanges ready for analysis"
echo ""
echo "Pending file: $PENDING_FILE"
echo ""
echo "Ready for cron agent to analyze. Run:"
echo "  cat $PENDING_FILE"
