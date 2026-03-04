#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/skill-zip-audit.sh /path/to/skill.zip
#
# Output:
#   report folder under /tmp/skill-audit/<zip-name>-<timestamp>/

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/skill.zip"
  exit 1
fi

ZIP_PATH="$1"
if [[ ! -f "$ZIP_PATH" ]]; then
  echo "ZIP not found: $ZIP_PATH"
  exit 1
fi

if ! command -v unzip >/dev/null 2>&1; then
  echo "Missing dependency: unzip"
  exit 1
fi

if ! command -v rg >/dev/null 2>&1; then
  echo "Missing dependency: rg (ripgrep). Install: brew install ripgrep"
  exit 1
fi

TS="$(date +%Y%m%d-%H%M%S)"
NAME="$(basename "$ZIP_PATH" .zip)"
BASE="/tmp/skill-audit/${NAME}-${TS}"
SRC_DIR="$BASE/src"
mkdir -p "$SRC_DIR"

unzip -qq "$ZIP_PATH" -d "$SRC_DIR"

REPORT="$BASE/report.md"
TREE="$BASE/tree.txt"
HASHES="$BASE/hashes.txt"
SUSPICIOUS="$BASE/suspicious.txt"
PERMS="$BASE/permissions.txt"

{
  echo "# Skill ZIP Audit Report"
  echo
  echo "- ZIP: $ZIP_PATH"
  echo "- Audit time: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "- Extracted to: $SRC_DIR"
  echo
} > "$REPORT"

# File inventory
( cd "$SRC_DIR" && find . -type f | sort ) > "$TREE"

# Hashes
( cd "$SRC_DIR" && find . -type f -print0 | xargs -0 shasum -a 256 ) > "$HASHES" || true

# Try to extract declared requirements from SKILL.md
if find "$SRC_DIR" -name SKILL.md | grep -q .; then
  {
    echo "## Declared requirements from SKILL.md"
    echo
    find "$SRC_DIR" -name SKILL.md -print0 | while IFS= read -r -d '' f; do
      echo "### $(realpath "$f")"
      rg -n "requires|bins|install|curl|wget|bash|python|node|npm|pnpm|brew" "$f" || true
      echo
    done
  } > "$PERMS"
else
  echo "No SKILL.md found" > "$PERMS"
fi

# Suspicious pattern scan
PATTERN='(curl\s+http|wget\s+http|nc\s+-e|bash\s+-c|python\s+-c|eval\(|child_process|os\.system|subprocess|/tmp/|~/.ssh|id_rsa|api[_-]?key|token|Authorization:|openssl enc|base64 -d|chmod \+x|launchctl|crontab|rm -rf|scp\s+|rsync\s+|http://|https://)'

rg -n -S -g '!*.png' -g '!*.jpg' -g '!*.jpeg' -g '!*.gif' -g '!*.webp' "$PATTERN" "$SRC_DIR" > "$SUSPICIOUS" || true

# Summary scoring
SCORE=0
FLAGS=()

# Heuristics
if rg -q "rm -rf|launchctl|crontab|nc -e" "$SUSPICIOUS"; then
  SCORE=$((SCORE+4)); FLAGS+=("high-risk commands")
fi
if rg -q "~/.ssh|id_rsa|api[_-]?key|token|Authorization:" "$SUSPICIOUS"; then
  SCORE=$((SCORE+3)); FLAGS+=("credential/access patterns")
fi
if rg -q "curl\s+http|wget\s+http|http://|https://" "$SUSPICIOUS"; then
  SCORE=$((SCORE+2)); FLAGS+=("network/download activity")
fi
if rg -q "bash -c|python -c|eval\(|child_process|subprocess" "$SUSPICIOUS"; then
  SCORE=$((SCORE+2)); FLAGS+=("dynamic execution")
fi

RISK="SAFE"
if (( SCORE >= 6 )); then
  RISK="REMOVE"
elif (( SCORE >= 3 )); then
  RISK="CAUTION"
fi

{
  echo "## Summary"
  echo
  echo "- Score: $SCORE"
  echo "- Risk: **$RISK**"
  if (( ${#FLAGS[@]} > 0 )); then
    echo "- Flags: ${FLAGS[*]}"
  else
    echo "- Flags: none triggered"
  fi
  echo
  echo "## Artifacts"
  echo "- File tree: $TREE"
  echo "- Hashes: $HASHES"
  echo "- Declared requirements: $PERMS"
  echo "- Suspicious matches: $SUSPICIOUS"
  echo
  echo "## Recommended action"
  case "$RISK" in
    SAFE) echo "Promote to staging with minimal keys, then production." ;;
    CAUTION) echo "Review suspicious lines manually before any real credentials." ;;
    REMOVE) echo "Do not install in production. Isolate and inspect line-by-line." ;;
  esac
} >> "$REPORT"

echo "Audit complete"
echo "Report: $REPORT"
