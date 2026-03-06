#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

DISPLAY_NUM="${DISPLAY_NUM:-55}"
GEOM="${GEOM:-1920x1080}"
DEPTH="${DEPTH:-24}"
KASM_BIND="${KASM_BIND:-127.0.0.1}"
MOBILE_MODE="${MOBILE_MODE:-0}"          # 1 => mobile-friendly defaults
MOBILE_PRESET="${MOBILE_PRESET:-phone}"   # phone | tablet
KASM_MAX_FPS="${KASM_MAX_FPS:-60}"
WORKDIR="${WORKDIR:-$HOME/.openclaw/vrd-data}"
PIDFILE="${WORKDIR}/pids.env"
LOGDIR="${WORKDIR}/logs"
KASM_HOME="${KASM_HOME:-${WORKDIR}/kasm-home}"
KASM_CFG="${WORKDIR}/kasmvnc.override.yaml"
# IMPORTANT: vncserver wrapper checks ${HOME}/.kasmpasswd before startup.
# Keep password file under KASM_HOME so non-interactive startup won't hang.
KASM_PASS_FILE="${KASM_PASS_FILE:-${KASM_HOME}/.kasmpasswd}"
KASM_USER_FILE="${WORKDIR}/kasm.user"
KASM_SECRET_FILE="${WORKDIR}/kasm.secret"
AUTO_STOP_IDLE_SECS="${AUTO_STOP_IDLE_SECS:-900}"
AUTO_STOP_CHECK_SECS="${AUTO_STOP_CHECK_SECS:-15}"
AUTO_LAUNCH_URL="${AUTO_LAUNCH_URL:-}"
CHROME_PROFILE_DIR="${CHROME_PROFILE_DIR:-${WORKDIR}/chrome-profile}"
# Browser mobile emulation for website rendering (different from VNC mobile viewport)
BROWSER_MOBILE_MODE="${BROWSER_MOBILE_MODE:-0}"      # 1 => launch Chrome with mobile UA/viewport
BROWSER_DEVICE="${BROWSER_DEVICE:-iphone14pro}"       # iphone14pro | pixel7 | ipad
BROWSER_MOBILE_WIDTH="${BROWSER_MOBILE_WIDTH:-}"      # optional override
BROWSER_MOBILE_HEIGHT="${BROWSER_MOBILE_HEIGHT:-}"    # optional override
BROWSER_MOBILE_DPR="${BROWSER_MOBILE_DPR:-}"          # optional override
BROWSER_MOBILE_UA="${BROWSER_MOBILE_UA:-}"            # optional override
KASM_USER="${KASM_USER:-vrd}"
KASM_PASS="${KASM_PASS:-}"

if [[ ! "${DISPLAY_NUM}" =~ ^[0-9]+$ ]]; then
  echo "[ERR] DISPLAY_NUM must be an integer" >&2
  exit 1
fi
if [[ ! "${GEOM}" =~ ^[0-9]+x[0-9]+$ ]]; then
  echo "[ERR] GEOM must be like 1920x1080" >&2
  exit 1
fi
if [[ ! "${KASM_MAX_FPS}" =~ ^[0-9]+$ ]]; then
  echo "[ERR] KASM_MAX_FPS must be an integer" >&2
  exit 1
fi
if [[ ! "${BROWSER_MOBILE_MODE}" =~ ^[01]$ ]]; then
  echo "[ERR] BROWSER_MOBILE_MODE must be 0 or 1" >&2
  exit 1
fi
WIDTH="${GEOM%x*}"
HEIGHT="${GEOM#*x}"

if [[ "${MOBILE_MODE}" == "1" ]]; then
  case "${MOBILE_PRESET}" in
    phone)
      [[ "${GEOM}" == "1920x1080" ]] && GEOM="960x540"
      ;;
    tablet)
      [[ "${GEOM}" == "1920x1080" ]] && GEOM="1280x720"
      ;;
    *)
      echo "[ERR] MOBILE_PRESET must be phone|tablet" >&2
      exit 1
      ;;
  esac

  # Reduce rendering load for mobile network + touch viewport
  [[ "${DEPTH}" == "24" ]] && DEPTH="16"
  [[ "${KASM_MAX_FPS}" == "60" ]] && KASM_MAX_FPS="24"

  WIDTH="${GEOM%x*}"
  HEIGHT="${GEOM#*x}"
