#!/usr/bin/env bash
# wreckit — CLI bootstrap for triggering a full swarm audit
# Usage: ./run-audit.sh [project-path] [mode] [--spawn]
# Mode: BUILD | REBUILD | FIX | AUDIT (default: AUDIT)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRECKIT_DIR="$(dirname "$SCRIPT_DIR")"

SPAWN=0
SHOW_HELP=0
ARGS=()
for arg in "$@"; do
  case "$arg" in
    --spawn) SPAWN=1 ;;
    --help|-h) SHOW_HELP=1 ;;
    *) ARGS+=("$arg") ;;
  esac
done
set -- "${ARGS[@]}"

if [ "$SHOW_HELP" -eq 1 ]; then
  echo "wreckit — Swarm Audit Bootstrap"
  echo ""
  echo "Usage: ./run-audit.sh [project-path] [mode] [--spawn]"
  echo "  project-path: target project directory (default: .)"
  echo "  mode: BUILD | REBUILD | FIX | AUDIT (default: AUDIT)"
  echo "  --spawn: attempt to spawn the orchestrator via openclaw"
  exit 0
fi

PROJECT="${1:-.}"
MODE="${2:-AUDIT}"
PROJECT="$(cd "$PROJECT" && pwd)"

echo "================================================"
echo "  wreckit — Swarm Audit Bootstrap"
echo "================================================"
echo "Project: $PROJECT"
echo "Mode:    $MODE"
echo "Skill:   $WRECKIT_DIR"
echo ""

# ─── Validate mode ─────────────────────────────────────────────────────────
if [[ ! "$MODE" =~ ^(BUILD|REBUILD|FIX|AUDIT)$ ]]; then
  echo "ERROR: Mode must be BUILD, REBUILD, FIX, or AUDIT"
  exit 1
fi

# ─── Validate project exists ────────────────────────────────────────────────
if [ ! -d "$PROJECT" ]; then
  echo "ERROR: Project directory not found: $PROJECT"
  exit 1
fi

# ─── Check openclaw config ──────────────────────────────────────────────────
echo "Checking OpenClaw config..."
CONFIG_FILE="$HOME/.openclaw/openclaw.json"
if [ ! -f "$CONFIG_FILE" ]; then
  echo "ERROR: OpenClaw config not found at $CONFIG_FILE"
  exit 1
fi

