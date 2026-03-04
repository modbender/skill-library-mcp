#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
START_SCRIPT="${SCRIPT_DIR}/start_vrd.sh"

if [[ ! -x "${START_SCRIPT}" ]]; then
  echo "[ERR] missing start script: ${START_SCRIPT}" >&2
  exit 1
fi

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
fi

ask_choice() {
  local prompt="$1"
  shift
  local options=("$@")
  local i ans
  while true; do
    echo >&2
    echo "${prompt}" >&2
    for i in "${!options[@]}"; do
      printf '  [%d] %s\n' "$((i+1))" "${options[$i]}" >&2
    done
    if ! read -r -p "请选择编号: " ans; then
      echo "[ERR] 输入已结束，无法继续向导。" >&2
      exit 1
    fi
    ans="${ans//[[:space:]]/}"
    if [[ "${ans}" =~ ^[0-9]+$ ]] && (( ans >= 1 && ans <= ${#options[@]} )); then
      echo "$ans"
      return
    fi
    echo "无效输入，请重试。" >&2
  done
}

ask_text() {
  local prompt="$1"
  local default="${2:-}"
  local v
  if [[ -n "${default}" ]]; then
    if ! read -r -p "${prompt} [默认: ${default}]: " v; then
      echo "$default"
      return
    fi
    echo "${v:-$default}"
  else
    if ! read -r -p "${prompt}: " v; then
      echo ""
      return
    fi
    echo "${v}"
  fi
}

# 1) takeover device (for VNC stream tuning)
choice_takeover="$(ask_choice "你用什么设备接管 VNC？" "手机" "电脑")"
MOBILE_MODE=0
MOBILE_PRESET=phone
GEOM=1920x1080
DEPTH=24

if [[ "${choice_takeover}" == "1" ]]; then
  MOBILE_MODE=1
  choice_mobile_preset="$(ask_choice "手机屏幕倾向？" "手机竖屏优先（960x540）" "平板/大屏优先（1280x720）")"
  if [[ "${choice_mobile_preset}" == "1" ]]; then
    MOBILE_PRESET=phone
    GEOM=960x540
  else
    MOBILE_PRESET=tablet
    GEOM=1280x720
  fi
  DEPTH=16
fi

# 2) website rendering mode (browser emulation)
choice_browser="$(ask_choice "目标网站希望以什么形态渲染？" "桌面网页" "手机网页")"
BROWSER_MOBILE_MODE=0
BROWSER_DEVICE=iphone14pro
if [[ "${choice_browser}" == "2" ]]; then
  BROWSER_MOBILE_MODE=1
  choice_device="$(ask_choice "选择手机设备画像" "iPhone 14 Pro" "Pixel 7" "iPad")"
  case "${choice_device}" in
    1) BROWSER_DEVICE=iphone14pro ;;
    2) BROWSER_DEVICE=pixel7 ;;
    3) BROWSER_DEVICE=ipad ;;
  esac
fi

# 3) connection exposure
choice_expose="$(ask_choice "连接方式？" "安全模式（仅本地 127.0.0.1 + SSH 隧道）" "临时公网接管（0.0.0.0）")"
KASM_BIND=127.0.0.1
AUTO_STOP_IDLE_SECS=900
if [[ "${choice_expose}" == "2" ]]; then
  KASM_BIND=0.0.0.0
  AUTO_STOP_IDLE_SECS=300
fi

# 4) network quality
choice_net="$(ask_choice "当前网络情况？" "弱网" "普通" "良好")"
KASM_MAX_FPS=60
case "${choice_net}" in
  1)
    KASM_MAX_FPS=18
    if [[ "${MOBILE_MODE}" == "0" ]]; then
      GEOM=1280x720
      DEPTH=16
    fi
    ;;
  2)
    KASM_MAX_FPS=24
    if [[ "${MOBILE_MODE}" == "0" ]]; then
      GEOM=1600x900
    fi
    ;;
  3)
    if [[ "${MOBILE_MODE}" == "1" ]]; then
      KASM_MAX_FPS=30
    else
      KASM_MAX_FPS=60
    fi
    ;;
esac

AUTO_LAUNCH_URL="$(ask_text "可选：自动打开的 URL（留空则不自动打开）" "")"

cat <<EOF

========== VRD 配置摘要 ==========
MOBILE_MODE=${MOBILE_MODE}
MOBILE_PRESET=${MOBILE_PRESET}
GEOM=${GEOM}
DEPTH=${DEPTH}
BROWSER_MOBILE_MODE=${BROWSER_MOBILE_MODE}
BROWSER_DEVICE=${BROWSER_DEVICE}
KASM_BIND=${KASM_BIND}
KASM_MAX_FPS=${KASM_MAX_FPS}
AUTO_STOP_IDLE_SECS=${AUTO_STOP_IDLE_SECS}
AUTO_LAUNCH_URL=${AUTO_LAUNCH_URL}
=================================
EOF

if [[ "${DRY_RUN}" == "1" ]]; then
  printf '\n[DRY-RUN] 将使用以下命令启动：\n'
  echo "env MOBILE_MODE=${MOBILE_MODE} MOBILE_PRESET=${MOBILE_PRESET} GEOM=${GEOM} DEPTH=${DEPTH} BROWSER_MOBILE_MODE=${BROWSER_MOBILE_MODE} BROWSER_DEVICE=${BROWSER_DEVICE} KASM_BIND=${KASM_BIND} KASM_MAX_FPS=${KASM_MAX_FPS} AUTO_STOP_IDLE_SECS=${AUTO_STOP_IDLE_SECS} AUTO_LAUNCH_URL='${AUTO_LAUNCH_URL}' bash ${START_SCRIPT}"
  exit 0
fi

exec env \
  MOBILE_MODE="${MOBILE_MODE}" \
  MOBILE_PRESET="${MOBILE_PRESET}" \
  GEOM="${GEOM}" \
  DEPTH="${DEPTH}" \
  BROWSER_MOBILE_MODE="${BROWSER_MOBILE_MODE}" \
  BROWSER_DEVICE="${BROWSER_DEVICE}" \
  KASM_BIND="${KASM_BIND}" \
  KASM_MAX_FPS="${KASM_MAX_FPS}" \
  AUTO_STOP_IDLE_SECS="${AUTO_STOP_IDLE_SECS}" \
  AUTO_LAUNCH_URL="${AUTO_LAUNCH_URL}" \
  bash "${START_SCRIPT}"
