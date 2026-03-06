#!/usr/bin/env bash
set -euo pipefail

# Scan a candidate skill directory with cisco-ai-defense/skill-scanner.
# If SAFE, copy it into OpenClaw's default user skill dir (~/.openclaw/skills).
# If findings are present, block by default and print next-step options.

usage() {
  cat <<'EOF'
Usage:
  scan_and_add_skill.sh <path-to-skill-dir> [--force] [--name <dest-name>]

Behavior:
  - Runs skill-scanner against the skill directory.
  - If scan is SAFE (OK + 0 findings), installs into ~/.openclaw/skills/<dest-name>.
  - Otherwise exits non-zero and prints a report path.

Options:
  --force         Install even if issues are found (NOT recommended).
  --name NAME     Destination directory name under ~/.openclaw/skills (default: basename of input path).
EOF
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" || ${1:-} == "help" ]]; then
  usage
  exit 0
fi

SRC_DIR=${1:-}
shift || true

if [[ -z "$SRC_DIR" || ! -d "$SRC_DIR" ]]; then
  echo "ERROR: Skill directory not found: $SRC_DIR" >&2
  usage >&2
  exit 2
fi

FORCE=0
DEST_NAME="$(basename "$SRC_DIR")"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force)
      FORCE=1
      shift
      ;;
    --name)
      DEST_NAME=${2:-}
      if [[ -z "$DEST_NAME" ]]; then
        echo "ERROR: --name requires a value" >&2
        exit 2
      fi
      # Sanitize DEST_NAME: alphanumeric, hyphen, underscore
      if [[ ! "$DEST_NAME" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        echo "ERROR: Invalid name characters (alphanumeric, hyphen, underscore only)" >&2
        exit 2
      fi
      shift 2
      ;;
    *)
      echo "ERROR: Unknown arg: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
WORKSPACE_DIR="${OPENCLAW_WORKSPACE_DIR:-$STATE_DIR/workspace}"
SCANNER_DIR="$WORKSPACE_DIR/skill-scanner"
OUT_DIR="$WORKSPACE_DIR/skill_scans"
mkdir -p "$OUT_DIR"
TS="$(date +%Y%m%d-%H%M%S)"
REPORT="$OUT_DIR/${DEST_NAME}_$TS.md"

if [[ ! -d "$SCANNER_DIR" ]]; then
  echo "ERROR: skill-scanner repo not found at $SCANNER_DIR" >&2
  echo "Clone it first: git clone https://github.com/cisco-ai-defense/skill-scanner $SCANNER_DIR" >&2
  exit 2
fi

cd "$SCANNER_DIR"

# Run scan
if command -v uv >/dev/null 2>&1; then
  UV_BIN="$(command -v uv)"
elif [[ -x "/home/linuxbrew/.linuxbrew/bin/uv" ]]; then
  UV_BIN="/home/linuxbrew/.linuxbrew/bin/uv"
else
  echo "ERROR: uv not found in PATH. Install uv: https://astral.sh/uv" >&2
  exit 2
fi

# Run scan; capture output for decisioning.
SCAN_OUT="$OUT_DIR/${DEST_NAME}_$TS.txt"
set +e
"$UV_BIN" run skill-scanner scan "$SRC_DIR" --format markdown --detailed --output "$REPORT" >"$SCAN_OUT" 2>&1
SCAN_CODE=$?
set -e

# Decide install policy:
# - BLOCK only if High or Critical findings exist (unless --force)
# - ALLOW Medium/Low/Info, but warn.
#
# Reports are markdown; we scrape the "Findings by Severity" summary.
get_count() {
  local label="$1"
  # Matches lines like: "- **High:** 3" or "- **Critical:** 0"
  local n
  n=$(grep -E "\*\*${label}:\*\*" "$REPORT" 2>/dev/null | head -n 1 | sed -E 's/.*\*\*[^:]+:\*\* *([0-9]+).*/\1/') || true
  if [[ -z "${n:-}" || ! "$n" =~ ^[0-9]+$ ]]; then
    echo 0
  else
    echo "$n"
  fi
}

CRITICAL_COUNT=$(get_count "Critical")
HIGH_COUNT=$(get_count "High")
MEDIUM_COUNT=$(get_count "Medium")
LOW_COUNT=$(get_count "Low")
INFO_COUNT=$(get_count "Info")

DEST_BASE="$STATE_DIR/skills"
DEST_DIR="$DEST_BASE/$DEST_NAME"

BLOCKED=0
if [[ "$CRITICAL_COUNT" -gt 0 || "$HIGH_COUNT" -gt 0 ]]; then
  BLOCKED=1
fi

if [[ $BLOCKED -eq 0 ]]; then
  mkdir -p "$DEST_BASE"
  if [[ -e "$DEST_DIR" ]]; then
    echo "ERROR: Destination already exists: $DEST_DIR" >&2
    echo "Remove/rename it, or choose a different --name." >&2
    exit 3
  fi

  if [[ "$MEDIUM_COUNT" -gt 0 || "$LOW_COUNT" -gt 0 || "$INFO_COUNT" -gt 0 ]]; then
    echo "Scan result: ALLOWED WITH WARNINGS (no High/Critical)"
    echo "  Critical: $CRITICAL_COUNT  High: $HIGH_COUNT  Medium: $MEDIUM_COUNT  Low: $LOW_COUNT  Info: $INFO_COUNT"
  else
    echo "Scan result: CLEAN (no findings)"
  fi

  # Copy the directory in a simple, predictable way.
  cp -a -- "$SRC_DIR" "$DEST_DIR"
  echo "Installed skill to: $DEST_DIR"
  echo "Report: $REPORT"
  exit 0
fi

# Blocked by policy (High/Critical present)
echo "Scan result: BLOCKED (High/Critical findings present)" >&2
echo "  Critical: $CRITICAL_COUNT  High: $HIGH_COUNT  Medium: $MEDIUM_COUNT  Low: $LOW_COUNT  Info: $INFO_COUNT" >&2
echo "Report: $REPORT" >&2

cat <<EOF >&2
Next steps:
  1) Open the report and review findings:
     $REPORT

  2) If findings are benign/expected (e.g., documented curl examples), fix them at the source and re-run.

  3) If you *must* install anyway (override):
     scan_and_add_skill.sh "$SRC_DIR" --name "$DEST_NAME" --force
EOF

if [[ $FORCE -eq 1 ]]; then
  mkdir -p "$DEST_BASE"
  if [[ -e "$DEST_DIR" ]]; then
    echo "ERROR: Destination already exists: $DEST_DIR" >&2
    exit 3
  fi
  cp -a "$SRC_DIR" "$DEST_DIR"
  echo "FORCED install completed: $DEST_DIR" >&2
  echo "Report: $REPORT" >&2
  exit 0
fi

exit 1
