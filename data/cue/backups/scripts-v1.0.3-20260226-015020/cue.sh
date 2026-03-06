#!/bin/bash
#
# Cue - 主入口脚本
# 智能路由：自动识别用户意图并执行相应操作

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CUECUE_BASE_URL="https://cuecue.cn"

# 日志配置
LOG_DIR="$HOME/.cuecue/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/cue-$(date +%Y%m%d).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# 错误日志
log_error() {
    local msg="$1"
    local error_log="$LOG_DIR/error-$(date +%Y%m).log"
    mkdir -p "$LOG_DIR"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $msg" >> "$error_log"
    log "ERROR: $msg"
}

# 信息日志
log_info() {
    local msg="$1"
    local info_log="$LOG_DIR/info-$(date +%Y%m).log"
    mkdir -p "$LOG_DIR"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $msg" >> "$info_log"
}

# 当前版本号
CURRENT_VERSION="1.0.3"

# 检查是否首次使用
is_first_time() {
    local chat_id="$1"
    local user_flag="$HOME/.cuecue/users/${chat_id}/.initialized"
    [ ! -f "$user_flag" ]
}

# 标记用户已初始化
mark_initialized() {
    local chat_id="$1"
    local user_dir="$HOME/.cuecue/users/${chat_id}"
    mkdir -p "$user_dir"
    touch "$user_dir/.initialized"
    # 保存当前版本
    echo "$CURRENT_VERSION" > "$user_dir/.version"
}

# 检查是否需要显示更新提示
check_version_update() {
    local chat_id="$1"
    local version_file="$HOME/.cuecue/users/${chat_id}/.version"
    
    # 如果版本文件不存在，视为首次使用
    if [ ! -f "$version_file" ]; then
        echo "first_time"
        return
    fi
    
    local saved_version
    saved_version=$(cat "$version_file" 2>/dev/null || echo "0.0.0")
    
    # 比较版本号
    if [ "$saved_version" != "$CURRENT_VERSION" ]; then
        echo "updated"
        # 更新版本号
        echo "$CURRENT_VERSION" > "$version_file"
    else
        echo "normal"
    fi
}

# 显示更新提示
show_update_notice() {
    local old_version="$1"
    
    cat << EOF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ Cue 已更新至 v${CURRENT_VERSION}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**从 v${old_version} 升级到 v${CURRENT_VERSION}**

**本次更新内容**：

🔧 新增 /cn 命令 - 查看监控触发通知（默认最近3日）
🔧 优化 /key 配置 - 直接发送 API Key 即可自动识别配置
🔧 增强监控通知 - 触发记录自动保存，支持历史查询
🔧 新增自动角色匹配 - 根据主题智能选择研究视角
🔧 重写提示词格式 - 更专业的 rewritten_mandate 结构
🔧 智能状态检测 - 区分首次使用/版本更新/正常使用

**新功能试用**：
• /cn 3           # 查看最近3日监控通知
• /key            # 查看 API Key 配置状态
• /cue 今日龙虎榜  # 体验自动角色匹配（短线交易视角）

**查看详情**：
• /ch             # 显示完整帮助
• 查阅 SECURITY.md - 了解安全详情

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF
}

# 显示首次欢迎消息
show_welcome() {
    cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 欢迎使用 Cue - 你的专属调研助理
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cue 是一款面向专业场景的 AI 调研助理，不只是给答案，
还提供完整的证据链和可溯源的研究过程。

⚠️  **安全提示 / Security Notice：**
• 本工具会创建 ~/.cuecue 本地存储目录
• 会安装 cron 定时任务（每30分钟运行监控检查）
• 需要外部 API 访问权限 (cuecue.cn, api.tavily.com)

**核心亮点**：
🔍 低幻觉 - 全局事实校验，多源交叉验证
🔗 可溯源 - 每个结论都有来源和证据链
🤖 Multi-Agent - 自动搜集、验证、分析

**快速开始 / Quick Start**：
• /cue <研究主题>              # 开始深度研究（40-60分钟）
• /cue --mode trader 龙虎榜    # 短线交易视角分析
• /ct                          # 查看任务列表
• /cm                          # 查看监控项列表
• /cn 3                        # 查看最近3日监控通知
• /ch                          # 显示完整帮助

**配置 API Key / Setup：**
发送 /key 查看当前配置状态
或直接发送 API Key（如 tvly-xxxxx）自动识别配置

📚 详细文档：发送 /ch 或查阅 SECURITY.md

EOF
}

