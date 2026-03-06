#!/bin/bash
# setup.sh — 一键部署角色扮演系统
#
# 用法:
#   ./scripts/setup.sh                     # 默认创建 role-play agent + workspace
#   ./scripts/setup.sh /path/to/workspace  # 指定目标 workspace 路径
#
# 支持从两种位置运行：
#   1. git clone 后直接运行
#   2. clawhub install 后从 skills/daily-roleplay-game/ 运行
#
# 脚本会：
#   - 创建独立的 role-play agent（不影响现有 agent）
#   - 部署引擎文件到新 workspace 根目录
#   - 复制数据文件和脚本
#   - 引导角色设定（交互模式）或留空（非交互模式）

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

AGENT_ID="role-play"
AGENT_NAME="角色扮演"
DEFAULT_WORKSPACE="$HOME/.openclaw/workspace-role-play"
TARGET="${1:-$DEFAULT_WORKSPACE}"

log() {
    echo "[setup] $1"
}

# ─── 0. 前置检查 ───

log "=== 角色扮演系统部署 ==="
log "源目录: $SKILL_ROOT"
log "目标 workspace: $TARGET"
echo ""

# 检测 openclaw CLI 是否可用
HAS_OPENCLAW=false
if command -v openclaw &>/dev/null; then
    HAS_OPENCLAW=true
fi

# ─── 1. 创建 role-play agent（不影响现有 agent） ───

log "1. 检查 agent 配置..."

if [[ "$HAS_OPENCLAW" == true ]]; then
    if openclaw agents list 2>/dev/null | grep -q "$AGENT_ID"; then
        log "  [跳过] agent '$AGENT_ID' 已存在"
    else
        log "  创建独立 agent: $AGENT_ID..."
        openclaw agents add "$AGENT_ID" --workspace "$TARGET" 2>/dev/null || {
            log "  [警告] 自动创建 agent 失败，请手动执行: openclaw agents add $AGENT_ID"
        }
    fi
else
    log "  [提示] 未检测到 openclaw CLI，跳过自动创建 agent"
    log "  部署完成后请手动执行:"
    log "    openclaw agents add $AGENT_ID"
    log "  或将 agent 配置写入 ~/.openclaw/openclaw.json（见 openclaw.example.json5）"
fi

# ─── 2. 创建目标目录结构 ───

log "2. 创建目录结构..."
mkdir -p "$TARGET"/{archive,memory,backups,scripts}
mkdir -p "$TARGET"/data/{professions,kinks,themes,personality,weights,templates/comfyui}

# ─── 3. 收集角色信息（供后续步骤注入） ───

CHAR_NAME=""
CHAR_TZ=""
EXTRA_LINES=""
if [[ ! -f "$TARGET/IDENTITY.md" ]]; then
    if [[ -t 0 ]]; then
        log "3. 角色身份设定..."
        echo ""
        echo "=== 角色身份设定 ==="
        echo "（直接回车跳过，后续可手动编辑 IDENTITY.md）"
        echo ""

        read -rp "角色名称 (Name): " CHAR_NAME
        read -rp "时区 (Timezone): " CHAR_TZ

        echo ""
        echo "如有其他需要设定的信息，请逐行输入，输入空行结束："
        while true; do
            read -rp "> " line
            [[ -z "$line" ]] && break
            EXTRA_LINES="${EXTRA_LINES}${line}\n"
        done
        echo ""
    else
        log "3. [非交互模式] 跳过角色设定，部署后请手动编辑 IDENTITY.md"
    fi
else
    log "3. [跳过] IDENTITY.md 已存在，读取角色名..."
    CHAR_NAME=$(sed -n 's/^- \*\*Name:\*\* \(.*\)/\1/p' "$TARGET/IDENTITY.md" | head -1)
fi

# ─── 4. 复制引擎文件（不覆盖已存在的） ───