fi

KASM_PORT="${KASM_PORT:-$((8443 + DISPLAY_NUM))}"
RFB_PORT="${RFB_PORT:-$((5900 + DISPLAY_NUM))}"

need_bin() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "[ERR] missing command: $1" >&2
    exit 1
  }
}

need_bin vncserver
need_bin vncpasswd
need_bin python3
need_bin curl
need_bin ss
need_bin sg
if ! command -v xdotool >/dev/null 2>&1 || ! command -v scrot >/dev/null 2>&1; then
  echo "[WARN] xdotool/scrot not found. Install them if you need computer-use action scripts:" >&2
  echo "       sudo apt-get install -y xdotool scrot" >&2
fi

if [[ ! -x /usr/lib/kasmvncserver/select-de.sh ]]; then
  echo "[ERR] missing /usr/lib/kasmvncserver/select-de.sh (kasmvncserver not installed correctly)" >&2
  exit 1
fi

ensure_ssl_group() {
  if id -nG "$USER" | tr ' ' '\n' | grep -qx 'ssl-cert'; then
    return 0
  fi
  if command -v sudo >/dev/null 2>&1; then
    echo "[INFO] adding user '${USER}' to ssl-cert group (required by KasmVNC TLS cert)"
    sudo usermod -a -G ssl-cert "$USER"
    return 0
  fi
  echo "[ERR] user is not in ssl-cert and sudo is unavailable" >&2
  return 1
}

run_with_ssl_group() {
  if id -nG | tr ' ' '\n' | grep -qx 'ssl-cert'; then
    "$@"
    return
  fi
  if id -nG "$USER" | tr ' ' '\n' | grep -qx 'ssl-cert'; then
    local cmd
    printf -v cmd '%q ' "$@"
    sg ssl-cert -c "$cmd"
    return
  fi
  echo "[ERR] user '${USER}' is not in ssl-cert; run: sudo usermod -a -G ssl-cert ${USER}" >&2
  return 1
}

pick_chrome_bin() {
  if [[ -n "${CHROME_BIN:-}" ]] && [[ -x "${CHROME_BIN}" ]]; then
    echo "${CHROME_BIN}"
    return
  fi
  local cand
  for cand in \
    "$(command -v google-chrome-stable 2>/dev/null || true)" \
    "$(command -v google-chrome 2>/dev/null || true)" \
    "$(command -v chromium-browser 2>/dev/null || true)" \
    "$(command -v chromium 2>/dev/null || true)"; do
    if [[ -n "${cand}" && -x "${cand}" ]]; then
      echo "${cand}"
      return
    fi
  done

  # Playwright cache fallbacks
  local pw
  pw="$(ls -1d "$HOME"/.cache/ms-playwright/chromium-*/chrome-linux/chrome 2>/dev/null | sort -V | tail -n1 || true)"
  if [[ -n "${pw}" && -x "${pw}" ]]; then
    echo "${pw}"
    return
  fi
  pw="$(ls -1d "$HOME"/.cache/ms-playwright/chromium-*/chrome-linux64/chrome 2>/dev/null | sort -V | tail -n1 || true)"
  if [[ -n "${pw}" && -x "${pw}" ]]; then
    echo "${pw}"
    return
  fi

  echo ""
}

chrome_sandbox_flags() {
  local userns
  userns="$(cat /proc/sys/kernel/unprivileged_userns_clone 2>/dev/null || echo 1)"
  if [[ "${userns}" == "0" ]]; then
    echo "--no-sandbox --disable-dev-shm-usage"
  else
    echo "--disable-dev-shm-usage"
  fi
}

