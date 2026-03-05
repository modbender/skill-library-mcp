#!/usr/bin/env bash
set -euo pipefail

# Installs a sudo shim at ~/.openclaw/bin/sudo (matches live_assessment checks).
# For the shim to be used, OpenClaw's runtime PATH must include ~/.openclaw/bin
# before /usr/bin. This script attempts best-effort PATH injection for macOS
# LaunchAgent installs of the gateway.

log() {
  printf '[cyber-security-engineer] %s\n' "$*"
}

REAL_SUDO="$(command -v sudo || true)"
if [[ -z "${REAL_SUDO}" ]]; then
  log "sudo not found; nothing to install."
  exit 1
fi

OPENCLAW_DIR="${HOME}/.openclaw"
BIN_DIR="${OPENCLAW_DIR}/bin"
SKILL_DIR_DEFAULT="${OPENCLAW_DIR}/workspace/skills/cyber-security-engineer"

mkdir -p "${BIN_DIR}"
chmod 700 "${OPENCLAW_DIR}" "${BIN_DIR}" || true

WRAPPER="${BIN_DIR}/sudo"
cat > "${WRAPPER}" <<EOF
#!/usr/bin/env bash
set -euo pipefail

REAL_SUDO="\${OPENCLAW_REAL_SUDO:-${REAL_SUDO}}"
SKILL_DIR="\${OPENCLAW_CYBER_SKILL_DIR:-${SKILL_DIR_DEFAULT}}"

# Pass-through for sudo bookkeeping.
if [[ \$# -eq 0 ]]; then
  exec "\${REAL_SUDO}"
fi
case "\${1:-}" in
  -h|--help|-V|--version|-v|-l|-k)
    exec "\${REAL_SUDO}" "\$@"
    ;;
esac

# Refuse non-interactive privilege escalation by default (safety).
if [[ ! -t 0 && "\${OPENCLAW_ALLOW_NONINTERACTIVE_SUDO:-0}" != "1" ]]; then
  echo "[cyber-security-engineer] Refusing non-interactive sudo (set OPENCLAW_ALLOW_NONINTERACTIVE_SUDO=1 to override)." >&2
  exit 2
fi

REASON="\${OPENCLAW_PRIV_REASON:-OpenClaw requested privileged execution}"
export OPENCLAW_REAL_SUDO="\${REAL_SUDO}"
exec python3 "\${SKILL_DIR}/scripts/guarded_privileged_exec.py" \\
  --reason "\${REASON}" \\
  --use-sudo \\
  -- "\$@"
EOF
chmod 755 "${WRAPPER}"

log "Installed sudo shim: ${WRAPPER}"

if [[ "$(uname -s)" == "Darwin" ]]; then
  PLIST="${HOME}/Library/LaunchAgents/ai.openclaw.gateway.plist"
  if [[ -f "${PLIST}" ]] && command -v /usr/libexec/PlistBuddy >/dev/null 2>&1; then
    # Ensure EnvironmentVariables exists and prepend ~/.openclaw/bin to PATH.
    /usr/libexec/PlistBuddy -c "Add :EnvironmentVariables dict" "${PLIST}" 2>/dev/null || true
    EXISTING_PATH="$(/usr/libexec/PlistBuddy -c "Print :EnvironmentVariables:PATH" "${PLIST}" 2>/dev/null || true)"
    if [[ -z "${EXISTING_PATH}" ]]; then
      NEW_PATH="${BIN_DIR}:/usr/bin:/bin:/usr/sbin:/sbin"
      /usr/libexec/PlistBuddy -c "Add :EnvironmentVariables:PATH string ${NEW_PATH}" "${PLIST}" 2>/dev/null || \
        /usr/libexec/PlistBuddy -c "Set :EnvironmentVariables:PATH ${NEW_PATH}" "${PLIST}" 2>/dev/null || true
      log "Updated gateway LaunchAgent PATH to include ${BIN_DIR}"
    else
      case ":${EXISTING_PATH}:" in
        *":${BIN_DIR}:"*) ;;
        *)
          NEW_PATH="${BIN_DIR}:${EXISTING_PATH}"
          /usr/libexec/PlistBuddy -c "Set :EnvironmentVariables:PATH ${NEW_PATH}" "${PLIST}" 2>/dev/null || true
          log "Prepended ${BIN_DIR} to gateway LaunchAgent PATH"
          ;;
      esac
    fi
  else
    log "macOS gateway plist not found or PlistBuddy unavailable; PATH must include ${BIN_DIR} manually."
  fi
else
  log "Non-macOS: ensure the OpenClaw gateway process PATH includes ${BIN_DIR} before /usr/bin."
fi

log "Restart the OpenClaw gateway to apply:"
log "  openclaw gateway restart"

