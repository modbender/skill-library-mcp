#!/usr/bin/env bash
# tool-finder - 统一搜索 ClawHub skills 和 Smithery MCPs
# v1.2.0 优化：评分排序 + 推荐规则 + 来源标识

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMITHERY_API="https://api.smithery.ai"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GRAY='\033[0;90m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 错误计数
CLAWHUB_ERRORS=0
SMITHERY_ERRORS=0

# 推荐阈值（优化：降低默认过滤阈值，适应模糊搜索）
RECOMMEND_THRESHOLD=3.0
SHOW_THRESHOLD=1.0  # 降低到 1.0，避免过滤掉模糊搜索的相关结果

print_help() {
    cat << EOF
tool-finder - 统一搜索 ClawHub skills 和 Smithery MCPs

用法:
  $0 search <query> [--type skill|mcp] [--limit N] [--exact] [--verbose]
  $0 install <name> --type skill|mcp
  $0 describe <name> --type skill|mcp

选项:
  --type      指定来源类型 (skill|mcp|smithery-skill|all)
  --limit     限制结果数量 (默认：10)
  --exact     精确搜索模式（知道技能名时）
  --verbose   显示详细错误信息
  --all       显示所有结果（包括低评分）
  -h, --help  显示帮助

推荐规则:
  ⭐⭐⭐⭐⭐ 强烈推荐：评分 ≥ 3.5 + 名称高度匹配
  ⭐⭐⭐⭐  推荐：评分 ≥ 3.0 + 名称相关
  ⭐⭐⭐   一般：评分 ≥ 2.0 或 名称部分匹配
  ⭐⭐    低相关：评分 ≥ 1.0（模糊搜索常见）
  ❌     不推荐：评分 < 1.0（默认隐藏）

注意:
  - 模糊搜索分数通常较低 (1.0-2.0)，这是正常的
  - 精确搜索分数通常较高 (≥3.0)
  - 结果按评分降序排列

来源说明:
  skill         - ClawHub Skills (默认)
  mcp           - Smithery MCPs
  smithery-skill - Smithery Skills
  all           - 搜索所有来源 (ClawHub + Smithery MCPs + Smithery Skills)
EOF
}

# 同义词扩展（优化：避免过度扩展导致不相关结果）
expand_query() {
    local query="$1"
    local lower_query=$(echo "$query" | tr '[:upper:]' '[:lower:]')
    
    # RAG 相关
    if [[ "$lower_query" == *"rag"* ]]; then
        echo "$query clawrag rag retrieval augmented generation memory embedding vector knowledge base"
        return
    fi
    
    # GitHub 相关
    if [[ "$lower_query" == *"github"* ]] || [[ "$lower_query" == *"git"* ]]; then
        echo "$query github git repo repository"
        return
    fi
    
    # 搜索相关
    if [[ "$lower_query" == *"search"* ]] || [[ "$lower_query" == *"web"* ]]; then
        echo "$query search web crawl fetch scrape"
        return
    fi
    
    # 记忆相关
    if [[ "$lower_query" == *"memory"* ]] || [[ "$lower_query" == *"remember"* ]]; then
        echo "$query memory remember recall longterm context history"
        return
    fi
    
    # MCP 相关
    if [[ "$lower_query" == *"mcp"* ]]; then
        echo "$query mcp server protocol tool plugin"
        return
    fi
    
    # 默认：不扩展，返回原查询（避免扩展出无关词）
    # 之前的问题："agent create" 扩展成 "agent" "create" 导致大量不相关结果
    echo "$query"
}

# 检测 ClawHub 错误（限流/失败）
check_clawhub_error() {
    local output="$1"
    local verbose="${2:-false}"
    
    if echo "$output" | grep -qi "rate limit"; then
        echo -e "${RED}⚠️  ClawHub API 限流 (Rate limit exceeded)${NC}" >&2
        echo -e "${GRAY}   建议：等待几分钟后重试，或登录 clawhub login${NC}" >&2
        ((CLAWHUB_ERRORS++)) || true
        return 1
    fi
    
    if echo "$output" | grep -qi "error\|failed\|exited with code"; then
        if [[ "$verbose" == "true" ]]; then
            echo -e "${RED}⚠️  ClawHub 搜索失败:${NC}" >&2
            echo -e "${GRAY}   $output${NC}" >&2
        else
            echo -e "${RED}⚠️  ClawHub 搜索失败 (使用 --verbose 查看详情)${NC}" >&2
        fi
        ((CLAWHUB_ERRORS++)) || true
        return 1
    fi
    
    return 0
}

