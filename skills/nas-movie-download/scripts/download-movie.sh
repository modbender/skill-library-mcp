#!/bin/bash

# NAS电影下载脚本 (v3.0 - 集成SMB字幕下载)
# 用途：一键搜索并下载最高清版本的电影，支持通过SMB自动字幕下载

set -e

# 配置
JACKETT_URL="${JACKETT_URL:-http://192.168.1.246:9117}"
JACKETT_API_KEY="${JACKETT_API_KEY:-o5gp976vq8cm084cqkcv30av9v3e5jpy}"
QB_URL="${QB_URL:-http://192.168.1.246:8888}"
QB_USERNAME="${QB_USERNAME:-admin}"
QB_PASSWORD="${QB_PASSWORD:-adminadmin}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# SMB配置
SMB_USERNAME="${SMB_USERNAME:-13917908083}"
SMB_PASSWORD="${SMB_PASSWORD:-Roger0808}"
SMB_SERVER="${SMB_SERVER:-192.168.1.246}"
SMB_SHARE="${SMB_SHARE:-super8083}"
SMB_PATH="${SMB_PATH:-qb/downloads}"

# 字幕配置
SUBTITLE_LANGUAGES="${SUBTITLE_LANGUAGES:-zh,en}"
WITH_SUBTITLE="false"

# 帮助信息
usage() {
    echo "用法: $0 -q <电影名称> [选项]"
    echo ""
    echo "参数："
    echo "  -q, --query          电影名称（必需）"
    echo "  -u, --url            Jackett URL（默认：$JACKETT_URL）"
    echo "  -k, --api-key        Jackett API密钥"
    echo "  -b, --qb-url         qBittorrent URL（默认：$QB_URL）"
    echo "  -n, --qb-user        qBittorrent用户名（默认：$QB_USERNAME）"
    echo "  -p, --qb-pass        qBittorrent密码（默认：$QB_PASSWORD）"
    echo "  -s, --subtitle       下载完成后通过SMB自动下载字幕"
    echo "  -l, --lang           字幕语言（默认：$SUBTITLE_LANGUAGES）"
    echo "  -w, --wait           等待下载完成后再下载字幕"
    echo "  -h, --help           显示帮助信息"
    echo ""
    echo "示例："
    echo "  $0 -q \"死期将至\""
    echo "  $0 -q \"Young Sheldon\" -s -l zh,en"
    echo "  $0 -q \"Inception\" -s -w"
    echo ""
    echo "工作流程："
    echo "  1. Jackett搜索种子"
    echo "  2. 选择最高质量版本"
    echo "  3. 添加到qBittorrent下载"
    echo "  4. 等待下载完成（-w选项）"
    echo "  5. 通过SMB自动下载并上传字幕"
    exit 1
}

# 登录 qBittorrent
qb_login() {
    local qb_url="$1"
    local username="$2"
    local password="$3"
    local cookie_file="$4"
    
    curl -s -X POST "$qb_url/api/v2/auth/login" \
        -d "username=$username&password=$password" \
        -c "$cookie_file" 2>/dev/null | grep -q "Ok"
}

# 获取下载状态
get_torrent_info() {
    local qb_url="$1"
    local cookie_file="$2"
    local torrent_hash="$3"
    
    curl -s "$qb_url/api/v2/torrents/info?hashes=$torrent_hash" \
        -b "$cookie_file" 2>/dev/null
}

# 提取磁力链接的 hash
extract_magnet_hash() {
    local magnet="$1"
    echo "$magnet" | grep -oP 'btih:\K[A-Fa-f0-9]+' | head -1
}

