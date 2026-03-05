#!/bin/bash
# xhs-cover.sh - 小红书封面生成脚本
# 配合 mcporter 调用 @emit/xhs-cover-mcp-server

set -e

# 默认配置
API_URL="${XHS_COVER_API_URL:-https://api.xhscover.cn}"
API_KEY="${XHS_COVER_API_KEY:-}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

error() {
  echo -e "${RED}错误: $1${NC}" >&2
  exit 1
}

success() {
  echo -e "${GREEN}$1${NC}"
}

info() {
  echo -e "$1"
}

check_config() {
  if [ -z "$API_KEY" ]; then
    error "请设置 XHS_COVER_API_KEY 环境变量\n  export XHS_COVER_API_KEY=\"xhs_your_api_key\"\n  在 https://xhscover.cn/dashboard 获取"
  fi
}

# 生成封面
generate_cover() {
  local text="$1"
  local ratio="${2:-3:4}"
  
  if [ -z "$text" ]; then
    error "请提供封面文案\n  用法: $0 generate <文案> [宽高比]"
  fi
  
  check_config
  
  info "生成封面: ${YELLOW}${text}${NC}"
  info "宽高比: ${ratio}"
  info "..."
  
  local result
  result=$(mcporter call @emit/xhs-cover-mcp-server.generate_cover \
    text="$text" \
    aspectRatio="$ratio" \
    XHS_COVER_API_URL="$API_URL" \
    XHS_COVER_API_KEY="$API_KEY" \
    --output json 2>&1)
  
  if echo "$result" | jq -e '.success == true' > /dev/null 2>&1; then
    local url=$(echo "$result" | jq -r '.resultUrl')
    local cost=$(echo "$result" | jq -r '.creditCost')
    success "✓ 生成成功!"
    info "图片链接: ${url}"
    info "消耗 credits: ${cost}"
  else
    local err=$(echo "$result" | jq -r '.error // .message // "未知错误"' 2>/dev/null || echo "$result")
    error "生成失败: ${err}"
  fi
}

# 查询余额
get_balance() {
  check_config
  
  info "查询余额..."
  
  local result
  result=$(mcporter call @emit/xhs-cover-mcp-server.get_credits \
    XHS_COVER_API_URL="$API_URL" \
    XHS_COVER_API_KEY="$API_KEY" \
    --output json 2>&1)
  
  if echo "$result" | jq -e '.balance' > /dev/null 2>&1; then
    local balance=$(echo "$result" | jq -r '.balance')
    local used=$(echo "$result" | jq -r '.totalUsed')
    success "✓ 余额: ${balance} credits"
    info "已使用: ${used} credits"
    info "可生成: $((balance / 10)) 张封面"
  else
    local err=$(echo "$result" | jq -r '.error // .message // "未知错误"' 2>/dev/null || echo "$result")
    error "查询失败: ${err}"
  fi
}

# 获取历史
get_history() {
  local limit="${1:-10}"
  
  check_config
  
  info "获取最近 ${limit} 条记录..."
  
  mcporter call @emit/xhs-cover-mcp-server.get_history \
    limit="$limit" \
    XHS_COVER_API_URL="$API_URL" \
    XHS_COVER_API_KEY="$API_KEY" \
    --output json 2>&1 | jq '.tasks[] | {prompt, status, resultUrl, createdAt}'
}

# 显示帮助
show_help() {
  cat << EOF
小红书封面生成器

用法:
  $0 generate <文案> [宽高比]   生成封面
  $0 balance                    查询余额
  $0 history [数量]             获取历史记录
  $0 help                       显示帮助

环境变量:
  XHS_COVER_API_URL   API 地址 (默认: https://api.xhscover.cn)
  XHS_COVER_API_KEY   API 密钥 (在 xhscover.cn/dashboard 获取)

宽高比:
  3:4   小红书标准竖版 (默认)
  9:16  超长竖版
  1:1   正方形
  16:9  横版

示例:
  $0 generate "5个习惯让你越来越自律"
  $0 generate "今日份好心情" 1:1
  $0 balance
  $0 history 20

EOF
}

# 主入口
case "${1:-}" in
  generate)
    generate_cover "$2" "$3"
    ;;
  balance|credits)
    get_balance
    ;;
  history)
    get_history "${2:-10}"
    ;;
  help|--help|-h)
    show_help
    ;;
  *)
    if [ -n "$1" ]; then
      # 如果只提供一个参数，当作文案处理
      generate_cover "$1" "$2"
    else
      show_help
    fi
    ;;
esac