# 计算推荐等级（返回数字 1-5）
get_recommend_level() {
    local score="$1"
    local name="$2"
    local query="$3"
    
    # 名称匹配度检查
    local match_score=0
    local lower_name=$(echo "$name" | tr '[:upper:]' '[:lower:]')
    local lower_query=$(echo "$query" | tr '[:upper:]' '[:lower:]')
    
    if [[ "$lower_name" == *"$lower_query"* ]]; then
        match_score=2
    elif echo "$lower_name" | grep -qi "$lower_query"; then
        match_score=1
    fi
    
    # 综合评分（优化：降低阈值，适应模糊搜索）
    if (( $(echo "$score >= 3.5" | bc -l 2>/dev/null || echo 0) )) && [[ $match_score -ge 1 ]]; then
        echo "5"
    elif (( $(echo "$score >= 3.0" | bc -l 2>/dev/null || echo 0) )) && [[ $match_score -ge 1 ]]; then
        echo "4"
    elif (( $(echo "$score >= 2.0" | bc -l 2>/dev/null || echo 0) )); then
        echo "3"
    elif (( $(echo "$score >= 1.0" | bc -l 2>/dev/null || echo 0) )); then
        echo "2"  # 新增：低相关（模糊搜索常见）
    else
        echo "1"
    fi
}

