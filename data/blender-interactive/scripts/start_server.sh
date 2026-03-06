#!/bin/bash
# Blender Interactive Socket Server 시작 스크립트
# MiniPC에서 실행
#
# 사용법:
#   ./start_server.sh                    # 기본 (포트 9876)
#   ./start_server.sh --port 9877        # 커스텀 포트
#   ./start_server.sh --background       # 백그라운드 실행
#   ./start_server.sh --stop             # 서버 중지

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ADDON="${SCRIPT_DIR}/blender_socket_addon.py"
PORT="${PORT:-9876}"
HOST="${HOST:-127.0.0.1}"
PID_FILE="/tmp/blender_socket_server.pid"
LOG_FILE="/tmp/blender_socket_server.log"

# 인자 파싱
BACKGROUND=false
STOP=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --port) PORT="$2"; shift 2;;
        --host) HOST="$2"; shift 2;;
        --background|-d) BACKGROUND=true; shift;;
        --stop) STOP=true; shift;;
        --help|-h)
            echo "Usage: $0 [--port PORT] [--host HOST] [--background|-d] [--stop]"
            exit 0
            ;;
        *) shift;;
    esac
done

# 서버 중지
if [ "$STOP" = true ]; then
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "Stopping Blender server (PID: $PID)..."
            kill "$PID"
            rm -f "$PID_FILE"
            echo "Stopped."
        else
            echo "Process $PID not running. Cleaning up."
            rm -f "$PID_FILE"
        fi
    else
        echo "No PID file found. Trying pkill..."
        pkill -f "blender.*blender_socket_addon" || echo "No process found."
    fi
    exit 0
fi

# 이미 실행 중인지 확인
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Server already running (PID: $PID)"
        exit 0
    fi
    rm -f "$PID_FILE"
fi

# Blender 확인
if ! command -v blender &>/dev/null; then
    echo "ERROR: blender not found in PATH"
    exit 1
fi

echo "Starting Blender Socket Server..."
echo "  Addon: $ADDON"
echo "  Host:  $HOST"
echo "  Port:  $PORT"

if [ "$BACKGROUND" = true ]; then
    nohup blender -b --factory-startup --python "$ADDON" -- --host "$HOST" --port "$PORT" \
        > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "  PID:   $(cat $PID_FILE)"
    echo "  Log:   $LOG_FILE"
    echo "Background mode. Use --stop to terminate."
else
    echo "Foreground mode. Ctrl+C to stop."
    blender -b --factory-startup --python "$ADDON" -- --host "$HOST" --port "$PORT"
fi