# 检查 API Key 并引导注册
check_and_guide_api_key() {
    local missing_keys=()
    
    if [ -z "$CUECUE_API_KEY" ]; then
        missing_keys+=("CueCue")
    fi
    
    if [ -z "$TAVILY_API_KEY" ]; then
        missing_keys+=("Tavily")
    fi
    
    if [ ${#missing_keys[@]} -gt 0 ]; then
        echo ""
        echo "⚠️  **需要配置 API Key**"
        echo ""
        
        for key in "${missing_keys[@]}"; do
            case "$key" in
                "CueCue")
                    echo "📌 **CueCue API Key**（必需）"
                    echo "   功能：深度研究服务"
                    echo "   获取：https://cuecue.cn"
                    echo ""
                    ;;
                "Tavily")
                    echo "📌 **Tavily API Key**（监控必需）"
                    echo "   功能：新闻搜索、公告监控"
                    echo "   获取：https://tavily.com（免费）"
                    echo ""
                    ;;
            esac
        done
        
        echo "**快速配置**（推荐）："
        echo "   直接发送 API Key，我会自动识别并配置"
        echo ""
        echo "   • Tavily: tvly-xxxxx"
        echo "   • CueCue: skb-xxxxx 或 sk-xxxxx"
        echo "   • QVeris: sk-xxxxx (长格式)"
        echo ""
        echo "**或手动配置**："
        echo "   1. 编辑 ~/.openclaw/.env 文件"
        echo "   2. 添加："
        
        for key in "${missing_keys[@]}"; do
            case "$key" in
                "CueCue")
                    echo "      CUECUE_API_KEY=your-key"
                    ;;
                "Tavily")
                    echo "      TAVILY_API_KEY=your-key"
                    ;;
            esac
        done
        
        echo "   3. 重启：openclaw gateway restart"
        echo ""
        echo "💡 或使用交互式配置：发送 /config"
        echo ""
        return 1
    fi
    return 0
}

