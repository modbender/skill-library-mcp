#!/usr/bin/env bash
# Memory Mastery - Audit Script
# Diagnoses the current memory system state in an OpenClaw workspace.
# Usage: bash audit.sh [workspace_path]
# Output: JSON report to stdout

set -euo pipefail

WORKSPACE="${1:-${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}}"

# Helper: check if command exists
has_cmd() { command -v "$1" &>/dev/null; }

# Check MEMORY.md
memory_md="$WORKSPACE/MEMORY.md"
if [ -f "$memory_md" ]; then
  memory_md_exists=true
  memory_md_size=$(wc -c < "$memory_md" | tr -d ' ')
  memory_md_lines=$(wc -l < "$memory_md" | tr -d ' ')
else
  memory_md_exists=false
  memory_md_size=0
  memory_md_lines=0
fi

# Check memory/ directory
memory_dir="$WORKSPACE/memory"
if [ -d "$memory_dir" ]; then
  memory_dir_exists=true
  memory_file_count=$(find "$memory_dir" -name '*.md' -type f 2>/dev/null | wc -l | tr -d ' ')
  if [ "$memory_file_count" -gt 0 ]; then
    memory_total_size=$(find "$memory_dir" -name '*.md' -type f -exec cat {} + 2>/dev/null | wc -c | tr -d ' ')
    memory_oldest=$(find "$memory_dir" -name '????-??-??.md' -type f 2>/dev/null | sort | head -1 | xargs basename 2>/dev/null | sed 's/.md$//' || echo "unknown")
    memory_newest=$(find "$memory_dir" -name '????-??-??.md' -type f 2>/dev/null | sort | tail -1 | xargs basename 2>/dev/null | sed 's/.md$//' || echo "unknown")
  else
    memory_total_size=0
    memory_oldest="none"
    memory_newest="none"
  fi
else
  memory_dir_exists=false
  memory_file_count=0
  memory_total_size=0
  memory_oldest="none"
  memory_newest="none"
fi

# Check AGENTS.md for memory rules
agents_md="$WORKSPACE/AGENTS.md"
if [ -f "$agents_md" ]; then
  agents_md_exists=true
  if grep -qi "memory\|記憶" "$agents_md" 2>/dev/null; then
    has_memory_rules=true
  else
    has_memory_rules=false
  fi
else
  agents_md_exists=false
  has_memory_rules=false
fi

# Check HEARTBEAT.md for memory maintenance
heartbeat_md="$WORKSPACE/HEARTBEAT.md"
if [ -f "$heartbeat_md" ]; then
  heartbeat_exists=true
  if grep -qi "memory\|maintenance\|メンテ\|統合" "$heartbeat_md" 2>/dev/null; then
    has_memory_maintenance=true
  else
    has_memory_maintenance=false
  fi
else
  heartbeat_exists=false
  has_memory_maintenance=false
fi

# Check OpenClaw config for memory search
config_file="$HOME/.openclaw/openclaw.json"
if [ -f "$config_file" ]; then
  if has_cmd python3; then
    memory_search_enabled=$(python3 -c "
import json, sys
try:
    c = json.load(open('$config_file'))
    slots = c.get('plugins',{}).get('slots',{})
    mem = slots.get('memory','memory-core')
    print('true' if mem and mem != 'none' else 'false')
except: print('unknown')
" 2>/dev/null || echo "unknown")
  else
    memory_search_enabled="unknown"
  fi
else
  memory_search_enabled="unknown"
fi

# Output JSON
cat <<EOF
{
  "workspace": "$WORKSPACE",
  "memory_md": {
    "exists": $memory_md_exists,
    "size_bytes": $memory_md_size,
    "lines": $memory_md_lines
  },
  "memory_dir": {
    "exists": $memory_dir_exists,
    "file_count": $memory_file_count,
    "total_size_bytes": $memory_total_size,
    "oldest_date": "$memory_oldest",
    "newest_date": "$memory_newest"
  },
  "agents_md": {
    "exists": $agents_md_exists,
    "has_memory_rules": $has_memory_rules
  },
  "heartbeat": {
    "exists": $heartbeat_exists,
    "has_memory_maintenance": $has_memory_maintenance
  },
  "memory_search": {
    "enabled": $memory_search_enabled
  }
}
EOF
