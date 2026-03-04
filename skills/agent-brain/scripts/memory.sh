#!/bin/bash
# memory.sh — Thin dispatcher for Agent Brain v4
# Routes all commands to brain.py (Python engine with pluggable storage)
#
# Usage: ./scripts/memory.sh <command> [args]
#
# Environment:
#   MEMORY_DIR           Path to memory directory (default: ../memory)
#   AGENT_BRAIN_BACKEND  Storage backend: 'sqlite' (default) or 'json'
#   AGENT_BRAIN_SUPERMEMORY_SYNC  SuperMemory sync mode: auto|on|off
#   AGENT_BRAIN_PII_MODE PII policy: strict (default) | off
#   SUPERMEMORY_API_KEY  Optional API key for cloud mirror
#   AGENT_BRAIN_ENV_FILE Optional local env file (default: ../.env)
#
# Core Commands:
#   init                                              Initialize memory
#   add <type> <content> [source] [tags] [url] [ctx]  Add an entry
#   get <query> [--policy] [--stores] [--explain]    Hybrid retrieval
#   loop <message> [--user-feedback] [--response] [--policy] [--stores] Orchestrated retrieve/extract/learn
#   list [type]                                       List all or by type
#   update <id> <field> <value>                       Update a field on an entry
#   touch <id>                                        Mark as accessed
#   supersede <old_id> <new_id>                       Mark entry as superseded
#
# Learning Commands:
#   conflicts <content>                               Find potential conflicts
#   similar <content> [threshold]                     Find related entries (TF-IDF)
#   correct <wrong_id> <right> [reason] [tags]        Track a correction
#   success <id> [context]                            Record successful use
#
# Analysis Commands:
#   reflect                                           Memory health analysis
#   consolidate                                       Find consolidation candidates
#   tags                                              List tag hierarchy
#   decay                                             Downgrade stale entries
#   export                                            Dump full JSON
#   stats                                             Memory statistics
#   log [count] [action]                               Activity log
#
# Session Commands:
#   session [context]                                 Start new session

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export MEMORY_DIR="${MEMORY_DIR:-$(cd "$SCRIPT_DIR/../memory" && pwd 2>/dev/null || echo "$SCRIPT_DIR/../memory")}"

# Optional local env auto-load for standalone skill packaging.
if [[ -z "${SUPERMEMORY_API_KEY:-}" ]]; then
  SUPERMEMORY_ENV="${AGENT_BRAIN_ENV_FILE:-$SCRIPT_DIR/../.env}"
  if [[ -f "$SUPERMEMORY_ENV" ]]; then
    parsed_key="$(python3 - "$SUPERMEMORY_ENV" <<'PY'
import sys

path = sys.argv[1]
value = ""
with open(path, "r", encoding="utf-8") as fh:
    for raw in fh:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        if key.startswith("export "):
            key = key[len("export "):].strip()
        if key != "SUPERMEMORY_API_KEY":
            continue
        val = val.strip()
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        value = val
        break
print(value)
PY
)"
    if [[ -n "$parsed_key" ]]; then
      export SUPERMEMORY_API_KEY="$parsed_key"
    fi
  fi
fi

exec python3 "$SCRIPT_DIR/brain.py" "$@"