log "4. 复制引擎文件到 workspace 根目录..."
for f in ENGINE.md AGENTS.md HEARTBEAT.md SOUL.md; do
    if [[ -f "$TARGET/$f" ]]; then
        log "  [跳过] $f 已存在"
    else
        cp "$SKILL_ROOT/engine/$f" "$TARGET/$f"
        if [[ "$f" == "SOUL.md" && -n "$CHAR_NAME" ]]; then
            if [[ "$OSTYPE" == darwin* ]]; then
                sed -i '' "s/{{CHAR_NAME}}/$CHAR_NAME/g" "$TARGET/$f"
            else
                sed -i "s/{{CHAR_NAME}}/$CHAR_NAME/g" "$TARGET/$f"
            fi
        fi
        log "  [新建] $f"
    fi
done

# ─── 5. 复制数据文件（始终覆盖，保持最新） ───

log "5. 复制数据文件..."
cp "$SKILL_ROOT/data/index.yaml" "$TARGET/data/"
cp "$SKILL_ROOT/data/age_profiles.yaml" "$TARGET/data/"
cp "$SKILL_ROOT/data/holidays_china.json" "$TARGET/data/"
cp "$SKILL_ROOT/data/achievements.yaml" "$TARGET/data/"
cp "$SKILL_ROOT/data/professions/"*.yaml "$TARGET/data/professions/"
cp "$SKILL_ROOT/data/kinks/"*.yaml "$TARGET/data/kinks/"
cp "$SKILL_ROOT/data/themes/"*.yaml "$TARGET/data/themes/"
cp "$SKILL_ROOT/data/personality/"*.yaml "$TARGET/data/personality/"
cp "$SKILL_ROOT/data/weights/"*.yaml "$TARGET/data/weights/"
cp "$SKILL_ROOT/data/templates/morning_greeting.md" "$TARGET/data/templates/"
if ls "$SKILL_ROOT/data/templates/comfyui/"* &>/dev/null; then
    cp -r "$SKILL_ROOT/data/templates/comfyui/"* "$TARGET/data/templates/comfyui/"
fi
log "  数据文件已更新"

# ─── 6. 复制脚本 ───

log "6. 复制脚本..."
cp "$SKILL_ROOT/scripts/wrapup.sh" "$TARGET/scripts/"
cp "$SKILL_ROOT/scripts/validate-generation.sh" "$TARGET/scripts/"
chmod +x "$TARGET/scripts/"*.sh
log "  脚本已就位"

# ─── 7. 从模板初始化运行时文件（不覆盖已存在的） ───

log "7. 初始化运行时文件..."

init_from_template() {
    local template="$1"
    local dest="$2"
    local name=$(basename "$dest")
    if [[ -f "$dest" ]]; then
        log "  [跳过] $name 已存在"
    else
        cp "$template" "$dest"
        log "  [新建] $name"
    fi
}

init_from_template "$SKILL_ROOT/templates/history_tracker.json" "$TARGET/data/history_tracker.json"
init_from_template "$SKILL_ROOT/templates/achievement_tracker.json" "$TARGET/data/achievement_tracker.json"
init_from_template "$SKILL_ROOT/templates/kink_game_enabled.json" "$TARGET/kink_game_enabled.json"
init_from_template "$SKILL_ROOT/templates/USER.md" "$TARGET/USER.md"
init_from_template "$SKILL_ROOT/templates/MEMORY.md" "$TARGET/MEMORY.md"
init_from_template "$SKILL_ROOT/templates/TOOLS.md" "$TARGET/TOOLS.md"

if [[ -f "$TARGET/IDENTITY.md" ]]; then
    log "  [跳过] IDENTITY.md 已存在"
