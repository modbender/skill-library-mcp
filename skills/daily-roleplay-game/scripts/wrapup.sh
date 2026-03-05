#!/bin/bash
# wrapup.sh — 每日角色扮演收尾脚本
# 用法: ./wrapup.sh [workspace_dir]

set -e

WORKSPACE="${1:-$HOME/.openclaw/workspace-role-play}"
ACTIVE_FILE="$WORKSPACE/roleplay-active.md"
ARCHIVE_DIR="$WORKSPACE/archive"
MEDIA_DIR="$HOME/.openclaw/media"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Step 1: 检查 roleplay-active.md 是否存在
if [[ ! -f "$ACTIVE_FILE" ]]; then
    log "无需收尾：roleplay-active.md 不存在"
    echo "WRAPUP_OK"
    exit 0
fi

# Step 2: 从 roleplay-active.md 读取信息
DATE_LINE=$(grep "^# 今日设定" "$ACTIVE_FILE" | head -1)
DATE_STR=$(echo "$DATE_LINE" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}')

# 优先从 YAML front-matter 提取，否则从 "## 职业" 段落提取
if head -5 "$ACTIVE_FILE" | grep -q "^profession:"; then
    PROFESSION=$(grep "^profession:" "$ACTIVE_FILE" | head -1 | sed 's/^profession:[[:space:]]*//')
else
    PROFESSION=$(grep "^## 职业" "$ACTIVE_FILE" -A 1 | tail -1 | sed 's/\*\*//g; s/（[^）]*）//g' | tr -d ' ')
fi

# 获取 media_prefix
MEDIA_PREFIX=$(grep "media_prefix:" "$ACTIVE_FILE" | tail -1 | sed 's/media_prefix:[[:space:]]*//' | tr -d ' ')

if [[ -z "$DATE_STR" ]] || [[ -z "$PROFESSION" ]]; then
    log "错误：无法从 roleplay-active.md 读取日期或职业"
    exit 1
fi

log "日期: $DATE_STR, 职业: $PROFESSION, 前缀: $MEDIA_PREFIX"

# Step 3: 创建归档目录
TODAY_ARCHIVE="$ARCHIVE_DIR/${DATE_STR}-${PROFESSION}"
TODAY_IMAGES="$TODAY_ARCHIVE/images"

mkdir -p "$TODAY_IMAGES"
log "创建归档目录: $TODAY_ARCHIVE"

# Step 4: 复制 roleplay-active.md 到归档（保留原文件）
cp "$ACTIVE_FILE" "$TODAY_ARCHIVE/"
log "归档 roleplay-active.md（复制）"

# Step 5: 移动 guess-log.md (如果存在且不在归档目录内)
GUESS_LOG="$WORKSPACE/guess-log.md"
if [[ -f "$GUESS_LOG" ]]; then
    mv "$GUESS_LOG" "$TODAY_ARCHIVE/"
    log "归档 guess-log.md"
fi

# Step 6: 移动相关图片
if [[ -n "$MEDIA_PREFIX" ]]; then
    IMAGE_COUNT=$(find "$MEDIA_DIR" -name "${MEDIA_PREFIX}*.png" -type f 2>/dev/null | wc -l)
    if [[ "$IMAGE_COUNT" -gt 0 ]]; then
        mv "$MEDIA_DIR"/${MEDIA_PREFIX}*.png "$TODAY_IMAGES/" 2>/dev/null || true
        log "归档 ${IMAGE_COUNT} 张图片"
    else
        log "未找到匹配图片: ${MEDIA_PREFIX}*.png"
    fi
fi

# Step 7: 更新 history.md
HISTORY_FILE="$ARCHIVE_DIR/history.md"
GUESS_LOG_FILE="$TODAY_ARCHIVE/guess-log.md"

# 读取猜测进度（支持 4~6 个性癖，不再硬编码 /5）
GUESSED="0/0"
if [[ -f "$GUESS_LOG_FILE" ]]; then
    GUESSED=$(grep -oE '[0-9]+/[0-9]+' "$GUESS_LOG_FILE" | head -1 || echo "0/0")
fi
GUESSED_RIGHT="${GUESSED%%/*}"
GUESSED_TOTAL="${GUESSED##*/}"

# 确定状态
if [[ "$GUESSED_TOTAL" -gt 0 ]] && [[ "$GUESSED_RIGHT" -eq "$GUESSED_TOTAL" ]]; then
    STATUS="全裸通关"
elif [[ "$GUESSED_RIGHT" -gt 0 ]]; then
    STATUS="脱至第${GUESSED_RIGHT}件"
else
    STATUS="未脱衣"
fi

# 计算图片数量
IMAGE_COUNT=$(find "$TODAY_IMAGES" -name "*.png" -type f 2>/dev/null | wc -l)

# 追加到 history.md
echo "| $DATE_STR | $PROFESSION | $GUESSED | $STATUS | ${IMAGE_COUNT}张图片 |" >> "$HISTORY_FILE"
log "更新 history.md: $DATE_STR | $PROFESSION | $GUESSED"

# Step 8: 更新成就追踪
ACHIEVEMENT_FILE="$WORKSPACE/data/achievement_tracker.json"
if [[ -f "$ACHIEVEMENT_FILE" ]] && command -v python3 &>/dev/null; then
    CLEARED="false"
    if [[ "$GUESSED_TOTAL" -gt 0 ]] && [[ "$GUESSED_RIGHT" -eq "$GUESSED_TOTAL" ]]; then
        CLEARED="true"
    fi
    python3 -c "
import json, sys
with open('$ACHIEVEMENT_FILE', 'r') as f:
    data = json.load(f)
date_str = '$DATE_STR'
profession = '$PROFESSION'
result = '$GUESSED'
cleared = $CLEARED
existing = [d for d in data.get('daily_log', []) if d.get('date') != date_str]
existing.append({'date': date_str, 'profession': profession, 'result': result, 'cleared': cleared})
existing.sort(key=lambda x: x['date'])
data['daily_log'] = existing
data['updated'] = date_str
stats = data.get('stats', {})
stats['total_days_played'] = len(existing)
stats['total_clears'] = sum(1 for d in existing if d.get('cleared'))
profs = list(set(d.get('profession','') for d in existing))
stats['unique_professions'] = profs
streak = 0
for d in reversed(existing):
    if d.get('cleared'):
        streak += 1
    else:
        break
stats['current_streak'] = streak
stats['max_streak'] = max(stats.get('max_streak', 0), streak)
data['stats'] = stats
with open('$ACHIEVEMENT_FILE', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f'streak={streak}, total_clears={stats[\"total_clears\"]}')
" 2>/dev/null && log "更新成就追踪" || log "成就追踪更新跳过（python3 不可用或解析失败）"
fi

# Step 9: 完成
log "收尾完成！"
echo "WRAPUP_OK"
