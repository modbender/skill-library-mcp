#!/bin/bash
# doubao.sh - Doubao API Shell 脚本实现
# 文生图、文生视频、图片编辑、任务状态查询
#
# 使用前请设置环境变量：
#   export ARK_API_KEY="<your_api_key>"
#
# 命令：
#   img   <prompt>                  文生图
#   edit  <image_url> [prompt]      图片编辑（去除水印）
#   vid   <prompt> [sync|async]    文生视频（默认异步）
#   vid   <prompt> <image_url> [sync]  文生视频（带参考图）
#   status <task_id>               查询任务状态
#

set -euo pipefail

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${SCRIPT_DIR}/../data"

# 确保 data 目录存在
mkdir -p "${DATA_DIR}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查环境变量
if [ -z "${ARK_API_KEY:-}" ]; then
    echo -e "${RED}错误${NC}: ARK_API_KEY 环境变量未设置"
    echo "请执行: export ARK_API_KEY=\"your_api_key\""
    exit 1
fi

# API 端点
BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
IMAGE_ENDPOINT="${BASE_URL}/images/generations"
VIDEO_ENDPOINT="${BASE_URL}/contents/generations/tasks"
TASK_ENDPOINT="${BASE_URL}/contents/generations/tasks"

# 辅助函数：打印 JSON（如果安装了 jq 则格式化输出）
print_json() {
    if command -v jq &> /dev/null; then
        jq '.' <<< "$1" 2>/dev/null || echo "$1"
    else
        echo "$1"
    fi
}

# 辅助函数：生成时间戳文件名
generate_filename() {
    local prefix="$1"
    local ext="$2"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    echo "${prefix}_${timestamp}.${ext}"
}

# 辅助函数：下载文件
download_file() {
    local url="$1"
    local filename="$2"
    local filepath="${DATA_DIR}/${filename}"
    
    echo -e "${GREEN}↓ 下载文件${NC}: ${filename}"
    
    if curl -s -o "${filepath}" "${url}"; then
        local size=$(du -h "${filepath}" | cut -f1)
        echo -e "${GREEN}✅ 下载成功${NC}: ${filepath} (${size})"
        
        # 返回本地路径
        print_json "{\"status\":\"success\",\"local_path\":\"${filepath}\",\"filename\":\"${filename}\"}"
        return 0
    else
        echo -e "${RED}❌ 下载失败${NC}: ${url}"
        print_json "{\"status\":\"error\",\"error\":\"Download failed\"}"
        return 1
    fi
}

