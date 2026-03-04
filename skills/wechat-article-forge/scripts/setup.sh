#!/usr/bin/env bash
# wechat-article-writer 一键安装配置脚本
# 用法: bash scripts/setup.sh [workspace_dir]
#
# 自动完成:
# 1. 创建数据目录 (~/.wechat-article-writer/)
# 2. 安装依赖技能 (article-illustrator, wechat-publisher)
# 3. 安装 bun runtime + baoyu renderer deps
# 4. 追加 AGENTS.md 规则到工作区
# 5. 追加 HEARTBEAT.md pipeline 检查
# 6. 验证环境变量
# 7. 生成默认 config.json

set -euo pipefail

WORKSPACE="${1:-$(pwd)}"
DATA_DIR="$HOME/.wechat-article-writer"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
fail() { echo -e "${RED}❌ $1${NC}"; }

echo "═══════════════════════════════════════════"
echo "  wechat-article-writer 安装配置"
echo "═══════════════════════════════════════════"
echo ""
echo "工作区: $WORKSPACE"
echo "数据目录: $DATA_DIR"
echo ""

# ─── 1. 数据目录 ────────────────────────────────────────────
echo "── 步骤 1/7: 创建数据目录"
mkdir -p "$DATA_DIR/drafts"
ok "数据目录已创建: $DATA_DIR"

# ─── 2. 依赖技能 ────────────────────────────────────────────
echo ""
echo "── 步骤 2/7: 检查依赖技能"

check_skill() {
  local name="$1"
  local search_dirs=(
    "$HOME/.openclaw/skills/$name"
    "$WORKSPACE/skills/$name"
  )
  for d in "${search_dirs[@]}"; do
    if [ -d "$d" ]; then
      ok "$name 已安装: $d"
      return 0
    fi
  done
  return 1
}

if ! check_skill "article-illustrator"; then
  warn "article-illustrator 未安装 — 尝试安装..."
  if command -v openclaw &>/dev/null; then
    openclaw skill install article-illustrator 2>/dev/null && ok "article-illustrator 已安装" || fail "安装失败，请手动安装: openclaw skill install article-illustrator"
  else
    fail "请手动安装: openclaw skill install article-illustrator"
  fi
fi

if ! check_skill "wechat-publisher"; then
  warn "wechat-publisher 未安装 — 尝试安装..."
  if command -v openclaw &>/dev/null; then
    openclaw skill install wechat-publisher 2>/dev/null && ok "wechat-publisher 已安装" || fail "安装失败，请手动安装: openclaw skill install wechat-publisher"
  else
    fail "请手动安装: openclaw skill install wechat-publisher"
  fi
fi

# ─── 3. bun runtime + baoyu renderer ──────────────────────
echo ""
echo "── 步骤 3/7: 检查 bun runtime"
if [[ -f "$HOME/.bun/bin/bun" ]]; then
  ok "bun already installed: $($HOME/.bun/bin/bun --version)"
else
  warn "bun not found — install from https://bun.sh then re-run setup"
fi
export PATH="$HOME/.bun/bin:$PATH"

RENDERER_MD="$SKILL_DIR/scripts/renderer/md"
if [[ -f "$RENDERER_MD/package.json" ]]; then
  (cd "$RENDERER_MD" && "$HOME/.bun/bin/bun" install --frozen-lockfile --silent 2>/dev/null) && ok "renderer deps installed" || warn "run: cd $RENDERER_MD && bun install"
fi
fi

# ─── 4. AGENTS.md 规则 ──────────────────────────────────────
echo ""
echo "── 步骤 4/7: 配置 AGENTS.md"
AGENTS_FILE="$WORKSPACE/AGENTS.md"
MARKER="## 微信公众号文章写作规则"

if [ -f "$AGENTS_FILE" ] && grep -q "$MARKER" "$AGENTS_FILE" 2>/dev/null; then
  ok "AGENTS.md 已包含写作规则"
else
  cat >> "$AGENTS_FILE" << 'AGENTS_BLOCK'

## 微信公众号文章写作规则

### 自动执行（不问人）
- 选题调研（web_search）
- 撰写大纲
- 生成初稿（spawn Writer 子代理，用 Opus 模型）
- 评审打分（spawn Reviewer 子代理，用 Sonnet 模型）
- 自动修改循环（最多2轮）
- baoyu renderer 排版 (scripts/renderer/, default 主题)
- 启动预览服务器

