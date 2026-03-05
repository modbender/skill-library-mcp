#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_PATH="${MOBY_CONFIG:-$ROOT_DIR/config/defaults.yaml}"

cli_path=$(python3 - <<'PY'
import os
from pathlib import Path
path = Path(os.environ.get('MOBY_CONFIG', 'config/defaults.yaml'))
cli_path = None
for line in path.read_text().splitlines():
    stripped = line.strip()
    if stripped.startswith('cli_path:'):
        value = stripped.split(':', 1)[1].split('#', 1)[0].strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        cli_path = value
        break
if not cli_path:
    cli_path = '/usr/local/bin/moby'
print(Path(cli_path).expanduser())
PY
)

echo "[verify] Config: $CONFIG_PATH"
echo "[verify] CLI path: $cli_path"

if [ ! -x "$cli_path" ]; then
  echo "[verify] ERROR: moby CLI not found or not executable at $cli_path" >&2
  exit 1
fi

set +e
"$cli_path" --version
version_status=$?
set -e
if [ $version_status -ne 0 ]; then
  echo "[verify] ERROR: moby --version failed" >&2
  exit 1
fi

echo "[verify] Checking auth status"
if ! "$cli_path" auth status --json >/tmp/moby_auth_status.json; then
  echo "[verify] ERROR: moby auth status failed" >&2
  exit 1
fi

cat /tmp/moby_auth_status.json

echo "[verify] Checking balance"
if ! "$cli_path" balance --json >/tmp/moby_balance.json; then
  echo "[verify] ERROR: moby balance failed" >&2
  exit 1
fi
cat /tmp/moby_balance.json

echo "[verify] OK"
