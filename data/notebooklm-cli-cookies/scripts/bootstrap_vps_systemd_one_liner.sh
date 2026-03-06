#!/usr/bin/env bash
set -euo pipefail

# One-liner bootstrap for OpenClaw + NotebookLM on generic VPS (Ubuntu/Debian).
#
# This script is designed to ship INSIDE the ClawHub skill bundle, so the user can:
# 1) clawhub install notebooklm-cli-cookies
# 2) bash ./skills/notebooklm-cli/scripts/bootstrap_vps_systemd_one_liner.sh --service <unit>
# 3) copy /etc/openclaw/notebooklm-auth.json
#
# What it does:
# - Installs prerequisites: jq, pipx, python3-pip/python3-venv
# - Installs NotebookLM CLI: notebooklm-mcp-cli (provides `nlm`)
# - Installs ClawHub CLI (provides `clawhub`) if missing
# - Ensures the skill exists in the target workspace (skips install if already present)
# - Creates/updates ~/.openclaw/openclaw.json to inject NOTEBOOKLM_MCP_CLI_PATH
# - Creates a helper injector script and (optional) a systemd drop-in for your OpenClaw service
#
# What it does NOT do:
# - It does not obtain Google/NotebookLM cookies. You must provide notebooklm-auth.json.

SLUG_DEFAULT="notebooklm-cli-cookies"
SKILL_NAME_DEFAULT="notebooklm-cli"

WORKDIR=""
TARGET_USER=""
OPENCLOW_SERVICE=""
NLM_STORAGE=""
AUTH_FILE="/etc/openclaw/notebooklm-auth.json"
SKILL_NAME="${SKILL_NAME_DEFAULT}"
SLUG="${SLUG_DEFAULT}"

usage() {
  cat <<'EOF'
Usage: bootstrap_vps_systemd_one_liner.sh [options]

Options:
  --workdir <dir>        OpenClaw workspace directory (default: /home/<user>/.openclaw/workspace)
  --user <name>          Linux user running OpenClaw (default: current user or SUDO_USER)
  --service <unit>       systemd unit name for OpenClaw (optional)
  --nlm-storage <dir>    NOTEBOOKLM_MCP_CLI_PATH (default: /home/<user>/.notebooklm-mcp-cli)
  --auth-file <path>     NotebookLM auth JSON file path (default: /etc/openclaw/notebooklm-auth.json)
  --slug <slug>          ClawHub skill slug (default: notebooklm-cli-cookies)
  --skill-name <name>    OpenClaw skill name/folder (default: notebooklm-cli)
  -h, --help             Show help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workdir) WORKDIR="$2"; shift 2;;
    --user) TARGET_USER="$2"; shift 2;;
    --service) OPENCLOW_SERVICE="$2"; shift 2;;
    --nlm-storage) NLM_STORAGE="$2"; shift 2;;
    --auth-file) AUTH_FILE="$2"; shift 2;;
    --slug) SLUG="$2"; shift 2;;
    --skill-name) SKILL_NAME="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2;;
  esac
done

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "Error: this bootstrap is intended for Linux VPS." >&2
  exit 1
fi

if [[ -z "${TARGET_USER}" ]]; then
  TARGET_USER="${SUDO_USER:-$(id -un)}"
fi

TARGET_HOME="$(getent passwd "${TARGET_USER}" | cut -d: -f6 || true)"
if [[ -z "${TARGET_HOME}" ]]; then
  echo "Error: could not resolve home directory for user: ${TARGET_USER}" >&2
  exit 1
fi

if [[ -z "${WORKDIR}" ]]; then
  WORKDIR="${TARGET_HOME}/.openclaw/workspace"
fi

if [[ -z "${NLM_STORAGE}" ]]; then
  NLM_STORAGE="${TARGET_HOME}/.notebooklm-mcp-cli"
fi

require_sudo() {
  if [[ "$(id -u)" -ne 0 ]]; then
    if ! command -v sudo >/dev/null 2>&1; then
      echo "Error: sudo is required (run as root or install sudo)." >&2
      exit 1
    fi
  fi
}

as_user() {
  local cmd="$1"
  if [[ "$(id -un)" == "${TARGET_USER}" ]]; then
    bash -lc "${cmd}"
  else
    sudo -u "${TARGET_USER}" -H bash -lc "${cmd}"
  fi
}

require_sudo

echo "[1/7] Installing OS packages (jq, pipx, python tooling)..."
sudo apt-get update -y
sudo apt-get install -y jq python3-pip python3-venv pipx

