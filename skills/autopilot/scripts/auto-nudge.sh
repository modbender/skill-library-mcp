#!/bin/bash
# auto-nudge.sh v3 — 自动检测并处理 Codex session 各种状态
# 用法: auto-nudge.sh <window_name> <project_dir> [nudge_message]
#
# 状态处理：
#   working              → 不干预
#   idle                 → 发送 nudge
#   idle_low_context     → /compact → 等待 → 重新检测 → nudge
#   permission           → Enter
#   permission_with_remember → Down + Enter (永久允许)
#   shell                → resume --last，失败则新建 session
#   absent               → 报错

set -uo pipefail
# NOTE: do NOT add set -e; codex-status.sh returns non-zero for idle/permission

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/autopilot-lib.sh"
TMUX="/opt/homebrew/bin/tmux"
CODEX="/opt/homebrew/bin/codex"
SESSION="autopilot"

WINDOW="${1:?用法: auto-nudge.sh <window> <project_dir> [nudge_message]}"
PROJECT_DIR="${2:?缺少项目目录}"
NUDGE="${3:-先 git add -A && git commit 提交改动，然后继续推进下一项任务}"

# ---- 持久化状态目录（不用 /tmp，重启不丢失）----
STATE_DIR="$HOME/.autopilot/state"
mkdir -p "$STATE_DIR"
COMPACT_FLAG="$STATE_DIR/${WINDOW}.compact_sent"
COOLDOWN_DIR="$STATE_DIR/watchdog-cooldown"

# ---- 检查 watchdog 冷却（防止双重 nudge）----
SAFE_WINDOW=$(echo "$WINDOW" | tr -cd 'a-zA-Z0-9_-')
WATCHDOG_COOLDOWN_FILE="${COOLDOWN_DIR}/nudge-${SAFE_WINDOW}"
if [ -f "$WATCHDOG_COOLDOWN_FILE" ]; then
    last_nudge=$(cat "$WATCHDOG_COOLDOWN_FILE" 2>/dev/null || echo 0)
    now=$(date +%s)
    if [ $((now - last_nudge)) -lt 300 ]; then
        echo "⏭ $WINDOW: watchdog 已在 $((now - last_nudge))s 前 nudge，跳过"
        exit 0
    fi
fi

# ---- 辅助函数 ----
get_status() {
    "$SCRIPT_DIR/codex-status.sh" "$WINDOW" 2>&1 || true
}

get_field() {
    echo "$1" | grep -o "\"$2\":\"[^\"]*\"" | head -1 | cut -d'"' -f4 || echo ""
}

get_last_commit() {
    cd "$PROJECT_DIR" && git log --oneline -1 --format="%h %ar: %s" 2>/dev/null || echo "无 commit"
}

# ---- 检测状态 ----
STATUS_JSON=$(get_status)
STATUS=$(get_field "$STATUS_JSON" "status")
CONTEXT=$(get_field "$STATUS_JSON" "context")
LAST_COMMIT=$(get_last_commit)

