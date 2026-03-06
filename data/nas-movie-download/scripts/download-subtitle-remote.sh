#!/bin/bash

# 本地下载字幕并上传到 NAS
# 用途：在本地使用 subliminal 下载字幕，然后通过 scp 复制到 NAS

set -e

# NAS 配置
NAS_HOST="${NAS_HOST:-192.168.1.246}"
NAS_USER="${NAS_USER:-roger}"
NAS_DOWNLOAD_PATH="${NAS_DOWNLOAD_PATH:-/downloads}"
LOCAL_TEMP_DIR="/tmp/subtitle-downloads"

# 帮助信息
usage() {
    echo "用法: download-subtitle-remote.sh [选项]"
    echo ""
    echo "选项："
    echo "  -n, --nas-host     NAS IP (默认: $NAS_HOST)"
    echo "  -u, --nas-user     NAS 用户名 (默认: $NAS_USER)"
    echo "  -p, --nas-path     NAS 下载路径 (默认: $NAS_DOWNLOAD_PATH)"
    echo "  -t, --torrent-name 要处理的种子名称关键词"
    echo "  -l, --languages    字幕语言 (默认: zh,en)"
    echo "  -h, --help         显示帮助"
    echo ""
    echo "示例："
    echo "  download-subtitle-remote.sh -t \"Lilo Stitch\" -l zh,en"
    echo "  download-subtitle-remote.sh -t \"Young Sheldon\" -l zh-cn,en"
    exit 1
}

# 解析参数
TORRENT_NAME=""
LANGUAGES="zh,en"

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--nas-host)
            NAS_HOST="$2"
            shift 2
            ;;
        -u|--nas-user)
            NAS_USER="$2"
            shift 2
            ;;
        -p|--nas-path)
            NAS_DOWNLOAD_PATH="$2"
            shift 2
            ;;
        -t|--torrent-name)
            TORRENT_NAME="$2"
            shift 2
            ;;
        -l|--languages)
            LANGUAGES="$2"
            shift 2
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

if [[ -z "$TORRENT_NAME" ]]; then
    echo "❌ 错误：需要指定种子名称关键词 (-t)"
    usage
fi

echo "=== 远程字幕下载工具 ==="
echo "NAS: $NAS_USER@$NAS_HOST:$NAS_DOWNLOAD_PATH"
echo "关键词: $TORRENT_NAME"
echo "语言: $LANGUAGES"
echo ""

# 检查 subliminal
if ! command -v subliminal >/dev/null 2>&1; then
    echo "❌ subliminal 未安装"
    echo "请先安装: pip3 install --user subliminal"
    exit 1
fi

# 步骤 1: 通过 SSH 列出 NAS 上的视频文件
echo "🔍 步骤 1: 在 NAS 上查找视频文件..."

VIDEO_FILES=$(ssh "$NAS_USER@$NAS_HOST" "find $NAS_DOWNLOAD_PATH -name '*.mp4' -o -name '*.mkv' -o -name '*.avi' 2>/dev/null | grep -i '$TORRENT_NAME'" 2>/dev/null)

if [[ -z "$VIDEO_FILES" ]]; then
    echo "❌ 未找到匹配的视频文件"
    exit 1
fi

echo "✅ 找到以下视频文件："
echo "$VIDEO_FILES"
echo ""

# 步骤 2: 创建本地临时目录
mkdir -p "$LOCAL_TEMP_DIR"
cd "$LOCAL_TEMP_DIR"

# 步骤 3: 为每个视频下载字幕
echo "📥 步骤 2: 在本地下载字幕..."

for video_path in $VIDEO_FILES; do
    video_name=$(basename "$video_path")
    
    echo ""
    echo "处理: $video_name"
    
    # 创建本地占位文件（只需要文件名，不需要实际视频内容）
    touch "$video_name"
    
    # 使用 subliminal 下载字幕
    echo "  下载字幕..."
    subliminal download -l zho -l eng "$video_name" 2>&1 || echo "  ⚠️ 下载可能失败"
    
    # 检查是否下载成功
    subtitle_files=$(find . -name "${video_name%.*}.*.srt" -o -name "${video_name%.*}.*.ass" 2>/dev/null)
    
    if [[ -n "$subtitle_files" ]]; then
        echo "  ✅ 找到字幕文件:"
        echo "$subtitle_files" | while read sub; do
            echo "    - $sub"
        done
    else
        echo "  ❌ 未找到字幕文件"
    fi
done

echo ""
echo "📤 步骤 3: 上传字幕到 NAS..."

# 步骤 4: 上传字幕到 NAS
for subtitle in *.srt *.ass 2>/dev/null; do
    if [[ -f "$subtitle" ]]; then
        # 确定目标目录（根据视频文件名找到对应目录）
        video_base="${subtitle%.*}"
        # 移除语言后缀
        video_base="${video_base%.zh}"
        video_base="${video_base%.zh-cn}"
        video_base="${video_base%.en}"
        video_base="${video_base%.eng}"
        
        # 在 NAS 上找到对应的视频目录
        target_dir=$(ssh "$NAS_USER@$NAS_HOST" "find $NAS_DOWNLOAD_PATH -name '${video_base}*' -type f -exec dirname {} \; 2>/dev/null | head -1" 2>/dev/null)
        
        if [[ -n "$target_dir" ]]; then
            echo "上传 $subtitle -> $NAS_USER@$NAS_HOST:$target_dir/"
            scp "$subtitle" "$NAS_USER@$NAS_HOST:$target_dir/" 2>&1 && echo "  ✅ 上传成功" || echo "  ❌ 上传失败"
        else
            echo "未找到 $subtitle 对应的目标目录，上传到根目录"
            scp "$subtitle" "$NAS_USER@$NAS_HOST:$NAS_DOWNLOAD_PATH/" 2>&1 && echo "  ✅ 上传成功" || echo "  ❌ 上传失败"
        fi
    fi
done

# 清理
cd >/dev/null
rm -rf "$LOCAL_TEMP_DIR"

echo ""
echo "✅ 全部完成！"
echo "字幕已上传到 NAS 的 qBittorrent 下载目录"
