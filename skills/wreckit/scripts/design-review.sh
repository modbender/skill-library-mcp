#!/usr/bin/env bash
# wreckit — dependency graph analysis, coupling metrics, circular dep detection
# Usage: ./design-review.sh [project-path]
# Output: JSON to stdout, human summary to stderr
# Fix: avoid duplicate zero output when counting circular deps
# Exit 0 = results produced, check JSON verdict for pass/fail
# v2: package-boundary awareness for library and monorepo project types

set -euo pipefail
PROJECT="${1:-.}"
PROJECT="$(cd "$PROJECT" && pwd)"
cd "$PROJECT"

echo "=== Design Review ===" >&2
echo "Project: $(pwd)" >&2

# ─── Detect language ───────────────────────────────────────────────────────────
LANGUAGE="unknown"
if [ -f "package.json" ]; then
  LANGUAGE="ts"
elif [ -f "Cargo.toml" ]; then
  LANGUAGE="rust"
elif [ -f "go.mod" ]; then
  LANGUAGE="go"
elif [ -f "requirements.txt" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
  LANGUAGE="python"
elif find . -name '*.sh' -not -path '*/.git/*' -maxdepth 3 2>/dev/null | head -1 | grep -q .; then
  LANGUAGE="shell"
fi
echo "Language: $LANGUAGE" >&2

# ─── Package-boundary awareness (library / monorepo) ──────────────────────────
# Read project type from env (set by run-all-gates.sh or caller)
WRECKIT_PROJECT_TYPE="${WRECKIT_PROJECT_TYPE:-unknown}"
echo "Project type (env): $WRECKIT_PROJECT_TYPE" >&2

# Detect monorepo structure: multiple package.json / Cargo.toml / pyproject.toml at depth 1-2
IS_MONOREPO=0
MONOREPO_PACKAGE_DIRS=""
if [ "$WRECKIT_PROJECT_TYPE" = "monorepo" ]; then
  IS_MONOREPO=1
  echo "Monorepo mode: scoring packages independently" >&2
  # Collect sub-package roots (dirs that have their own package manifest)
  MONOREPO_PACKAGE_DIRS=$(find . -mindepth 2 -maxdepth 3 \
    \( -name 'package.json' -o -name 'Cargo.toml' -o -name 'pyproject.toml' \) \
    -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' \
    2>/dev/null | xargs -I{} dirname {} | sort -u || true)
  PKG_COUNT=$(echo "$MONOREPO_PACKAGE_DIRS" | grep -c '.' 2>/dev/null || echo 0)
  echo "Monorepo sub-packages found: $PKG_COUNT" >&2
else
  # Auto-detect monorepo even if not explicitly tagged
  PKG_MANIFESTS=$(find . -mindepth 2 -maxdepth 3 \
    \( -name 'package.json' -o -name 'Cargo.toml' \) \
    -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null | wc -l | tr -d ' ')
  if [ "${PKG_MANIFESTS:-0}" -ge 3 ]; then
    IS_MONOREPO=1
    echo "Auto-detected monorepo structure ($PKG_MANIFESTS sub-manifests)" >&2
    MONOREPO_PACKAGE_DIRS=$(find . -mindepth 2 -maxdepth 3 \
      \( -name 'package.json' -o -name 'Cargo.toml' \) \
      -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null | xargs -I{} dirname {} | sort -u || true)
  fi
fi

# ─── Project-type calibration hooks (global driver via run-all-gates.sh) ──────
GOD_FAIL_THRESHOLD="${WRECKIT_GOD_MODULE_FANIN:-10}"
if ! [[ "$GOD_FAIL_THRESHOLD" =~ ^[0-9]+$ ]] || [ "$GOD_FAIL_THRESHOLD" -lt 1 ]; then
  GOD_FAIL_THRESHOLD=10
fi

# Library mode: relax god module thresholds
# Libraries legitimately have high-fan-in utility modules (many callers is expected)
# and many "orphan" exports that are part of the public API, not dead code
ORPHAN_IS_EXPECTED=0
LIBRARY_MODE_NOTES=""
if [ "$WRECKIT_PROJECT_TYPE" = "library" ] || [ "$WRECKIT_PROJECT_TYPE" = "npm-package" ] || [ "$WRECKIT_PROJECT_TYPE" = "crate" ]; then
  # Relax god module fan-in threshold: libraries often have intentional high-fan-in utils
  GOD_FAIL_THRESHOLD=$((GOD_FAIL_THRESHOLD + 5))
  echo "Library mode: relaxed god_module threshold to $GOD_FAIL_THRESHOLD (was $((GOD_FAIL_THRESHOLD - 5)))" >&2
  # Orphan files in libraries = public API exports (not dead code)
  ORPHAN_IS_EXPECTED=1
  LIBRARY_MODE_NOTES="Library project: orphan files are expected (public API exports). God module threshold relaxed."
fi

GOD_WARN_THRESHOLD=$((GOD_FAIL_THRESHOLD - 2))
if [ "$GOD_WARN_THRESHOLD" -lt 1 ]; then
  GOD_WARN_THRESHOLD=1
fi

# ─── JS/TS: try madge first ────────────────────────────────────────────────────
MADGE_OUTPUT=""
USED_MADGE=false

if [ "$LANGUAGE" = "ts" ] && command -v npx >/dev/null 2>&1; then
  echo "Attempting madge analysis..." >&2
  if MADGE_OUTPUT=$(npx --yes madge --circular --json . 2>/dev/null); then
    USED_MADGE=true
    echo "madge succeeded" >&2
  else
    echo "madge failed or not available, using manual scan" >&2
  fi
fi

# ─── Build dependency map (manual fallback or non-JS) ─────────────────────────

# Collect source files
SRC_FILES=""
case "$LANGUAGE" in
  ts)
    SRC_FILES=$(find . \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' \) \
      -not -name '*.test.*' -not -name '*.spec.*' -not -name '*.d.ts' \
      -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' \
      -not -path '*/build/*' -not -path '*/coverage/*' 2>/dev/null || true)
    ;;
  python)
    SRC_FILES=$(find . -name '*.py' \
      -not -name 'test_*' -not -name '*_test.py' \
      -not -path '*/.git/*' -not -path '*/venv/*' -not -path '*/__pycache__/*' \
      -not -path '*/site-packages/*' 2>/dev/null || true)
    ;;
  go)
    SRC_FILES=$(find . -name '*.go' \
      -not -name '*_test.go' -not -path '*/.git/*' -not -path '*/vendor/*' 2>/dev/null || true)
    ;;
  rust)
    SRC_FILES=$(find . -name '*.rs' \
      -not -path '*/target/*' -not -path '*/.git/*' 2>/dev/null || true)
    ;;
  shell)
    SRC_FILES=$(find . -name '*.sh' \
      -not -name 'run_tests.sh' -not -path '*/.git/*' 2>/dev/null || true)
    ;;
  *)
    # Generic: try common source extensions
    SRC_FILES=$(find . \( -name '*.ts' -o -name '*.js' -o -name '*.py' -o -name '*.go' \) \
      -not -path '*/.git/*' -not -path '*/node_modules/*' 2>/dev/null || true)
    ;;