case "$STATUS" in
  working)
    rm -f "$COMPACT_FLAG"
    echo "✅ $WINDOW: 工作中 ($CONTEXT) | 最近 commit: $LAST_COMMIT"
    exit 0
    ;;

  idle_low_context)
    # 检查是否刚发过 compact
    if [ -f "$COMPACT_FLAG" ]; then
      FLAG_AGE=$(( $(date +%s) - $(stat -f %m "$COMPACT_FLAG" 2>/dev/null || echo 0) ))
      if [ "$FLAG_AGE" -lt 600 ]; then
        # compact 已触发过但 context 仍低 → 直接 nudge（compact 可能已完成但 context 恢复后又用掉了）
        echo "⚠️ $WINDOW: 低 context ($CONTEXT)，compact 已触发 ${FLAG_AGE}s 前，发 nudge..."
        "$SCRIPT_DIR/tmux-send.sh" "$WINDOW" "$NUDGE"
        echo "📤 已发送: $NUDGE"
        echo "📝 最近 commit: $LAST_COMMIT"
        exit 0
      fi
    fi

    # 发送 /compact
    echo "🗜️ $WINDOW: 低 context ($CONTEXT)，触发 /compact..."
    "$SCRIPT_DIR/tmux-send.sh" "$WINDOW" "/compact"
    touch "$COMPACT_FLAG"
    echo "📝 最近 commit: $LAST_COMMIT"

    # 不再 sleep 等待，靠下一轮 cron 自然检测 compact 完成后 nudge
    echo "⏳ compact 已触发，下轮检测时自动 nudge"
    exit 0
    ;;

  idle)
    rm -f "$COMPACT_FLAG"
    # 读取 watchdog 暂停状态（达到最大重试后暂停 30 分钟）
    WD_PAUSE_FILE="${STATE_DIR}/nudge-paused-until-${SAFE_WINDOW}"
    if [ -f "$WD_PAUSE_FILE" ]; then
        WD_PAUSE_UNTIL=$(cat "$WD_PAUSE_FILE" 2>/dev/null || echo 0)
        WD_PAUSE_UNTIL=$(normalize_int "$WD_PAUSE_UNTIL")
        WD_NOW=$(date +%s)
        if [ "$WD_PAUSE_UNTIL" -gt "$WD_NOW" ]; then
            echo "⏭ $WINDOW: watchdog 暂停中（到 $(date -r "$WD_PAUSE_UNTIL" '+%H:%M:%S' 2>/dev/null || echo "$WD_PAUSE_UNTIL")），跳过 nudge"
            exit 0
        fi
        rm -f "$WD_PAUSE_FILE"
    fi
    # 兼容旧版 stalled 标记
    if [ -f "${STATE_DIR}/alert-stalled-${SAFE_WINDOW}" ]; then
        echo "⏭ $WINDOW: watchdog 旧版 stalled 标记存在，跳过 nudge"
        exit 0
    fi
    WD_NUDGE_COUNT_FILE="${COOLDOWN_DIR}/nudge-count-${SAFE_WINDOW}"
    WD_NUDGE_COUNT=$(cat "$WD_NUDGE_COUNT_FILE" 2>/dev/null || echo 0)
    WD_NUDGE_COUNT=$(normalize_int "$WD_NUDGE_COUNT")
    WD_EXP=$((WD_NUDGE_COUNT > 5 ? 5 : WD_NUDGE_COUNT))
    WD_EFFECTIVE_COOLDOWN=$((300 * (1 << WD_EXP)))
    WD_LAST_NUDGE_FILE="${COOLDOWN_DIR}/nudge-${SAFE_WINDOW}"
    if [ -f "$WD_LAST_NUDGE_FILE" ]; then
        WD_LAST_NUDGE=$(cat "$WD_LAST_NUDGE_FILE" 2>/dev/null || echo 0)
        WD_ELAPSED=$(($(date +%s) - $(normalize_int "$WD_LAST_NUDGE")))
        if [ "$WD_ELAPSED" -lt "$WD_EFFECTIVE_COOLDOWN" ]; then
            echo "⏭ $WINDOW: watchdog 退避中 (${WD_ELAPSED}s/${WD_EFFECTIVE_COOLDOWN}s)，跳过 nudge"
            exit 0
        fi
    fi
    echo "⚠️ $WINDOW: 空转 ($CONTEXT)，发送 nudge..."
    "$SCRIPT_DIR/tmux-send.sh" "$WINDOW" "$NUDGE"
    echo "📤 已发送: $NUDGE"
    echo "📝 最近 commit: $LAST_COMMIT"
    exit 0
    ;;

  permission|permission_with_remember)
    echo "🔑 $WINDOW: 卡在权限确认，选永久允许 (p)..."
    # 与 watchdog.sh 共享锁，防止同时操作
    LOCK_DIR="$HOME/.autopilot/locks"
    mkdir -p "$LOCK_DIR"
    SAFE_NAME=$(echo "$WINDOW" | tr -cd 'a-zA-Z0-9_-')
    LOCK_D="${LOCK_DIR}/${SAFE_NAME}.lock.d"
    if mkdir "$LOCK_D" 2>/dev/null; then
      "$TMUX" send-keys -t "${SESSION}:${WINDOW}" "p" Enter
      rm -rf "$LOCK_D"
    else
      echo "⏭ 已被 watchdog 处理"
    fi
    echo "📝 最近 commit: $LAST_COMMIT"
    exit 0
    ;;

  shell)
    echo "🔄 $WINDOW: Codex 已退出，尝试 resume..."
    # 获取锁防止与 watchdog 并发 shell recovery
    LOCK_DIR="$HOME/.autopilot/locks"
    mkdir -p "$LOCK_DIR"
    SAFE_WINDOW=$(echo "$WINDOW" | tr -cd 'a-zA-Z0-9_-')
    LOCK_D="${LOCK_DIR}/${SAFE_WINDOW}.lock.d"
    if mkdir "$LOCK_D" 2>/dev/null; then
      "$TMUX" send-keys -t "${SESSION}:${WINDOW}" "cd $PROJECT_DIR && $CODEX resume --last 2>/dev/null || $CODEX --full-auto" Enter
      rm -rf "$LOCK_D"
    else
      echo "⏭ $WINDOW: shell recovery 已被 watchdog 处理"
    fi
    echo "📝 最近 commit: $LAST_COMMIT"
    exit 0
    ;;

  *)
    echo "❌ $WINDOW: 异常状态 — $STATUS_JSON"
    exit 1
    ;;
esac
