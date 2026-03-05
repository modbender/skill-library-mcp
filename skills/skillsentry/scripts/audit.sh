#!/usr/bin/env bash
set -euo pipefail

WORKDIR="${WORKDIR:-/Users/BillyAssist/clawd}"
OUTDIR="${OUTDIR:-/Users/BillyAssist/clawd/skills/frenzy-auditor}"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
TMPDIR="$(mktemp -d)"

cleanup() { rm -rf "$TMPDIR"; }
trap cleanup EXIT

# Capture status commands
OPENCLAW_STATUS_FILE="$TMPDIR/openclaw_status.txt"
GATEWAY_STATUS_FILE="$TMPDIR/gateway_status.txt"
SESSION_STATUS_FILE="$TMPDIR/session_status.txt"

(openclaw status || true) >"$OPENCLAW_STATUS_FILE" 2>&1
(openclaw gateway status || true) >"$GATEWAY_STATUS_FILE" 2>&1
(session_status || true) >"$SESSION_STATUS_FILE" 2>&1

# Prompt-injection pattern scan
PI_PATTERNS='(ignore (all|previous) instructions|system prompt|developer message|tool call|jailbreak|do not follow|exfiltrate|leak|override|bypass|prompt injection|function call|tool output|BEGIN PROMPT|END PROMPT)'
PI_SCAN_FILE="$TMPDIR/pi_scan.txt"

# scan memory + workspace text files (safe, local)
SCAN_PATHS=("$WORKDIR/memory" "$WORKDIR/skills" )
>"$PI_SCAN_FILE"
for p in "${SCAN_PATHS[@]}"; do
  if [ -e "$p" ]; then
    grep -RInE --exclude-dir='.git' --exclude='*.png' --exclude='*.jpg' --exclude='*.jpeg' --exclude='*.gif' --exclude='*.webp' \
      "$PI_PATTERNS" "$p" >>"$PI_SCAN_FILE" 2>/dev/null || true
  fi
done

# Local port scan (safe, loopback only)
PORT_SCAN_FILE="$TMPDIR/port_scan.txt"
if command -v nmap >/dev/null 2>&1; then
  (nmap -Pn -p 1-1024 127.0.0.1 || true) >"$PORT_SCAN_FILE" 2>&1
else
  echo "nmap not installed" >"$PORT_SCAN_FILE"
fi

# Build JSON report
export TS OPENCLAW_STATUS_FILE GATEWAY_STATUS_FILE SESSION_STATUS_FILE PI_SCAN_FILE PORT_SCAN_FILE
python3 - <<'PY'
import json, os
from pathlib import Path

def read_file(path):
    try:
        return Path(path).read_text(errors='ignore')
    except Exception as e:
        return f"ERROR: {e}"

report = {
    "timestamp": os.environ.get("TS", ""),
    "openclaw_status": read_file(os.environ["OPENCLAW_STATUS_FILE"]),
    "gateway_status": read_file(os.environ["GATEWAY_STATUS_FILE"]),
    "session_status": read_file(os.environ["SESSION_STATUS_FILE"]),
    "prompt_injection_hits": [l for l in read_file(os.environ["PI_SCAN_FILE"]).splitlines() if l.strip()],
    "local_port_scan": read_file(os.environ["PORT_SCAN_FILE"]),
}
print(json.dumps(report, indent=2))
PY