else
    {
        echo "# IDENTITY.md - 角色数据"
        echo ""
        echo "- **Name:** ${CHAR_NAME}"
        echo "- **Timezone:** ${CHAR_TZ}"
        echo ""
        echo "> 本文件为静态角色数据，按需引用，不在启动时全量加载。"
        echo "> 可根据个人偏好自定义身体数据、行为设定等。"

        if [[ -n "$EXTRA_LINES" ]]; then
            echo ""
            echo "---"
            echo ""
            echo -e "$EXTRA_LINES"
        fi
    } > "$TARGET/IDENTITY.md"
    log "  [新建] IDENTITY.md"
fi

# ─── 8. 复制文档（可选） ───

log "8. 复制文档..."
mkdir -p "$TARGET/docs"
cp "$SKILL_ROOT/docs/"*.md "$TARGET/docs/" 2>/dev/null || true
if [[ ! -f "$TARGET/docs/README.md" ]]; then
    cat > "$TARGET/docs/README.md" << 'DOCSREADME'
# docs/ — 设计文档（agent 不读）

本目录存放设计文档与配置说明，**agent 启动与运行时不会读取**，仅供人类维护与参考。

- **运行时规则唯一权威**：workspace 根目录的 `ENGINE.md`
- **收尾说明**：`WRAPUP.md`（Cron/脚本执行时参考）
- **Cron 配置**：`CRON_CONFIG.md`
- **设计文档**：`daily-roleplay-game.md`（若为旧版，请以 ENGINE.md 与根目录实际结构为准）
DOCSREADME
fi

# ─── 9. 创建 archive/history.md（若不存在） ───

if [[ ! -f "$TARGET/archive/history.md" ]]; then
    cat > "$TARGET/archive/history.md" << 'HISTORY'
# 历史存档索引

| 日期 | 职业 | 猜对 | 最终状态 | 备注 |
|------|------|------|---------|------|
HISTORY
    log "  [新建] archive/history.md"
fi

# ─── 完成 ───

echo ""
log "=== 部署完成 ==="
echo ""
echo "workspace: $TARGET"
echo ""
echo "后续步骤："
echo "  1. 编辑 $TARGET/IDENTITY.md 设定角色名称和时区"
echo "  2. 编辑 $TARGET/USER.md 填写你的个人信息"
echo "  3. 编辑 $TARGET/MEMORY.md 配置消息频道（discord/telegram/feishu 等）"
echo "  4. 编辑 $TARGET/TOOLS.md 配置生图工具（ComfyUI/SD WebUI/Midjourney 等，不需要可填「无」）"

if [[ "$HAS_OPENCLAW" == true ]]; then
    echo ""
    echo "配置定时任务："
    echo "  openclaw cron add --agent $AGENT_ID --name '每日角色生成' \\"
    echo "    --cron '0 6 * * *' --tz 'Asia/Shanghai' --session isolated \\"
    echo "    --delivery none --model opus \\"
    echo "    --message '读取 ENGINE.md 并按步骤执行每日初始化（Step 0-8）'"
    echo ""
    echo "  openclaw cron add --agent $AGENT_ID --name '每日收尾归档' \\"
    echo "    --cron '30 23 * * *' --tz 'Asia/Shanghai' --session isolated \\"
    echo "    --delivery none \\"
    echo "    --message '读取 docs/WRAPUP.md 按步骤执行收尾归档，完成后回复 WRAPUP_OK'"
else
    echo ""
    echo "OpenClaw 配置："
    echo "  1. 安装 OpenClaw 并执行: openclaw agents add $AGENT_ID"
    echo "  2. 将 openclaw.example.json5 中的配置合并到 ~/.openclaw/openclaw.json"
    echo "  3. 添加定时任务（参考 docs/CRON_CONFIG.md）"
fi

echo ""
echo "配置参考: docs/OPENCLAW_SETUP.md | openclaw.example.json5"
echo ""
echo "首次运行："
echo "  对 $AGENT_ID agent 发消息，或手动触发 cron 任务"
echo "  agent 读取 ENGINE.md 并执行每日初始化流程（Step 0-8）"
