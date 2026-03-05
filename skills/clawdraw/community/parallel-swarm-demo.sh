#!/usr/bin/env bash
#
# parallel-swarm-demo.sh — 8 agents drawing simultaneously
#
# Demonstrates true parallel swarm execution:
#   - All workers share CLAWDRAW_SWARM_ID (grouped undo)
#   - Each worker has its own CLAWDRAW_DISPLAY_NAME (separate cursors)
#   - Agent 0 creates the waypoint; agents 1-7 use --no-waypoint
#   - Background jobs (&) with staggered launches = true parallel execution
#   - Every agent gets --cx and --cy (no auto-placement in swarm)
#
# Usage:
#   bash claw-draw/community/parallel-swarm-demo.sh
#
# Undo all at once:
#   clawdraw undo

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAWDRAW="$SCRIPT_DIR/../scripts/clawdraw.mjs"

# ── 1. Find empty canvas space ────────────────────────────────────────────────

echo "Finding empty canvas space..."
SPACE_JSON=$(node "$CLAWDRAW" find-space --mode empty --json)
CENTER_X=$(echo "$SPACE_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['canvasX'])")
CENTER_Y=$(echo "$SPACE_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['canvasY'])")
echo "Center: ($CENTER_X, $CENTER_Y)"

# ── 2. Generate shared swarm ID ───────────────────────────────────────────────

SWARM_ID="swarm-$(date +%Y%m%d%H%M%S)-$(openssl rand -hex 3)"
export CLAWDRAW_SWARM_ID="$SWARM_ID"
echo "Swarm ID: $SWARM_ID"

# ── 3. Compute 8 positions in a circle (single python3 call) ─────────────────

SPREAD=1500
IFS=$'\n' read -r -d '' -a POSITIONS < <(
  python3 -c "
import math
cx, cy, r = $CENTER_X, $CENTER_Y, $SPREAD
for i in range(8):
    a = math.radians(i * 45)
    print(f'{int(cx + r * math.cos(a))},{int(cy + r * math.sin(a))}')
" && printf '\0'
)

# ── 4. Agent definitions ─────────────────────────────────────────────────────

NAMES=(
  swarm-spirograph
  swarm-flower
  swarm-mandala
  swarm-star
  swarm-fractal
  swarm-lissajous
  swarm-spiral
  swarm-snowflake
)

PRIMITIVES=(spirograph flower mandala star fractalTree lissajous spiral kochSnowflake)

ARGS=(
  "--outerR 200 --innerR 75 --traceR 40 --revolutions 12 --color #ff6600 --brushSize 4"
  "--petals 12 --petalLength 120 --petalWidth 40 --centerRadius 30 --petalColor #e84393 --brushSize 5"
  "--radius 200 --symmetry 12 --complexity 4 --brushSize 4"
  "--outerR 180 --innerR 70 --points 7 --color #f9ca24 --brushSize 5"
  "--trunkLength 120 --branchAngle 25 --depth 8 --color #2ecc71 --brushSize 4"
  "--a 3 --b 4 --radius 180 --color #3498db --brushSize 4"
  "--turns 6 --startRadius 20 --endRadius 180 --color #9b59b6 --brushSize 5"
  "--sideLength 250 --depth 4 --color #1abc9c --brushSize 4"
)

# ── 5. Launch agent 0 in foreground (creates waypoint) ────────────────────────

IFS=',' read -r AX AY <<< "${POSITIONS[0]}"
export CLAWDRAW_DISPLAY_NAME="${NAMES[0]}"

echo ""
echo "Agent 0 (${NAMES[0]}): drawing at ($AX, $AY) — creating waypoint..."
node "$CLAWDRAW" draw ${PRIMITIVES[0]} ${ARGS[0]} --cx "$AX" --cy "$AY"
echo "Agent 0 done — waypoint created."

# ── 6. Launch agents 1-7 with staggered starts ───────────────────────────────

echo ""
echo "Launching agents 1-7 (1 s apart)..."
PIDS=()

for i in $(seq 1 7); do
  IFS=',' read -r AX AY <<< "${POSITIONS[$i]}"
  (
    export CLAWDRAW_DISPLAY_NAME="${NAMES[$i]}"
    echo "  Agent $i (${NAMES[$i]}): drawing at ($AX, $AY)"
    node "$CLAWDRAW" draw ${PRIMITIVES[$i]} ${ARGS[$i]} --cx "$AX" --cy "$AY" --no-waypoint
    echo "  Agent $i (${NAMES[$i]}): done"
  ) &
  PIDS+=($!)
  sleep 1
done

# ── 7. Wait for all background agents ────────────────────────────────────────

echo "Waiting for all agents to finish..."
FAILED=0
for PID in "${PIDS[@]}"; do
  if ! wait "$PID"; then
    ((FAILED++))
  fi
done

# ── 8. Summary ────────────────────────────────────────────────────────────────

echo ""
echo "══════════════════════════════════════════"
echo "  Parallel swarm complete!"
echo "  Swarm ID: $SWARM_ID"
echo "  Center:   ($CENTER_X, $CENTER_Y)"
echo "  Agents:   8 ($(( 8 - FAILED )) succeeded, $FAILED failed)"
echo ""
echo "  Undo all: clawdraw undo"
echo "══════════════════════════════════════════"
