#!/bin/bash
# V2Ray 代理管理脚本
# 功能：开关代理、配置系统代理、自动代理

set -e

# 配置
V2RAY_DIR="/media/felix/d/v2rayN-linux-64"
V2RAY_BIN="$V2RAY_DIR/bin/xray/xray"
CONFIG_FILE="$V2RAY_DIR/config.json"
PROXY_PORT="10808"
PROXY_URL="http://127.0.0.1:$PROXY_PORT"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查v2ray是否运行
is_running() {
    pgrep -f "xray.*config" > /dev/null 2>&1
}

# 启动v2ray
start_v2ray() {
    if is_running; then
        log_info "V2Ray 已经在运行"
        return 0
    fi
    
    log_info "启动 V2Ray..."
    cd "$V2RAY_DIR"
    nohup ./v2rayN > /dev/null 2>&1 &
    sleep 2
    
    if is_running; then
        log_info "V2Ray 已启动 (PID: $(pgrep -f 'xray.*config'))"
        return 0
    else
        log_error "V2Ray 启动失败"
        return 1
    fi
}

# 停止v2ray
stop_v2ray() {
    # 停止前先清除系统代理，确保网络正常
    disable_system_proxy
    
    if ! is_running; then
        log_info "V2Ray 没有运行"
        return 0
    fi
    
    log_info "停止 V2Ray..."
    pkill -f "xray.*config" || true
    pkill -f "v2rayN" || true
    sleep 1
    
    if ! is_running; then
        log_info "V2Ray 已停止"
        return 0
    else
        log_error "停止失败"
        return 1
    fi
}

# 设置系统代理（自动配置系统代理）
enable_system_proxy() {
    log_info "开启系统代理..."
    
    # 设置HTTP/HTTPS代理
    export http_proxy="$PROXY_URL"
    export https_proxy="$PROXY_URL"
    export HTTP_PROXY="$PROXY_URL"
    export HTTPS_PROXY="$PROXY_URL"
    
    # 设置no_proxy（跳过本地地址）
    export no_proxy="localhost,127.0.0.1,::1,*.local"
    export NO_PROXY="$no_proxy"
    
    log_info "系统代理已开启: http_proxy=$PROXY_URL"
    
    # 持久化到bashrc（可选）
    if ! grep -q "V2RAY_PROXY" ~/.bashrc 2>/dev/null; then
        echo "" >> ~/.bashrc
        echo "# V2Ray Proxy (managed by OpenClaw)" >> ~/.bashrc
        echo "export V2RAY_PROXY=1" >> ~/.bashrc
    fi
}

# 清除系统代理
disable_system_proxy() {
    log_info "清除系统代理..."
    
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
    unset no_proxy NO_PROXY
    
    log_info "系统代理已清除"
}

