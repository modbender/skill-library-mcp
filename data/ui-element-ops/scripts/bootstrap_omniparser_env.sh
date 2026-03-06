#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   bootstrap_omniparser_env.sh [workdir] [venv_path] [omniparser_dir]
#
# Example:
#   skills/ui-element-ops/scripts/bootstrap_omniparser_env.sh "$PWD"

WORKDIR="${1:-$PWD}"
VENV_PATH="${2:-$WORKDIR/.venv}"
OMNIPARSER_DIR="${3:-/tmp/OmniParser}"

if ! command -v python3.12 >/dev/null 2>&1; then
  echo "python3.12 is required but not found." >&2
  exit 1
fi

mkdir -p "$WORKDIR"
python3.12 -m venv "$VENV_PATH"

"$VENV_PATH/bin/python" -m pip install --upgrade pip
"$VENV_PATH/bin/pip" install \
  pillow \
  requests \
  openai \
  numpy==1.26.4 \
  matplotlib \
  torch \
  torchvision \
  easyocr \
  supervision==0.18.0 \
  ultralytics==8.3.70 \
  "transformers==4.49.0" \
  accelerate \
  timm \
  einops==0.8.0 \
  opencv-python \
  pyautogui \
  screeninfo \
  huggingface_hub

if [ ! -d "$OMNIPARSER_DIR/.git" ]; then
  git clone --depth 1 https://github.com/microsoft/OmniParser "$OMNIPARSER_DIR"
fi

mkdir -p "$OMNIPARSER_DIR/weights" /tmp/hf /tmp/xdg

HF_HOME=/tmp/hf XDG_CACHE_HOME=/tmp/xdg \
  "$VENV_PATH/bin/hf" download microsoft/OmniParser-v2.0 \
  icon_detect/train_args.yaml \
  icon_detect/model.pt \
  icon_detect/model.yaml \
  icon_caption/config.json \
  icon_caption/generation_config.json \
  icon_caption/model.safetensors \
  --local-dir "$OMNIPARSER_DIR/weights"

if [ -d "$OMNIPARSER_DIR/weights/icon_caption" ] && [ ! -d "$OMNIPARSER_DIR/weights/icon_caption_florence" ]; then
  mv "$OMNIPARSER_DIR/weights/icon_caption" "$OMNIPARSER_DIR/weights/icon_caption_florence"
fi

echo "Environment ready:"
echo "  venv: $VENV_PATH"
echo "  OmniParser: $OMNIPARSER_DIR"
echo "  weights: $OMNIPARSER_DIR/weights"