# 检测 API Key 对应的服务
detect_service_from_key() {
    local api_key="$1"
    
    # 验证 key 长度
    if [ ${#api_key} -lt 10 ]; then
        echo ""
        return 1
    fi
    
    # Tavily: tvly-xxxxx
    if [[ "$api_key" == tvly-* ]]; then
        echo "tavily"
        return 0
    fi
    
    # CueCue: skb... 开头
    if [[ "$api_key" == skb* ]]; then
        echo "cuecue"
        return 0
    fi
    
    # 根据长度区分 CueCue 和 QVeris
    local key_len=${#api_key}
    if [[ "$api_key" == sk-* ]]; then
        if [ "$key_len" -gt 40 ]; then
            echo "qveris"
        else
            echo "cuecue"
        fi
        return 0
    fi
    
    echo ""
    return 1
}

# 自动配置 API Key
auto_configure_key() {
    local api_key="$1"
    local chat_id="$2"
    
    # 验证 key 长度
    if [ -z "$api_key" ] || [ ${#api_key} -lt 10 ]; then
        echo ""
        echo "❌ **API Key 格式不正确**"
        echo ""
        echo "请检查："
        echo "   • Key 长度应至少 10 个字符"
        echo "   • 确保复制完整，没有遗漏"
        echo ""
        log_error "API Key format error: length ${#api_key}"
        return 1
    fi
    
    local service
    service=$(detect_service_from_key "$api_key")
    
    if [ -z "$service" ]; then
        echo ""
        echo "❌ **无法识别 API Key 类型**"
        echo ""
        echo "请确保使用正确的 Key 格式："
        echo "   • Tavily:    tvly-xxxxx (以 tvly- 开头)"
        echo "   • CueCue:    skb-xxxxx 或 sk-xxxxx (skb 开头或短格式 sk-)"
        echo "   • QVeris:    sk-xxxxx (长格式 sk-，长度 >40 字符)"
        echo ""
        echo "示例："
        echo "   tvly-dev-abc123xyz"
        echo "   skbX1fQos33AVv7NWMi2ux"
        echo "   sk-s7puGi-wt9zkhRVcsAelDvaoYuNJAnupX2LoHDJEl3k"
        echo ""
        log_error "API Key recognition failed: ${api_key:0:10}..."
        return 1
    fi
    
    local var_name=""
    local service_name=""
    local service_url=""
    
    case "$service" in
        "tavily")
            var_name="TAVILY_API_KEY"
            service_name="Tavily"
            service_url="https://tavily.com"
            ;;
        "cuecue")
            var_name="CUECUE_API_KEY"
            service_name="CueCue"
            service_url="https://cuecue.cn"
            ;;
        "qveris")
            var_name="QVERIS_API_KEY"
            service_name="QVeris"
            service_url="https://qveris.ai"
            ;;
    esac
    
    # 保存到 .env
    local env_file="$HOME/.openclaw/.env"
    local updated=false
    
    if grep -q "^${var_name}=" "$env_file" 2>/dev/null; then
        # 更新现有配置
        sed -i "s/^${var_name}=.*/${var_name}=${api_key}/" "$env_file"
        updated=true
    else
        # 添加新配置
        echo "${var_name}=${api_key}" >> "$env_file"
    fi
    
    # 立即导出到当前环境
    export "$var_name=$api_key"
    
    log_info "API Key configured for $service_name"
    
    echo ""
    echo "✅ **${service_name} API Key 配置成功！**"
    echo ""
    if [ "$updated" = true ]; then
        echo "ℹ️  已更新现有配置"
    else
        echo "ℹ️  已添加新配置"
    fi
    echo ""
    echo "密钥已保存到 ~/.openclaw/.env 并生效，无需重启。"
    echo ""
    echo "服务信息："
    echo "   • 名称: $service_name"
    echo "   • 官网: $service_url"
    
    # 检查是否还有其他未配置的
    local still_missing=()
    [ -z "$CUECUE_API_KEY" ] && [ "$service" != "cuecue" ] && still_missing+=("CueCue")
    [ -z "$TAVILY_API_KEY" ] && [ "$service" != "tavily" ] && still_missing+=("Tavily")
    [ -z "$QVERIS_API_KEY" ] && [ "$service" != "qveris" ] && still_missing+=("QVeris")
    
    if [ ${#still_missing[@]} -gt 0 ]; then
        echo ""
        echo "📋 **仍需配置**:"
        for s in "${still_missing[@]}"; do
            echo "   • $s"
        done
        echo ""
        echo "继续发送对应的 API Key 即可自动配置。"
    else
        echo ""
        echo "🎉 **所有 API Key 配置完成！**"
        echo ""
        echo "现在可以："
        echo "   • /cue <主题> → 启动深度研究"
        echo "   • /ct → 查看任务和监控"
    fi
    
    return 0
}

# 显示帮助
show_help() {
    cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Cue - 你的专属调研助理
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**核心功能**：低幻觉、可溯源的深度研究

**使用方式**：
• /cue <主题>                    # 智能调研
• /cue --mode <模式> <主题>      # 指定视角
• /ct                            # 查看任务列表
• /cm                            # 查看监控项列表
• /cn [天数]                     # 查看监控通知（默认3日）
• /cs <任务ID>                   # 查看任务详情
• /ch                            # 显示帮助
• /config                        # 配置 API Key

**研究视角模式**（自动匹配或手动指定）：
• trader       - 短线交易视角（龙虎榜、资金流向、游资动向）
• fund-manager - 基金经理视角（财报、估值、投资决策）
• researcher   - 产业研究视角（产业链、竞争格局）
• advisor      - 理财顾问视角（投资建议、资产配置）

**自动匹配规则**：
• 龙虎榜/涨停/资金流向 → 短线交易视角
• 财报/估值/业绩 → 基金经理视角
• 产业链/竞争格局 → 产业研究视角

**首次使用**：
发送 /config 配置 API Key（仅需一次）

**示例**：
• /cue 宁德时代2024财报
• /cue --mode fund-manager 特斯拉
• /cn 7                        # 查看最近7日通知

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
}

# 显示详细进度描述
show_detailed_progress() {
    local topic="$1"
    local elapsed="${2:-0}"
    
    cat << EOF
🔬 **正在深度研究：${topic}**

**研究阶段**：
${elapsed}  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 **进度说明**：
• 0-10分钟：全网信息搜集与初步筛选
• 10-30分钟：多源交叉验证与事实核查  
• 30-50分钟：深度分析与逻辑推理
• 50-60分钟：报告生成与质量检查

⏱️ **预计剩余时间**：$((60 - elapsed / 60)) 分钟
💡 **您无需等待**，完成后会自动推送结果

🔗 **实时查看**：${CUECUE_BASE_URL}/c/<任务ID>

EOF
}

# 根据主题自动匹配合适的研究角色
auto_detect_mode() {
    local topic="$1"
    local topic_lower=$(echo "$topic" | tr '[:upper:]' '[:lower:]')
    
    # 交易/短线/龙虎榜/资金流向 → 短线交易者视角
    if echo "$topic_lower" | grep -qiE "(龙虎榜|涨停|游资|资金流向|短线|打板|连板|换手率|主力资金)"; then
        echo "trader"
        return
    fi
    
    # 财报/估值/业绩/投资 → 基金经理视角
    if echo "$topic_lower" | grep -qiE "(财报|估值|业绩|年报|季报|投资|财务|ROE|PE|PB|现金流|盈利)"; then
        echo "fund-manager"
        return
    fi
    
    # 产业链/竞争格局/技术路线 → 研究员视角
    if echo "$topic_lower" | grep -qiE "(产业链|竞争格局|技术路线|市场格局|行业分析|市场份额|供应链|上下游)"; then
        echo "researcher"
        return
    fi
    
    # 投资建议/配置/风险 → 理财顾问视角
    if echo "$topic_lower" | grep -qiE "(投资建议|资产配置|风险控制|适合买|怎么买|定投|组合)"; then
        echo "advisor"
        return
    fi
    
    # 默认使用研究员视角（最通用）
    echo "researcher"
}

# 获取角色显示名称
get_mode_display_name() {
    local mode="$1"
    case "$mode" in
        trader|短线交易者)
            echo "短线交易视角"
            ;;
        fund-manager|基金经理)
            echo "基金经理视角"
            ;;
        researcher|研究员)
            echo "产业研究视角"
            ;;
        advisor|理财顾问)
            echo "理财顾问视角"
            ;;
        *)
            echo "智能分析视角"
            ;;
    esac
}

