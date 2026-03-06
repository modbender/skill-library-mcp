#!/bin/bash
set -euo pipefail

# install.sh — Install an executable as a macOS launchd user agent
# Usage: install.sh <service-name> <command> [args...] [--workdir <dir>] [--env KEY=VALUE ...]

usage() {
  echo "Usage: $0 <service-name> <command> [args...] [--workdir <dir>] [--env KEY=VALUE ...]"
  exit 1
}

[[ $# -lt 2 ]] && usage

SERVICE_NAME="$1"; shift
LABEL="ai.toolguard.${SERVICE_NAME}"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="${PLIST_DIR}/${LABEL}.plist"
LOG_DIR="$HOME/Library/Logs/toolguard/${SERVICE_NAME}"
WORKDIR="$HOME"

# Parse command, args, and options
COMMAND=""
ARGS=()
ENV_VARS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workdir)
      WORKDIR="$2"; shift 2 ;;
    --env)
      ENV_VARS+=("$2"); shift 2 ;;
    *)
      if [[ -z "$COMMAND" ]]; then
        COMMAND="$1"
      else
        ARGS+=("$1")
      fi
      shift ;;
  esac
done

[[ -z "$COMMAND" ]] && usage

# Resolve command to absolute path
if [[ "$COMMAND" != /* ]]; then
  RESOLVED=$(which "$COMMAND" 2>/dev/null || true)
  if [[ -n "$RESOLVED" ]]; then
    COMMAND="$RESOLVED"
  else
    echo "Error: Cannot resolve '$COMMAND' to an absolute path."
    exit 1
  fi
fi

# Expand workdir
WORKDIR=$(eval echo "$WORKDIR")

# Create directories
mkdir -p "$PLIST_DIR" "$LOG_DIR"

# Unload existing service if present
if launchctl list "$LABEL" &>/dev/null; then
  echo "Unloading existing service ${LABEL}..."
  launchctl unload "$PLIST_PATH" 2>/dev/null || true
fi

# Build ProgramArguments
PROGRAM_ARGS="    <array>
      <string>${COMMAND}</string>"
for arg in "${ARGS[@]}"; do
  PROGRAM_ARGS+="
      <string>${arg}</string>"
done
PROGRAM_ARGS+="
    </array>"

# Build EnvironmentVariables section
ENV_SECTION=""
if [[ ${#ENV_VARS[@]} -gt 0 ]]; then
  ENV_SECTION="    <key>EnvironmentVariables</key>
    <dict>"
  for env_pair in "${ENV_VARS[@]}"; do
    KEY="${env_pair%%=*}"
    VALUE="${env_pair#*=}"
    ENV_SECTION+="
      <key>${KEY}</key>
      <string>${VALUE}</string>"
  done
  ENV_SECTION+="
    </dict>"
fi

# Write plist
cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${LABEL}</string>
    <key>ProgramArguments</key>
${PROGRAM_ARGS}
    <key>WorkingDirectory</key>
    <string>${WORKDIR}</string>
    <key>StandardOutPath</key>
    <string>${LOG_DIR}/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/stderr.log</string>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
${ENV_SECTION}
</dict>
</plist>
EOF

# Load and start service
launchctl load "$PLIST_PATH"

echo "Service '${SERVICE_NAME}' installed and started."
echo "  Label:  ${LABEL}"
echo "  Plist:  ${PLIST_PATH}"
echo "  Logs:   ${LOG_DIR}/"
echo "  Status: $(launchctl list "$LABEL" 2>/dev/null | head -1 || echo 'unknown')"