echo "[2/7] Installing notebooklm-mcp-cli (nlm)..."
if as_user "command -v nlm >/dev/null 2>&1"; then
  echo "nlm already installed; skipping install."
else
  if as_user "command -v pipx >/dev/null 2>&1"; then
    as_user "pipx install notebooklm-mcp-cli >/dev/null 2>&1 || pipx upgrade notebooklm-mcp-cli >/dev/null 2>&1 || true"
    as_user "pipx ensurepath >/dev/null 2>&1 || true"
  fi

  if ! as_user "command -v nlm >/dev/null 2>&1"; then
    # Fallback for environments where pipx is unavailable/misconfigured.
    as_user "python3 -m pip install --user --upgrade --break-system-packages notebooklm-mcp-cli"
  fi

  if ! as_user "command -v nlm >/dev/null 2>&1"; then
    echo "Error: failed to install 'nlm'. Install manually with one of:" >&2
    echo "  pipx install notebooklm-mcp-cli" >&2
    echo "  python3 -m pip install --user --upgrade --break-system-packages notebooklm-mcp-cli" >&2
    exit 1
  fi
fi

echo "[3/7] Installing ClawHub CLI (clawhub) if missing..."
if ! command -v clawhub >/dev/null 2>&1; then
  if command -v npm >/dev/null 2>&1; then
    sudo npm i -g clawhub
  elif command -v pnpm >/dev/null 2>&1; then
    sudo pnpm add -g clawhub
  else
    echo "Error: clawhub is missing and neither npm nor pnpm is available." >&2
    echo "Install one of them, then run: npm i -g clawhub  (or pnpm add -g clawhub)" >&2
    exit 1
  fi
fi

echo "[4/7] Ensuring the skill exists in the workspace..."
as_user "mkdir -p \"${WORKDIR}\""
SKILL_DIR="${WORKDIR}/skills/${SKILL_NAME}"
if as_user "[[ -f \"${SKILL_DIR}/SKILL.md\" ]]"; then
  echo "Skill already present at: ${SKILL_DIR} (skipping clawhub install)"
else
  as_user "cd \"${WORKDIR}\" && clawhub install \"${SLUG}\""
fi

echo "[5/7] Creating helper injector script..."
INJECT_BIN_DIR="${TARGET_HOME}/.openclaw/bin"
INJECT_BIN="${INJECT_BIN_DIR}/notebooklm-auth-inject"
sudo -u "${TARGET_USER}" -H mkdir -p "${INJECT_BIN_DIR}"

cat > /tmp/notebooklm-auth-inject.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required but not installed." >&2
  exit 1
fi

AUTH_FILE="${NOTEBOOKLM_AUTH_FILE:-/etc/openclaw/notebooklm-auth.json}"
NOTEBOOKLM_MCP_CLI_PATH="${NOTEBOOKLM_MCP_CLI_PATH:-}"

if [[ -z "${NOTEBOOKLM_MCP_CLI_PATH}" ]]; then
  echo "Error: NOTEBOOKLM_MCP_CLI_PATH is not set." >&2
  exit 1
fi

if [[ ! -f "${AUTH_FILE}" ]]; then
  echo "Error: auth file not found: ${AUTH_FILE}" >&2
  exit 1
fi

PROFILE_DIR="${NOTEBOOKLM_MCP_CLI_PATH}/profiles/default"
mkdir -p "${PROFILE_DIR}"

SECRET_JSON="$(cat "${AUTH_FILE}")"

if ! echo "${SECRET_JSON}" | jq -e '.cookies' >/dev/null 2>&1; then
  echo "Error: auth JSON must include .cookies" >&2
  exit 1
fi

echo "${SECRET_JSON}" | jq '.cookies' > "${PROFILE_DIR}/cookies.json"

if echo "${SECRET_JSON}" | jq -e '.metadata' >/dev/null 2>&1; then
  echo "${SECRET_JSON}" | jq '.metadata' > "${PROFILE_DIR}/metadata.json"
else
  jq -n --arg now "$(date -u +"%Y-%m-%dT%H:%M:%S")" \
    '{csrf_token:"", session_id:"", email:null, last_validated:$now}' \
    > "${PROFILE_DIR}/metadata.json"
fi

chmod 700 "${NOTEBOOKLM_MCP_CLI_PATH}" "${NOTEBOOKLM_MCP_CLI_PATH}/profiles" "${PROFILE_DIR}" || true
chmod 600 "${PROFILE_DIR}/cookies.json" "${PROFILE_DIR}/metadata.json" || true

echo "OK: injected NotebookLM auth into ${PROFILE_DIR}"
EOF