# 搜索 ClawHub（优化：优先原词搜索 + 扩展补充）
search_clawhub() {
    local query="$1"
    local limit="${2:-10}"
    local exact="${3:-false}"
    local verbose="${4:-false}"
    local show_all="${5:-false}"
    local tmpfile=$(mktemp)
    local errfile=$(mktemp)
    local sorted_file=$(mktemp)
    local all_results_file=$(mktemp)
    
    # 精确模式：直接搜
    if [[ "$exact" == "true" ]]; then
        local result
        result=$(npx clawhub@latest search "$query" 2>"$errfile") || true
        
        if ! check_clawhub_error "$result\n$(cat "$errfile")" "$verbose"; then
            echo -e "${YELLOW}   继续搜索其他来源...${NC}" >&2
        fi
        
        echo "$result" | \
            grep -v "^-" | grep -v "^$" | grep -v "^Searching" | \
            head -n "$limit" > "$tmpfile" || true
    else
        # 优化逻辑：优先原词搜索，再扩展补充
        local hit_rate_limit=false
        
        # 步骤 1：先用原词搜索（保证基础结果）
        echo -e "${GRAY}   [1/2] 原词搜索：$query${NC}" >&2
        local result
        result=$(npx clawhub@latest search "$query" 2>"$errfile") || true
        
        if echo "$result\n$(cat "$errfile")" | grep -qi "rate limit"; then
            hit_rate_limit=true
            echo -e "${RED}   ⚠️  原词搜索限流，结果可能不完整${NC}" >&2
            echo -e "${YELLOW}   提示：使用 --all 显示低评分结果${NC}" >&2
        fi
        
        echo "$result" | \
            grep -v "^-" | grep -v "^$" | grep -v "^Searching" >> "$all_results_file" 2>/dev/null || true
        
        # 统计原词结果数量
        local original_count=$(wc -l < "$all_results_file" | tr -d ' ')
        echo -e "${GRAY}   原词结果：$original_count 条${NC}" >&2
        
        # 步骤 2：如果原词结果不足，再用扩展词补充
        if [[ $original_count -lt $limit ]] && [[ "$hit_rate_limit" == "false" ]]; then
            echo -e "${GRAY}   [2/2] 扩展搜索（补充结果）...${NC}" >&2
            local expanded=$(expand_query "$query")
            
            # 只有当扩展词与原词不同时才搜索
            if [[ "$expanded" != "$query" ]]; then
                local queries=$(echo "$expanded" | tr ' ' '\n' | head -n 5)
                
                for q in $queries; do
                    [[ "$q" == "$query" ]] && continue  # 跳过原词
                    
                    local ext_result
                    ext_result=$(npx clawhub@latest search "$q" 2>"$errfile") || true
                    
                    if echo "$ext_result\n$(cat "$errfile")" | grep -qi "rate limit"; then
                        echo -e "${YELLOW}   ⚠️  扩展词 '$q' 限流，跳过${NC}" >&2
                        continue
                    fi
                    
                    echo "$ext_result" | \
                        grep -v "^-" | grep -v "^$" | grep -v "^Searching" >> "$all_results_file" 2>/dev/null || true
                done
            else
                echo -e "${GRAY}   无扩展词，跳过${NC}" >&2
            fi
            
            local total_count=$(wc -l < "$all_results_file" | tr -d ' ')
            local added_count=$((total_count - original_count))
            echo -e "${GRAY}   扩展结果：+$added_count 条（总计：$total_count 条）${NC}" >&2
        else
            if [[ $original_count -ge $limit ]]; then
                echo -e "${GRAY}   原词结果已足够，跳过扩展搜索${NC}" >&2
            elif [[ "$hit_rate_limit" == "true" ]]; then
                echo -e "${YELLOW}   原词限流，跳过扩展搜索${NC}" >&2
            fi
        fi
        
        # 智能排序 + 去重（优化：名称匹配优先于评分）
        # 问题：ClawHub 评分是向量相似度，不是功能相关性
        # 解决：名称包含搜索词的优先显示，即使评分低
        local matched_file=$(mktemp)
        local other_file=$(mktemp)
        
        # 分离：名称匹配 vs 其他
        while read -r line; do
            [[ -z "$line" ]] && continue
            local name=$(echo "$line" | awk '{print $1}')
            local lower_name=$(echo "$name" | tr '[:upper:]' '[:lower:]')
            local lower_query=$(echo "$query" | tr '[:upper:]' '[:lower:]')
            local query_dash=$(echo "$lower_query" | tr ' ' '-')
            
            # 名称匹配检查（优先级从高到低）
            local match_level=0
            
            # 1. 完整匹配（空格或连字符形式）
            if [[ "$lower_name" == *"$lower_query"* ]] || [[ "$lower_name" == *"$query_dash"* ]]; then
                match_level=2
            fi
            
            # 2. 包含搜索词中的任意一个词
            for word in $lower_query; do
                if [[ "$lower_name" == *"$word"* ]]; then
                    match_level=1
                    break
                fi
            done
            
            # 根据匹配级别分类
            if [[ $match_level -ge 1 ]]; then
                echo "$line" >> "$matched_file"
            else
                echo "$line" >> "$other_file"
            fi
        done < "$all_results_file"
        
        # 合并：名称匹配的在前，其他按评分排序在后
        {
            cat "$matched_file" 2>/dev/null | awk '!seen[$1]++' || true
            sort -t'(' -k2 -rn "$other_file" 2>/dev/null | awk '!seen[$1]++' || true
        } | head -n "$limit" > "$tmpfile"
        
        rm -f "$matched_file" "$other_file"
    fi
    
    # 转换为带评分的 tab 分隔格式，按评分降序排序
    while read -r line; do
        [[ -z "$line" ]] && continue
        local name=$(echo "$line" | awk '{print $1}')
        local desc=$(echo "$line" | sed 's/^[^ ]*  *//' | sed 's/  *([0-9.]*).*$//')
        local score=$(echo "$line" | grep -oE '\([0-9.]+\)' | tr -d '()')
        score=${score:-0}
        printf "%s\t%s\t%s\tclawhub\t%s\n" "$name" "$desc" "$name" "$score"
    done < "$tmpfile" | sort -t$'\t' -k5 -rn > "$sorted_file"
    
    # 输出结果（过滤低评分）
    local has_results=false
    while IFS=$'\t' read -r name desc slug source score; do
        [[ -z "$name" ]] && continue
        
        # 过滤低评分（除非 --all）
        if [[ "$show_all" != "true" ]] && (( $(echo "$score < $SHOW_THRESHOLD" | bc -l 2>/dev/null || echo 0) )); then
            continue
        fi
        
        has_results=true
        printf "%s\t%s\t%s\t%s\t%s\n" "$name" "$desc" "$slug" "$source" "$score"
    done < "$sorted_file"
    
    # 如果没有结果，提示用户使用 --all 或等待限流解除
    if [[ "$has_results" == "false" ]]; then
        echo -e "${YELLOW}   提示：当前结果为空，可能是因为:${NC}" >&2
        echo -e "${YELLOW}     1. 所有结果评分 < 2.0（使用 --all 显示）${NC}" >&2
        echo -e "${YELLOW}     2. API 限流，请等待几分钟后重试${NC}" >&2
        echo -e "${YELLOW}     3. 搜索词太具体，尝试更通用的词${NC}" >&2
    fi
    
    rm -f "$tmpfile" "$errfile" "$sorted_file" "$all_results_file" 2>/dev/null || true
}

