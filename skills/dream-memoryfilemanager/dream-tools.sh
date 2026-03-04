#!/usr/bin/env bash
# dream-tools.sh — Dream 技能辅助脚本
# 所有精确计算、文件操作、日期运算由此脚本承担，AI 不做心算
# 依赖：jq, wc, md5sum（macOS 用 md5），openclaw CLI
# 用法：dream-tools.sh <--command> [args...]

set -euo pipefail

# ── 环境变量 ────────────────────────────────────────────────────────────────

DREAM_VAULT_PATH="${DREAM_VAULT_PATH:-$HOME/Documents/Obsidian/dream-vault}"
WORKSPACE_PATH="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
MEMORY_MD="$WORKSPACE_PATH/MEMORY.md"
LEDGER_MD="$DREAM_VAULT_PATH/ledger.md"
LEDGER_INDEX="$DREAM_VAULT_PATH/ledger-index.json"
REMOVED_ENTRIES="$DREAM_VAULT_PATH/meta/removed-entries.json"
OBSIDIAN_INDEX="$DREAM_VAULT_PATH/obsidian-index/_index.md"
MEMORY_HARD_LIMIT=18000
MEMORY_COMPRESS_TRIGGER=16000

# ── 工具函数 ────────────────────────────────────────────────────────────────

log() { echo "[dream-tools] $*" >&2; }

die() { echo "[dream-tools] ERROR: $*" >&2; exit 1; }

# 跨平台 MD5（macOS 用 md5，Linux 用 md5sum）
md5_hash() {
    local input="$1"
    if command -v md5sum &>/dev/null; then
        echo -n "$input" | md5sum | cut -c1-8
    elif command -v md5 &>/dev/null; then
        echo -n "$input" | md5 -q | cut -c1-8
    else
        die "未找到 md5sum 或 md5 命令"
    fi
}

# 确保目录存在
ensure_dir() { mkdir -p "$(dirname "$1")"; }

# ── 命令实现 ────────────────────────────────────────────────────────────────

# --check-idle
# 检查 OpenClaw 是否空闲，返回 idle 或 busy
# 超时 5 秒默认返回 busy，避免 gateway 无响应时挂起
cmd_check_idle() {
    local status
    status=$(timeout 5s openclaw agent status 2>/dev/null) || {
        echo "busy"
        return 0
    }
    # 根据 openclaw agent status 的输出判断
    # 若有 "running" / "active" / "processing" 字样则视为 busy
    if echo "$status" | grep -qiE "running|active|processing|busy"; then
        echo "busy"
    else
        echo "idle"
    fi
}

# --check-size
# 返回 MEMORY.md 当前字符数
# 输出格式：<当前字符数> <压缩触发阈值> <硬上限> <状态:ok|warn|critical>
cmd_check_size() {
    if [[ ! -f "$MEMORY_MD" ]]; then
        echo "0 $MEMORY_COMPRESS_TRIGGER $MEMORY_HARD_LIMIT ok"
        return 0
    fi
    local size
    size=$(wc -c < "$MEMORY_MD" | tr -d ' ')
    local state="ok"
    if [[ $size -ge $MEMORY_HARD_LIMIT ]]; then
        state="critical"
    elif [[ $size -ge $MEMORY_COMPRESS_TRIGGER ]]; then
        state="warn"
    fi
    echo "$size $MEMORY_COMPRESS_TRIGGER $MEMORY_HARD_LIMIT $state"
}

# --hash "<内容>"
# 输出 8 位短哈希，用于条目 ID 生成和去重
cmd_hash() {
    local input="${1:-}"
    [[ -z "$input" ]] && die "--hash 需要提供内容参数"
    md5_hash "$input"
}

