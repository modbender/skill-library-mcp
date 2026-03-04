#!/bin/bash

#######################################
# 七牛云 KODO 技能 - 自动安装配置脚本
# 参考：Tencent Cloud COS 技能
#######################################

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 默认值
CHECK_ONLY=false
INSTALL_MCP=false
INSTALL_SDK=false
ACCESS_KEY=""
SECRET_KEY=""
REGION=""
BUCKET=""
DOMAIN=""

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$BASE_DIR/config"
CONFIG_FILE="$CONFIG_DIR/qiniu-config.json"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 解析参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --check-only)
                CHECK_ONLY=true
                shift
                ;;
            --install-mcp)
                INSTALL_MCP=true
                shift
                ;;
            --install-sdk)
                INSTALL_SDK=true
                shift
                ;;
            --access-key)
                ACCESS_KEY="$2"
                shift 2
                ;;
            --secret-key)
                SECRET_KEY="$2"
                shift 2
                ;;
            --region)
                REGION="$2"
                shift 2
                ;;
            --bucket)
                BUCKET="$2"
                shift 2
                ;;
            --domain)
                DOMAIN="$2"
                shift 2
                ;;
            *)
                log_error "未知参数: $1"
                exit 1
                ;;
        esac
    done
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查 Node.js 环境
check_nodejs() {
    log_info "检查 Node.js 环境..."
    
    if command_exists node; then
        NODE_VERSION=$(node --version 2>&1)
        log_info "✅ Node.js 已安装: $NODE_VERSION"
        return 0
    else
        log_error "❌ Node.js 未安装"
        return 1
    fi
}

# 检查 npm
check_npm() {
    log_info "检查 npm..."
    
    if command_exists npm; then
        NPM_VERSION=$(npm --version 2>&1)
        log_info "✅ npm 已安装: $NPM_VERSION"
        return 0
    else
        log_error "❌ npm 未安装"
        return 1
    fi
}

# 检查 qiniu-mcp 是否已安装
check_mcp() {
    log_info "检查 qiniu-mcp..."
    
    if command_exists qiniu-mcp || [ -f "$HOME/.mcporter/servers/qiniu-mcp" ]; then
        log_info "✅ qiniu-mcp 已安装"
        return 0
    else
        log_warn "⚠️  qiniu-mcp 未安装"
        return 1
    fi
}

# 检查 qiniu Node.js SDK
check_sdk() {
    log_info "检查 qiniu Node.js SDK..."
    
    # 检查技能目录下的 node_modules
    if [ -d "$BASE_DIR/node_modules/qiniu" ]; then
        SDK_VERSION=$(node -p "require('$BASE_DIR/node_modules/qiniu/package.json').version" 2>/dev/null || echo "unknown")
        log_info "✅ qiniu Node.js SDK 已安装: $SDK_VERSION"
        return 0
    else
        log_warn "⚠️  qiniu Node.js SDK 未安装"
        return 1
    fi
}

# 检查 qshell 命令行工具
check_qshell() {
    log_info "检查 qshell..."
    
    if command_exists qshell; then
        QSHELL_VERSION=$(qshell version 2>&1 | head -1)
        log_info "✅ qshell 已安装: $QSHELL_VERSION"
        return 0
    else
        log_warn "⚠️  qshell 未安装"
        return 1
    fi
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."
    
    if [ -f "$CONFIG_FILE" ]; then
        log_info "✅ 配置文件已存在: $CONFIG_FILE"
        
        # 验证配置（使用 node 检查 JSON）
        if node -e "require('$CONFIG_FILE')" 2>/dev/null; then
            log_info "✅ 配置文件格式正确"
            return 0
        else
            log_error "❌ 配置文件格式错误"
            return 1
        fi
    else
        log_warn "⚠️  配置文件不存在"
        return 1
    fi
}

# 检查凭证是否已配置
check_credentials() {
    log_info "检查凭证配置..."
    
    if [ -f "$CONFIG_FILE" ]; then
        ACCESS_KEY_CHECK=$(node -p "require('$CONFIG_FILE').accessKey || ''" 2>/dev/null)
        
        if [ -n "$ACCESS_KEY_CHECK" ] && [ "$ACCESS_KEY_CHECK" != "你的AccessKey" ]; then
            log_info "✅ 凭证已配置"
            return 0
        else
            log_warn "⚠️  凭证未配置或使用示例值"
            return 1
        fi
    else
        log_warn "⚠️  配置文件不存在"
        return 1
    fi
}