esac

TOTAL_FILES=$(echo "$SRC_FILES" | grep -c '.' 2>/dev/null || true)
TOTAL_FILES="${TOTAL_FILES:-0}"
echo "Source files found: $TOTAL_FILES" >&2

# ─── Extract imports and build dep map ────────────────────────────────────────

DEPMAP_FILE=$(mktemp)
FANIN_FILE=$(mktemp)
FANOUT_FILE=$(mktemp)

# For each file, extract what it imports
for file in $SRC_FILES; do
  normalized="${file#./}"
  imports=""
  case "$LANGUAGE" in
    ts)
      # Match: import ... from './x' or require('../y')
      imports=$(grep -oE "(import|require)[^'\"]*['\"](\./|\.\./)([^'\"]+)['\"]" "$file" 2>/dev/null \
        | grep -oE "['\"](\./|\.\./)([^'\"]+)['\"]" \
        | tr -d "'\"" || true)
      ;;
    python)
      # Match: from .module import or import .module
      imports=$(grep -oE "^(from [a-zA-Z0-9_.]+|import [a-zA-Z0-9_.,\ ]+)" "$file" 2>/dev/null \
        | grep -v "^from [a-zA-Z]" | grep -v "^import [a-zA-Z]" \
        | grep -oE "[a-zA-Z0-9_]+" | head -20 || true)
      # Also catch absolute same-package imports
      pkg_imports=$(grep -oE "^from [a-zA-Z0-9_]+" "$file" 2>/dev/null \
        | awk '{print $2}' || true)
      imports="${imports} ${pkg_imports}"
      ;;
    go)
      imports=$(grep -oE '"[^"]+/[^"]+"' "$file" 2>/dev/null \
        | tr -d '"' | grep -v '^\.' || true)
      ;;
  esac

  import_count=$(echo "$imports" | grep -c '[a-zA-Z]' 2>/dev/null || echo 0)
  echo "${normalized}:${import_count}" >> "$FANOUT_FILE"

  # Record each dependency
  for dep in $imports; do
    dep_path="$dep"
    if [ "$LANGUAGE" = "ts" ]; then
      file_dir=$(dirname "$normalized")
      # Resolve relative imports to real files when possible
      candidate="$file_dir/${dep_path}"
      candidate="${candidate#./}"
      resolved=""
      if [ -f "$candidate" ]; then
        resolved="$candidate"
      else
        # try extension mapping
        base="${candidate%.*}"
        for ext in ts tsx js jsx mjs cjs; do
          if [ -f "${base}.${ext}" ]; then resolved="${base}.${ext}"; break; fi
          if [ -f "${candidate}.${ext}" ]; then resolved="${candidate}.${ext}"; break; fi
        done
        if [ -z "$resolved" ] && [ -d "$candidate" ]; then
          for ext in ts tsx js jsx; do
            if [ -f "$candidate/index.${ext}" ]; then resolved="$candidate/index.${ext}"; break; fi
          done
        fi
      fi
      if [ -n "$resolved" ]; then
        dep_path="${resolved}"
      else
        dep_path="${candidate}"
      fi
    fi
    dep_path="${dep_path#./}"
    echo "${dep_path} <- ${normalized}" >> "$DEPMAP_FILE"
  done
