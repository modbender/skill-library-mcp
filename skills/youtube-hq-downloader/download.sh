#!/bin/bash
# YouTube Highest Quality Downloader Script
# Youtube最高码率下载器 - 用法: ./download.sh "YouTube_URL" "输出文件名(可选)" "输出目录(可选)"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="${3:-$HOME/Movies}"

if [ -z "$1" ]; then
    echo "用法: $0 <YouTube_URL> [输出文件名] [输出目录]"
    echo "示例: $0 \"https://www.youtube.com/watch?v=xxxxx\" \"我的视频\""
    echo "示例: $0 \"https://www.youtube.com/watch?v=xxxxx\" \"视频名\" \"~/Downloads\""
    exit 1
fi

URL="$1"
OUTPUT_NAME="${2:-merged}"

mkdir -p "$OUTPUT_DIR"

# 检查 yt-dlp
YT_DLP=""
if command -v yt-dlp &> /dev/null; then
    YT_DLP="yt-dlp"
elif [ -f "$SCRIPT_DIR/.venv/bin/yt-dlp" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
    YT_DLP="$SCRIPT_DIR/.venv/bin/yt-dlp"
elif [ -f "$HOME/clawd/skills/video-subtitles/.venv/bin/yt-dlp" ]; then
    source "$HOME/clawd/skills/video-subtitles/.venv/bin/activate"
    YT_DLP="$HOME/clawd/skills/video-subtitles/.venv/bin/yt-dlp"
else
    echo "❌ 未找到 yt-dlp，正在尝试安装..."
    python3 -m venv "$SCRIPT_DIR/.venv"
    source "$SCRIPT_DIR/.venv/bin/activate"
    pip install yt-dlp
    YT_DLP="$SCRIPT_DIR/.venv/bin/yt-dlp"
fi

echo "📥 Step 1: Downloading video (highest quality)..."
$YT_DLP -f "bestvideo" "$URL" -o "$OUTPUT_DIR/${OUTPUT_NAME}_video.%(ext)s"

echo "📥 步骤2: 下载音频..."
$YT_DLP -x --audio-format m4a "$URL" -o "$OUTPUT_DIR/${OUTPUT_NAME}_audio.%(ext)s"

echo "🔧 Step 3: Merging video and audio..."
cd "$OUTPUT_DIR"

# Find the video file (could be .mp4 or .webm)
VIDEO_FILE=$(ls ${OUTPUT_NAME}_video.* 2>/dev/null | head -1)
if [ -z "$VIDEO_FILE" ]; then
    echo "❌ Video file not found!"
    exit 1
fi

ffmpeg -i "$VIDEO_FILE" -i "${OUTPUT_NAME}_audio.m4a" -c:v libx264 -c:a aac -shortest "${OUTPUT_NAME}_combined.mp4" -y

# 清理中间文件 (可选)
rm -f "${OUTPUT_NAME}_video.mp4" "${OUTPUT_NAME}_audio.m4a"

echo "✅ 完成!"
echo "📁 输出文件: $OUTPUT_DIR/${OUTPUT_NAME}_combined.mp4"

# 显示文件信息
ls -lh "${OUTPUT_NAME}_combined.mp4"
