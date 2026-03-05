#!/usr/bin/env bash
set -euo pipefail

# Auto-scan OpenClaw user skills when ~/.openclaw/skills changes.
# Triggered by a systemd --user path unit.

STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
WORKSPACE_DIR="${OPENCLAW_WORKSPACE_DIR:-$STATE_DIR/workspace}"
SCANNER_DIR="$WORKSPACE_DIR/skill-scanner"
USER_SKILLS="$STATE_DIR/skills"
OUT_DIR="$WORKSPACE_DIR/skill_scans/auto"
mkdir -p "$OUT_DIR"
TS="$(date +%Y%m%d-%H%M%S)"
REPORT="$OUT_DIR/openclaw_user_skills_$TS.md"

if [[ ! -d "$USER_SKILLS" ]]; then
  echo "No user skills dir at $USER_SKILLS; nothing to scan."
  exit 0
fi

if [[ ! -d "$SCANNER_DIR" ]]; then
  echo "ERROR: skill-scanner repo not found at $SCANNER_DIR" >&2
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

"$UV_BIN" run skill-scanner scan-all "$USER_SKILLS" --format markdown --detailed --output "$REPORT"

# Print a short summary to the journal
get_count() {
  local label="$1"
  local n
  n=$(grep -E "\*\*${label}:\*\*" "$REPORT" 2>/dev/null | head -n 1 | sed -E 's/.*\*\*[^:]+:\*\* *([0-9]+).*/\1/') || true
  if [[ -z "${n:-}" || ! "$n" =~ ^[0-9]+$ ]]; then
    echo 0
  else
    echo "$n"
  fi
}

CRITICAL=$(get_count "Critical")
HIGH=$(get_count "High")
MEDIUM=$(get_count "Medium")

echo "Skill scan complete: report=$REPORT critical=$CRITICAL high=$HIGH medium=$MEDIUM"

QUARANTINE_BASE="$STATE_DIR/skills-quarantine"

# If High/Critical exist, quarantine failing skills (Max Severity HIGH/CRITICAL).
if [[ "$CRITICAL" -gt 0 || "$HIGH" -gt 0 ]]; then
  mkdir -p "$QUARANTINE_BASE"
  echo "BLOCKING FINDINGS DETECTED (High/Critical). Quarantining affected skills. Review: $REPORT" >&2

  # Parse the markdown to find failing skills and their directories.
  # Looks for sections like:
  #   ### [FAIL] <skill>
  #   - **Max Severity:** HIGH
  #   ...
  #   - **Directory:** /path
  mapfile -t FAIL_DIRS < <(
    awk '
      /^### \[FAIL\] / { fail=1; sev=""; dir="" }
      fail && /\*\*Max Severity:\*\*/ { if (match($0, /\*\*Max Severity:\*\* ([A-Z]+)/, m)) sev=m[1] }
      fail && /\*\*Directory:\*\*/ { if (match($0, /\*\*Directory:\*\* (.*)$/, m)) dir=m[1] }
      fail && sev ~ /^(HIGH|CRITICAL)$/ && dir != "" { print dir; fail=0; sev=""; dir="" }
      # End section guard
      /^---$/ { if (fail && dir != "") { fail=0; sev=""; dir="" } }
    ' "$REPORT" | sort -u
  )

  if [[ ${#FAIL_DIRS[@]} -eq 0 ]]; then
    echo "High/Critical present, but could not parse failing directories from report. Leaving skills in place." >&2
    exit 1
  fi

  for d in "${FAIL_DIRS[@]}"; do
    if [[ -d "$d" && "$d" == "$USER_SKILLS"/* ]]; then
      name="$(basename "$d")"
      qdest="$QUARANTINE_BASE/${name}-$TS"
      echo "Quarantining: $d -> $qdest" >&2
      mv -- "$d" "$qdest"
    fi
  done

  # Non-zero so it shows up in status, but the bad skills are now out of the load path.
  exit 1
fi