# --atomic-write <target-file> <tmp-file>
# 验证 tmp-file 存在且字符数不超过硬上限后，原子替换 target-file
# 针对 MEMORY.md 额外做字符数校验，其他文件只做存在性校验
cmd_atomic_write() {
    local target="${1:-}"
    local tmpfile="${2:-}"
    [[ -z "$target" || -z "$tmpfile" ]] && die "--atomic-write 需要 <target> <tmpfile>"
    [[ ! -f "$tmpfile" ]] && die "tmp 文件不存在：$tmpfile"

    # 若目标是 MEMORY.md，检查字符数上限
    if [[ "$(realpath "$target" 2>/dev/null)" == "$(realpath "$MEMORY_MD" 2>/dev/null)" ]] || \
       [[ "$target" == *"MEMORY.md" ]]; then
        local size
        size=$(wc -c < "$tmpfile" | tr -d ' ')
        if [[ $size -gt $MEMORY_HARD_LIMIT ]]; then
            die "写入中止：tmp 文件大小 ${size} 字符，超过硬上限 ${MEMORY_HARD_LIMIT}。请先压缩内容。"
        fi
        log "MEMORY.md 写入校验通过：${size}/${MEMORY_HARD_LIMIT} 字符"
    fi

    ensure_dir "$target"
    # mv 在同一文件系统上是原子操作
    mv "$tmpfile" "$target"
    log "原子写入完成：$target"
}

# --ledger-append <id> <category> <content> [<note>]
# 向 ledger.md 追加一条记录区块，同时更新 ledger-index.json
cmd_ledger_append() {
    local id="${1:-}"
    local category="${2:-}"
    local content="${3:-}"
    local note="${4:-首次入档}"
    [[ -z "$id" || -z "$category" || -z "$content" ]] && \
        die "--ledger-append 需要 <id> <category> <content>"

    ensure_dir "$LEDGER_MD"
    ensure_dir "$LEDGER_INDEX"

    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M')
    local datestamp
    datestamp=$(date '+%Y-%m-%d')

    # 追加到 ledger.md
    cat >> "$LEDGER_MD" << EOF

---
ID: $id
入档时间: $timestamp
类别: $category
内容: $content
备注: $note
---
EOF

    # 更新 ledger-index.json
    # 若文件不存在或为空，初始化为空数组
    if [[ ! -f "$LEDGER_INDEX" ]] || [[ ! -s "$LEDGER_INDEX" ]]; then
        echo '[]' > "$LEDGER_INDEX"
    fi

    # 检查 ID 是否已存在
    local exists
    exists=$(jq --arg id "$id" 'any(.[]; .id == $id)' "$LEDGER_INDEX")

    if [[ "$exists" == "true" ]]; then
        # 已存在：追加事件记录到该条目的 events 数组
        local tmp_index
        tmp_index=$(mktemp)
        jq --arg id "$id" \
           --arg ts "$timestamp" \
           --arg note "$note" \
           'map(if .id == $id then
               .events += [{"time": $ts, "note": $note}] |
               .last_updated = $ts
           else . end)' \
           "$LEDGER_INDEX" > "$tmp_index"
        mv "$tmp_index" "$LEDGER_INDEX"
        log "ledger-index 更新（已有条目追加事件）：$id"
    else
        # 不存在：新增条目
        local tmp_index
        tmp_index=$(mktemp)
        jq --arg id "$id" \
           --arg category "$category" \
           --arg content "$content" \
           --arg ts "$timestamp" \
           --arg date "$datestamp" \
           --arg note "$note" \
           '. += [{
               "id": $id,
               "category": $category,
               "summary": ($content | .[0:80]),
               "first_archived": $date,
               "last_updated": $ts,
               "status": "active",
               "events": [{"time": $ts, "note": $note}]
           }]' \
           "$LEDGER_INDEX" > "$tmp_index"
        mv "$tmp_index" "$LEDGER_INDEX"
        log "ledger-index 新增条目：$id"
    fi

    log "ledger 追加完成：[$category] ${content:0:60}..."
}

# --ledger-search "<keyword>"
# 在 ledger-index.json 中检索，输出匹配条目的 ID、类别、摘要、入档时间
cmd_ledger_search() {
    local keyword="${1:-}"
    [[ -z "$keyword" ]] && die "--ledger-search 需要提供关键词"
    [[ ! -f "$LEDGER_INDEX" ]] && { echo "[]"; return 0; }

    # 在 summary 和 category 中进行大小写不敏感的字符串匹配
    jq --arg kw "$keyword" \
       '[.[] | select(
           (.summary | ascii_downcase | contains($kw | ascii_downcase)) or
           (.category | ascii_downcase | contains($kw | ascii_downcase))
       ) | {id, category, summary, first_archived, status}]' \
       "$LEDGER_INDEX"
}

