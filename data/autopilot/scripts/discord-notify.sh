#!/usr/bin/env bash
# discord-notify.sh — 自动推送开发动态到 Discord 对应频道
# 用法:
#   discord-notify.sh <channel> <message>
#   discord-notify.sh --by-window <window_name> <message>
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/autopilot-lib.sh"

usage() {
  echo "Usage: $0 <channel> <message>" >&2
  echo "   or: $0 --by-window <window_name> <message>" >&2
}

# 兼容旧逻辑：作为 fallback 的固定频道映射
fallback_channel_id() {
  local channel="$1"
  case "$channel" in
    gonggao|公告)     echo "1473294121878687837" ;;
    ribao|日报)       echo "1473294128799416443" ;;
    chat|闲聊)        echo "1473294135116169238" ;;
    agent-log)        echo "1473294141843705877" ;;
    code-review)      echo "1473294148126769364" ;;
    job-feed)         echo "1473294154850369650" ;;
    applications)     echo "1473294162240471284" ;;
    shike)            echo "1473294169203150941" ;;
    replyher)         echo "1473294176128077888" ;;
    simcity)          echo "1473294182905938013" ;;
    autopilot)        echo "1473294190094848133" ;;
    wpk)              echo "1477291487170400429" ;;
    conduit)          echo "1473294196717912310" ;;
    research)         echo "1473294203596443690" ;;
    incidents)        echo "1473294209682378815" ;;
    resources)        echo "1473294216875479123" ;;
    *)                return 1 ;;
  esac
}

# 兼容旧逻辑：窗口反查频道名的 fallback
fallback_channel_for_window() {
  local window="$1"
  local safe_window
  safe_window=$(sanitize "$window")
  case "$safe_window" in
    Shike|shike)                    echo "shike" ;;
    replyher_android-2|replyher)    echo "replyher" ;;
    agent-simcity|simcity)          echo "simcity" ;;
    autopilot-dev|autopilot)        echo "autopilot" ;;
    kpw-bot-js|wpk)                 echo "wpk" ;;
    *)                              return 1 ;;
  esac
}

MODE="by-channel"
TARGET="${1:-}"
if [[ "$TARGET" == "--by-window" ]]; then
  MODE="by-window"
  WINDOW_NAME="${2:-}"
  MSG="${3:-}"
  if [[ -z "$WINDOW_NAME" || -z "$MSG" ]]; then
    usage
    exit 1
  fi
  CHANNEL_NAME="$(get_discord_channel_for_window "$WINDOW_NAME" 2>/dev/null || true)"
  if [[ -z "$CHANNEL_NAME" ]]; then
    CHANNEL_NAME="$(fallback_channel_for_window "$WINDOW_NAME" 2>/dev/null || true)"
  fi
else
  CHANNEL_NAME="$TARGET"
  MSG="${2:-}"
  if [[ -z "$CHANNEL_NAME" || -z "$MSG" ]]; then
    usage
    exit 1
  fi
fi

if [[ -z "${CHANNEL_NAME:-}" ]]; then
  if [[ "$MODE" == "by-window" ]]; then
    echo "ERROR: 无法根据窗口找到频道: ${WINDOW_NAME}" >&2
  else
    echo "ERROR: 未提供频道名" >&2
  fi
  exit 1
fi

BOT_TOKEN=$(
  python3 - "$HOME/.openclaw/openclaw.json" 2>/dev/null <<'PY' || true
import json
import sys

path = sys.argv[1]
try:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    token = data.get("channels", {}).get("discord", {}).get("token", "")
    if isinstance(token, str):
        print(token.strip())
except Exception:
    pass
PY
)

if [[ -z "$BOT_TOKEN" ]]; then
  echo "ERROR: failed to load Discord bot token from $HOME/.openclaw/openclaw.json" >&2
  exit 1
fi

CHANNEL_ID=""
if [[ "$CHANNEL_NAME" =~ ^[0-9]{10,}$ ]]; then
  CHANNEL_ID="$CHANNEL_NAME"
else
  CHANNEL_ID="$(get_discord_channel_id_for_channel "$CHANNEL_NAME" 2>/dev/null || true)"
  if [[ -z "$CHANNEL_ID" ]]; then
    CHANNEL_ID="$(fallback_channel_id "$CHANNEL_NAME" 2>/dev/null || true)"
  fi
fi

if [[ -z "$CHANNEL_ID" ]]; then
  echo "Unknown channel: $CHANNEL_NAME" >&2
  exit 1
fi

MSG_TRUNCATED="${MSG:0:1990}"

curl -s -X POST \
  --connect-timeout 5 \
  --max-time 15 \
  -H "Authorization: Bot $BOT_TOKEN" \
  -H "Content-Type: application/json" \
  "https://discord.com/api/v10/channels/$CHANNEL_ID/messages" \
  -d "$(jq -n --arg content "$MSG_TRUNCATED" '{content: $content}')" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id','ERR'))" 2>/dev/null