# 函数：文生图
generate_image() {
    local prompt="$1"
    
    echo -e "${YELLOW}📸 生成图片...${NC}"
    echo "提示词: ${prompt}"
    
    # 构造请求
    local payload=$(cat <<EOF
{
  "model": "doubao-seedream-3-0-t2i-250415",
  "prompt": "${prompt}",
  "n": 1
}
EOF
)
    
    # 调用 API
    local response=$(curl -s --show-error --fail "${IMAGE_ENDPOINT}" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${ARK_API_KEY}" \
        -d "$payload")
    
    echo "Respose: $response"
    # 检查响应
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ API 调用失败${NC}"
        print_json "{\"status\":\"error\",\"error\":\"API call failed\"}"
        return 1
    fi
    
    # 解析响应
    local image_url=$(echo "$response" | jq -r '.data[0].url' 2>/dev/null)
    
    if [ -z "$image_url" ]; then
        echo -e "${RED}❌ 解析失败${NC}"
        print_json "{\"status\":\"error\",\"error\":\"Failed to parse image URL\"}"
        return 1
    fi
    
    # 生成文件名
    local filename=$(generate_filename "img" "jpeg")
    
    # 下载文件
    download_file "$image_url" "$filename"
}

# 函数：图片编辑
edit_image() {
    local image_url="$1"
    local prompt="${2:-remove watermark, keep main content}"
    
    echo -e "${YELLOW}🎨 编辑图片...${NC}"
    echo "图片 URL: ${image_url}"
    echo "提示词: ${prompt}"
    
    # 构造请求
    local payload=$(cat <<EOF
{
  "model": "doubao-seedream-4-0-250828",
  "image": "${image_url}",
  "prompt": "${prompt}",
  "n": 1,
  "strength": 0.3
}
EOF
)
    
    # 调用 API
    local response=$(curl -s --show-error --fail "${IMAGE_ENDPOINT}" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${ARK_API_KEY}" \
        -d "$payload")
    
    echo "Respose: $response"

    # 检查响应
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ API 调用失败${NC}"
        print_json "{\"status\":\"error\",\"error\":\"API call failed\"}"
        return 1
    fi
    
    # 解析响应
    local edited_url=$(echo "$response" | jq -r '.data[0].url' 2>/dev/null)
    
    if [ -z "$edited_url" ]; then
        echo -e "${RED}❌ 解析失败${NC}"
        print_json "{\"status\":\"error\",\"error\":\"Failed to parse edited image URL\"}"
        return 1
    fi
    
    # 生成文件名
    local filename=$(generate_filename "edit" "jpeg")
    
    # 下载文件
    download_file "$edited_url" "$filename"
}

# 函数：文生视频
generate_video() {
    local prompt="$1"
    local image_url="${2:-}"
    local sync_mode="${3:-sync}"
    
    echo -e "${YELLOW}🎬 生成视频...${NC}"
    echo "提示词: ${prompt}"
    [ -n "$image_url" ] && echo "参考图: ${image_url}"
    echo "模式: ${sync_mode}"
    
    # 构造 payload
    local payload
    
    if [ -n "$image_url" ]; then
        # 带参考图
        payload=$(cat <<EOF
{
  "model": "doubao-seedance-1-0-pro-fast-251015",
  "content": [
    {"type": "text", "text": "${prompt}"},
    {"type": "image_url", "image_url": {"url": "${image_url}"}}
  ],
  "resolution": "720p",
  "ratio":"16:9",
  "duration": 5,
  "seed": 11,
  "camera_fixed": false,
  "watermark": true
}
EOF
)
    else
        # 不带参考图
        payload=$(cat <<EOF
{
  "model": "doubao-seedance-1-0-pro-fast-251015",
  "content": [
    {"type": "text", "text": "${prompt}"}
  ],
  "resolution": "720p",
  "ratio":"16:9",
  "duration": 5,
  "seed": 11,
  "camera_fixed": false,
  "watermark": true
}
EOF
)
    fi
    
    # 调用 API
    local response=$(curl -s --show-error --fail "${VIDEO_ENDPOINT}" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${ARK_API_KEY}" \
        -d "$payload")
    
    # 检查响应
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ API 调用失败${NC}"
        print_json "{\"status\":\"error\",\"error\":\"API call failed\"}"
        return 1
    fi
    
    # 解析响应
    echo "Respose: $response"
    local task_id=$(echo "$response" | jq -r '.id' 2>/dev/null)
    
    if [ -z "$task_id" ]; then
        echo -e "${RED}❌ 解析失败${NC}"
        print_json "{\"status\":\"error\",\"error\":\"Failed to parse task ID\"}"
        return 1
    fi
    
    if [ "$sync_mode" = "sync" ]; then
        # 同步模式：等待完成
        wait_for_completion "$task_id" "$prompt"
    else
        # 异步模式：立即返回 task_id
        print_json "{\"status\":\"success\",\"task_id\":\"${task_id}\",\"prompt\":\"${prompt}\",\"action\":\"vid\",\"mode\":\"async\"}"
    fi
}

# 函数：等待任务完成
wait_for_completion() {
    local task_id="$1"
    local prompt="$2"
    
    echo -e "${YELLOW}⏳ 等待任务完成${NC}: ${task_id}"
    
    local max_attempts=30  # 最多等待 5 分钟
    local count=0
    
    while [ $count -lt $max_attempts ]; do
        sleep 10
        
        local status=$(check_task_status "$task_id")
        local state=$(echo "$status" | jq -r '.status' 2>/dev/null)
        
        echo -e "  [$((count+1))/${max_attempts}] 状态: ${state}"
        
        if [ "$state" = "succeeded" ]; then
            echo -e "${GREEN}✅ 任务完成${NC}"
            
            # 解析视频 URL
            local video_url=$(echo "$status" | jq -r '.content.video_url' 2>/dev/null)
            
            if [ -n "$video_url" ]; then
                # 生成文件名
                local filename=$(generate_filename "vid" "mp4")
                
                # 尝试下载视频（可能会失败）
                if ! download_file "$video_url" "$filename"; then
                    echo -e "${YELLOW}⚠️  视频下载失败（可能是访问限制）${NC}"
                    print_json "{\"status\":\"success\",\"video_url\":\"${video_url}\",\"task_id\":\"${task_id}\",\"prompt\":\"${prompt}\",\"action\":\"vid\",\"mode\":\"sync\",\"download_warning\":true}"
                else
                    print_json "{\"status\":\"success\",\"local_path\":\"${DATA_DIR}/${filename}\",\"video_url\":\"${video_url}\",\"task_id\":\"${task_id}\",\"prompt\":\"${prompt}\",\"action\":\"vid\",\"mode\":\"sync\"}"
                fi
            else
                print_json "{\"status\":\"succeeded\",\"task_id\":\"${task_id}\",\"prompt\":\"${prompt}\",\"action\":\"vid\",\"mode\":\"sync\"}"
            fi
            return 0
        elif [ "$state" = "failed" ]; then
            echo -e "${RED}❌ 任务失败${NC}"
            local error=$(echo "$status" | jq -r '.error' 2>/dev/null)
            print_json "{\"status\":\"error\",\"error\":\"${error}\",\"task_id\":\"${task_id}\",\"prompt\":\"${prompt}\"}"
            return 1
        fi
        
        count=$((count+1))
    done
    
    echo -e "${YELLOW}⏱️  超时：任务仍在运行中${NC}"
    print_json "{\"status\":\"timeout\",\"task_id\":\"${task_id}\",\"prompt\":\"${prompt}\"}"
    return 1
}

# 函数：检查任务状态
check_task_status() {
    local task_id="$1"
    
    # 调用 API
    local response=$(curl -s --show-error --fail "${TASK_ENDPOINT}/${task_id}" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${ARK_API_KEY}")
    
    # 直接返回响应
    echo "$response"
}

# 主函数
main() {
    # 显示帮助
    if [ $# -lt 1 ]; then
        cat <<'HELP'
用法: doubao.sh <command> [options...]

命令:
  img <prompt>                        文生图
  edit <image_url> [prompt]           图片编辑（去除水印）
  vid <prompt> [sync|async]          文生视频（默认异步）
  vid <prompt> <image_url> [sync]    文生视频（带参考图）
  status <task_id>                     查询任务状态
  help                                显示此帮助信息

示例:
  # 文生图
  ./doubao.sh img "一只可爱的小猫"
  
  # 图片编辑（使用默认提示词）
  ./doubao.sh edit "https://example.com/image.png"
  
  # 图片编辑（自定义提示词）
  ./doubao.sh edit "https://example.com/image.png" "remove logo and watermark"
  
  # 文生视频（异步）
  ./doubao.sh vid "一个人在跳舞"
  
  # 文生视频（同步 - 等待完成）
  ./doubao.sh vid "一个人在跳舞" sync
  
  # 文生视频（带参考图）
  ./doubao.sh vid "一个人在跳舞" "https://example.com/image.jpg" async
  
  # 查询任务状态
  ./doubao.sh status "task_xxxxx"

环境变量:
  ARK_API_KEY                (必需) Volcengine ARK API 密钥

目录结构:
  data/                       生成的文件存储目录
  scripts/doubao.sh            本脚本
HELP
        exit 0
    fi
    
    local cmd="$1"
    shift
    
    # 执行命令
    case "$cmd" in
        img)
            if [ $# -lt 1 ]; then
                echo -e "${RED}错误${NC}: img 命令需要提示词"
                echo "用法: ./doubao.sh img \"<prompt>\""
                exit 1
            fi
            generate_image "$1"
            ;;
        
        edit)
            if [ $# -lt 1 ]; then
                echo -e "${RED}错误${NC}: edit 命令需要图片 URL"
                echo "用法: ./doubao.sh edit \"<image_url>\" [\"<prompt>\"]"
                exit 1
            fi
            edit_image "$1" "${2:-}"
            ;;
        
        vid)
            if [ $# -lt 1 ]; then
                echo -e "${RED}错误${NC}: vid 命令需要提示词"
                echo "用法: ./doubao.sh vid \"<prompt>\" [\"<image_url>\"] [\"sync|async\"]"
                exit 1
            fi
            
            local prompt="$1"
            local image_url="${2:-}"
            local sync_mode="sync"
            
            # 判断第二个参数是图片 URL 还是模式
            if [ -n "$image_url" ]; then
                # 检查是否是 sync/async
                if [ "$image_url" = "sync" ] || [ "$image_url" = "async" ]; then
                    sync_mode="$image_url"
                    image_url=""
                fi
            fi
            
            # 检查第三个参数
            if [ $# -ge 2 ] && -n "$3" ]; then
                sync_mode="$3"
            fi
            
            if [ -n "$image_url" ]; then
                generate_video "$prompt" "$image_url" "$sync_mode"
            else
                generate_video "$prompt" "" "$sync_mode"
            fi
            ;;
        
        status)
            if [ $# -lt 1 ]; then
                echo -e "${RED}错误${NC}: status 命令需要任务 ID"
                echo "用法: ./doubao.sh status \"<task_id>\""
                exit 1
            fi
            check_task_status "$1"
            ;;
        
        help|--help|-h)
            main
            ;;
        
        *)
            echo -e "${RED}错误${NC}: 未知命令 ${cmd}"
            echo "使用: ./doubao.sh help"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
