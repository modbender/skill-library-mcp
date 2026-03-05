#!/usr/bin/env bash
set -euo pipefail

# XHS CDP 半自动发布桥接：
# - 读取 publish-pack.json 或命令行参数
# - 调用 XiaohongshuSkills/scripts/publish_pipeline.py --preview
# - 只填充，不点发布

WORKSPACE="$HOME/.openclaw/workspace"
XHS_DIR="$WORKSPACE/skills/social-push-semi/vendor/xhs"
PY="$XHS_DIR/.venv/bin/python"

PACK=""
VIDEO=""
TITLE=""
CONTENT=""
HOST="127.0.0.1"
PORT="9222"
ACCOUNT=""
REUSE_TAB=1

usage() {
  cat <<EOF
Usage:
  # 方式1：直接吃 publish-pack（推荐）
  bash $0 --pack /abs/path/publish-pack.json [--host 127.0.0.1] [--port 9222]

  # 方式2：手动传参
  bash $0 --video /abs/path.mp4 --title "标题" --content "正文\n\n#话题1 #话题2"

Optional:
  --account <name>      指定账号（可选）
  --no-reuse-tab        不复用已有 tab
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pack) PACK="$2"; shift 2 ;;
    --video) VIDEO="$2"; shift 2 ;;
    --title) TITLE="$2"; shift 2 ;;
    --content) CONTENT="$2"; shift 2 ;;
    --host) HOST="$2"; shift 2 ;;
    --port) PORT="$2"; shift 2 ;;
    --account) ACCOUNT="$2"; shift 2 ;;
    --no-reuse-tab) REUSE_TAB=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 2 ;;
  esac
done

if [[ ! -x "$PY" ]]; then
  echo "Missing python venv: $PY" >&2
  echo "请先执行：bash $WORKSPACE/skills/social-push-semi/scripts/setup_vendor_xhs.sh" >&2
  exit 3
fi

if [[ -n "$PACK" ]]; then
  if [[ ! -f "$PACK" ]]; then
    echo "pack not found: $PACK" >&2
    exit 4
  fi

  # 用 python 解析 JSON，避免 jq 依赖
  mapfile -t parsed < <("$PY" - <<'PY' "$PACK"
import json,sys
p=sys.argv[1]
obj=json.load(open(p,'r',encoding='utf-8'))
video=obj.get('video','')
topic=obj.get('topic','')
keywords=obj.get('keywords') or []
draft_path=obj.get('draft','')
content=''
if draft_path:
    try:
        txt=open(draft_path,'r',encoding='utf-8').read().strip()
        # 默认取版本A
        marker='## 版本A｜稳妥'
        if marker in txt:
            part=txt.split(marker,1)[1]
            # 截到下一个版本
            for sep in ['## 版本B｜干货','## 版本B', '## 版本C｜故事','## 版本C']:
                if sep in part:
                    part=part.split(sep,1)[0]
                    break
            content=part.strip()
        else:
            content=txt
    except Exception:
        content=''
tags=' '.join([f"#{str(k).strip().lstrip('#')}" for k in keywords if str(k).strip()])
if tags:
    content = (content + '\n\n' + tags).strip()

title = (topic or '自动生成内容').strip()[:20]
print(video)
print(title)
print(content)
PY
)

  VIDEO="${parsed[0]:-}"
  TITLE="${parsed[1]:-}"
  CONTENT="${parsed[2]:-}"
fi

if [[ -z "$VIDEO" || -z "$TITLE" || -z "$CONTENT" ]]; then
  echo "missing required fields: video/title/content" >&2
  usage
  exit 5
fi

if [[ "$VIDEO" != $WORKSPACE/* ]]; then
  echo "Refuse video outside workspace: $VIDEO" >&2
  exit 6
fi

if [[ ! -f "$VIDEO" ]]; then
  echo "video not found: $VIDEO" >&2
  exit 7
fi

REUSE_ARGS=()
if [[ "$REUSE_TAB" -eq 1 ]]; then
  REUSE_ARGS+=(--reuse-existing-tab)
fi

ACCOUNT_ARGS=()
if [[ -n "$ACCOUNT" ]]; then
  ACCOUNT_ARGS+=(--account "$ACCOUNT")
fi

echo "[social-push-semi] CDP preview fill start..."
"$PY" "$XHS_DIR/scripts/publish_pipeline.py" \
  --host "$HOST" --port "$PORT" \
  --preview \
  "${REUSE_ARGS[@]}" \
  "${ACCOUNT_ARGS[@]}" \
  --title "$TITLE" \
  --content "$CONTENT" \
  --video "$VIDEO"

echo "[social-push-semi] Done. 已停在待发布页（未点击发布）。"