# 搜索 Smithery MCPs（使用官方 CLI）
search_smithery_mcp() {
    local query="$1"
    local limit="${2:-10}"
    local verbose="${3:-false}"
    local tmpfile=$(mktemp)
    local errfile=$(mktemp)
    
    # 使用 Smithery CLI 搜索 MCPs
    local result
    result=$(npx @smithery/cli@latest mcp search "$query" --json 2>"$errfile") || true
    
    if [[ -n "$(cat "$errfile")" ]] && [[ "$verbose" == "true" ]]; then
        echo -e "${RED}⚠️  Smithery MCP 搜索警告:${NC}" >&2
        echo -e "${GRAY}   $(cat "$errfile")${NC}" >&2
    fi
    
    if [[ -s "$tmpfile" ]]; then
        jq -r --argjson n "$limit" '
            .servers[:$n][] 
            | "\(.name)\t\(.description | gsub("\n"; " ") | .[0:80])\t\(.qualifiedName)\tsmithery\t0"
        ' "$tmpfile" 2>/dev/null || true
    fi
    
    rm -f "$tmpfile" "$errfile"
}

# 搜索 Smithery Skills（使用官方 CLI）
search_smithery_skills() {
    local query="$1"
    local limit="${2:-10}"
    local verbose="${3:-false}"
    local tmpfile=$(mktemp)
    local errfile=$(mktemp)
    
    # 使用 Smithery CLI 搜索 Skills
    local result
    result=$(npx @smithery/cli@latest skill search "$query" --json 2>"$errfile") || true
    
    if [[ -n "$(cat "$errfile")" ]] && [[ "$verbose" == "true" ]]; then
        echo -e "${RED}⚠️  Smithery Skill 搜索警告:${NC}" >&2
        echo -e "${GRAY}   $(cat "$errfile")${NC}" >&2
    fi
    
    if [[ -s "$tmpfile" ]]; then
        jq -r --argjson n "$limit" '
            .skills[:$n][] 
            | "\(.displayName)\t\(.description | gsub("\n"; " ") | .[0:80])\t\(.qualifiedName)\tsmithery\t0"
        ' "$tmpfile" 2>/dev/null || true
    fi
    
    rm -f "$tmpfile" "$errfile"
}

# 格式化表格（带推荐等级）
format_table_header() {
    printf "${BLUE}%-30s ${YELLOW}%-8s ${GREEN}%-12s ${MAGENTA}%-10s ${NC}%s\n" "名称" "来源" "评分" "推荐" "描述"
    printf "%s\n" "────────────────────────────────────────────────────────────────────────────────────────"
}