# --ledger-mark-reemergence <id>
# 将指定条目标记为 re-emerged，在 ledger 追加事件记录
cmd_ledger_mark_reemergence() {
    local id="${1:-}"
    [[ -z "$id" ]] && die "--ledger-mark-reemergence 需要提供 ID"
    [[ ! -f "$LEDGER_INDEX" ]] && die "ledger-index.json 不存在"

    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M')

    # 追加事件到 ledger.md
    cat >> "$LEDGER_MD" << EOF

---
ID: $id
更新时间: $timestamp
事件: re-emerged
备注: 该条目曾被遗忘，在后续对话中再次出现，重要性提升
---
EOF

    # 更新 ledger-index.json 中的状态和事件
    local tmp_index
    tmp_index=$(mktemp)
    jq --arg id "$id" \
       --arg ts "$timestamp" \
       'map(if .id == $id then
           .status = "re-emerged" |
           .last_updated = $ts |
           .events += [{"time": $ts, "note": "re-emerged"}]
       else . end)' \
       "$LEDGER_INDEX" > "$tmp_index"
    mv "$tmp_index" "$LEDGER_INDEX"
    log "ledger re-emergence 标记完成：$id"
}

# --dedup-index "<url-or-hash>"
# 检查 obsidian-index/_index.md 是否已有该条目
# 返回 exists 或 new
cmd_dedup_index() {
    local input="${1:-}"
    [[ -z "$input" ]] && die "--dedup-index 需要提供 URL 或哈希"

    if [[ ! -f "$OBSIDIAN_INDEX" ]]; then
        echo "new"
        return 0
    fi

    local hash
    hash=$(md5_hash "$input")

    # 在索引文件中搜索原始 URL 或其哈希
    if grep -qF "$input" "$OBSIDIAN_INDEX" 2>/dev/null || \
       grep -qF "$hash" "$OBSIDIAN_INDEX" 2>/dev/null; then
        echo "exists"
    else
        echo "new"
    fi
}

# --record-removed "<id>" "<summary>" "<content-hash>"
# 将从 MEMORY.md 移除的条目记录到 removed-entries.json（Re-emergence 用）
cmd_record_removed() {
    local id="${1:-}"
    local summary="${2:-}"
    local content_hash="${3:-}"
    [[ -z "$id" || -z "$summary" ]] && die "--record-removed 需要 <id> <summary>"

    ensure_dir "$REMOVED_ENTRIES"

    if [[ ! -f "$REMOVED_ENTRIES" ]] || [[ ! -s "$REMOVED_ENTRIES" ]]; then
        echo '[]' > "$REMOVED_ENTRIES"
    fi

    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M')
    local datestamp
    datestamp=$(date '+%Y-%m-%d')

    local tmp
    tmp=$(mktemp)
    jq --arg id "$id" \
       --arg summary "$summary" \
       --arg hash "$content_hash" \
       --arg ts "$timestamp" \
       --arg date "$datestamp" \
       '. += [{
           "id": $id,
           "summary": $summary,
           "content_hash": $hash,
           "removed_at": $date,
           "removed_ts": $ts,
           "reemergence_count": 0
       }]' \
       "$REMOVED_ENTRIES" > "$tmp"
    mv "$tmp" "$REMOVED_ENTRIES"
    log "removed-entries 记录：$id"
}

# --check-reemergence "<content>"
# 检查新内容是否与曾被移除的条目相似
# 当前实现：关键词匹配（精度够用，避免引入向量依赖）
# 返回：matched <id> <summary> 或 no-match
cmd_check_reemergence() {
    local content="${1:-}"
    [[ -z "$content" ]] && die "--check-reemergence 需要提供内容"
    [[ ! -f "$REMOVED_ENTRIES" ]] && { echo "no-match"; return 0; }

    # 提取内容中的关键词（去除常见停用词，取前 5 个有意义的词）
    local keywords
    keywords=$(echo "$content" | \
        tr '[:upper:]' '[:lower:]' | \
        grep -oE '[a-z\u4e00-\u9fa5]{2,}' | \
        grep -vE '^(the|and|for|with|that|this|from|have|will|been|they|them|我|的|是|了|在|和|也|就|都|但)$' | \
        head -5 | tr '\n' '|' | sed 's/|$//')

    if [[ -z "$keywords" ]]; then
        echo "no-match"
        return 0
    fi

    # 在 removed-entries 的 summary 中搜索关键词
    local match
    match=$(jq --arg pattern "$keywords" \
        '[.[] | select(.summary | test($pattern; "i"))] | first // empty' \
        "$REMOVED_ENTRIES" 2>/dev/null)

    if [[ -n "$match" && "$match" != "null" ]]; then
        local matched_id matched_summary
        matched_id=$(echo "$match" | jq -r '.id')
        matched_summary=$(echo "$match" | jq -r '.summary')

        # 更新 reemergence_count
        local tmp
        tmp=$(mktemp)
        jq --arg id "$matched_id" \
            'map(if .id == $id then
                .reemergence_count += 1
            else . end)' \
            "$REMOVED_ENTRIES" > "$tmp"
        mv "$tmp" "$REMOVED_ENTRIES"

        echo "matched $matched_id $matched_summary"
    else
        echo "no-match"
    fi
}

