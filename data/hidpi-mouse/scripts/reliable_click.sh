#!/bin/bash
# reliable_click.sh - 可靠的 HiDPI 鼠标点击
# 使用 xdotool/xwininfo 获取正确坐标（不受 Xft.dpi 影响）

set -e

usage() {
    echo "Usage: $0 <x> <y> [--window <window_name>] [--relative]"
    echo ""
    echo "Options:"
    echo "  x, y              目标坐标（屏幕绝对坐标）"
    echo "  --window <name>   在指定窗口内点击"
    echo "  --relative        坐标相对于窗口（需要配合 --window）"
    echo ""
    echo "Examples:"
    echo "  $0 500 500                    # 点击屏幕坐标 (500, 500)"
    echo "  $0 100 200 --window 'WPS'     # 点击 WPS 窗口内相对位置 (100, 200)"
    echo "  $0 100 200 --window 'WPS' --relative"
    exit 1
}

# 解析参数
if [ $# -lt 2 ]; then
    usage
fi

X=$1
Y=$2
shift 2

WINDOW_NAME=""
RELATIVE=false

while [ $# -gt 0 ]; do
    case "$1" in
        --window)
            WINDOW_NAME="$2"
            shift 2
            ;;
        --relative)
            RELATIVE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# 如果指定了窗口
if [ -n "$WINDOW_NAME" ]; then
    # 使用 xdotool 获取窗口 ID (--onlyvisible 避免隐藏窗口)
    WIN_ID=$(xdotool search --onlyvisible --name "$WINDOW_NAME" 2>/dev/null | head -1)
    
    # 如果没找到，尝试不带 --onlyvisible，但选择最大的窗口
    if [ -z "$WIN_ID" ]; then
        WIN_ID=$(xdotool search --name "$WINDOW_NAME" 2>/dev/null | while read wid; do
            SIZE=$(xdotool getwindowgeometry "$wid" 2>/dev/null | grep Geometry | awk '{print $2}' | tr 'x' '*' | bc)
            echo "$SIZE $wid"
        done | sort -rn | head -1 | awk '{print $2}')
    fi
    
    if [ -z "$WIN_ID" ]; then
        echo "Error: Window '$WINDOW_NAME' not found"
        exit 1
    fi
    
    # 激活窗口
    xdotool windowactivate "$WIN_ID" 2>/dev/null || true
    sleep 0.2
    
    if [ "$RELATIVE" = true ]; then
        # 获取窗口位置（使用 xdotool，不是 wmctrl！）
        WIN_INFO=$(xdotool getwindowgeometry "$WIN_ID")
        WIN_X=$(echo "$WIN_INFO" | grep "Position:" | awk -F'[ ,()]' '{print $4}')
        WIN_Y=$(echo "$WIN_INFO" | grep "Position:" | awk -F'[ ,()]' '{print $5}')
        
        # 计算绝对坐标
        ABS_X=$((WIN_X + X))
        ABS_Y=$((WIN_Y + Y))
        
        echo "Window position: ($WIN_X, $WIN_Y)"
        echo "Relative click: ($X, $Y)"
        echo "Absolute click: ($ABS_X, $ABS_Y)"
        
        X=$ABS_X
        Y=$ABS_Y
    fi
fi

# 执行点击
echo "Clicking at ($X, $Y)"
xdotool mousemove "$X" "$Y"
sleep 0.1
xdotool click 1

echo "Click completed"
