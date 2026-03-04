#!/usr/bin/env bash
# ============================================================
# scripts/v5/fleet-analyzer.sh — Fleet (Multi-Instance) Analysis
#
# Analyzes all agent instances in ~/.openclaw/agents/ and finds:
#   - Common patterns (across 2+ instances) → system-level issue
#   - Instance-specific patterns → model-specific tuning needed
#   - Fleet health score (weighted average)
#
# Usage:
#   fleet-analyzer.sh [--agents opus,sonnet] [--output output.json]
#
# Environment:
#   AGENTS_BASE          Base dir with agent instances (default: ~/.openclaw/agents)
#   FLEET_OUTPUT         Output file path
#   FLEET_AGENTS         Comma-separated agent list (default: auto-detect)
#   COMMON_THRESHOLD     Min instances for "common" pattern (default: 2)
#   SEA_TMP_DIR          Temp directory
#
# SECURITY MANIFEST:
#   - Reads: $AGENTS_BASE/*/sessions/*.jsonl
#   - Writes: $FLEET_OUTPUT
#   - Network: None
#   - Exec: None
# ============================================================
# shellcheck shell=bash

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="${SKILL_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

# ── Configuration ──────────────────────────────────────────
AGENTS_BASE="${AGENTS_BASE:-$HOME/.openclaw/agents}"
FLEET_OUTPUT="${FLEET_OUTPUT:-${SEA_TMP_DIR:-/tmp/sea-v5}/fleet-result.json}"
FLEET_AGENTS="${FLEET_AGENTS:-}"           # comma-separated, or auto
COMMON_THRESHOLD="${COMMON_THRESHOLD:-2}"
SEA_TMP="${SEA_TMP_DIR:-/tmp/sea-v5}"

mkdir -p "$(dirname "$FLEET_OUTPUT")" "$SEA_TMP" 2>/dev/null || true

log() { echo "[SEA-v5 fleet] $*" >&2; }

# ── Parse --agents flag ────────────────────────────────────
for arg in "$@"; do
  case "$arg" in
    --agents=*) FLEET_AGENTS="${arg#--agents=}" ;;
    --output=*) FLEET_OUTPUT="${arg#--output=}" ;;
  esac
done
# Handle space-separated args
i=1
for arg in "$@"; do
  prev_i=$((i - 1))
  prev=""
  set -- "$@"  # trick: rebuild positional params
  if [ $# -ge $prev_i ]; then
    :
  fi
  case "$arg" in
    --agents) shift; FLEET_AGENTS="${1:-}" ;;
    --output) shift; FLEET_OUTPUT="${1:-$FLEET_OUTPUT}" ;;
  esac
  i=$((i + 1))
done 2>/dev/null || true