# 等待下载完成
wait_for_completion() {
    local qb_url="$1"
    local username="$2"
    local password="$3"
    local torrent_hash="$4"
    local max_wait_minutes="${5:-60}"
    
    local cookie_file=$(mktemp)
    local max_wait_seconds=$((max_wait_minutes * 60))
    local waited=0
    
    echo ""
    echo "⏳ 等待下载完成（最多 ${max_wait_minutes} 分钟）..."
    
    # 登录
    if ! qb_login "$qb_url" "$username" "$password" "$cookie_file"; then
        echo "❌ 无法登录 qBittorrent"
        rm -f "$cookie_file"
        return 1
    fi
    
    while [[ $waited -lt $max_wait_seconds ]]; do
        local info=$(get_torrent_info "$qb_url" "$cookie_file" "$torrent_hash")
        local progress=$(echo "$info" | jq -r '.[0].progress // 0')
        local state=$(echo "$info" | jq -r '.[0].state // "unknown"')
        
        # 转换为百分比
        local percent=$(echo "$progress * 100" | bc 2>/dev/null | cut -d. -f1)
        [[ -z "$percent" ]] && percent=0
        
        # 显示进度
        printf "\r   进度: %d%% | 状态: %s" "$percent" "$state"
        
        # 检查是否完成
        if [[ "$state" == "uploading" || "$state" == "stalledUP" ]] || [[ "$progress" == "1" ]]; then
            echo ""
            echo "✅ 下载完成！"
            rm -f "$cookie_file"
            return 0
        fi
        
        # 检查是否出错
        if [[ "$state" == "error" || "$state" == "missingFiles" ]]; then
            echo ""
            echo "❌ 下载出错"
            rm -f "$cookie_file"
            return 1
        fi
        
        sleep 10
        waited=$((waited + 10))
    done
    
    echo ""
    echo "⚠️  等待超时，下载仍在进行中"
    rm -f "$cookie_file"
    return 1
}

# 通过SMB下载字幕
download_subtitle_via_smb() {
    local video_name="$1"
    local languages="$2"
    
    echo ""
    echo "📝 通过SMB下载字幕..."
    
    # 使用Python脚本通过SMB下载字幕
    export SMB_USERNAME="$SMB_USERNAME"
    export SMB_PASSWORD="$SMB_PASSWORD"
    export SMB_SERVER_IP="$SMB_SERVER"
    export SMB_SHARE="$SMB_SHARE"
    export SMB_PATH="$SMB_PATH"
    export SUBTITLE_LANGUAGES="$languages"
    
    # 查找视频文件
    python3 "$SCRIPT_DIR/smb-download-subtitle.py" --all
}

# 解析参数
MOVIE_NAME=""
WAIT_COMPLETION="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        -q|--query)
            MOVIE_NAME="$2"
            shift 2
            ;;
        -u|--url)
            JACKETT_URL="$2"
            shift 2
            ;;
        -k|--api-key)
            JACKETT_API_KEY="$2"
            shift 2
            ;;
        -b|--qb-url)
            QB_URL="$2"
            shift 2
            ;;
        -n|--qb-user)
            QB_USERNAME="$2"
            shift 2
            ;;
        -p|--qb-pass)
            QB_PASSWORD="$2"
            shift 2
            ;;
        -s|--subtitle)
            WITH_SUBTITLE="true"
            shift
            ;;
        -l|--lang)
            SUBTITLE_LANGUAGES="$2"
            shift 2
            ;;
        -w|--wait)
            WAIT_COMPLETION="true"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "未知参数: $1"
            usage
            ;;
    esac
done

# 检查必需参数
if [[ -z "$MOVIE_NAME" ]]; then
    echo "错误：缺少电影名称"
    usage
fi

echo "========================================"
echo "🎥 NAS电影下载助手"
echo "========================================"
echo "电影: $MOVIE_NAME"
echo "Jackett: $JACKETT_URL"
echo "qBittorrent: $QB_URL"
[[ "$WITH_SUBTITLE" == "true" ]] && echo "SMB字幕下载: 启用 ($SUBTITLE_LANGUAGES)"
echo ""

# 第一步：搜索种子
echo "🔍 正在搜索种子..."

# 构建搜索URL
JACKETT_URL="${JACKETT_URL%/}"
SEARCH_URL="$JACKETT_URL/api/v2.0/indexers/all/results?apikey=$JACKETT_API_KEY&Query=$(echo "$MOVIE_NAME" | jq -sRr @uri)"

# 发送搜索请求
SEARCH_RESPONSE=$(curl -s "$SEARCH_URL")

# 检查响应
if [[ -z "$SEARCH_RESPONSE" ]]; then
    echo "❌ 搜索失败：未收到响应"
    exit 1
fi

# 检查结果数量
RESULTS_COUNT=$(echo "$SEARCH_RESPONSE" | jq -r '.Results | length')

if [[ "$RESULTS_COUNT" -eq 0 ]]; then
    echo "❌ 未找到任何结果"
    echo "提示：尝试使用英文电影名称搜索"
    exit 1
fi

echo "✅ 找到 $RESULTS_COUNT 个结果"
echo ""