# --active-days-since "<YYYY-MM-DD>"
# 计算从指定日期到今天之间记录在 active-days.json 中的活跃天数
cmd_active_days_since() {
    local since="${1:-}"
    [[ -z "$since" ]] && die "--active-days-since 需要提供日期（YYYY-MM-DD）"

    local active_days_file="$DREAM_VAULT_PATH/meta/active-days.json"
    if [[ ! -f "$active_days_file" ]]; then
        echo "0"
        return 0
    fi

    jq --arg since "$since" \
        '[.[] | select(. >= $since)] | length' \
        "$active_days_file"
}

# --record-active-day
# 将今日加入 active-days.json（去重）
cmd_record_active_day() {
    local active_days_file="$DREAM_VAULT_PATH/meta/active-days.json"
    ensure_dir "$active_days_file"

    local today
    today=$(date '+%Y-%m-%d')

    if [[ ! -f "$active_days_file" ]] || [[ ! -s "$active_days_file" ]]; then
        echo '[]' > "$active_days_file"
    fi

    local tmp
    tmp=$(mktemp)
    jq --arg today "$today" \
        'if any(.[]; . == $today) then . else . += [$today] | sort end' \
        "$active_days_file" > "$tmp"
    mv "$tmp" "$active_days_file"
    log "活跃天记录：$today"
}

# --init
# 初始化 Dream vault 目录结构
cmd_init() {
    log "初始化 Dream vault：$DREAM_VAULT_PATH"

    mkdir -p "$DREAM_VAULT_PATH/meta"
    mkdir -p "$DREAM_VAULT_PATH/obsidian-index/topics"

    # 初始化 JSON 文件
    [[ ! -f "$LEDGER_INDEX" ]]      && echo '[]' > "$LEDGER_INDEX"
    [[ ! -f "$REMOVED_ENTRIES" ]]   && echo '[]' > "$REMOVED_ENTRIES"
    [[ ! -f "$DREAM_VAULT_PATH/meta/active-days.json" ]] && \
        echo '[]' > "$DREAM_VAULT_PATH/meta/active-days.json"

    # 初始化 dream-state.txt
    if [[ ! -f "$DREAM_VAULT_PATH/meta/dream-state.txt" ]]; then
        echo "active" > "$DREAM_VAULT_PATH/meta/dream-state.txt"
    fi

    # 初始化 ledger.md（带说明头）
    if [[ ! -f "$LEDGER_MD" ]]; then
        cat > "$LEDGER_MD" << 'EOF'
# Dream Ledger — 永久档案

> 只追加，永不删除。每条记录代表曾经到达过长期记忆的内容。
> 即使被遗忘、被移除，历史记录永久保留。

EOF
    fi

    # 初始化 obsidian-index/_index.md
    if [[ ! -f "$OBSIDIAN_INDEX" ]]; then
        cat > "$OBSIDIAN_INDEX" << 'EOF'
# Obsidian 内容索引

> 由 Dream 技能维护。文章、笔记、网页的结构化索引，按日期倒序。

EOF
    fi

    log "初始化完成"
    echo "ok"
}