# 安装 qiniu Node.js SDK
install_sdk() {
    log_info "安装 qiniu Node.js SDK..."
    
    cd "$BASE_DIR"
    
    # 初始化 package.json（如果不存在）
    if [ ! -f "package.json" ]; then
        npm init -y > /dev/null 2>&1
    fi
    
    # 安装 qiniu SDK
    if npm install qiniu --save 2>/dev/null; then
        log_info "✅ qiniu Node.js SDK 安装成功"
        return 0
    else
        log_error "❌ qiniu Node.js SDK 安装失败"
        return 1
    fi
}

# 安装 qiniu-mcp
install_mcp() {
    log_info "安装 qiniu-mcp..."
    
    # 检查 Node.js
    if ! check_nodejs; then
        log_error "需要先安装 Node.js"
        return 1
    fi
    
    # 检查 npm
    if ! check_npm; then
        log_error "需要先安装 npm"
        return 1
    fi
    
    # 安装 mcporter
    if ! command_exists mcporter; then
        log_info "安装 mcporter..."
        npm install -g @openclaw/mcporter
    fi
    
    # 安装 qiniu-mcp-server
    if npm install -g @qiniu/qiniu-mcp-server 2>/dev/null; then
        log_info "✅ qiniu-mcp 安装成功"
        
        # 配置 mcporter
        if [ -d "$HOME/.mcporter" ]; then
            cat > "$HOME/.mcporter/mcporter.json" <<EOF
{
  "servers": {
    "qiniu-mcp": {
      "command": "qiniu-mcp-server",
      "env": {
        "QINIU_ACCESS_KEY": "$ACCESS_KEY",
        "QINIU_SECRET_KEY": "$SECRET_KEY"
      }
    }
  }
}
EOF
            log_info "✅ mcporter 配置已更新"
        fi
        
        return 0
    else
        log_error "❌ qiniu-mcp 安装失败"
        return 1
    fi
}

# 安装 qshell
install_qshell() {
    log_info "安装 qshell..."
    
    local OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    local ARCH=$(uname -m)
    
    if [ "$ARCH" = "x86_64" ]; then
        ARCH="x64"
    elif [ "$ARCH" = "aarch64" ]; then
        ARCH="arm64"
    fi
    
    local QSHELL_URL="https://devtools.qiniu.com/qshell-${OS}-${ARCH}-v2.6.2.zip"
    
    log_info "下载 qshell: $QSHELL_URL"
    
    local TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    if wget -q "$QSHELL_URL" -O qshell.zip && unzip -q qshell.zip && chmod +x qshell; then
        sudo mv qshell /usr/local/bin/ 2>/dev/null || mv qshell "$HOME/.local/bin/"
        log_info "✅ qshell 安装成功"
        cd - > /dev/null
        rm -rf "$TEMP_DIR"
        return 0
    else
        log_error "❌ qshell 安装失败"
        cd - > /dev/null
        rm -rf "$TEMP_DIR"
        return 1
    fi
}

# 创建配置文件
create_config() {
    log_info "创建配置文件..."
    
    mkdir -p "$CONFIG_DIR"
    
    cat > "$CONFIG_FILE" <<EOF
{
  "accessKey": "$ACCESS_KEY",
  "secretKey": "$SECRET_KEY",
  "bucket": "$BUCKET",
  "region": "$REGION",
  "domain": "$DOMAIN",
  "options": {
    "use_https": true,
    "use_cdn": true,
    "timeout": 30,
    "upload_threshold": 4194304,
    "chunk_size": 4194304,
    "retry_times": 3
  }
}
EOF
    
    # 设置权限
    chmod 600 "$CONFIG_FILE"
    
    log_info "✅ 配置文件已创建: $CONFIG_FILE"
}

