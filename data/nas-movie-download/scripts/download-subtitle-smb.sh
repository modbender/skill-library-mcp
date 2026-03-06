#!/bin/bash
# SMB 字幕下载脚本
# 挂载 NAS SMB，本地下载字幕后复制到 qb 目录

NAS_HOST="${NAS_HOST:-192.168.1.246}"
NAS_SHARE="${NAS_SHARE:-downloads}"
MOUNT_POINT="${MOUNT_POINT:-/mnt/nas-downloads}"

usage() {
    echo "用法: download-subtitle-smb.sh -t \"关键词\" [-p \"密码\"]"
    exit 1
}

TORRENT_NAME=""
NAS_PASS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -t) TORRENT_NAME="$2"; shift 2 ;;
        -p) NAS_PASS="$2"; shift 2 ;;
        *) usage ;;
    esac
done

[[ -z "$TORRENT_NAME" ]] && usage

echo "=== SMB 字幕下载 ==="
echo "NAS: //$NAS_HOST/$NAS_SHARE"
echo "关键词: $TORRENT_NAME"

# 挂载
sudo mkdir -p "$MOUNT_POINT"
if [[ -n "$NAS_PASS" ]]; then
    sudo mount -t cifs "//$NAS_HOST/$NAS_SHARE" "$MOUNT_POINT" -o username="$USER",password="$NAS_PASS",uid=$(id -u)
else
    sudo mount -t cifs "//$NAS_HOST/$NAS_SHARE" "$MOUNT_POINT" -o guest,uid=$(id -u)
fi

cleanup() { sudo umount "$MOUNT_POINT" 2>/dev/null; }
trap cleanup EXIT

# 查找视频
VIDEO=$(find "$MOUNT_POINT" -type f \( -name "*.mp4" -o -name "*.mkv" \) | grep -i "$TORRENT_NAME" | head -1)
[[ -z "$VIDEO" ]] && { echo "未找到视频"; exit 1; }

echo "找到: $(basename "$VIDEO")"

# 下载字幕
VIDEO_NAME=$(basename "$VIDEO")
VIDEO_DIR=$(dirname "$VIDEO")
cd /tmp
touch "$VIDEO_NAME"
subliminal download -l zho -l eng "$VIDEO_NAME"

# 复制字幕
cp *.srt *.ass "$VIDEO_DIR/" 2>/dev/null && echo "✅ 字幕已复制"
rm -f *.srt *.ass "$VIDEO_NAME"

echo "完成！"