# 启动深度研究
start_research() {
    local topic="$1"
    local chat_id="$2"
    local mode="${3:-default}"
    
    # Mode 映射：中文 -> 英文
    case "$mode" in
        理财顾问|advisor)
            mode="advisor"
            ;;
        研究员|researcher)
            mode="researcher"
            ;;
        基金经理|fund-manager)
            mode="fund-manager"
            ;;
        短线|交易者|trader)
            mode="trader"
            ;;
    esac
    
    # 如果用户没有指定模式，自动检测
    if [ "$mode" = "default" ]; then
        mode=$(auto_detect_mode "$topic")
        local mode_display=$(get_mode_display_name "$mode")
        echo "🎯 根据主题自动匹配研究视角：${mode_display}"
        echo ""
    fi
    
    log "🔬 启动研究: $topic (模式: $mode, chat: $chat_id)"
    
    # 显示详细进度说明
    show_detailed_progress "$topic" 0
    
    # 调用 research.sh
    "$SCRIPT_DIR/research.sh" "$topic" "$chat_id" "$mode" &
    local pid=$!
    
    # 等待初始化完成（获取任务ID）
    sleep 2
    
    # 查找最新创建的任务
    local task_file
    task_file=$(ls -t "$HOME/.cuecue/users/$chat_id/tasks/"/*.json 2>/dev/null | head -1)
    
    if [ -n "$task_file" ]; then
        local task_id
        task_id=$(basename "$task_file" .json)
        
        local session
        session=$(jq -r '.session // empty' "$task_file")
        
        local report_url="${CUECUE_BASE_URL}/c/${session}"
        
        cat << EOF

✅ **研究任务已启动！**

📋 **任务信息**：
• 主题：${topic}
• 任务ID：${task_id}

⏳ **进度更新**：每 5 分钟推送一次
🔔 **完成通知**：研究完成后自动推送

您无需等待，可以继续其他工作。
EOF
    else
        echo "⚠️ 任务启动中，请稍候使用 /ct 查看"
    fi
}

# 查看任务列表
list_tasks() {
    local chat_id="$1"
    local tasks_dir="$HOME/.cuecue/users/$chat_id/tasks"
    
    if [ ! -d "$tasks_dir" ] || [ -z "$(ls -A "$tasks_dir" 2>/dev/null)" ]; then
        echo "📭 暂无研究任务"
        return
    fi
    
    echo "📊 **研究任务列表**"
    echo ""
    
    # 显示最近的10个任务
    local count=0
    for task_file in $(ls -t "$tasks_dir"/*.json 2>/dev/null | head -10); do
        local task_info
        task_info=$(cat "$task_file")
        
        local task_id
        task_id=$(echo "$task_info" | jq -r '.task_id')
        
        local topic
        topic=$(echo "$task_info" | jq -r '.topic')
        
        local status
        status=$(echo "$task_info" | jq -r '.status')
        
        local status_emoji="🔄"
        [ "$status" = "completed" ] && status_emoji="✅"
        [ "$status" = "failed" ] && status_emoji="❌"
        [ "$status" = "timeout" ] && status_emoji="⏱️"
        
        echo "${status_emoji} ${topic}"
        echo "   ID: ${task_id} | 状态: ${status}"
        echo ""
        
        count=$((count + 1))
    done
    
    if [ $count -eq 0 ]; then
        echo "📭 暂无研究任务"
    fi
}

# 查看监控项列表
list_monitors() {
    local chat_id="$1"
    local monitors_dir="$HOME/.cuecue/users/$chat_id/monitors"
    
    if [ ! -d "$monitors_dir" ] || [ -z "$(ls -A "$monitors_dir" 2>/dev/null)" ]; then
        echo "📭 暂无监控项"
        echo ""
        echo "💡 研究完成后回复 Y 可创建监控项"
        return
    fi
    
    echo "🔔 **监控项列表**"
    echo ""
    
    # 统计信息
    local total=0
    local active=0
    local triggered=0
    
    # 统计监控项数量
    total=$(find "$monitors_dir" -maxdepth 1 -name "*.json" -type f 2>/dev/null | wc -l)
    
    # 显示最近的15个监控项
    for monitor_file in $(ls -t "$monitors_dir"/*.json 2>/dev/null | head -15); do
        local monitor_info
        monitor_info=$(cat "$monitor_file")
        
        local title
        title=$(echo "$monitor_info" | jq -r '.title // "未命名"')
        
        local symbol
        symbol=$(echo "$monitor_info" | jq -r '.symbol // .related_asset_symbol // "-"')
        
        local category
        category=$(echo "$monitor_info" | jq -r '.category // "Data"')
        
        local trigger
        trigger=$(echo "$monitor_info" | jq -r '.semantic_trigger // "-"' | cut -c1-30)
        [ "${#trigger}" -gt 30 ] && trigger="${trigger}..."
        
        local is_active
        is_active=$(echo "$monitor_info" | jq -r '.is_active // true')
        
        local status_emoji="✅"
        [ "$is_active" = "false" ] && status_emoji="⏸️"
        
        local cat_emoji="📊"
        [ "$category" = "Price" ] && cat_emoji="💰"
        [ "$category" = "Event" ] && cat_emoji="📅"
        
        echo "${status_emoji} ${cat_emoji} ${title}"
        [ "$symbol" != "null" ] && [ "$symbol" != "-" ] && echo "   标的: ${symbol}"
        echo "   触发: ${trigger}"
        echo ""
    done
    
    if [ $total -gt 15 ]; then
        echo "... 还有 $((total - 15)) 个监控项"
        echo ""
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "总计: ${total} | 激活: ${active} | 已触发: ${triggered}"
}

# 查看监控通知列表（最近3日）
list_notifications() {
    local chat_id="$1"
    local days="${2:-3}"
    local notif_dir="$HOME/.cuecue/users/$chat_id/notifications"
    
    echo "🔔 **监控触发通知（最近${days}日）**"
    echo ""
    
    # 如果目录不存在
    if [ ! -d "$notif_dir" ]; then
        echo "📭 暂无触发通知"
        echo ""
        echo "💡 当监控条件满足时，会自动发送通知到这里"
        return
    fi
    
    # 计算N天前的时间戳
    local cutoff_ts
    cutoff_ts=$(date -d "${days} days ago" +%s 2>/dev/null || date -v-${days}d +%s 2>/dev/null || echo "0")
    
    # 收集最近的通知
    local notif_count=0
    local notif_files=()
    
    for notif_file in $(ls -t "$notif_dir"/*.json 2>/dev/null); do
        # 从文件名提取时间戳（格式: monitor_id_timestamp.json）
        local filename
        filename=$(basename "$notif_file" .json)
        local file_ts
        file_ts=$(echo "$filename" | grep -oE '[0-9]{10}$' || echo "0")
        
        # 检查是否在时间范围内
        if [ "$file_ts" -ge "$cutoff_ts" ] 2>/dev/null; then
            notif_files+=("$notif_file")
            notif_count=$((notif_count + 1))
        fi
    done
    
    if [ $notif_count -eq 0 ]; then
        echo "📭 最近${days}日暂无触发通知"
        echo ""
        echo "💡 所有监控运行正常，未触发任何条件"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "提示: 使用 /cm 查看监控项列表"
        return
    fi
    
    # 显示通知
    local display_count=0
    for notif_file in "${notif_files[@]}"; do
        if [ $display_count -ge 10 ]; then
            echo "... 还有 $((notif_count - 10)) 条通知"
            break
        fi
        
        local notif_info
        notif_info=$(cat "$notif_file" 2>/dev/null || echo '{}')
        
        local monitor_title
        monitor_title=$(echo "$notif_info" | jq -r '.monitor_title // "未命名监控"')
        
        local triggered_at
        triggered_at=$(echo "$notif_info" | jq -r '.triggered_at // "未知时间"')
        
        local message
        message=$(echo "$notif_info" | jq -r '.message // "监控条件已触发"' | cut -c1-50)
        [ "${#message}" -gt 50 ] && message="${message}..."
        
        local category
        category=$(echo "$notif_info" | jq -r '.category // "Data"')
        
        local cat_emoji="📊"
        [ "$category" = "Price" ] && cat_emoji="💰"
        [ "$category" = "Event" ] && cat_emoji="📅"
        
        echo "${cat_emoji} ${monitor_title}"
        echo "   ⏰ ${triggered_at}"
        echo "   📝 ${message}"
        echo ""
        
        display_count=$((display_count + 1))
    done
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "最近${days}日共 ${notif_count} 条触发通知"
    echo ""
    echo "提示: 使用 /cn 7 查看最近7日通知"
}

# 查看任务详情
show_task_status() {
    local task_id="$1"
    local chat_id="${2:-default}"
    local task_file="$HOME/.cuecue/users/${chat_id}/tasks/${task_id}.json"
    
    if [ ! -f "$task_file" ]; then
        echo "❌ 任务不存在: $task_id"
        return 1
    fi
    
    local task_info
    task_info=$(cat "$task_file")
    
    local topic
    topic=$(echo "$task_info" | jq -r '.topic')
    
    local status
    status=$(echo "$task_info" | jq -r '.status')
    
    local session
    session=$(echo "$task_info" | jq -r '.session // empty')
    
    local report_url=""
    [ -n "$session" ] && report_url="${CUECUE_BASE_URL}/c/${session}"
    
    local created_at
    created_at=$(echo "$task_info" | jq -r '.created_at')
    
    local completed_at
    completed_at=$(echo "$task_info" | jq -r '.completed_at // "未完成"')
    
    cat << EOF
📋 **任务详情**

**主题**：${topic}
**任务ID**：${task_id}
**状态**：${status}
**创建时间**：${created_at}
**完成时间**：${completed_at}

EOF
    
    if [ -n "$report_url" ]; then
        echo "🔗 **报告链接**：${report_url}"
    fi
}

# 处理用户回复 Y/N（创建监控项）
handle_monitor_reply() {
    local chat_id="$1"
    local reply="$2"
    
    if [ "$reply" = "Y" ] || [ "$reply" = "y" ]; then
        echo "🔔 正在为您创建监控项..."
        
        # 检查依赖（首次使用时提示）
        if [ -z "$TAVILY_API_KEY" ]; then
            echo ""
            echo "⚠️  监控功能需要配置 API Key"
            echo ""
            echo "【快速配置】"
            echo "1. 访问 https://tavily.com 注册（免费）"
            echo "2. 获取 API Key"
            echo "3. 执行：echo 'TAVILY_API_KEY=your-key' >> ~/.openclaw/.env"
            echo "4. 重启：openclaw gateway restart"
            echo ""
            echo "配置完成后即可使用监控功能。"
            return 1
        fi
        
        # 查找最新的监控建议文件（优先使用 monitor_suggest_* 格式）
        local latest_monitor
        latest_monitor=$(ls -t /tmp/monitor_suggest_*.json 2>/dev/null | head -1)
        
        # 如果没找到，尝试其他格式
        if [ -z "$latest_monitor" ]; then
            latest_monitor=$(ls -t /tmp/monitor_*.json 2>/dev/null | head -1)
        fi
        
        if [ -n "$latest_monitor" ] && [ -f "$SCRIPT_DIR/create-monitor.sh" ]; then
            echo "   使用监控建议: $(basename "$latest_monitor")"
            
            # 调用 create-monitor.sh 创建监控项
            local result
            result=$("$SCRIPT_DIR/create-monitor.sh" "$latest_monitor" "/tmp/monitor_create_result.json" 2>&1)
            
            if [ -f "/tmp/monitor_create_result.json" ]; then
                local success
                success=$(jq -r '.success // false' "/tmp/monitor_create_result.json" 2>/dev/null)
                local monitor_title
                monitor_title=$(jq -r '.title // "未命名"' "/tmp/monitor_create_result.json" 2>/dev/null)
                
                if [ "$success" = "true" ]; then
                    echo "✅ 成功创建监控项：${monitor_title}"
                    echo "📊 您可以使用 /ct 查看任务和监控状态"
                    
                    # 提示 QVeris 可选配置
                    if [ -z "$QVERIS_API_KEY" ]; then
                        echo ""
                        echo "💡 提示：配置 QVeris API Key 可获得实时股价监控能力"
                        echo "   1. 访问 https://qveris.ai/?ref=OTXNTKI78gS6Gg 注册"
                        echo "   2. 添加环境变量：echo 'QVERIS_API_KEY=your-key' >> ~/.openclaw/.env"
                        echo "   3. 重启：openclaw gateway restart"
                        echo "   （无需安装额外 skill，直接 curl 调用）"
                    fi
                else
                    echo "⚠️ 监控项创建失败"
                    local error_msg
                    error_msg=$(jq -r '.error // "未知错误"' "/tmp/monitor_create_result.json" 2>/dev/null)
                    echo "   原因: ${error_msg}"
                fi
            else
                echo "⚠️ 监控创建无响应，请稍后重试"
            fi
        else
            echo "⚠️ 未找到监控建议文件"
            echo "💡 提示: 请完成一次研究任务，系统会自动生成监控建议"
        fi
        
    elif [ "$reply" = "N" ] || [ "$reply" = "n" ]; then
        echo "✅ 已跳过监控项创建"
        
    else
        # 用户输入了自定义监控需求
        echo "🔔 收到自定义监控需求: $reply"
        echo "💡 功能开发中，请使用标准回复 Y/N，或联系管理员"
    fi
}

# 主函数
main() {
    # 获取 chat_id（从 OpenClaw 环境变量或默认）
    # 优先使用 OPENCLAW_CHAT_ID，其次是 FEISHU_CHAT_ID，最后是 CHAT_ID
    local chat_id="${OPENCLAW_CHAT_ID:-${FEISHU_CHAT_ID:-${CHAT_ID:-default}}}"
    
    # 如果 chat_id 是 default，尝试从当前会话获取
    if [ "$chat_id" = "default" ]; then
        # 尝试从 openclaw 状态获取当前用户
        if command -v openclaw &> /dev/null; then
            local current_user
            current_user=$(openclaw status 2>/dev/null | grep -oE 'user:[^ ]+' | head -1)
            if [ -n "$current_user" ]; then
                chat_id="${current_user#user:}"
            fi
        fi
    fi
    
    log "当前 chat_id: $chat_id"
    
    # 检查用户状态：首次使用 / 版本更新 / 正常使用
    local user_status
    user_status=$(check_version_update "$chat_id")
    
    case "$user_status" in
        "first_time")
            # 首次使用
            show_welcome
            mark_initialized "$chat_id"
            
            # 检查 API Key
            if ! check_and_guide_api_key; then
                return 0
            fi
            
            echo ""
            echo "💡 输入 /ch 可随时查看使用指南"
            echo ""
            ;;
            
        "updated")
            # 版本更新
            local old_version
            old_version=$(cat "$HOME/.cuecue/users/$chat_id/.version" 2>/dev/null || echo "未知版本")
            show_update_notice "$old_version"
            ;;
            
        "normal")
            # 正常使用，不显示额外提示
            ;;
    esac
    
    # ====== 方案2: 自动检测 API Key ======
    # 如果用户直接发送了 API Key（以 tvly- 或 sk- 或 skb 开头）
    local first_arg="$1"
    if [[ "$first_arg" == tvly-* ]] || [[ "$first_arg" == sk-* ]] || [[ "$first_arg" == skb* ]]; then
        # 尝试自动配置
        if auto_configure_key "$first_arg" "$chat_id"; then
            return 0
        fi
    fi
    # ======================================
    
    # 非首次使用，检查 API Key
    if ! check_and_guide_api_key; then
        return 0
    fi
    
    # 解析命令
    local cmd="$1"
    shift || true
    
    case "$cmd" in
        /cue|cue)
            # 解析参数
            local mode=""
            local topic=""
            
            # 检查是否有 --mode 参数
            if [ "$1" = "--mode" ]; then
                mode="$2"
                shift 2
                topic="$*"
            else
                topic="$*"
            fi
            
            # 移除 topic 中的 user:xxx 后缀（如果有）
            topic=$(echo "$topic" | sed 's/ user:[^ ]*$//')
            
            if [ -z "$topic" ]; then
                show_help
            else
                start_research "$topic" "$chat_id" "$mode"
            fi
            ;;
            
        /ct|ct)
            list_tasks "$chat_id"
            ;;
            
        /cm|cm)
            list_monitors "$chat_id"
            ;;
            
        /cn|cn|/notice|notice)
            # 支持 /cn 或 /cn 7 格式
            local days="${1:-3}"
            # 如果参数不是数字，默认使用3
            if ! [[ "$days" =~ ^[0-9]+$ ]]; then
                days=3
            fi
            list_notifications "$chat_id" "$days"
            ;;
            
        /cs|cs)
            if [ -z "$1" ]; then
                echo "❌ 请提供任务ID"
                echo "用法: /cs <任务ID>"
            else
                show_task_status "$1" "$chat_id"
            fi
            ;;
            
        /ch|ch|--help|-h)
            show_help
            ;;
            
        /config|config)
            # 运行配置助手
            if [ -f "$SCRIPT_DIR/config-helper.sh" ]; then
                bash "$SCRIPT_DIR/config-helper.sh"
            else
                echo "📋 手动配置指南："
                echo ""
                echo "1. 编辑 ~/.openclaw/.env 文件："
                echo "   vim ~/.openclaw/.env"
                echo ""
                echo "2. 添加以下内容："
                echo "   TAVILY_API_KEY=your-tavily-key"
                echo "   QVERIS_API_KEY=your-qveris-key"
                echo ""
                echo "3. 获取 API Key："
                echo "   • Tavily: https://tavily.com"
                echo "   • QVeris: https://qveris.ai/?ref=OTXNTKI78gS6Gg"
                echo ""
                echo "4. 重启生效："
                echo "   openclaw gateway restart"
            fi
            ;;
            
        Y|y|N|n)
            # 处理监控项创建回复
            handle_monitor_reply "$chat_id" "$cmd"
            ;;
            
        *)
            # 自然语言输入，尝试智能路由
            if [ -n "$cmd" ]; then
                # 简单关键词判断
                local input="$cmd $*"
                
                # 移除 input 中的 user:xxx 后缀（如果有）
                input=$(echo "$input" | sed 's/ user:[^ ]*$//')
                
                # 如果包含查询类词汇，可能是快速搜索
                if echo "$input" | grep -qiE "^(查询?|查一下?|搜索|什么是|怎么|如何|最新|今天|现在)"; then
                    echo "🔍 检测到快速查询意图..."
                    # 这里可以调用 search 功能
                    echo "💡 建议：使用更明确的研究主题，如："
                    echo "   /cue 宁德时代2024财报分析"
                else
                    # 默认进入深度研究
                    start_research "$input" "$chat_id"
                fi
            else
                show_help
            fi
            ;;
    esac
}

# 确保目录存在
mkdir -p "$HOME/.cuecue/users/$chat_id/tasks"
mkdir -p "$HOME/.cuecue/users"

# 执行
main "$@"
