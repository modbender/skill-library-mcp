#!/usr/bin/env bash
set -euo pipefail

# 一条命令：生成发布包 -> CDP 预填到待发布页（不点发布）

VIDEO=""
TOPIC=""
KEYWORDS=""
OUT="${HOME}/.openclaw/workspace/output/social-push"
HOST="127.0.0.1"
PORT="9222"
ACCOUNT=""

usage() {
  cat <<EOF
Usage:
  bash $0 --video /abs/path.mp4 --topic "主题" [--keywords "a,b,c"] [--out /path]
          [--host 127.0.0.1] [--port 9222] [--account xxx]
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --video) VIDEO="$2"; shift 2 ;;
    --topic) TOPIC="$2"; shift 2 ;;
    --keywords) KEYWORDS="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --host) HOST="$2"; shift 2 ;;
    --port) PORT="$2"; shift 2 ;;
    --account) ACCOUNT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 2 ;;
  esac
done

if [[ -z "$VIDEO" || -z "$TOPIC" ]]; then
  usage
  exit 2
fi

BASE="$HOME/.openclaw/workspace/skills/social-push-semi/scripts"

echo "[one-shot] Step1: 生成发布包"
CMD1=(bash "$BASE/run.sh" --video "$VIDEO" --topic "$TOPIC" --out "$OUT")
if [[ -n "$KEYWORDS" ]]; then
  CMD1+=(--keywords "$KEYWORDS")
fi
"${CMD1[@]}"

PACK="$OUT/publish-pack.json"
if [[ ! -f "$PACK" ]]; then
  echo "[one-shot] publish-pack not found: $PACK" >&2
  exit 3
fi

echo "[one-shot] Step2: CDP 预填到待发布页"
CMD2=(bash "$BASE/fill_preview_cdp.sh" --pack "$PACK" --host "$HOST" --port "$PORT")
if [[ -n "$ACCOUNT" ]]; then
  CMD2+=(--account "$ACCOUNT")
fi
"${CMD2[@]}"

echo "[one-shot] 完成：已停在待发布页（未点击发布）"
