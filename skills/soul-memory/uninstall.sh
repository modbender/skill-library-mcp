#!/bin/bash

###############################################################################
# Soul Memory Uninstall Script v1.0
###############################################################################
# 功能：
#   1. 移除 OpenClaw Plugin 配置
#   2. 禁用 Heartbeat 自動觸發
#   3. 禁用自動記憶注入
#   4. 禁用自動記憶保存
#
# 用法：
#   bash uninstall.sh [--backup] [--confirm]
#   --backup:   創建卸載前備份
#   --confirm:  自動確認所有操作（無需手動確認）
###############################################################################

set -e  # 遇到錯誤立即退出

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 變量
CREATE_BACKUP=false
AUTO_CONFIRM=false
WORKSPACE="${XDG_DATA_HOME:-$HOME/.local/share}/openclaw/workspace"
OPPENCLAW_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/openclaw"
OPPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
HEARTBEAT_FILE="$WORKSPACE/HEARTBEAT.md"
BACKUP_DIR="$WORKSPACE/soul-memory-backup/$(date +%Y%m%d-%H%M%S)"

# 顯示幫助信息
show_help() {
    cat << EOF
${BLUE}Soul Memory Uninstall Script v1.0${NC}

${YELLOW}用法：${NC}
  bash uninstall.sh [選項]

${YELLOW}選項：${NC}
  --backup    創建卸載前的配置備份
  --confirm   自動確認所有操作（無需手動確認）
  -h, --help  顯示幫助信息

${YELLOW}卸載項目：${NC}
  1. 移除 OpenClaw Plugin 配置（openclaw.json）
  2. 禁用 Heartbeat 自動觸發（HEARTBEAT.md）
  3. 禁用自動記憶注入（Plugin）
  4. 禁用自動記憶保存（post-response）

${YELLOW}示例：${NC}
  bash uninstall.sh --backup --confirm

EOF
}

# 解析命令行參數
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backup)
                CREATE_BACKUP=true
                shift
                ;;
            --confirm)
                AUTO_CONFIRM=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo -e "${RED}錯誤：未知選項 $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
}

# 顯示信息
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 創建備份
create_backup() {
    log_info "創建配置備份..."

    mkdir -p "$BACKUP_DIR"

    # 備份 openclaw.json
    if [ -f "$OPPENCLAW_CONFIG" ]; then
        cp "$OPPENCLAW_CONFIG" "$BACKUP_DIR/openclaw.json.backup"
        log_success "已備份 openclaw.json"
    fi

    # 備份 HEARTBEAT.md
    if [ -f "$HEARTBEAT_FILE" ]; then
        cp "$HEARTBEAT_FILE" "$BACKUP_DIR/HEARTBEAT.md.backup"
        log_success "已備份 HEARTBEAT.md"
    fi

    # 記錄備份位置
    echo "Backup created at: $BACKUP_DIR" > "$BACKUP_DIR/README.txt"
    echo "Date: $(date)" >> "$BACKUP_DIR/README.txt"

    log_success "備份完成：$BACKUP_DIR"
}

# 檢查配置是否存在
check_config() {
    local config_exists=false

    if [ -f "$OPPENCLAW_CONFIG" ]; then
        if grep -q "soul-memory" "$OPPENCLAW_CONFIG" 2>/dev/null; then
            config_exists=true
        fi
    fi

    if [ -f "$HEARTBEAT_FILE" ]; then
        if grep -q "soul-memory" "$HEARTBEAT_FILE" 2>/dev/null || \
           grep -q "heartbeat-trigger" "$HEARTBEAT_FILE" 2>/dev/null; then
            config_exists=true
        fi
    fi

    if [ "$config_exists" = false ]; then
        log_warning "未找到 Soul Memory 配置，無需卸載"
        exit 0
    fi
}

