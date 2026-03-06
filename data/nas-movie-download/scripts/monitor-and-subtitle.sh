#!/bin/bash

# 监控 qBittorrent 下载完成并自动下载字幕
# 用途：后台监控指定 torrent，完成后自动调用字幕下载

TORRENT_HASH="$1"
TORRENT_NAME="$2"
QB_URL="${QB_URL:-http://192.168.1.246:8888}"
QB_USERNAME="${QB_USERNAME:-admin}"
QB_PASSWORD="${QB_PASSWORD:-adminadmin}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 登录 qBittorrent
qb_login() {
    local cookie_file="$1"
    curl -s -X POST "$QB_URL/api/v2/auth/login" \
        -d "username=$QB_USERNAME&password=$QB_PASSWORD" \
        -c "$cookie_file" 2>/dev/null | grep -q "Ok"
}

# 获取 torrent 信息
get_torrent_info() {
    local cookie_file="$1"
    local hash="$2"
    curl -s "$QB_URL/api/v2/torrents/info?hashes=$hash" \
        -b "$cookie_file" 2>/dev/null
}

# 主监控循环
monitor_and_download_subtitles() {
    local hash="$1"
    local name="$2"
    local cookie_file=$(mktemp)
    local check_interval=300  # 每5分钟检查一次
    local max_wait=86400      # 最多等24小时
    local waited=0
    
    echo "⏰ 开始监控: $name"
    echo "   检查间隔: ${check_interval}秒"
    echo ""
    
    while [[ $waited -lt $max_wait ]]; do
        if ! qb_login "$cookie_file"; then
            echo "❌ 无法登录 qBittorrent"
            rm -f "$cookie_file"
            return 1
        fi
        
        local info=$(get_torrent_info "$cookie_file" "$hash")
        local state=$(echo "$info" | jq -r '.[0].state // "unknown"')
        local progress=$(echo "$info" | jq -r '.[0].progress // 0')
        local content_path=$(echo "$info" | jq -r '.[0].content_path // empty')
        
        local percent=$(echo "$progress * 100" | bc 2>/dev/null | cut -d. -f1)
        [[ -z "$percent" ]] && percent=0
        
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$timestamp] 进度: $percent% | 状态: $state"
        
        # 检查是否完成
        if [[ "$state" == "uploading" || "$state" == "stalledUP" || "$progress" == "1" ]]; then
            echo ""
            echo "✅ 下载完成！"
            echo "   文件路径: $content_path"
            echo ""
            
            # 生成字幕下载命令
            echo "=== 字幕下载命令 ==="
            echo ""
            echo "请在 NAS (192.168.1.246) 上执行以下命令："
            echo ""
            echo "1. 安装 subliminal（如未安装）："
            echo "   pip3 install --user subliminal"
            echo ""
            echo "2. 下载中英双语字幕："
            echo "   subliminal download -l zho -l eng \"$content_path\""
            echo ""
            echo "或批量处理整个文件夹："
            echo "   subliminal download -l zho -l eng \"$(dirname "$content_path")\""
            echo ""
            
            # 发送通知（如果配置了）
            if command -v notify-send >/dev/null 2>&1; then
                notify-send "下载完成" "$name 已下载完成，请执行字幕下载命令"
            fi
            
            rm -f "$cookie_file"
            return 0
        fi
        
        # 检查是否出错
        if [[ "$state" == "error" || "$state" == "missingFiles" ]]; then
            echo "❌ 下载出错"
            rm -f "$cookie_file"
            return 1
        fi
        
        sleep $check_interval
        waited=$((waited + check_interval))
    done
    
    echo "⚠️  监控超时"
    rm -f "$cookie_file"
    return 1
}

# 如果直接运行此脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ -z "$1" ]]; then
        echo "用法: $0 <torrent_hash> [torrent_name]"
        echo ""
        echo "示例:"
        echo "  $0 124c710925a8d383564483d46f701b260eb19a93 \"Lilo Stitch 2025\""
        exit 1
    fi
    
    monitor_and_download_subtitles "$1" "$2"
fi
