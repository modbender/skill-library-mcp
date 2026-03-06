#!/usr/bin/env bash
set -euo pipefail

# setup-openclaw-local-memory.sh
# Configure OpenClaw memory search for local embeddings (privacy-first).
#
# Usage:
#   ./setup-openclaw-local-memory.sh
#
# Optional env vars:
#   OPENCLAW_MEMORY_MODEL_URL (override default download URL)
#   OPENCLAW_MODEL_DIR (default: ~/.openclaw/models)

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing required command: $1" >&2; exit 1; }
}

need_cmd curl
need_cmd openclaw

MODEL_DIR="${OPENCLAW_MODEL_DIR:-$HOME/.openclaw/models}"
MODEL_FILE="$MODEL_DIR/embeddinggemma-300M-Q8_0.gguf"
MODEL_URL_DEFAULT="https://huggingface.co/ggml-org/embeddinggemma-300M-GGUF/resolve/main/embeddinggemma-300M-Q8_0.gguf"
MODEL_URL="${OPENCLAW_MEMORY_MODEL_URL:-$MODEL_URL_DEFAULT}"

mkdir -p "$MODEL_DIR"

if [[ ! -f "$MODEL_FILE" ]]; then
  echo "Downloading embedding model -> $MODEL_FILE" >&2
  tmp="$MODEL_FILE.tmp"
  curl -fL --retry 3 --retry-delay 1 -o "$tmp" "$MODEL_URL"
  mv "$tmp" "$MODEL_FILE"
fi

# Set config keys via openclaw CLI (creates config if needed)
openclaw config set agents.defaults.compaction.memoryFlush.enabled true --json
openclaw config set agents.defaults.memorySearch.enabled true --json
openclaw config set agents.defaults.memorySearch.provider "local"
openclaw config set agents.defaults.memorySearch.fallback "none"
openclaw config set agents.defaults.memorySearch.sources '["memory","sessions"]' --json
openclaw config set agents.defaults.memorySearch.experimental.sessionMemory true --json
openclaw config set agents.defaults.memorySearch.local.modelPath "$MODEL_FILE"

cat <<MSG

OK: local memory search configured.

Next steps:
1) Restart OpenClaw gateway.
2) Run: openclaw memory index --agent main
3) Verify: openclaw memory status --json

MSG
