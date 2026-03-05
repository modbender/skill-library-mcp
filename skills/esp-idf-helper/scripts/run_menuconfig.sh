#!/usr/bin/env bash
set -euo pipefail

# Run idf.py menuconfig in a dedicated terminal window (TTY required)
# Usage:
#   bash run_menuconfig.sh --project <PROJECT_DIR> --idf <IDF_DIR>

PROJECT_DIR=""
IDF_DIR=""

usage() {
  cat <<'EOF'
Usage:
  run_menuconfig.sh --project <PROJECT_DIR> --idf <IDF_DIR>

Example:
  bash run_menuconfig.sh \
    --project /path/to/your/project \
    --idf /path/to/esp-idf
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) PROJECT_DIR="$2"; shift 2;;
    --idf) IDF_DIR="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 2;;
  esac
done

[[ -n "$PROJECT_DIR" && -n "$IDF_DIR" ]] || { usage; exit 2; }

cd "$PROJECT_DIR"
source "$IDF_DIR/export.sh"
exec idf.py menuconfig