# 聚合搜索（优化：评分排序 + 推荐规则）
search_all() {
    local query="$1"
    local type="${2:-all}"
    local limit="${3:-10}"
    local exact="${4:-false}"
    local verbose="${5:-false}"
    local show_all="${6:-false}"
    
    case "$type" in
        skill)
            # 只搜索 ClawHub Skills（显示评分和推荐）
            echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
            echo -e "${BLUE}║${NC} 🔍 搜索结果：${query}"
            echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
            echo ""
            format_table_header
            search_clawhub "$query" "$limit" "$exact" "$verbose" "$show_all" | while IFS=$'\t' read -r name desc slug source score; do
                [[ -n "$name" ]] || continue
                local rec_level=$(get_recommend_level "$score" "$name" "$query")
                local rec_icon=""
                case "$rec_level" in
                    5) rec_icon="⭐⭐⭐⭐⭐" ;;
                    4) rec_icon="⭐⭐⭐⭐" ;;
                    3) rec_icon="⭐⭐⭐" ;;
                    2) rec_icon="⭐⭐" ;;
                    *) rec_icon="❌" ;;
                esac
                printf "${GREEN}%-30s ${YELLOW}%-8s ${GREEN}%-12s ${MAGENTA}%-10s ${NC}%s\n" "$name" "ClawHub" "${score:-0}" "$rec_icon" "${desc:0:50}"
            done
            ;;
        mcp)
            # 只搜索 Smithery MCPs
            search_smithery_mcp "$query" "$limit" "$verbose" | while IFS=$'\t' read -r name desc slug source score; do
                [[ -n "$name" ]] && printf "${GREEN}%-30s ${YELLOW}%-8s ${NC}%s\n" "$name" "Smithery" "${desc:0:50}"
            done
            ;;
        smithery-skill)
            # 只搜索 Smithery Skills
            search_smithery_skills "$query" "$limit" "$verbose" | while IFS=$'\t' read -r name desc slug source score; do
                [[ -n "$name" ]] && printf "${GREEN}%-30s ${YELLOW}%-8s ${NC}%s\n" "$name" "Smithery" "${desc:0:50}"
            done
            ;;
        all|*)
            echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
            echo -e "${BLUE}║${NC} 🔍 搜索结果：${query}"
            echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
            echo ""
            
            echo -e "${GREEN}━━━ ClawHub Skills ━━━${NC}"
            format_table_header
            search_clawhub "$query" "$limit" "$exact" "$verbose" "$show_all" | while IFS=$'\t' read -r name desc slug source score; do
                [[ -n "$name" ]] || continue
                local rec_level=$(get_recommend_level "$score" "$name" "$query")
                local rec_icon=""
                case "$rec_level" in
                    5) rec_icon="⭐⭐⭐⭐⭐" ;;
                    4) rec_icon="⭐⭐⭐⭐" ;;
                    3) rec_icon="⭐⭐⭐" ;;
                    2) rec_icon="⭐⭐" ;;
                    *) rec_icon="❌" ;;
                esac
                printf "${GREEN}%-30s ${YELLOW}%-8s ${GREEN}%-12s ${MAGENTA}%-10s ${NC}%s\n" "$name" "ClawHub" "${score:-0}" "$rec_icon" "${desc:0:50}"
            done
            echo ""
            
            echo -e "${GREEN}━━━ Smithery MCPs ━━━${NC}"
            format_table_header
            search_smithery_mcp "$query" "$limit" "$verbose" | while IFS=$'\t' read -r name desc slug source score; do
                [[ -n "$name" ]] && printf "${GREEN}%-30s ${YELLOW}%-8s ${GREEN}%-12s ${MAGENTA}%-10s ${NC}%s\n" "$name" "Smithery" "N/A" "-" "${desc:0:50}"
            done
            echo ""
            
            echo -e "${GREEN}━━━ Smithery Skills ━━━${NC}"
            format_table_header
            search_smithery_skills "$query" "$limit" "$verbose" | while IFS=$'\t' read -r name desc slug source score; do
                [[ -n "$name" ]] && printf "${GREEN}%-30s ${YELLOW}%-8s ${GREEN}%-12s ${MAGENTA}%-10s ${NC}%s\n" "$name" "Smithery" "N/A" "-" "${desc:0:50}"
            done
            ;;
    esac
    
    # 推荐规则说明
    if [[ "$type" == "skill" ]] || [[ "$type" == "all" ]]; then
        echo ""
        echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
        echo -e "${CYAN}📊 推荐规则${NC}"
        echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}⭐⭐⭐⭐⭐ 强烈推荐${NC}: 评分 ≥ 3.5 + 名称高度匹配"
        echo -e "${GREEN}⭐⭐⭐⭐  推荐${NC}: 评分 ≥ 3.0 + 名称相关"
        echo -e "${YELLOW}⭐⭐⭐   一般${NC}: 评分 ≥ 2.0 或 名称部分匹配"
        echo -e "${GRAY}⭐⭐    低相关${NC}: 评分 ≥ 1.0（模糊搜索常见）"
        echo -e "${RED}❌     不推荐${NC}: 评分 < 1.0 (默认隐藏，使用 --all 显示)"
        echo ""
    fi
    
    # 错误汇总报告
    if [[ $CLAWHUB_ERRORS -gt 0 ]] || [[ $SMITHERY_ERRORS -gt 0 ]]; then
        echo ""
        echo -e "${RED}══════════════════════════════════════════════════════════════${NC}"
        echo -e "${RED}⚠️  搜索警告${NC}"
        echo -e "${RED}══════════════════════════════════════════════════════════════${NC}"
        [[ $CLAWHUB_ERRORS -gt 0 ]] && echo -e "${YELLOW}• ClawHub: $CLAWHUB_ERRORS 次错误/限流${NC}"
        [[ $SMITHERY_ERRORS -gt 0 ]] && echo -e "${YELLOW}• Smithery: $SMITHERY_ERRORS 次错误${NC}"
        echo ""
        echo -e "${GRAY}提示：结果可能不完整，建议:${NC}"
        echo -e "${GRAY}  1. 等待几分钟后重试（限流情况）${NC}"
        echo -e "${GRAY}  2. 使用精确模式：--exact（知道技能名时）${NC}"
        echo -e "${GRAY}  3. 直接访问 https://clawhub.ai 搜索验证${NC}"
        echo -e "${GRAY}  4. 使用 --verbose 查看详细错误${NC}"
    fi
}

