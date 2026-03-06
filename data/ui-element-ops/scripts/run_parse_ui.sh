#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   run_parse_ui.sh <image> [output_json] [overlay_png]
#
# Env (optional):
#   VENV_PATH: Python venv path (default: $PWD/.venv)
#   OMNIPARSER_DIR: OmniParser repo path (default: /tmp/OmniParser)
#   TYPE_RULES: type rule json path

if [ $# -lt 1 ]; then
  echo "Usage: $0 <image> [output_json] [overlay_png]" >&2
  exit 1
fi

IMAGE="$1"
IMAGE_BASE="${IMAGE%.*}"
OUTPUT_JSON="${2:-${IMAGE_BASE}.elements.json}"
OVERLAY_PNG="${3:-${IMAGE_BASE}.overlay.png}"

VENV_PATH="${VENV_PATH:-$PWD/.venv}"
OMNIPARSER_DIR="${OMNIPARSER_DIR:-/tmp/OmniParser}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TYPE_RULES="${TYPE_RULES:-$SCRIPT_DIR/../references/type_rules.example.json}"

if [ ! -f "$IMAGE" ]; then
  echo "Input image not found: $IMAGE" >&2
  exit 1
fi

if [ ! -x "$VENV_PATH/bin/python" ]; then
  echo "Python runtime not found at $VENV_PATH/bin/python" >&2
  echo "Run bootstrap first: skills/ui-element-ops/scripts/bootstrap_omniparser_env.sh \"\$PWD\"" >&2
  exit 1
fi

mkdir -p /tmp/mpl /tmp/xdg /tmp/easyocr /tmp/hf /tmp/ultra

MPLCONFIGDIR=/tmp/mpl \
XDG_CACHE_HOME=/tmp/xdg \
EASYOCR_MODULE_PATH=/tmp/easyocr \
HF_HOME=/tmp/hf \
YOLO_CONFIG_DIR=/tmp/ultra \
"$VENV_PATH/bin/python" "$SCRIPT_DIR/parse_ui.py" \
  --image "$IMAGE" \
  --output "$OUTPUT_JSON" \
  --overlay "$OVERLAY_PNG" \
  --omniparser-dir "$OMNIPARSER_DIR" \
  --type-rules "$TYPE_RULES"
