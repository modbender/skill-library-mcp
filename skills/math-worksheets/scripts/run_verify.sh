#!/usr/bin/env bash
# run_verify.sh — Run worksheet answer verification
# Usage: run_verify.sh <verify_TOPIC_DATE.json>
#
# Passes the JSON verification file to the bundled verify.py script.
# No code is generated or executed from user input — only structured
# data (the JSON file) is evaluated by the fixed verify.py.
#
# Requires: python3 with sympy installed
#   pip3 install sympy
#
# Exit codes:
#   0 — all automated checks passed — safe to compile
#   1 — one or more checks FAILED — fix answer key before compiling
#   2 — manual review needed — no automated failures, safe to compile

set -uo pipefail

JSON_FILE="${1:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERIFY_PY="${SCRIPT_DIR}/verify.py"

if [[ -z "$JSON_FILE" ]]; then
  echo "Usage: run_verify.sh <verify_TOPIC_DATE.json>" >&2
  exit 1
fi

if [[ ! -f "$JSON_FILE" ]]; then
  echo "Error: verification file not found: $JSON_FILE" >&2
  exit 1
fi

# ── Find Python 3 ─────────────────────────────────────────────────────────────
PYTHON=""
for candidate in "/opt/homebrew/bin/python3" "/usr/local/bin/python3" "$(command -v python3 2>/dev/null || true)"; do
  if [[ -x "$candidate" ]]; then
    PYTHON="$candidate"
    break
  fi
done

if [[ -z "$PYTHON" ]]; then
  echo "Error: python3 not found. Install Python 3 to use verification." >&2
  exit 1
fi

# ── Check sympy is available ──────────────────────────────────────────────────
if ! "$PYTHON" -c "import sympy" 2>/dev/null; then
  echo "Error: sympy is not installed." >&2
  echo "Run: pip3 install sympy" >&2
  exit 1
fi

# ── Run the fixed verification script ────────────────────────────────────────
"$PYTHON" "$VERIFY_PY" "$JSON_FILE"
EXIT_CODE=$?

exit $EXIT_CODE
