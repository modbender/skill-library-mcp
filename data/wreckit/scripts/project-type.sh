#!/usr/bin/env bash
# wreckit — Project type classifier
# Usage: ./project-type.sh [project-path]
# Output: JSON with type, confidence, signals, and calibration profile

set -euo pipefail
PROJECT="${1:-.}"
PROJECT="$(cd "$PROJECT" && pwd)"
cd "$PROJECT"

# Helpers
has_file() {
  local pattern="$1"
  compgen -G "$pattern" >/dev/null 2>&1
}

json_get_pkg() {
  local expr="$1"
  if [ -f package.json ]; then
    python3 - <<PYEOF
import json
with open('package.json','r',encoding='utf-8') as f:
    d=json.load(f)
print($expr)
PYEOF
  fi
}

safe_int() {
  local v="$1"
  if [[ "$v" =~ ^[0-9]+$ ]]; then
    echo "$v"
  else
    echo "0"
  fi
}

# ─── Detect signals ─────────────────────────────────────────────────────────

# package.json signals
PKG_HAS_EXPORTS="false"
PKG_MAIN=""
PKG_MAIN_DIST="false"
PKG_MAIN_APP="false"
PKG_EXPORTS_DIST="false"
if [ -f package.json ]; then
  PKG_HAS_EXPORTS=$(json_get_pkg "'true' if 'exports' in d else 'false'")
  PKG_MAIN=$(json_get_pkg "d.get('main','')")
  if echo "$PKG_MAIN" | grep -q "dist/"; then
    PKG_MAIN_DIST="true"
  fi
  if echo "$PKG_MAIN" | grep -Eq "(^|/)(src/)?(app|pages)(/|$)"; then
    PKG_MAIN_APP="true"
  fi
  if python3 - <<'PYEOF' >/dev/null 2>&1
import json, sys
with open('package.json','r',encoding='utf-8') as f:
    d=json.load(f)
exp=d.get('exports',{})
vals=[]
if isinstance(exp,str):
    vals=[exp]
elif isinstance(exp,dict):
    for v in exp.values():
        if isinstance(v,str):
            vals.append(v)
        elif isinstance(v,dict):
            vals.extend([x for x in v.values() if isinstance(x,str)])
sys.exit(0 if any('dist/' in v for v in vals) else 1)
PYEOF
  then
    PKG_EXPORTS_DIST="true"
  fi
fi

HAS_DIST_DIR="false"
HAS_LIB_DIR="false"
[ -d "dist" ] && HAS_DIST_DIR="true"
[ -d "lib" ] && HAS_LIB_DIR="true"

HAS_APP_DIR="false"
[ -d "src/app" ] && HAS_APP_DIR="true"
[ -d "src/pages" ] && HAS_APP_DIR="true"

HAS_APP_CONFIG="false"
if has_file "next.config.*" || has_file "vite.config.*"; then
  HAS_APP_CONFIG="true"
fi

HAS_ENV_FILE="false"
if find . -maxdepth 1 -name ".env*" 2>/dev/null | head -1 | grep -q .; then
  HAS_ENV_FILE="true"
fi

# AI-generated signals
GIT_IS_SHALLOW="false"
[ -f ".git/shallow" ] && GIT_IS_SHALLOW="true"
git rev-parse --is-shallow-repository 2>/dev/null | grep -q "true" && GIT_IS_SHALLOW="true"

GIT_COMMIT_COUNT=0
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  GIT_COMMIT_COUNT=$(git log --oneline 2>/dev/null | wc -l | tr -d ' ')
fi
GIT_COMMIT_COUNT=$(safe_int "$GIT_COMMIT_COUNT")

PROJECT_AGE_DAYS=9999
if [ "$GIT_IS_SHALLOW" = "false" ] && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  FIRST_COMMIT_TS=$(git log --reverse --format=%ct 2>/dev/null | head -1 || true)
  if [[ "$FIRST_COMMIT_TS" =~ ^[0-9]+$ ]]; then
    NOW_TS=$(date +%s)
    PROJECT_AGE_DAYS=$(( (NOW_TS - FIRST_COMMIT_TS) / 86400 ))
  fi
else
  # Fallback: oldest file mtime
  OLDEST_TS=$(python3 - <<'PYEOF'
import os, time
old=None
for root, dirs, files in os.walk('.'):
    if '/.git' in root or '/node_modules' in root or '/dist' in root or '/build' in root or '/.wreckit' in root:
        continue
    for f in files:
        p=os.path.join(root,f)
        try:
            m=os.path.getmtime(p)
            if old is None or m < old:
                old=m
        except Exception:
            pass
print(int(old) if old else 0)
PYEOF
  )
  if [[ "$OLDEST_TS" =~ ^[0-9]+$ ]] && [ "$OLDEST_TS" -gt 0 ]; then
    NOW_TS=$(date +%s)
    PROJECT_AGE_DAYS=$(( (NOW_TS - OLDEST_TS) / 86400 ))
  fi