# --status
# 输出 Dream 系统状态摘要（低 IO，只读 meta）
cmd_status() {
    local state_file="$DREAM_VAULT_PATH/meta/dream-state.txt"
    local last_review_file="$DREAM_VAULT_PATH/meta/last-review.txt"
    local active_days_file="$DREAM_VAULT_PATH/meta/active-days.json"

    local state="unknown"
    [[ -f "$state_file" ]] && state=$(cat "$state_file")

    local last_review="从未"
    local hours_since="-"
    if [[ -f "$last_review_file" ]]; then
        last_review=$(cat "$last_review_file")
        # 计算距上次蒸馏的小时数
        if command -v python3 &>/dev/null; then
            hours_since=$(python3 -c "
from datetime import datetime
last = datetime.strptime('$last_review', '%Y-%m-%d %H:%M')
diff = datetime.now() - last
print(int(diff.total_seconds() / 3600))
" 2>/dev/null || echo "-")
        fi
    fi

    local memory_size=0
    [[ -f "$MEMORY_MD" ]] && memory_size=$(wc -c < "$MEMORY_MD" | tr -d ' ')

    local ledger_count=0
    [[ -f "$LEDGER_INDEX" ]] && \
        ledger_count=$(jq 'length' "$LEDGER_INDEX" 2>/dev/null || echo 0)

    local active_days=0
    [[ -f "$active_days_file" ]] && \
        active_days=$(jq 'length' "$active_days_file" 2>/dev/null || echo 0)

    local obsidian_count=0
    [[ -f "$OBSIDIAN_INDEX" ]] && \
        obsidian_count=$(grep -c '^## ' "$OBSIDIAN_INDEX" 2>/dev/null || echo 0)

    cat << EOF
MEMORY.md: ${memory_size} 字符 / ${MEMORY_HARD_LIMIT} 上限
永久档案: ${ledger_count} 条记录
活跃天数: ${active_days} 天
上次蒸馏: ${last_review}（${hours_since} 小时前）
系统状态: ${state}
Obsidian 索引: ${obsidian_count} 条
EOF
}

# ── 主入口 ──────────────────────────────────────────────────────────────────

CMD="${1:-}"
shift || true

case "$CMD" in
    --check-idle)             cmd_check_idle ;;
    --check-size)             cmd_check_size ;;
    --hash)                   cmd_hash "$@" ;;
    --atomic-write)           cmd_atomic_write "$@" ;;
    --ledger-append)          cmd_ledger_append "$@" ;;
    --ledger-search)          cmd_ledger_search "$@" ;;
    --ledger-mark-reemergence) cmd_ledger_mark_reemergence "$@" ;;
    --dedup-index)            cmd_dedup_index "$@" ;;
    --record-removed)         cmd_record_removed "$@" ;;
    --check-reemergence)      cmd_check_reemergence "$@" ;;
    --active-days-since)      cmd_active_days_since "$@" ;;
    --record-active-day)      cmd_record_active_day ;;
    --init)                   cmd_init ;;
    --status)                 cmd_status ;;
    *)
        cat << 'EOF'
用法：dream-tools.sh <命令> [参数...]

命令列表：
  --check-idle                        检查 OpenClaw 是否空闲（返回 idle/busy）
  --check-size                        返回 MEMORY.md 字符数和状态
  --hash "<内容>"                     生成 8 位短哈希（ID 生成/去重用）
  --atomic-write <目标文件> <tmp文件>  原子替换文件（含 MEMORY.md 字符数校验）
  --ledger-append <id> <类别> <内容> [备注]  向 ledger 追加记录
  --ledger-search "<关键词>"           检索 ledger-index.json
  --ledger-mark-reemergence <id>       标记 ledger 条目为 re-emerged
  --dedup-index "<url或哈希>"          检查 obsidian-index 是否已有该条目
  --record-removed <id> <摘要> <哈希>  记录从 MEMORY.md 移除的条目
  --check-reemergence "<内容>"         检查内容是否与曾被移除条目相似
  --active-days-since "<YYYY-MM-DD>"  计算指定日期后的活跃天数
  --record-active-day                 记录今日为活跃天
  --init                              初始化 Dream vault 目录结构
  --status                            输出系统状态摘要

环境变量：
  DREAM_VAULT_PATH    Dream vault 路径（默认：~/Documents/Obsidian/dream-vault）
  OPENCLAW_WORKSPACE  OpenClaw workspace 路径（默认：~/.openclaw/workspace）
EOF
        exit 1
        ;;
esac