### 必须等人确认
- **文字预览**（步骤9）：发预览链接后等用户反馈，不要自行继续
- **插图生成**（步骤10）：用户明确说"可以了"/"好了"/"生成图片"才执行
- **发布**（步骤13）：始终保存为草稿，用户手动发布

### 用户反馈处理
- 用户可能通过**语音消息**给反馈 — 直接根据转录文字行动
- 用户说"改一下XX" → 直接改，不要确认
- 用户说"不好"/"重写" → 回到步骤4重写
- 用户说"可以了" → 进入下一步
- 用户沉默超过30分钟 → 发一条提醒，不要反复催

### 成本控制
- 插图是最贵的步骤（~$0.50/篇），放在最后
- 不要在被拒绝的草稿上生成插图
- article-illustrator 原样使用，不修改提示词或添加风格前缀

### Pipeline 状态
- 每个主要步骤完成后更新 pipeline-state.json
- 会话重启后先读 pipeline-state.json 恢复进度
- 不要依赖会话记忆来跟踪进度
AGENTS_BLOCK
  ok "AGENTS.md 已追加写作规则"
fi

# ─── 5. HEARTBEAT.md ────────────────────────────────────────
echo ""
echo "── 步骤 5/7: 配置 HEARTBEAT.md"
HEARTBEAT_FILE="$WORKSPACE/HEARTBEAT.md"
HB_MARKER="## 文章 Pipeline 检查"

if [ -f "$HEARTBEAT_FILE" ] && grep -q "$HB_MARKER" "$HEARTBEAT_FILE" 2>/dev/null; then
  ok "HEARTBEAT.md 已包含 pipeline 检查"
else
  cat >> "$HEARTBEAT_FILE" << 'HB_BLOCK'

## 文章 Pipeline 检查
每次心跳检查 ~/.wechat-article-writer/drafts/*/pipeline-state.json
- 如果有 phase 不是 "done" 且不是等待人工的阶段 → 继续执行
- 如果 phase 是 "previewing_text" 或 "illustrating" → 不要自动继续，等用户
- 如果 pipeline 超过 24 小时没更新 → 提醒用户
HB_BLOCK
  ok "HEARTBEAT.md 已追加 pipeline 检查"
fi

# ─── 6. 环境变量 ────────────────────────────────────────────
echo ""
echo "── 步骤 6/7: 检查环境变量"
if [ -n "${OPENROUTER_API_KEY:-}" ]; then
  ok "OPENROUTER_API_KEY 已设置"
else
  warn "OPENROUTER_API_KEY 未设置 — 插图生成将不可用"
  warn "设置方法: export OPENROUTER_API_KEY=sk-or-..."
fi

# ─── 7. 默认配置 ────────────────────────────────────────────
echo ""
echo "── 步骤 7/7: 生成默认配置"
CONFIG_FILE="$DATA_DIR/config.json"
if [ -f "$CONFIG_FILE" ]; then
  ok "config.json 已存在: $CONFIG_FILE"
else
  cat > "$CONFIG_FILE" << 'CONFIG'
{
  "default_theme": "condensed",
  "default_article_type": "观点",
  "auto_publish_types": [],
  "cover_style": "from_content",
  "chrome_debug_port": 18800,
  "chrome_display": ":1",
  "chrome_user_data_dir": "/tmp/openclaw-browser2",
  "wechat_author": "",
  "word_count_targets": {
    "资讯": [800, 1500],
    "周报": [1000, 2000],
    "教程": [1500, 3000],
    "观点": [1200, 2500],
    "科普": [1500, 3000]
  }
}
CONFIG
  ok "config.json 已创建: $CONFIG_FILE"
  warn "请编辑 config.json 设置 wechat_author（公众号名称）"
fi

# ─── 完成 ───────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════"
echo -e "  ${GREEN}安装配置完成！${NC}"
echo "═══════════════════════════════════════════"
echo ""
echo "下一步:"
echo "  1. 确保 Chrome 已启动并登录 mp.weixin.qq.com"
echo "  2. 编辑 $CONFIG_FILE 设置 wechat_author"
echo "  3. 试试: forge write about AI编程工具"
echo ""