# Check maxSpawnDepth
MAX_SPAWN=$(python3 -c "
import json
with open('$CONFIG_FILE') as f:
    c = json.load(f)
subagents = c.get('agents',{}).get('defaults',{}).get('subagents',{})
print(subagents.get('maxSpawnDepth', 1))
" 2>/dev/null || echo "1")

MAX_CHILDREN=$(python3 -c "
import json
with open('$CONFIG_FILE') as f:
    c = json.load(f)
subagents = c.get('agents',{}).get('defaults',{}).get('subagents',{})
print(subagents.get('maxChildrenPerAgent', 4))
" 2>/dev/null || echo "4")

echo "  maxSpawnDepth:     $MAX_SPAWN (need >= 2)"
echo "  maxChildrenPerAgent: $MAX_CHILDREN (need >= 8)"

ERRORS=0
if [ "$MAX_SPAWN" -lt 2 ] 2>/dev/null; then
  echo "  ❌ maxSpawnDepth too low!"
  ERRORS=$((ERRORS + 1))
else
  echo "  ✅ maxSpawnDepth ok"
fi

if [ "$MAX_CHILDREN" -lt 8 ] 2>/dev/null; then
  echo "  ❌ maxChildrenPerAgent too low!"
  ERRORS=$((ERRORS + 1))
else
  echo "  ✅ maxChildrenPerAgent ok"
fi

if [ "$ERRORS" -gt 0 ]; then
  echo ""
  echo "Fix your config with:"
  echo "  openclaw config set agents.defaults.subagents.maxSpawnDepth 2"
  echo "  openclaw config set agents.defaults.subagents.maxChildrenPerAgent 8"
  echo "  openclaw config set agents.defaults.subagents.maxConcurrent 8"
  exit 1
fi

# ─── Detect project type + stack ────────────────────────────────────────────
echo ""
echo "Detecting project profile..."
PROJECT_TYPE_JSON=$("$SCRIPT_DIR/project-type.sh" "$PROJECT" 2>/dev/null || echo "{}")
P_TYPE=$(echo "$PROJECT_TYPE_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('type','unknown'))" 2>/dev/null || echo "unknown")
P_CONF=$(echo "$PROJECT_TYPE_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('confidence',0.0))" 2>/dev/null || echo "0.0")
P_SLOP=$(echo "$PROJECT_TYPE_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('calibration',{}).get('slop_per_kloc',5))" 2>/dev/null || echo "5")
P_GOD=$(echo "$PROJECT_TYPE_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('calibration',{}).get('god_module_fanin',10))" 2>/dev/null || echo "10")
P_CI_REQ=$(echo "$PROJECT_TYPE_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(str(bool(d.get('calibration',{}).get('ci_required', False))).lower())" 2>/dev/null || echo "false")

echo "  Project type: $P_TYPE (confidence $P_CONF)"
echo "  Calibration: slop_per_kloc=$P_SLOP god_module_fanin=$P_GOD ci_required=$P_CI_REQ"

echo ""
echo "Detecting project stack..."
STACK_JSON=$("$SCRIPT_DIR/detect-stack.sh" "$PROJECT" 2>/dev/null || echo "{}")
LANG=$(echo "$STACK_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('language','unknown'))" 2>/dev/null || echo "unknown")
FRAMEWORK=$(echo "$STACK_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('framework',''))" 2>/dev/null || echo "")
TEST_CMD=$(echo "$STACK_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('commands',{}).get('test',''))" 2>/dev/null || echo "")
TYPE_CMD=$(echo "$STACK_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('commands',{}).get('typeCheck',''))" 2>/dev/null || echo "")

echo "  Language:  $LANG"
echo "  Framework: $FRAMEWORK"
echo "  Tests:     $TEST_CMD"
echo "  TypeCheck: $TYPE_CMD"

# Check if .wreckit dir exists (previous run)
PREV_RUN=""
if [ -f "$PROJECT/.wreckit/dashboard.json" ]; then
  PREV_RUN=$(python3 -c "
import json
with open('$PROJECT/.wreckit/dashboard.json') as f:
    d = json.load(f)
print(d.get('verdict','unknown') + ' on ' + d.get('timestamp','?'))
" 2>/dev/null || echo "exists")
  echo ""
  echo "Previous run: $PREV_RUN"
fi

# ─── Build orchestrator task ────────────────────────────────────────────────
echo ""
echo "================================================"
echo "  READY-TO-PASTE ORCHESTRATOR TASK"
echo "================================================"
echo ""
TASK_TEXT=$(cat << TASK
You are the wreckit orchestrator for a code verification run.

PROJECT: $PROJECT
MODE: $MODE
WRECKIT SKILL: $WRECKIT_DIR
STACK: $LANG / $FRAMEWORK
TEST COMMAND: $TEST_CMD
TYPE CHECK: $TYPE_CMD

Read these files FIRST before doing anything else:
1. $WRECKIT_DIR/SKILL.md
2. $WRECKIT_DIR/references/swarm/orchestrator.md
3. $WRECKIT_DIR/references/swarm/collect.md
4. $WRECKIT_DIR/references/swarm/handoff.md

ANTI-FABRICATION OATH: Output this literally before starting:
"I will not write the proof bundle until ALL workers have announced back.
I will not fabricate any results. If a worker times out, I mark it ERROR."

Then:
1. DECLARE the verification checklist (all workers PENDING) BEFORE spawning
2. Spawn all parallel verification workers simultaneously (slop, typecheck, testquality, mutation, security)
3. STOP and wait. Update checklist after EVERY announce. DO NOT proceed until all complete.
4. Run sequential gates (cross-verify for BUILD, regression for REBUILD/FIX)
5. Output pre-proof-bundle verification checklist — all boxes must check
6. Write proof bundle to $PROJECT/.wreckit/
7. Final verdict as last line: Ship ✅ / Caution ⚠️ / Blocked 🚫

Use these scripts from $WRECKIT_DIR/scripts/:
Core (all modes):
- detect-stack.sh $PROJECT         → language, test cmd, type checker
- check-deps.sh $PROJECT           → hallucinated dep detection
- slop-scan.sh $PROJECT            → placeholders, empty stubs, template artifacts
- coverage-stats.sh $PROJECT       → raw coverage stats
- mutation-test.sh $PROJECT        → mutation testing (mutmut/cargo-mutants/Stryker/AI fallback)
- red-team.sh $PROJECT             → SAST + security vulnerability scan (20+ patterns)

Additional (include in Phase 3 workers):
- dynamic-analysis.sh $PROJECT     → memory leaks, race conditions, FD leaks
- perf-benchmark.sh $PROJECT       → benchmark detection + regression vs baseline
- property-test.sh $PROJECT        → property-based/fuzz testing
- design-review.sh $PROJECT        → dep graph, circular deps, god modules (AUDIT/REBUILD)
- ci-integration.sh $PROJECT       → CI config detection + scoring
- differential-test.sh $PROJECT    → oracle comparison, golden tests (BUILD/REBUILD)

Worker models:
- slop/typecheck/testquality/mutation/security: anthropic/claude-sonnet-4-6
- cross-verify/regression/judge: anthropic/claude-opus-4-6
TASK
)

echo "$TASK_TEXT"

echo ""
echo "================================================"
echo ""
echo "Copy the task above and paste it into:"
echo "  sessions_spawn(task=<above>, label='wreckit-orchestrator')"
echo ""
echo "Or trigger from OpenClaw:"
echo "  'Use wreckit to audit $PROJECT. Don\\'t change anything.'"

if [ "$SPAWN" -eq 1 ] || [[ "${*}" == *"--spawn"* ]]; then
  echo ""
  echo "Attempting to spawn via openclaw..."
  if command -v openclaw >/dev/null 2>&1; then
    openclaw session spawn --task "$TASK_TEXT" --label "wreckit-orchestrator-$(date +%s)" 2>/dev/null && \
      echo "✅ Spawned! Monitor with: openclaw session list" || \
      echo "⚠️  Spawn failed. Copy the task above and paste it into your agent session."
  else
    echo "openclaw not found. Copy the task above and paste it into your agent session."
  fi
fi