# 移除 Plugin 配置
remove_plugin_config() {
    log_info "移除 OpenClaw Plugin 配置..."

    if [ ! -f "$OPPENCLAW_CONFIG" ]; then
        log_warning "openclaw.json 不存在，跳過"
        return
    fi

    # 創建臨時文件
    local temp_file=$(mktemp)

    # 移除 soul-memory plugin 配置
    if grep -q "soul-memory" "$OPPENCLAW_CONFIG"; then
        # 使用 jq 移除 plugin 配置（如果可用）
        if command -v jq &> /dev/null; then
            jq 'del(.plugins.entries["soul-memory"])' "$OPPENCLAW_CONFIG" > "$temp_file"
            mv "$temp_file" "$OPPENCLAW_CONFIG"
            log_success "已移除 Plugin 配置（使用 jq）"
        else
            # 備用方案：使用 sed
            sed -i '/soul-memory/,/}/d' "$OPPENCLAW_CONFIG"
            log_success "已移除 Plugin 配置（使用 sed）"
        fi
    else
        log_warning "未找到 Plugin 配置"
    fi
}

# 禁用 Heartbeat 自動觸發
disable_heartbeat_trigger() {
    log_info "禁用 Heartbeat 自動觸發..."

    if [ ! -f "$HEARTBEAT_FILE" ]; then
        log_warning "HEARTBEAT.md 不存在，跳過"
        return
    fi

    # 備份原文
    cp "$HEARTBEAT_FILE" "$HEARTBEAT_FILE.uninstall-backup"

    # 移除或註釋 heartbeat-trigger 相關代碼
    if grep -q "heartbeat-trigger" "$HEARTBEAT_FILE"; then
        sed -i '/python3.*heartbeat-trigger.py/d' "$HEARTBEAT_FILE"
        sed -i '/soul-memory\/heartbeat-trigger.py/d' "$HEARTBEAT_FILE"
        log_success "已移除 Heartbeat 觸發命令"
    else
        log_warning "未找到 Heartbeat 觸發配置"
    fi
}

# 禁用自動記憶注入（通過禁用 Plugin）
disable_auto_inject() {
    log_info "禁用自動記憶注入..."

    # Plugin 已在 remove_plugin_config 中移除
    # 此處僅確認並記錄
    log_success "Plugin 配置已移除，自動記憶注入已禁用"
}

# 禁用自動記憶保存
disable_auto_save() {
    log_info "禁用自動記憶保存..."

    if [ ! -f "$HEARTBEAT_FILE" ]; then
        log_warning "HEARTBEAT.md 不存在，跳過"
        return
    fi

    # 移除 Post-Response Auto-Save 相關代碼
    if grep -q "SoulMemorySystem" "$HEARTBEAT_FILE"; then
        sed -i '/from soul_memory.core import SoulMemorySystem/,/print("✅ 自動儲存/d' "$HEARTBEAT_FILE"
        log_success "已移除自動記憶保存代碼"
    else
        log_warning "未找到自動記憶保存配置"
    fi
}

# 顯示卸載摘要
show_summary() {
    echo ""
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}  Soul Memory 卸載完成${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo ""
    echo "已移除項目："
    echo "  1. OpenClaw Plugin 配置"
    echo "  2. Heartbeat 自動觸發"
    echo "  3. 自動記憶注入"
    echo "  4. 自動記憶保存"
    echo ""

    if [ "$CREATE_BACKUP" = true ]; then
        echo "備份位置：$BACKUP_DIR"
        echo ""
    fi

    echo "建議操作："
    echo "  - 重啟 OpenClaw Gateway: openclaw gateway restart"
    echo "  - 如需恢復配置，請查看備份文件"
    echo ""
}

# 確認操作
confirm_operation() {
    if [ "$AUTO_CONFIRM" = true ]; then
        return 0
    fi

    echo ""
    log_warning "即將卸載 Soul Memory，將移除以下配置："
    echo "  1. OpenClaw Plugin 配置（openclaw.json）"
    echo "  2. Heartbeat 自動觸發（HEARTBEAT.md）"
    echo "  3. 自動記憶注入"
    echo "  4. 自動記憶保存"
    echo ""
    read -p "確認卸載？(yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        log_info "卸載已取消"
        exit 0
    fi
}

# 主函數
main() {
    # 解析參數
    parse_args "$@"

    # 檢查配置
    check_config

    # 創建備份
    if [ "$CREATE_BACKUP" = true ]; then
        create_backup
    fi

    # 確認操作
    confirm_operation

    # 執行卸載
    remove_plugin_config
    disable_heartbeat_trigger
    disable_auto_inject
    disable_auto_save

    # 顯示摘要
    show_summary
}

# 執行主函數
main "$@"
