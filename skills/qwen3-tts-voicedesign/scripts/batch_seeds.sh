#!/usr/bin/env bash
# Generate TTS samples with multiple seeds for voice comparison
# Usage: bash batch_seeds.sh [text] [seeds...] [output_dir]
# Example: bash batch_seeds.sh "你好呀！今天天气真好。" 100 200 300 400 500 /tmp/seeds

set -euo pipefail

HOST="${TTS_HOST:-localhost}"
PORT="${TTS_PORT:-8881}"
TEXT="${1:-你好呀！今天天气真好，想出去走走呢。}"
shift 2>/dev/null || true

# Collect seeds (default: 10 random-ish seeds)
SEEDS=()
OUT_DIR=""
while [[ $# -gt 0 ]]; do
  if [[ $# -eq 1 && "$1" == /* ]]; then
    OUT_DIR="$1"
    shift
  else
    SEEDS+=("$1")
    shift
  fi
done

[[ ${#SEEDS[@]} -eq 0 ]] && SEEDS=(42 123 201 456 789 1024 2048 4096 8888 20260201)
[[ -z "$OUT_DIR" ]] && OUT_DIR="/tmp/tts_seeds_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$OUT_DIR"
echo "Generating ${#SEEDS[@]} samples → $OUT_DIR"
echo "Text: $TEXT"
echo "---"

for seed in "${SEEDS[@]}"; do
  out="$OUT_DIR/seed_${seed}.mp3"
  printf "Seed %-10s → " "$seed"
  t0=$(date +%s)
  http_code=$(curl -s -o "$out" -w "%{http_code}" \
    -X POST "http://${HOST}:${PORT}/tts" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"${TEXT}\", \"seed\": ${seed}, \"format\": \"mp3\"}")
  t1=$(date +%s)
  size=$(stat -f%z "$out" 2>/dev/null || stat -c%s "$out" 2>/dev/null || echo "?")
  echo "${http_code} ${size}B $((t1-t0))s → $out"
done

echo "---"
echo "Done! Listen and compare: open $OUT_DIR"
