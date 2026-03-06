#!/bin/bash
# validate-generation.sh — 验证每日生成器输出完整性
# 用法: ./scripts/validate-generation.sh [workspace_dir]
# 在 Step 8 之后或手动执行，检查 roleplay-active.md 和存档文件是否齐全

WORKSPACE="${1:-$HOME/.openclaw/workspace-role-play}"
ACTIVE_FILE="$WORKSPACE/roleplay-active.md"
ERRORS=0
WARNINGS=0

pass() { echo "  [OK] $1"; }
fail() { echo "  [FAIL] $1"; ERRORS=$((ERRORS + 1)); }
warn() { echo "  [WARN] $1"; WARNINGS=$((WARNINGS + 1)); }

echo "=== 生成器输出验证 ==="
echo ""

if [[ ! -f "$ACTIVE_FILE" ]]; then
    fail "roleplay-active.md 不存在"
    echo ""
    echo "结果: ${ERRORS} 错误, ${WARNINGS} 警告"
    exit 1
fi

echo "1. YAML Front-matter"
if head -1 "$ACTIVE_FILE" | grep -q "^---"; then
    pass "front-matter 存在"
    for field in date profession age age_profile theme kink_count media_prefix; do
        if grep -q "^${field}:" "$ACTIVE_FILE"; then
            pass "  字段 ${field} 存在"
        else
            fail "  字段 ${field} 缺失"
        fi
    done
else
    fail "front-matter 缺失（文件不以 --- 开头）"
fi

echo ""
echo "2. 必要段落"

check_section() {
    local section="$1"
    local label="$2"
    if grep -q "^## ${section}" "$ACTIVE_FILE" || grep -q "^### ${section}" "$ACTIVE_FILE"; then
        pass "${label}"
    else
        fail "${label} 缺失"
    fi
}

check_section "职业" "职业段"
check_section "今日年龄" "今日年龄段"
check_section "今日主题" "今日主题段"
check_section "今日性格（五维）" "今日性格（五维）段"

for dim in "1. 职业维度" "2. 自我" "3. 本我" "4. 超我" "5. NSFW性格" "今日言行参考"; do
    if grep -q "### ${dim}" "$ACTIVE_FILE"; then
        pass "  五维子段: ${dim}"
    else
        fail "  五维子段缺失: ${dim}"
    fi
done

check_section "行为准则" "行为准则段"
check_section "专业术语" "专业术语段"
check_section "今日穿着" "今日穿着段"
check_section "穿着清单" "穿着清单段"
check_section "ComfyUI" "ComfyUI 关键词段"
check_section "⛔ 禁止泄漏" "禁止泄漏提醒段"

if grep -q "〔隐藏.*当日性癖" "$ACTIVE_FILE"; then
    pass "隐藏性癖表段"
else
    fail "隐藏性癖表段缺失"
fi

if grep -q "〔隐藏〕暗示策略" "$ACTIVE_FILE"; then
    pass "暗示策略段"
else
    fail "暗示策略段缺失"
fi

echo ""
echo "3. 引用行"

if grep -q "bio.md" "$ACTIVE_FILE"; then
    pass "bio.md 引用行存在"
else
    fail "bio.md 引用行缺失"
fi

if grep -q "personality.md" "$ACTIVE_FILE"; then
    pass "personality.md 引用行存在"
else
    fail "personality.md 引用行缺失"
fi

echo ""
echo "4. 存档文件"

DATE_STR=$(grep "^date:" "$ACTIVE_FILE" | head -1 | sed 's/^date:[[:space:]]*//')
PROFESSION=$(grep "^profession:" "$ACTIVE_FILE" | head -1 | sed 's/^profession:[[:space:]]*//')

if [[ -n "$DATE_STR" ]] && [[ -n "$PROFESSION" ]]; then
    ARCHIVE_DIR="$WORKSPACE/archive/${DATE_STR}-${PROFESSION}"

    if [[ -d "$ARCHIVE_DIR" ]]; then
        pass "存档目录 ${DATE_STR}-${PROFESSION}/ 存在"
    else
        fail "存档目录 ${DATE_STR}-${PROFESSION}/ 不存在"
    fi

    if [[ -f "$ARCHIVE_DIR/bio.md" ]]; then
        BIO_CHARS=$(wc -c < "$ARCHIVE_DIR/bio.md" | tr -d ' ')
        if [[ "$BIO_CHARS" -gt 500 ]]; then
            pass "bio.md 存在 (${BIO_CHARS} 字节)"
        else
            warn "bio.md 存在但内容较短 (${BIO_CHARS} 字节，建议 ~800 字)"
        fi
    else
        fail "bio.md 不存在"
    fi

    if [[ -f "$ARCHIVE_DIR/personality.md" ]]; then
        PERS_CHARS=$(wc -c < "$ARCHIVE_DIR/personality.md" | tr -d ' ')
        if [[ "$PERS_CHARS" -gt 300 ]]; then
            pass "personality.md 存在 (${PERS_CHARS} 字节)"
        else
            warn "personality.md 存在但内容较短 (${PERS_CHARS} 字节，建议 ~500 字)"
        fi
    else
        fail "personality.md 不存在"
    fi
else
    warn "无法从 front-matter 提取日期/职业，跳过存档文件检查"
fi

echo ""
echo "5. guess-log.md"

if [[ -f "$WORKSPACE/guess-log.md" ]]; then
    pass "根目录 guess-log.md 存在"
else
    warn "根目录 guess-log.md 不存在（可能已归档或尚未创建）"
fi

echo ""
echo "6. history_tracker.json"

TRACKER="$WORKSPACE/data/history_tracker.json"
if [[ -f "$TRACKER" ]]; then
    if grep -q '"recent_daily_theme"' "$TRACKER" && ! grep -q '"recent_daily_theme": \[\]' "$TRACKER"; then
        pass "recent_daily_theme 非空"
    else
        fail "recent_daily_theme 为空（Step 7 未写入主题追踪）"
    fi

    if grep -q '"recent_personality_traits"' "$TRACKER" && ! grep -q '"recent_personality_traits": \[\]' "$TRACKER"; then
        pass "recent_personality_traits 非空"
    else
        fail "recent_personality_traits 为空（Step 7 未写入性格特质追踪）"
    fi
else
    fail "history_tracker.json 不存在"
fi

echo ""
echo "=== 验证完成: ${ERRORS} 错误, ${WARNINGS} 警告 ==="

if [[ "$ERRORS" -gt 0 ]]; then
    echo "⚠️ 有 ${ERRORS} 项未通过，请检查生成器流程是否完整执行了所有 Step。"
    exit 1
else
    echo "✅ 所有必要检查通过。"
    exit 0
fi