browser_mobile_profile() {
  case "${BROWSER_DEVICE,,}" in
    iphone14pro|iphone14|iphone)
      MOBILE_W_DEFAULT=393
      MOBILE_H_DEFAULT=852
      MOBILE_DPR_DEFAULT=3
      MOBILE_UA_DEFAULT='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
      ;;
    pixel7|android)
      MOBILE_W_DEFAULT=412
      MOBILE_H_DEFAULT=915
      MOBILE_DPR_DEFAULT=2.625
      MOBILE_UA_DEFAULT='Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36'
      ;;
    ipad|ipadpro)
      MOBILE_W_DEFAULT=820
      MOBILE_H_DEFAULT=1180
      MOBILE_DPR_DEFAULT=2
      MOBILE_UA_DEFAULT='Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
      ;;
    *)
      echo "[ERR] unsupported BROWSER_DEVICE: ${BROWSER_DEVICE} (use iphone14pro|pixel7|ipad)" >&2
      exit 1
      ;;
  esac
}

if [[ -f "${PIDFILE}" ]]; then
  echo "[WARN] Existing session detected. Stopping old stack first..."
  WORKDIR="${WORKDIR}" bash "${SCRIPT_DIR}/stop_vrd.sh" >/dev/null 2>&1 || true
  sleep 1
fi

mkdir -p "${WORKDIR}" "${LOGDIR}" "${KASM_HOME}/.vnc" "${CHROME_PROFILE_DIR}" "$(dirname "${KASM_PASS_FILE}")"

if [[ -z "${KASM_PASS}" ]]; then
  KASM_PASS="$(python3 - <<'PY'
import secrets,string
alphabet=string.ascii_letters+string.digits
print(''.join(secrets.choice(alphabet) for _ in range(18)))
PY
)"
fi

printf '%s\n' "${KASM_USER}" > "${KASM_USER_FILE}"
printf '%s\n' "${KASM_PASS}" > "${KASM_SECRET_FILE}"
chmod 600 "${KASM_USER_FILE}" "${KASM_SECRET_FILE}" 2>/dev/null || true

cat > "${KASM_HOME}/.vnc/xstartup" <<'EOF'
#!/usr/bin/env bash
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
xsetroot -solid "#1e1e1e"
exec fluxbox
EOF
chmod +x "${KASM_HOME}/.vnc/xstartup"

cat > "${KASM_CFG}" <<EOF
network:
  protocol: http
  interface: ${KASM_BIND}
  websocket_port: ${KASM_PORT}
  use_ipv4: true
  use_ipv6: false
  ssl:
    require_ssl: true
    pem_certificate: /etc/ssl/certs/ssl-cert-snakeoil.pem
    pem_key: /etc/ssl/private/ssl-cert-snakeoil.key

desktop:
  resolution:
    width: ${WIDTH}
    height: ${HEIGHT}
  pixel_depth: ${DEPTH}
  allow_resize: true

encoding:
  max_frame_rate: ${KASM_MAX_FPS}

user_session:
  session_type: shared
  idle_timeout: never

server:
  advanced:
    kasm_password_file: ${KASM_PASS_FILE}

command_line:
  prompt: false
EOF
chmod 600 "${KASM_CFG}" 2>/dev/null || true

ensure_ssl_group

# Ensure no stale display lock
rm -f "/tmp/.X${DISPLAY_NUM}-lock" "/tmp/.X11-unix/X${DISPLAY_NUM}" 2>/dev/null || true

# Configure non-interactive desktop selection for this HOME
HOME="${KASM_HOME}" /usr/lib/kasmvncserver/select-de.sh --select-de manual --assume-yes >/dev/null 2>&1 || true

# Set/update Kasm auth user
printf '%s\n%s\n' "${KASM_PASS}" "${KASM_PASS}" | vncpasswd -u "${KASM_USER}" -w -r "${KASM_PASS_FILE}" >/dev/null
chmod 600 "${KASM_PASS_FILE}" 2>/dev/null || true

DEFAULT_CFG="/usr/share/kasmvnc/kasmvnc_defaults.yaml"
SYSTEM_CFG="/etc/kasmvnc/kasmvnc.yaml"
CONFIG_CHAIN="${DEFAULT_CFG},${SYSTEM_CFG},${KASM_CFG}"