JSON_PART="$SEARCH_RESPONSE"

if [[ -z "$JSON_PART" ]]; then
    echo "❌ 未找到任何种子"
    exit 1
fi

# 解析JSON并选择最高质量种子
echo "📊 正在分析种子质量..."

# 使用jq选择最高质量的种子
BEST_TORRENT=$(echo "$JSON_PART" | jq -r '
    # 定义质量排序函数
    def quality_sort:
        if (.Title | ascii_downcase | test("4k|2160p")) then 4
        elif (.Title | ascii_downcase | test("1080p|fullhd")) then 3
        elif (.Title | ascii_downcase | test("720p|hd")) then 2
        else 1 end;

    # 选择最佳种子
    .Results | sort_by(
        # 主要排序：质量
        quality_sort,
        # 次要排序：种子数
        (.Seeders // 0),
        # 最后排序：文件大小
        (.Size // 0)
    )
    | reverse | .[0]
')

# 检查是否找到有效种子
if [[ "$BEST_TORRENT" == "null" ]]; then
    echo "❌ 无法解析搜索结果"
    exit 1
fi

# 提取信息
TITLE=$(echo "$BEST_TORRENT" | jq -r '.Title')
MAGNET=$(echo "$BEST_TORRENT" | jq -r '.MagnetUri')
SIZE=$(echo "$BEST_TORRENT" | jq -r '.Size')
SEEDERS=$(echo "$BEST_TORRENT" | jq -r '.Seeders')

echo "✅ 找到最佳种子："
echo "   📽️  标题: $TITLE"
echo "   📏 大小: $SIZE"
echo "   🌱 种子数: $SEEDERS"

if [[ -z "$MAGNET" || "$MAGNET" == "null" ]]; then
    echo "❌ 无法获取磁力链接"
    exit 1
fi

echo ""
echo "🎬 正在添加到下载队列..."

# 第二步：添加到qBittorrent
QB_SCRIPT="$(dirname "$0")/qbittorrent-add.sh"
TEMP_QB_SCRIPT=$(mktemp)
sed -e "s|QB_URL=.*|QB_URL=\"$QB_URL\"|" \
    -e "s|QB_USERNAME=.*|QB_USERNAME=\"$QB_USERNAME\"|" \
    -e "s|QB_PASSWORD=.*|QB_PASSWORD=\"$QB_PASSWORD\"|" \
    "$QB_SCRIPT" > "$TEMP_QB_SCRIPT"
chmod +x "$TEMP_QB_SCRIPT"

if ! "$TEMP_QB_SCRIPT" -m "$MAGNET"; then
    echo "❌ 添加到qBittorrent失败"
    rm -f "$TEMP_QB_SCRIPT"
    exit 1
fi

rm -f "$TEMP_QB_SCRIPT"

echo ""
echo "🎉 下载任务已成功添加！"
echo "📁 文件将自动下载到qBittorrent指定的目录"
echo "🔄 你可以在qBittorrent中监控下载进度"

# 提取磁力链接 hash
TORRENT_HASH=$(extract_magnet_hash "$MAGNET")

# 如果启用了字幕下载
if [[ "$WITH_SUBTITLE" == "true" ]]; then
    if [[ -z "$TORRENT_HASH" ]]; then
        echo "⚠️  无法获取 torrent hash，跳过字幕下载"
    elif [[ "$WAIT_COMPLETION" == "true" ]]; then
        echo ""
        echo "📝 字幕下载已启用，等待下载完成..."
        
        if wait_for_completion "$QB_URL" "$QB_USERNAME" "$QB_PASSWORD" "$TORRENT_HASH"; then
            # 等待文件系统稳定
            sleep 5
            
            # 通过SMB下载字幕
            download_subtitle_via_smb "$TITLE" "$SUBTITLE_LANGUAGES"
        else
            echo "⚠️  下载未完成或超时"
            echo "    稍后可通过以下命令手动下载字幕："
            echo "    python3 $SCRIPT_DIR/smb-download-subtitle.py --all"
        fi
    else
        echo ""
        echo "💡 提示：下载完成后可通过以下命令下载字幕："
        echo "    python3 $SCRIPT_DIR/smb-download-subtitle.py --all"
    fi
fi

# 清理临时文件
rm -f /tmp/qb-cookies.txt /temp-script.sh

echo ""
echo "========================================"
echo "✅ 任务完成"
echo "========================================"
exit 0
