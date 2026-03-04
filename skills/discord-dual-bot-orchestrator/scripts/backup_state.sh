#!/usr/bin/env bash
set -euo pipefail

TS=$(date +%Y%m%d-%H%M%S)
OUT_DIR="${OUT_DIR:-$PWD/backups/dual-bot-$TS}"
mkdir -p "$OUT_DIR"

cp -f "$HOME/.openclaw/openclaw.json" "$OUT_DIR/openclaw.main.json"
cp -f "$HOME/.openclaw-bot-b/openclaw.json" "$OUT_DIR/openclaw.bot-b.json"

echo "$OUT_DIR"
