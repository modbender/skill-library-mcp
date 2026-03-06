#!/usr/bin/env bash
set -euo pipefail

# Capture idf.py help text into references/ so it can be searched quickly.
# Uses ESPIDF_ROOT to activate the environment if available.

OUT_REL="references/idf-py-help.txt"

ESPIDF_ROOT="${ESPIDF_ROOT:-}"

cd "$(dirname "$0")/.."  # skill root

if [[ -n "${ESPIDF_ROOT:-}" && -f "$ESPIDF_ROOT/export.sh" ]]; then
  bash -lc "set -euo pipefail; source \"$ESPIDF_ROOT/export.sh\" >/dev/null; idf.py --help" > "$OUT_REL"
elif command -v idf.py >/dev/null 2>&1; then
  idf.py --help > "$OUT_REL"
else
  echo "ERROR: idf.py not found. Either activate ESP-IDF in this shell, or set ESPIDF_ROOT to an ESP-IDF checkout (with export.sh)." >&2
  exit 1
fi

echo "Wrote: $(pwd)/$OUT_REL"