done

# Compute fan-in: count how many files import each file
echo "" >> "$DEPMAP_FILE"  # ensure file exists and is non-empty for sort
FANIN_DATA=$(sort "$DEPMAP_FILE" | uniq -c | sort -rn 2>/dev/null || true)

# ─── Detect circular dependencies (DFS via bash) ──────────────────────────────

detect_cycles() {
  # Simple cycle detection: look for any A->B->A pattern in dep map
  # (full DFS would require more complexity; this catches direct + 2-hop cycles)
  local cycles=()

  while IFS= read -r line; do
    # line format: "target <- source"
    target=$(echo "$line" | awk '{print $1}')
    source=$(echo "$line" | awk '{print $3}')
    [ -z "$target" ] || [ -z "$source" ] && continue

    # Check if target also imports source (direct cycle)
    if grep -q "^${source} <- ${target}$" "$DEPMAP_FILE" 2>/dev/null; then
      cycles+=("${source} <-> ${target}")
    fi
  done < "$DEPMAP_FILE"

  # Deduplicate
  printf '%s\n' "${cycles[@]}" | sort -u 2>/dev/null || true
}

CIRCULAR_DEPS=""
if [ "$USED_MADGE" = true ] && [ -n "$MADGE_OUTPUT" ]; then
  # Parse madge JSON output for circular deps
  # madge outputs array of arrays: [["a","b"],["b","a"]]
  CIRCULAR_DEPS=$(echo "$MADGE_OUTPUT" | grep -o '"[^"]*"' | tr -d '"' | paste -d' ' - - 2>/dev/null || true)
else
  CIRCULAR_DEPS=$(detect_cycles 2>/dev/null || true)
fi

CIRCULAR_COUNT=$(echo "$CIRCULAR_DEPS" | grep -c '[a-zA-Z]' 2>/dev/null || true)
CIRCULAR_COUNT=${CIRCULAR_COUNT:-0}

# ─── Identify god modules (high fan-in) ───────────────────────────────────────

GOD_MODULES_JSON="[]"
GOD_COUNT=0

if [ -s "$DEPMAP_FILE" ]; then
  # Count fan-in per target
  GOD_RAW=$(sort "$DEPMAP_FILE" | grep ' <- ' | awk '{print $1}' | sort | uniq -c | sort -rn | head -20 || true)

  god_list=""
  while IFS= read -r entry; do
    [ -z "$entry" ] && continue
    count=$(echo "$entry" | awk '{print $1}')
    fname=$(echo "$entry" | awk '{print $2}')
    if [ "$count" -gt "$GOD_WARN_THRESHOLD" ] 2>/dev/null; then
      god_list="${god_list}{\"file\":\"${fname}\",\"fan_in\":${count}},"
      GOD_COUNT=$((GOD_COUNT + 1))
    fi
  done <<< "$GOD_RAW"

  if [ -n "$god_list" ]; then
    GOD_MODULES_JSON="[${god_list%,}]"
  fi
fi

# ─── Orphan files (not imported by anything) ──────────────────────────────────

ORPHAN_FILES_JSON="[]"
ORPHAN_COUNT=0

