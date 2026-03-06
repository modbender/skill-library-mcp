#!/usr/bin/env bash
set -euo pipefail

# Compatibility wrapper. Canonical skill interface is now Python-first via xclaw_agent_skill.py.
base_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${base_dir}/xclaw_agent_skill.py" "$@"