# 配置 shell 环境
configure_shell() {
    log_info "配置 shell 环境..."
    
    local SHELL_RC=""
    
    if [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
    else
        SHELL_RC="$HOME/.bashrc"
    fi
    
    # 添加环境变量
    if ! grep -q "QINIU_ACCESS_KEY" "$SHELL_RC" 2>/dev/null; then
        cat >> "$SHELL_RC" <<EOF

# 七牛云 KODO 配置
export QINIU_ACCESS_KEY="$ACCESS_KEY"
export QINIU_SECRET_KEY="$SECRET_KEY"
export QINIU_BUCKET="$BUCKET"
export QINIU_REGION="$REGION"
EOF
        log_info "✅ Shell 环境已配置: $SHELL_RC"
    else
        log_info "✅ Shell 环境已存在配置"
    fi
}

# 配置 qshell
configure_qshell() {
    if command_exists qshell; then
        log_info "配置 qshell 账号..."
        
        if qshell account "$ACCESS_KEY" "$SECRET_KEY" "openclaw" 2>/dev/null; then
            log_info "✅ qshell 账号配置成功"
        else
            log_warn "⚠️  qshell 账号配置失败"
        fi
    fi
}

# 验证连接
verify_connection() {
    log_info "验证七牛云连接..."
    
    if node "$SCRIPT_DIR/qiniu_node.mjs" test-connection 2>/dev/null; then
        log_info "✅ 七牛云连接验证成功"
        return 0
    else
        log_error "❌ 七牛云连接验证失败"
        return 1
    fi
}

# 环境检查
check_environment() {
    log_info "=========================================="
    log_info "  七牛云 KODO 环境检查"
    log_info "=========================================="
    echo ""
    
    local ALL_OK=true
    
    check_nodejs || ALL_OK=false
    check_npm || ALL_OK=false
    check_mcp || true     # 可选
    check_sdk || ALL_OK=false
    check_qshell || true  # 可选
    check_config || true
    check_credentials || true
    
    echo ""
    log_info "=========================================="
    
    if $ALL_OK; then
        log_info "✅ 环境检查通过"
        return 0
    else
        log_warn "⚠️  环境检查未完全通过"
        return 1
    fi
}

# 完整安装
full_setup() {
    log_info "=========================================="
    log_info "  七牛云 KODO 自动安装"
    log_info "=========================================="
    echo ""
    
    # 检查必需项
    if ! check_nodejs; then
        log_error "Node.js 是必需的"
        exit 1
    fi
    
    if ! check_npm; then
        log_error "npm 是必需的"
        exit 1
    fi
    
    # 安装 SDK
    if ! check_sdk; then
        install_sdk
    fi
    
    # 安装 MCP（可选）
    if ! check_mcp; then
        log_info "是否安装 qiniu-mcp? [y/N]:"
        read -r INSTALL_MCP_CHOICE
        if [ "$INSTALL_MCP_CHOICE" = "y" ] || [ "$INSTALL_MCP_CHOICE" = "Y" ]; then
            install_mcp
        fi
    fi
    
    # 安装 qshell（可选）
    if ! check_qshell; then
        log_info "是否安装 qshell? [y/N]:"
        read -r INSTALL_QSHELL_CHOICE
        if [ "$INSTALL_QSHELL_CHOICE" = "y" ] || [ "$INSTALL_QSHELL_CHOICE" = "Y" ]; then
            install_qshell
        fi
    fi
    
    # 创建配置
    if [ -n "$ACCESS_KEY" ] && [ -n "$SECRET_KEY" ]; then
        create_config
        configure_shell
        configure_qshell
        verify_connection
    fi
    
    echo ""
    log_info "=========================================="
    log_info "✅ 安装完成！"
    log_info "=========================================="
}

# 主函数
main() {
    parse_args "$@"
    
    if $CHECK_ONLY; then
        check_environment
    elif $INSTALL_MCP; then
        install_mcp
    elif $INSTALL_SDK; then
        install_sdk
    elif [ -n "$ACCESS_KEY" ]; then
        full_setup
    else
        check_environment
        echo ""
        log_info "使用方法："
        log_info "  检查环境: $0 --check-only"
        log_info "  完整安装: $0 --access-key <KEY> --secret-key <KEY> --region <REGION> --bucket <BUCKET>"
        log_info "  安装 SDK: $0 --install-sdk"
        log_info "  安装 MCP: $0 --install-mcp"
    fi
}

main "$@"