LOCALHOST_FLAG=()
if [[ "${KASM_BIND}" == "127.0.0.1" ]]; then
  LOCALHOST_FLAG=(-localhost)
fi

run_with_ssl_group env HOME="${KASM_HOME}" vncserver \
  ":${DISPLAY_NUM}" \
  "${LOCALHOST_FLAG[@]}" \
  -select-de manual \
  -prompt false \
  -xstartup "${KASM_HOME}/.vnc/xstartup" \
  -geometry "${GEOM}" \
  -depth "${DEPTH}" \
  -rfbport "${RFB_PORT}" \
  -websocketPort "${KASM_PORT}" \
  -interface "${KASM_BIND}" \
  -SecurityTypes Plain \
  -PlainUsers "${KASM_USER}" \
  -KasmPasswordFile "${KASM_PASS_FILE}" \
  -config "${CONFIG_CHAIN}" \
  >"${LOGDIR}/kasmvnc-start.log" 2>&1

HOSTNAME_NOW="$(uname -n)"
KASM_PID="$(cat "${KASM_HOME}/.vnc/${HOSTNAME_NOW}:${DISPLAY_NUM}.pid" 2>/dev/null || true)"
if [[ -z "${KASM_PID}" ]] || ! kill -0 "${KASM_PID}" 2>/dev/null; then
  echo "[ERR] KasmVNC did not start correctly. See ${LOGDIR}/kasmvnc-start.log" >&2
  exit 1
fi

CHROME_BIN_ACTUAL="$(pick_chrome_bin)"
CHROME_PID=""
if [[ -n "${AUTO_LAUNCH_URL}" && -n "${CHROME_BIN_ACTUAL}" ]]; then
  mkdir -p "${CHROME_PROFILE_DIR}"
  CHROME_FLAGS="$(chrome_sandbox_flags)"
  # shellcheck disable=SC2206
  CHROME_ARGS=( ${CHROME_FLAGS} )

  if [[ "${BROWSER_MOBILE_MODE}" == "1" ]]; then
    browser_mobile_profile
    MOBILE_W="${BROWSER_MOBILE_WIDTH:-${MOBILE_W_DEFAULT}}"
    MOBILE_H="${BROWSER_MOBILE_HEIGHT:-${MOBILE_H_DEFAULT}}"
    MOBILE_DPR="${BROWSER_MOBILE_DPR:-${MOBILE_DPR_DEFAULT}}"
    MOBILE_UA="${BROWSER_MOBILE_UA:-${MOBILE_UA_DEFAULT}}"

    CHROME_ARGS+=(
      "--user-agent=${MOBILE_UA}"
      "--window-size=${MOBILE_W},${MOBILE_H}"
      "--force-device-scale-factor=${MOBILE_DPR}"
      "--touch-events=enabled"
    )
  fi

  CHROME_ARGS+=(
    "--user-data-dir=${CHROME_PROFILE_DIR}"
    "--profile-directory=Default"
    "--new-window"
    "${AUTO_LAUNCH_URL}"
  )

  nohup env DISPLAY=":${DISPLAY_NUM}" "${CHROME_BIN_ACTUAL}" \
    "${CHROME_ARGS[@]}" \
    >"${LOGDIR}/chrome.log" 2>&1 &
  CHROME_PID="$!"
fi

WATCHER_PID=""
if [[ "${AUTO_STOP_IDLE_SECS}" =~ ^[0-9]+$ ]] && (( AUTO_STOP_IDLE_SECS > 0 )); then
  nohup env \
    IDLE_TIMEOUT="${AUTO_STOP_IDLE_SECS}" \
    CHECK_INTERVAL="${AUTO_STOP_CHECK_SECS}" \
    bash "${SCRIPT_DIR}/watch_vrd_idle.sh" "${PIDFILE}" \
    >"${LOGDIR}/idle-watcher.log" 2>&1 &
  WATCHER_PID="$!"
fi