# 安装工具
install_tool() {
    local name="$1"
    local type="$2"
    
    case "$type" in
        skill)
            echo -e "${YELLOW}📦 安装 skill: $name${NC}"
            npx clawhub@latest install "$name" --no-input 2>&1 || {
                echo "安装失败，可能需要登录：npx clawhub login" >&2
                return 1
            }
            ;;
        mcp)
            echo -e "${YELLOW}🔌 安装 MCP: $name${NC}"
            echo "提示：MCP 安装需要指定客户端"
            echo "手动安装：npx @smithery/cli@latest mcp add $name --client <client>"
            ;;
        *)
            echo "错误：未知类型 $type" >&2
            return 1
            ;;
    esac
}

# 主逻辑
main() {
    local cmd="${1:-help}"
    shift || true
    
    case "$cmd" in
        search)
            local query="" type="all" limit="10" exact="false" verbose="false" show_all="false"
            while [[ $# -gt 0 ]]; do
                case "$1" in
                    --type) type="$2"; shift 2 ;;
                    --limit) limit="$2"; shift 2 ;;
                    --exact) exact="true"; shift ;;
                    --verbose) verbose="true"; shift ;;
                    -v) verbose="true"; shift ;;
                    --all) show_all="true"; shift ;;
                    *) query="$1"; shift ;;
                esac
            done
            [[ -z "$query" ]] && { echo "错误：请提供搜索关键词" >&2; exit 1; }
            search_all "$query" "$type" "$limit" "$exact" "$verbose" "$show_all"
            ;;
        install)
            local name="" type=""
            while [[ $# -gt 0 ]]; do
                case "$1" in
                    --type) type="$2"; shift 2 ;;
                    *) name="$1"; shift ;;
                esac
            done
            [[ -z "$name" || -z "$type" ]] && { echo "错误：请提供名称和类型" >&2; exit 1; }
            install_tool "$name" "$type"
            ;;
        -h|--help|help) print_help ;;
        *) echo "未知命令：$cmd" >&2; print_help; exit 1 ;;
    esac
}

main "$@"