# 测试代理连接
test_proxy() {
    log_info "测试代理连接..."
    
    # 测试直连
    local direct_result=$(curl -s --connect-timeout 5 -o /dev/null -w "%{http_code}" https://www.google.com 2>/dev/null || echo "000")
    
    # 测试代理
    local proxy_result=$(curl -s --connect-timeout 5 -o /dev/null -w "%{http_code}" --proxy "$PROXY_URL" https://www.google.com 2>/dev/null || echo "000")
    
    echo "直连: $direct_result"
    echo "代理: $proxy_result"
    
    if [ "$proxy_result" = "200" ]; then
        log_info "代理连接正常"
        return 0
    else
        log_warn "代理连接异常"
        return 1
    fi
}

# 确保代理开启（如果需要）
ensure_proxy() {
    if is_running && [ -n "$http_proxy" ]; then
        log_info "代理已在运行"
        return 0
    fi
    
    if ! check_network; then
        log_info "外网不可用，开启代理..."
        proxy_on
        return 1
    else
        return 0
    fi
}

# 检查网络是否需要代理（检测常见外网服务）
check_network() {
    # 需要代理的网站列表（按优先级排序）
    local sites=(
        "github.com"
        "google.com"
    )
    
    for site in "${sites[@]}"; do
        if curl -s --connect-timeout 2 -o /dev/null "https://$site" 2>/dev/null; then
            echo "$site: 可访问"
            return 0
        fi
    done
    
    echo "外网不可访问，需要代理"
    return 1
}

# 自动代理工作流

proxy_on() {
    start_v2ray
    sleep 2
    enable_system_proxy
    test_proxy
}

# 完整关闭代理（停止v2ray + 清除系统代理）
proxy_off() {
    disable_system_proxy
    stop_v2ray
}

# 自动代理模式（根据网络状况自动开关）
auto_proxy() {
    if check_network; then
        log_info "网络正常，无需代理"
        proxy_off
    else
        log_info "网络受限，开启代理"
        proxy_on
    fi
}

# 确保代理开启（如果需要）
ensure_proxy() {
    if is_running && [ -n "$http_proxy" ]; then
        log_info "代理已在运行"
        return 0
    fi
    
    if ! check_network; then
        log_info "外网不可用，开启代理..."
        proxy_on
        return 1
    fi
    
    return 0
}

# 自动代理包裹命令（执行命令前后自动开关代理）
wrap() {
    local cmd="$*"
    
    log_info "执行命令: $cmd"
    
    # 检查是否需要代理
    if check_network; then
        log_info "网络正常，直接执行..."
        eval "$cmd"
        return $?
    fi
    
    # 需要代理，开启后执行
    log_info "开启代理后执行..."
    proxy_on
    
    local result=0
    eval "$cmd" || result=$?
    
    log_info "命令执行完成，关闭代理..."
    proxy_off
    
    return $result
}

# 查看状态
status() {
    echo "=== V2Ray 代理状态 ==="
    
    if is_running; then
        echo "V2Ray: ${GREEN}运行中${NC}"
    else
        echo "V2Ray: ${RED}未运行${NC}"
    fi
    
    echo "代理端口: $PROXY_PORT"
    echo "代理地址: $PROXY_URL"
    echo ""
    echo "系统代理环境变量:"
    echo "  http_proxy: ${http_proxy:-未设置}"
    echo "  https_proxy: ${https_proxy:-未设置}"
    echo ""
    test_proxy
}

# 帮助
show_help() {
    echo "V2Ray 代理管理脚本"
    echo ""
    echo "用法: $0 <command>"
    echo ""
    echo "命令:"
    echo "  start          启动 V2Ray（不开系统代理）"
    echo "  stop           停止 V2Ray"
    echo "  on             完整开启（启动 + 系统代理）"
    echo "  off            完整关闭（清除代理 + 停止）"
    echo "  status         查看状态"
    echo "  test           测试代理连接"
    echo "  auto           自动模式（根据网络状况自动开关）"
    echo "  ensure         确保代理开启（如需要）"
    echo "  enable-sys     仅开启系统代理"
    echo "  disable-sys    仅清除系统代理"
    echo "  check          检查网络是否需要代理"
    echo "  wrap <cmd>     自动代理包裹命令（自动开关）"
    echo ""
    echo "示例:"
    echo "  $0 on          # 开启代理"
    echo "  $0 off         # 关闭代理"
    echo "  $0 auto        # 自动模式"
    echo "  $0 wrap curl https://github.com  # 自动代理访问GitHub"
}

# 主函数
case "${1:-status}" in
    start) start_v2ray ;;
    stop) stop_v2ray ;;
    on) proxy_on ;;
    off) proxy_off ;;
    status) status ;;
    test) test_proxy ;;
    auto) auto_proxy ;;
    ensure) ensure_proxy ;;
    enable-sys) enable_system_proxy ;;
    disable-sys) disable_system_proxy ;;
    check) check_network ;;
    wrap) shift; wrap "$@" ;;
    *) show_help ;;
esac