if [ -s "$DEPMAP_FILE" ] && [ "$TOTAL_FILES" -gt 0 ]; then
  orphan_list=""
  for file in $SRC_FILES; do
    normalized="${file#./}"
    basename_no_ext="${normalized%.*}"
    # Check if any line in depmap references this file
    if ! grep -q "$normalized\|$basename_no_ext" "$DEPMAP_FILE" 2>/dev/null; then
      orphan_list="${orphan_list}\"${normalized}\","
      ORPHAN_COUNT=$((ORPHAN_COUNT + 1))
    fi
  done
  if [ -n "$orphan_list" ]; then
    ORPHAN_FILES_JSON="[${orphan_list%,}]"
  fi
fi

# ─── Compute averages ──────────────────────────────────────────────────────────

AVG_FANIN="0"
AVG_FANOUT="0"

if [ "$TOTAL_FILES" -gt 0 ] && command -v bc >/dev/null 2>&1; then
  TOTAL_IMPORTS=$(grep -c ' <- ' "$DEPMAP_FILE" 2>/dev/null || true)
  TOTAL_IMPORTS="${TOTAL_IMPORTS:-0}"
  AVG_FANIN=$(echo "scale=1; ${TOTAL_IMPORTS} / ${TOTAL_FILES}" | bc 2>/dev/null || echo "0")
  AVG_FANIN="${AVG_FANIN:-0}"
  if [[ "$AVG_FANIN" == .* ]]; then
    AVG_FANIN="0${AVG_FANIN}"
  fi
  AVG_FANOUT="$AVG_FANIN"
  if [[ "$AVG_FANOUT" == .* ]]; then
    AVG_FANOUT="0${AVG_FANOUT}"
  fi
fi

# ─── Determine verdict ────────────────────────────────────────────────────────

VERDICT="PASS"
SUMMARY=""
CONFIDENCE="0.0"

# ─── Verdict: circular deps are always a hard fail ───────────────────────────
if [ "$CIRCULAR_COUNT" -gt 0 ]; then
  VERDICT="FAIL"
  SUMMARY="FAIL: ${CIRCULAR_COUNT} circular dependency/dependencies detected."
  CONFIDENCE="0.6"
elif [ "$GOD_COUNT" -gt 0 ]; then
  # Check if any god module has fan-in above calibrated fail threshold
  # Library mode: threshold already relaxed (+5) earlier in the script
  HIGH_GOD=$(echo "$GOD_MODULES_JSON" | grep -o '"fan_in":[0-9]*' | awk -F: -v fail_t="$GOD_FAIL_THRESHOLD" '{if($2>fail_t) print $2}' | head -1 || true)
  if [ -n "$HIGH_GOD" ]; then
    if [ "$ORPHAN_IS_EXPECTED" -eq 1 ]; then
      # Library: high fan-in is a design choice, warn but don't fail
      VERDICT="WARN"
      SUMMARY="WARN: ${GOD_COUNT} god module(s) with fan-in > ${GOD_FAIL_THRESHOLD}. Library project — high fan-in expected for shared utilities."
    else
      VERDICT="FAIL"
      SUMMARY="FAIL: God module(s) with fan-in > ${GOD_FAIL_THRESHOLD} detected."
    fi
    CONFIDENCE="0.6"
  else
    VERDICT="WARN"
    SUMMARY="WARN: No circular deps but ${GOD_COUNT} god module(s) with fan-in > ${GOD_WARN_THRESHOLD}."
    CONFIDENCE="0.6"
  fi
else
  SUMMARY="PASS: No circular deps, no god modules. Clean architecture."
fi

# ─── Orphan file scoring (library/monorepo aware) ────────────────────────────
ORPHAN_NOTES=""
if [ "$ORPHAN_COUNT" -gt 0 ]; then
  if [ "$ORPHAN_IS_EXPECTED" -eq 1 ]; then
    # Library: orphan files = public API exports — not dead code
    ORPHAN_NOTES="Library project: $ORPHAN_COUNT orphan file(s) are likely public API exports, not dead code."
    echo "Library mode: orphan files treated as public API exports (not penalized)" >&2
  elif [ "$IS_MONOREPO" -eq 1 ]; then
    # Monorepo: orphans may be cross-package entry points; apply per-package scoring
    ORPHAN_NOTES="Monorepo: $ORPHAN_COUNT apparent orphan(s) — may be inter-package entry points. Per-package scoring recommended."
    echo "Monorepo mode: orphan files may be inter-package entry points (not penalized at repo level)" >&2
  else
    ORPHAN_PCT=0
    if [ "$TOTAL_FILES" -gt 0 ] && command -v bc >/dev/null 2>&1; then
      ORPHAN_PCT=$(echo "scale=0; $ORPHAN_COUNT * 100 / $TOTAL_FILES" | bc 2>/dev/null || echo 0)
    fi
    # Only flag orphans if there are many of them (>3 files AND >15% of total)
    # Small projects with 1-3 entry points should not be penalized
    if [ "${ORPHAN_PCT:-0}" -gt 15 ] && [ "$ORPHAN_COUNT" -gt 3 ] && [ "$VERDICT" = "PASS" ]; then
      VERDICT="WARN"
      SUMMARY="WARN: ${ORPHAN_COUNT} orphan files (${ORPHAN_PCT}% of total) may indicate dead code."
      CONFIDENCE="0.5"
    fi
  fi
