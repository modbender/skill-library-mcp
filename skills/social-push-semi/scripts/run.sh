#!/usr/bin/env bash
set -euo pipefail

VIDEO=""
TOPIC=""
KEYWORDS=""
OUT="${HOME}/.openclaw/workspace/output/social-push"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --video) VIDEO="$2"; shift 2 ;;
    --topic) TOPIC="$2"; shift 2 ;;
    --keywords) KEYWORDS="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -z "$VIDEO" || -z "$TOPIC" ]]; then
  echo "Usage: run.sh --video /abs/path.mp4 --topic \"主题\" [--keywords \"a,b,c\"] [--out /path]"
  exit 1
fi

if [[ ! -f "$VIDEO" ]]; then
  echo "Video not found: $VIDEO"
  exit 1
fi

mkdir -p "$OUT"

# 关键词处理
IFS=',' read -r K1 K2 K3 <<< "${KEYWORDS:-自动化,AI效率,内容创作}"
K1="${K1:-自动化}"; K2="${K2:-AI效率}"; K3="${K3:-内容创作}"

# 抽封面（取第2秒）
COVER="$OUT/cover.jpg"
if command -v ffmpeg >/dev/null 2>&1; then
  ffmpeg -y -ss 00:00:02 -i "$VIDEO" -frames:v 1 -q:v 2 "$COVER" >/dev/null 2>&1 || true
fi

if [[ ! -f "$COVER" ]]; then
  # ffmpeg 不可用时兜底占位
  touch "$COVER"
fi

# 文案草稿
DRAFT="$OUT/draft.md"
cat > "$DRAFT" <<EOF
# 文案草稿（自动生成）

## 版本A｜稳妥
我把「${TOPIC}」做成了半自动流程，效率明显提升。

这次我主要优化了：
1. 流程拆分（生成→填充→检查）
2. 素材标准化（标题/正文/话题/封面）
3. 失败兜底（异常即人工接管）

#${K1} #${K2} #${K3}

## 版本B｜干货
如果你也在做 ${TOPIC}，建议先上半自动：
- 自动生成文案
- 自动准备封面
- 自动填入发布表单
- 人工确认后发布

这样稳定、可控、可复用。

#${K1} #${K2} #${K3}

## 版本C｜故事
以前发布 ${TOPIC}，总要手机来回点。
这次我把流程改成“先自动准备、最后人工确认”，
既省时间又不容易翻车。

#${K1} #${K2} #${K3}
EOF

# 发布包
PACK="$OUT/publish-pack.json"
cat > "$PACK" <<EOF
{
  "platform": "xhs",
  "mode": "semi-auto",
  "video": "${VIDEO}",
  "cover": "${COVER}",
  "topic": "${TOPIC}",
  "keywords": ["${K1}", "${K2}", "${K3}"],
  "draft": "${DRAFT}",
  "publish": {
    "autoFill": true,
    "autoUpload": true,
    "autoClickPublish": false,
    "reason": "半自动稳态：最后发布人工确认，降低风控与误发"
  }
}
EOF

# 人工检查单
cat > "$OUT/checklist.md" <<EOF
# 发布前检查（半自动）
- [ ] 标题不违规、无敏感词
- [ ] 正文无错别字，语气符合账号定位
- [ ] 话题 3~5 个，不堆砌
- [ ] 封面可读、清晰、无版权风险
- [ ] 视频时长/画质符合平台要求
- [ ] **确认后再手动点击发布**
EOF

echo "Done. Output: $OUT"
ls -lah "$OUT"
