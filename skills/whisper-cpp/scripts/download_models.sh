#!/usr/bin/env bash
set -euo pipefail

# Downloads ggml whisper models to ~/.cache/whisper
# Uses Hugging Face direct downloads (no whisper.cpp repo scripts required).

MODELS_DIR="$HOME/.cache/whisper"
mkdir -p "$MODELS_DIR"

BASE_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main"

download() {
  local name="$1"
  local out="$MODELS_DIR/ggml-$name.bin"
  local url="$BASE_URL/ggml-$name.bin"

  if [ -f "$out" ]; then
    echo "[SKIP] $out exists"
    return 0
  fi

  echo "[DL] $url -> $out"
  curl -L --fail --retry 3 --retry-delay 2 -o "$out" "$url"
}

# Choose which models to download.
# - Default: base + small
# - Pass args: `bash scripts/download_models.sh base small medium`

MODELS=( )

if [ "$#" -gt 0 ]; then
  MODELS=("$@")
else
  MODELS=(base small)
fi

for m in "${MODELS[@]}"; do
  [ -n "$m" ] || continue
  download "$m"
done

echo "[OK] Models are in: $MODELS_DIR"