cat > "${PIDFILE}" <<EOF
WORKDIR=${WORKDIR}
LOGDIR=${LOGDIR}
DISPLAY=:${DISPLAY_NUM}
DISPLAY_NUM=${DISPLAY_NUM}
GEOM=${GEOM}
DEPTH=${DEPTH}
KASM_MAX_FPS=${KASM_MAX_FPS}
MOBILE_MODE=${MOBILE_MODE}
MOBILE_PRESET=${MOBILE_PRESET}
KASM_BIND=${KASM_BIND}
KASM_PORT=${KASM_PORT}
RFB_PORT=${RFB_PORT}
KASM_HOME=${KASM_HOME}
KASM_CFG=${KASM_CFG}
KASM_PASS_FILE=${KASM_PASS_FILE}
KASM_USER_FILE=${KASM_USER_FILE}
KASM_SECRET_FILE=${KASM_SECRET_FILE}
KASM_USER=${KASM_USER}
KASM_PID=${KASM_PID}
WATCHER_PID=${WATCHER_PID}
AUTO_STOP_IDLE_SECS=${AUTO_STOP_IDLE_SECS}
AUTO_STOP_CHECK_SECS=${AUTO_STOP_CHECK_SECS}
AUTO_LAUNCH_URL=${AUTO_LAUNCH_URL}
BROWSER_MOBILE_MODE=${BROWSER_MOBILE_MODE}
BROWSER_DEVICE=${BROWSER_DEVICE}
BROWSER_MOBILE_WIDTH=${BROWSER_MOBILE_WIDTH}
BROWSER_MOBILE_HEIGHT=${BROWSER_MOBILE_HEIGHT}
BROWSER_MOBILE_DPR=${BROWSER_MOBILE_DPR}
CHROME_BIN=${CHROME_BIN_ACTUAL}
CHROME_PROFILE_DIR=${CHROME_PROFILE_DIR}
CHROME_PID=${CHROME_PID}
EOF
chmod 600 "${PIDFILE}" 2>/dev/null || true

PUBLIC_IP=""
if [[ "${KASM_BIND}" == "0.0.0.0" ]]; then
  PUBLIC_IP="$(python3 - <<'PY' 2>/dev/null || true
import urllib.request
for u in ("https://api.ipify.org", "https://ifconfig.me/ip", "https://checkip.amazonaws.com"):
    try:
        print(urllib.request.urlopen(u, timeout=2).read().decode().strip())
        break
    except Exception:
        pass
PY
)"
fi

if [[ "${KASM_BIND}" == "0.0.0.0" ]]; then
  URL_HOST="${PUBLIC_HOST:-${PUBLIC_IP:-0.0.0.0}}"
  echo "KasmVNC is up (public bind)."
  echo "URL: https://${URL_HOST}:${KASM_PORT}/"
else
  echo "KasmVNC is up (local bind)."
  echo "URL: https://127.0.0.1:${KASM_PORT}/"
  echo "SSH tunnel: ssh -L ${KASM_PORT}:127.0.0.1:${KASM_PORT} <user>@<server>"
fi

echo "Username: ${KASM_USER}"
echo "Password: ${KASM_PASS}"
echo "Display: :${DISPLAY_NUM}"
echo "PIDFILE: ${PIDFILE}"
echo "Logs: ${LOGDIR}"
if [[ -n "${WATCHER_PID}" ]]; then
  echo "Auto-stop: enabled (idle ${AUTO_STOP_IDLE_SECS}s)"
else
  echo "Auto-stop: disabled"
fi
if [[ -n "${CHROME_BIN_ACTUAL}" ]]; then
  echo "Chrome: ${CHROME_BIN_ACTUAL}"
else
  echo "Chrome: not found (install browser if needed)"
fi
if [[ "${BROWSER_MOBILE_MODE}" == "1" ]]; then
  echo "Browser mobile emulation: ON (${BROWSER_DEVICE})"
else
  echo "Browser mobile emulation: OFF"
fi

echo
echo "Automation actions (computer-use style):"
echo "  bash ${SCRIPT_DIR}/action_screenshot.sh"
echo "  bash ${SCRIPT_DIR}/action_click.sh 500 400 left"
echo "  bash ${SCRIPT_DIR}/action_type.sh 'hello world'"
echo "  bash ${SCRIPT_DIR}/action_key.sh 'ctrl+l'"