fi

TEST_FILE_COUNT=$(find . \( -name '*test*' -o -name '*spec*' -o -path '*/__tests__/*' -o -path '*/tests/*' \) \
  -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' -not -path '*/build/*' 2>/dev/null | wc -l | tr -d ' ')
TEST_FILE_COUNT=$(safe_int "$TEST_FILE_COUNT")

# Monorepo signals
HAS_PNPM_WORKSPACE="false"
HAS_NX="false"
HAS_TURBO="false"
[ -f "pnpm-workspace.yaml" ] && HAS_PNPM_WORKSPACE="true"
[ -f "nx.json" ] && HAS_NX="true"
[ -f "turbo.json" ] && HAS_TURBO="true"

PACKAGES_PKG_COUNT=0
if [ -d "packages" ]; then
  PACKAGES_PKG_COUNT=$(find packages -mindepth 1 -maxdepth 3 -name package.json 2>/dev/null | wc -l | tr -d ' ')
fi
PACKAGES_PKG_COUNT=$(safe_int "$PACKAGES_PKG_COUNT")
HAS_MULTI_PACKAGES="false"
if [ "$PACKAGES_PKG_COUNT" -ge 2 ] 2>/dev/null; then
  HAS_MULTI_PACKAGES="true"
fi

# ─── Score each type ─────────────────────────────────────────────────────────

LIB_SCORE=0
LIB_SIGNALS=()
if [ "$PKG_HAS_EXPORTS" = "true" ]; then
  LIB_SCORE=$((LIB_SCORE + 30))
  LIB_SIGNALS+=("package.json exports present")
fi
if [ "$PKG_MAIN_DIST" = "true" ] || [ "$PKG_EXPORTS_DIST" = "true" ]; then
  LIB_SCORE=$((LIB_SCORE + 25))
  LIB_SIGNALS+=("package.json main/exports point to dist/")
fi
if [ "$HAS_DIST_DIR" = "true" ] || [ "$HAS_LIB_DIR" = "true" ]; then
  LIB_SCORE=$((LIB_SCORE + 15))
  LIB_SIGNALS+=("dist/ or lib/ directory present")
fi
if [ "$HAS_APP_DIR" = "false" ] && [ "$HAS_APP_CONFIG" = "false" ] && [ "$PKG_MAIN_APP" = "false" ]; then
  LIB_SCORE=$((LIB_SCORE + 20))
  LIB_SIGNALS+=("no app entrypoints detected")
fi

APP_SCORE=0
APP_SIGNALS=()
if [ "$HAS_APP_CONFIG" = "true" ]; then
  APP_SCORE=$((APP_SCORE + 30))
  APP_SIGNALS+=("next/vite config detected")
fi
if [ "$HAS_APP_DIR" = "true" ]; then
  APP_SCORE=$((APP_SCORE + 25))
  APP_SIGNALS+=("src/app or src/pages present")
fi
if [ "$HAS_ENV_FILE" = "true" ]; then
  APP_SCORE=$((APP_SCORE + 15))
  APP_SIGNALS+=(".env file present")
fi
if [ "$PKG_MAIN_APP" = "true" ]; then
  APP_SCORE=$((APP_SCORE + 20))
  APP_SIGNALS+=("package.json main points to app")
fi

AI_SCORE=0
AI_SIGNALS=()
if [ "$GIT_IS_SHALLOW" = "false" ] && [ "$GIT_COMMIT_COUNT" -gt 0 ] && [ "$GIT_COMMIT_COUNT" -lt 10 ]; then
  AI_SCORE=$((AI_SCORE + 40))
  AI_SIGNALS+=("git history under 10 commits")
fi
if [ "$PROJECT_AGE_DAYS" -lt 30 ] 2>/dev/null; then
  AI_SCORE=$((AI_SCORE + 30))
  AI_SIGNALS+=("project age under 30 days")
fi
if [ "$TEST_FILE_COUNT" -eq 0 ]; then
  AI_SCORE=$((AI_SCORE + 30))
  AI_SIGNALS+=("no test files detected")
fi

MONO_SCORE=0
MONO_SIGNALS=()
if [ "$HAS_PNPM_WORKSPACE" = "true" ]; then
  MONO_SCORE=$((MONO_SCORE + 40))
  MONO_SIGNALS+=("pnpm-workspace.yaml present")
fi
if [ "$HAS_NX" = "true" ]; then
  MONO_SCORE=$((MONO_SCORE + 30))
  MONO_SIGNALS+=("nx.json present")
fi
if [ "$HAS_TURBO" = "true" ]; then
  MONO_SCORE=$((MONO_SCORE + 30))
  MONO_SIGNALS+=("turbo.json present")
fi
if [ "$HAS_MULTI_PACKAGES" = "true" ]; then
  MONO_SCORE=$((MONO_SCORE + 40))
  MONO_SIGNALS+=("multiple packages/ package.json files")
fi

# ─── Select best type ────────────────────────────────────────────────────────

TYPE="unknown"
CONF=0.0
SIGNALS=()

BEST_SCORE=$LIB_SCORE
TYPE="library"
SIGNALS=("${LIB_SIGNALS[@]}")
MAX_SCORE=90

if [ "$APP_SCORE" -gt "$BEST_SCORE" ]; then
  BEST_SCORE=$APP_SCORE
  TYPE="app"
  SIGNALS=("${APP_SIGNALS[@]}")
  MAX_SCORE=90
fi
if [ "$AI_SCORE" -gt "$BEST_SCORE" ]; then
  BEST_SCORE=$AI_SCORE
  TYPE="ai-generated"
  SIGNALS=("${AI_SIGNALS[@]}")
  MAX_SCORE=100
fi
if [ "$MONO_SCORE" -gt "$BEST_SCORE" ]; then
  BEST_SCORE=$MONO_SCORE
  TYPE="monorepo"
  SIGNALS=("${MONO_SIGNALS[@]}")
  MAX_SCORE=100
fi

if [ "$BEST_SCORE" -eq 0 ]; then
  TYPE="unknown"
  SIGNALS=("no strong signals detected")
  MAX_SCORE=100
fi

CONF=$(python3 - <<PYEOF
score=$BEST_SCORE
max_score=$MAX_SCORE
conf=0.0 if max_score<=0 else round(min(1.0, score/max_score), 2)
print(conf)
PYEOF
)

# ─── Calibration profiles ───────────────────────────────────────────────────

SLOP_PER_KLOC=5
GOD_MODULE_FANIN=10
CI_REQUIRED="false"
COVERAGE_MIN=70
SKIP_GATES=( )
TOLERATED_WARNS=( )

case "$TYPE" in
  library)
    SLOP_PER_KLOC=8
    GOD_MODULE_FANIN=20
    CI_REQUIRED="false"
    COVERAGE_MIN=70
    SKIP_GATES=("ralph_loop")
    TOLERATED_WARNS=("ci_integration")
    ;;
  app)
    SLOP_PER_KLOC=3
    GOD_MODULE_FANIN=10
    CI_REQUIRED="true"
    COVERAGE_MIN=60
    ;;
  ai-generated)
    SLOP_PER_KLOC=1
    GOD_MODULE_FANIN=5
    CI_REQUIRED="true"
    COVERAGE_MIN=80
    ;;
  monorepo)
    SLOP_PER_KLOC=8
    GOD_MODULE_FANIN=25
    CI_REQUIRED="false"
    COVERAGE_MIN=60
    ;;
  unknown)
    SLOP_PER_KLOC=5
    GOD_MODULE_FANIN=10
    CI_REQUIRED="false"
    COVERAGE_MIN=70
    ;;
  *)
    ;;
esac

# ─── Output JSON ─────────────────────────────────────────────────────────────

# Join arrays into pipe-delimited strings for safe passing to Python
SIGNALS_STR=$(printf '%s|' "${SIGNALS[@]+"${SIGNALS[@]}"}" | sed 's/|$//')
SKIP_STR=$(printf '%s|' "${SKIP_GATES[@]+"${SKIP_GATES[@]}"}" | sed 's/|$//')
TOLERATED_STR=$(printf '%s|' "${TOLERATED_WARNS[@]+"${TOLERATED_WARNS[@]}"}" | sed 's/|$//')

python3 - "$TYPE" "$CONF" "$SIGNALS_STR" "$SLOP_PER_KLOC" "$GOD_MODULE_FANIN" "$CI_REQUIRED" "$COVERAGE_MIN" "$SKIP_STR" "$TOLERATED_STR" <<'PYEOF'
import json, sys

_type, conf, signals_str, slop, fanin, ci_req, cov, skip_str, tolerated_str = sys.argv[1:]

signals = [s for s in signals_str.split("|") if s] if signals_str else []
skip = [s for s in skip_str.split("|") if s] if skip_str else []
tolerated = [s for s in tolerated_str.split("|") if s] if tolerated_str else []

print(json.dumps({
    "type": _type,
    "confidence": round(float(conf), 2),
    "signals": signals,
    "calibration": {
        "slop_per_kloc": int(slop),
        "god_module_fanin": int(fanin),
        "ci_required": ci_req == "true",
        "coverage_min": int(cov),
        "skip_gates": skip,
        "tolerated_warns": tolerated
    }
}))
PYEOF