# ── Detect agent instances ─────────────────────────────────
detect_agents() {
  if [ -n "$FLEET_AGENTS" ]; then
    echo "$FLEET_AGENTS" | tr ',' '\n'
    return
  fi

  # Auto-detect: directories with sessions/*.jsonl
  find "$AGENTS_BASE" -maxdepth 2 -type d -name "sessions" 2>/dev/null | while read -r sdir; do
    parent="$(dirname "$sdir")"
    agent_name="$(basename "$parent")"
    # Only include if has session files
    if ls "$sdir"/*.jsonl 2>/dev/null | head -1 | grep -q .; then
      echo "$agent_name"
    fi
  done
}

# ── Analyze a single agent instance ───────────────────────
analyze_agent() {
  local agent_name="$1"
  local agent_dir="$AGENTS_BASE/$agent_name"
  local sessions_dir="$agent_dir/sessions"

  if [ ! -d "$sessions_dir" ]; then
    echo "{\"agent\": \"$agent_name\", \"error\": \"sessions dir not found\", \"session_count\": 0}"
    return
  fi

  python3 - "$agent_name" "$sessions_dir" << 'PYEOF' 2>/dev/null || echo "{\"agent\": \"$1\", \"error\": \"analysis failed\"}"
import json, re, sys, os
from pathlib import Path

agent_name = sys.argv[1]
sessions_dir = Path(sys.argv[2])

# Complaint patterns (shared with v4)
complaint_patterns = {
    "ko": ["말했잖아", "왜 또", "또 그러네", "왜 자꾸", "몇 번", "다시 또"],
    "en": ["you forgot", "again?", "same mistake", "how many times", "I told you", "wrong again"]
}

session_files = list(sessions_dir.glob("*.jsonl"))
frustration_count = 0
exec_retry_count = 0
user_message_count = 0
sessions_analyzed = 0
language = "unknown"

for sf in session_files[:30]:  # cap at 30
    try:
        with open(sf, encoding='utf-8', errors='ignore') as f:
            lines = [l.strip() for l in f if l.strip()]
    except Exception:
        continue

    sessions_analyzed += 1
    session_lang = "en"
    ko_count = 0
    user_msgs = []

    for line in lines:
        try:
            d = json.loads(line)
        except Exception:
            continue

        msg = d.get('message', {}) if isinstance(d.get('message'), dict) else {}
        role = msg.get('role', d.get('role', ''))
        if role != 'user':
            continue

        content = msg.get('content', d.get('content', ''))
        if isinstance(content, list):
            text = ' '.join(
                item.get('text', '') for item in content
                if isinstance(item, dict) and item.get('type') == 'text'
            )
        else:
            text = str(content)

        if not text:
            continue
        user_message_count += 1
        user_msgs.append(text)
        if re.search(r'[가-힣]', text):
            ko_count += 1

        # Check frustration patterns
        session_lang = 'ko' if len(user_msgs) >= 3 and ko_count / len(user_msgs) > 0.5 else 'en'
        for pattern in complaint_patterns.get(session_lang, complaint_patterns['en']):
            if pattern.lower() in text.lower():
                frustration_count += 1
                break

        # Rough exec retry detection
        if re.search(r'exec.*retry|retry.*attempt', text, re.I):
            exec_retry_count += 1

    if user_msgs and ko_count / max(len(user_msgs), 1) > 0.5:
        language = 'ko'
    elif user_msgs:
        language = 'en'

# Health score: 10 - frustration_penalty - exec_penalty
frustration_rate = frustration_count / max(sessions_analyzed, 1)
exec_rate = exec_retry_count / max(sessions_analyzed, 1)
health_score = max(1.0, min(10.0, 10.0 - frustration_rate * 2 - exec_rate))

result = {
    "agent": agent_name,
    "sessions_analyzed": sessions_analyzed,
    "user_message_count": user_message_count,
    "frustration_count": frustration_count,
    "exec_retry_count": exec_retry_count,
    "health_score": round(health_score, 2),
    "primary_language": language,
    "patterns_detected": {
        "frustration_rate": round(frustration_rate, 4),
        "exec_retry_rate": round(exec_rate, 4)
    }
}
print(json.dumps(result, ensure_ascii=False))
PYEOF
}

# ── Main analysis ──────────────────────────────────────────
main() {
  log "Fleet analysis starting"
  log "AGENTS_BASE: $AGENTS_BASE"

  # Detect agents
  local agents_list
  agents_list=$(detect_agents | sort -u)

  if [ -z "$agents_list" ]; then
    log "No agent instances found in $AGENTS_BASE"
    python3 -c "
import json, sys
result = {
    'agents_analyzed': 0,
    'agents': [],
    'fleet_health': 0,
    'common_patterns': [],
    'recommendations': [],
    'error': 'No agent instances found'
}
with open(sys.argv[1], 'w') as f:
    json.dump(result, f, indent=2)
" "$FLEET_OUTPUT" 2>/dev/null || true
    return 0
  fi

  log "Found agents: $(echo "$agents_list" | tr '\n' ' ')"

  # Analyze each agent
  local agent_results_file="$SEA_TMP/fleet-agents.json"
  echo "[" > "$agent_results_file"
  local first=true

  while IFS= read -r agent; do
    [ -n "$agent" ] || continue
    log "Analyzing agent: $agent"

    local result
    result=$(analyze_agent "$agent")

    if [ "$first" = "true" ]; then
      first=false
    else
      echo "," >> "$agent_results_file"
    fi
    echo "$result" >> "$agent_results_file"
  done <<< "$agents_list"

  echo "]" >> "$agent_results_file"

  # Cross-agent analysis + output generation
  python3 - "$agent_results_file" "$FLEET_OUTPUT" "$COMMON_THRESHOLD" << 'PYEOF' 2>/dev/null || true
import json, sys

agents_file   = sys.argv[1]
output_file   = sys.argv[2]
common_thresh = int(sys.argv[3])

agents = []
try:
    with open(agents_file) as f:
        agents = json.load(f)
except Exception as e:
    agents = []

# Compute fleet health (weighted average of individual scores)
valid_agents = [a for a in agents if 'health_score' in a]
fleet_health = (
    sum(a['health_score'] for a in valid_agents) / len(valid_agents)
    if valid_agents else 0.0
)

# Find common patterns (issues in >= common_thresh agents)
high_frustration = [a['agent'] for a in valid_agents if a.get('frustration_count', 0) >= 3]
high_exec_retry  = [a['agent'] for a in valid_agents if a.get('exec_retry_count', 0) >= 3]

common_patterns = []
if len(high_frustration) >= common_thresh:
    common_patterns.append({
        "pattern": "high_frustration",
        "agents_affected": high_frustration,
        "is_systemic": len(high_frustration) >= common_thresh,
        "recommendation": "System-level AGENTS.md improvement needed"
    })
if len(high_exec_retry) >= common_thresh:
    common_patterns.append({
        "pattern": "exec_retry_loops",
        "agents_affected": high_exec_retry,
        "is_systemic": True,
        "recommendation": "Add exec retry limit rule to shared AGENTS.md"
    })

# Recommendations
recommendations = []
for a in valid_agents:
    if a.get('frustration_count', 0) >= 5:
        recommendations.append({
            "priority": "high",
            "type": "improvement",
            "target": a['agent'],
            "message": f"{a['agent']}: {a['frustration_count']} frustration signals — context management"
        })

# Best performer
if valid_agents:
    best = max(valid_agents, key=lambda x: x['health_score'])
    for a in valid_agents:
        if a['agent'] != best['agent'] and a['health_score'] < best['health_score'] - 1.0:
            recommendations.append({
                "priority": "medium",
                "type": "transfer",
                "source": best['agent'],
                "target": a['agent'],
                "message": f"Transfer best practices from {best['agent']} ({best['health_score']}) to {a['agent']} ({a['health_score']})"
            })

result = {
    "agents_analyzed": len(agents),
    "agents": agents,
    "fleet": {
        "health_score": round(fleet_health, 2),
        "agent_count": len(valid_agents)
    },
    "fleet_health": round(fleet_health, 2),
    "common_patterns": common_patterns,
    "recommendations": recommendations,
    "summary": {
        "systemic_issues": len([p for p in common_patterns if p.get('is_systemic')]),
        "total_recommendations": len(recommendations)
    }
}

with open(output_file, 'w') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"[SEA-v5 fleet] {len(agents)} agents analyzed, fleet health: {fleet_health:.1f}", file=sys.stderr)
PYEOF

  log "Fleet analysis complete: $FLEET_OUTPUT"
}

main "$@"