fi

# ─── Monorepo: append per-package note ────────────────────────────────────────
MONOREPO_NOTE=""
if [ "$IS_MONOREPO" -eq 1 ]; then
  PKG_LIST_SHORT=$(echo "$MONOREPO_PACKAGE_DIRS" | head -5 | tr '\n' ',' | sed 's/,$//' || true)
  MONOREPO_NOTE="Monorepo detected. Packages scored at repo level; for per-package scoring run design-review.sh on each sub-package."
  echo "Monorepo packages (sample): $PKG_LIST_SHORT" >&2
fi

# Append library/monorepo notes to summary
if [ -n "$LIBRARY_MODE_NOTES" ] && [ "$VERDICT" != "FAIL" ]; then
  SUMMARY="${SUMMARY} [${LIBRARY_MODE_NOTES}]"
fi
if [ -n "$ORPHAN_NOTES" ]; then
  SUMMARY="${SUMMARY} [${ORPHAN_NOTES}]"
fi

# ─── Output ───────────────────────────────────────────────────────────────────

echo "" >&2
echo "Circular deps: $CIRCULAR_COUNT" >&2
echo "God modules (fan-in > ${GOD_WARN_THRESHOLD}): $GOD_COUNT" >&2
echo "Orphan files: $ORPHAN_COUNT" >&2
if [ -n "$MONOREPO_NOTE" ]; then echo "Monorepo: $MONOREPO_NOTE" >&2; fi
echo "Verdict: $VERDICT" >&2
echo "Summary: $SUMMARY" >&2

# Build circular deps JSON array
CIRCULAR_JSON="[]"
if [ "$CIRCULAR_COUNT" -gt 0 ] && [ -n "$CIRCULAR_DEPS" ]; then
  circ_list=""
  while IFS= read -r c; do
    [ -z "$c" ] && continue
    circ_list="${circ_list}\"${c}\","
  done <<< "$CIRCULAR_DEPS"
  if [ -n "$circ_list" ]; then
    CIRCULAR_JSON="[${circ_list%,}]"
  fi
fi

# Escape summary for JSON
SUMMARY_ESCAPED=$(printf '%s' "$SUMMARY" | sed "s/\"/\\\\'/g" | tr -d '\n')
MONOREPO_NOTE_ESCAPED=$(printf '%s' "${MONOREPO_NOTE:-}" | sed "s/\"/\\\\'/g" | tr -d '\n')
ORPHAN_NOTE_ESCAPED=$(printf '%s' "${ORPHAN_NOTES:-}" | sed "s/\"/\\\\'/g" | tr -d '\n')

cat <<EOF
{
  "project": "$(pwd)",
  "language": "$LANGUAGE",
  "project_type": "$WRECKIT_PROJECT_TYPE",
  "is_monorepo": $IS_MONOREPO,
  "library_mode": $ORPHAN_IS_EXPECTED,
  "total_files": $TOTAL_FILES,
  "circular_deps": $CIRCULAR_JSON,
  "god_modules": $GOD_MODULES_JSON,
  "god_warn_threshold": $GOD_WARN_THRESHOLD,
  "god_fail_threshold": $GOD_FAIL_THRESHOLD,
  "orphan_files": $ORPHAN_FILES_JSON,
  "orphan_count": $ORPHAN_COUNT,
  "avg_fan_in": $AVG_FANIN,
  "avg_fan_out": $AVG_FANOUT,
  "status": "$VERDICT",
  "verdict": "$VERDICT",
  "summary": "$SUMMARY_ESCAPED",
  "confidence": $CONFIDENCE,
  "notes": {
    "monorepo": "$MONOREPO_NOTE_ESCAPED",
    "orphan": "$ORPHAN_NOTE_ESCAPED"
  }
}
EOF

rm -f "$DEPMAP_FILE" "$FANIN_FILE" "$FANOUT_FILE"