sudo mv /tmp/notebooklm-auth-inject.sh "${INJECT_BIN}"
sudo chown "${TARGET_USER}":"${TARGET_USER}" "${INJECT_BIN}"
sudo chmod 0755 "${INJECT_BIN}"

echo "[6/7] Ensuring OpenClaw config injects NOTEBOOKLM_MCP_CLI_PATH..."
OPENCLOW_DIR="${TARGET_HOME}/.openclaw"
OPENCLOW_CFG="${OPENCLOW_DIR}/openclaw.json"
sudo -u "${TARGET_USER}" -H mkdir -p "${OPENCLOW_DIR}"

OPENCLOW_CFG_ENV="${OPENCLOW_CFG}" \
SKILL_NAME_ENV="${SKILL_NAME}" \
NLM_STORAGE_ENV="${NLM_STORAGE}" \
TARGET_HOME_ENV="${TARGET_HOME}" \
python3 - <<'PY'
import json
import os
import pathlib
import sys

cfg_path = pathlib.Path(os.environ["OPENCLOW_CFG_ENV"])
skill_name = os.environ["SKILL_NAME_ENV"]
nlm_path = os.environ["NLM_STORAGE_ENV"]
target_home = os.environ["TARGET_HOME_ENV"]

data = {}
if cfg_path.exists():
    try:
        data = json.loads(cfg_path.read_text())
    except Exception:
        print(f"WARNING: {cfg_path} is not strict JSON. Skipping auto-edit.")
        print("Add this snippet manually under skills.entries:")
        print(json.dumps({
            skill_name: {"enabled": True, "env": {"NOTEBOOKLM_MCP_CLI_PATH": nlm_path}}
        }, indent=2))
        sys.exit(0)

data.setdefault("skills", {}).setdefault("entries", {}).setdefault(skill_name, {})
entry = data["skills"]["entries"][skill_name]
entry.setdefault("enabled", True)
entry.setdefault("env", {})
entry["env"].setdefault("NOTEBOOKLM_MCP_CLI_PATH", nlm_path)
entry["env"].setdefault("PATH", f"{target_home}/.local/bin:/usr/local/bin:/usr/bin:/bin")

cfg_path.write_text(json.dumps(data, indent=2) + "\\n")
PY

sudo chown "${TARGET_USER}":"${TARGET_USER}" "${OPENCLOW_CFG}" || true

echo "[7/7] Setting up systemd integration (optional)..."

sudo mkdir -p /etc/openclaw
sudo touch "${AUTH_FILE}"
sudo chown root:root "${AUTH_FILE}"

if ! getent group openclaw >/dev/null 2>&1; then
  sudo groupadd openclaw
fi
sudo usermod -aG openclaw "${TARGET_USER}" || true
sudo chgrp openclaw "${AUTH_FILE}"
sudo chmod 0640 "${AUTH_FILE}"

if [[ -n "${OPENCLOW_SERVICE}" ]]; then
  sudo mkdir -p "/etc/systemd/system/${OPENCLOW_SERVICE}.d"
  cat > "/tmp/notebooklm-dropin.conf" <<EOF
[Service]
Environment=NOTEBOOKLM_MCP_CLI_PATH=${NLM_STORAGE}
Environment=NOTEBOOKLM_AUTH_FILE=${AUTH_FILE}
ExecStartPre=${INJECT_BIN}
EOF
  sudo mv "/tmp/notebooklm-dropin.conf" "/etc/systemd/system/${OPENCLOW_SERVICE}.d/notebooklm.conf"
  sudo systemctl daemon-reload
  echo "Installed systemd drop-in: /etc/systemd/system/${OPENCLOW_SERVICE}.d/notebooklm.conf"
  echo "Restarting service: ${OPENCLOW_SERVICE}"
  sudo systemctl restart "${OPENCLOW_SERVICE}" || true
else
  echo "No --service provided. Skipping systemd drop-in."
fi

cat <<EOF

Bootstrap completed.

Next required step (you must do this once):
1) Put your NotebookLM auth JSON at:
   ${AUTH_FILE}
   (keep permissions 640 root:openclaw)

Then run:
  sudo -u ${TARGET_USER} -H NOTEBOOKLM_MCP_CLI_PATH="${NLM_STORAGE}" NOTEBOOKLM_AUTH_FILE="${AUTH_FILE}" ${INJECT_BIN}
  sudo -u ${TARGET_USER} -H NOTEBOOKLM_MCP_CLI_PATH="${NLM_STORAGE}" nlm login --check

Telegram tests (after OpenClaw restart):
  /nlm login --check
  /nlm notebook list --json

EOF

