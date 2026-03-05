#!/usr/bin/env bash
# Summarize recent session transcripts for self-reflection.
# Usage: summarize-sessions.sh [active_minutes]
#
# Outputs a condensed view of recent sessions: session key, age,
# and the last N user/assistant exchanges (stripped of tool noise).

set -euo pipefail

ACTIVE_MINUTES="${1:-120}"
SESSIONS_DIR="$HOME/.openclaw/agents/main/sessions"
MAX_LINES=50  # tail this many lines per session

# Get active sessions as JSON
sessions_json=$(openclaw sessions --active "$ACTIVE_MINUTES" --json 2>/dev/null)

# Parse session list
echo "$sessions_json" | python3 -c "
import json, sys, os, subprocess

data = json.load(sys.stdin)
sessions = data.get('sessions', [])
sessions_dir = '$SESSIONS_DIR'
max_lines = $MAX_LINES

for s in sessions:
    key = s.get('key', '')
    session_id = s.get('sessionId', '')
    age_ms = s.get('ageMs', 0)
    tokens = s.get('totalTokens', 0)

    # Skip subagent sessions and self-reflection cron sessions
    if ':subagent:' in key:
        continue

    age_min = age_ms // 60000

    # Find the session file
    jsonl_path = os.path.join(sessions_dir, f'{session_id}.jsonl')
    if not os.path.exists(jsonl_path):
        # Try topic variants
        candidates = [f for f in os.listdir(sessions_dir)
                      if f.startswith(session_id) and f.endswith('.jsonl')
                      and not '.deleted.' in f]
        if candidates:
            jsonl_path = os.path.join(sessions_dir, candidates[0])
        else:
            continue

    # Read last N lines
    try:
        result = subprocess.run(['tail', '-n', str(max_lines), jsonl_path],
                                capture_output=True, text=True, timeout=5)
        lines = result.stdout.strip().split('\n')
    except Exception:
        continue

    # Extract meaningful exchanges
    exchanges = []
    for line in lines:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        etype = entry.get('type', '')
        if etype in ('user', 'human'):
            # User message
            content = entry.get('content', '')
            if isinstance(content, list):
                content = ' '.join(
                    p.get('text', '') for p in content
                    if isinstance(p, dict) and p.get('type') == 'text'
                )
            if content:
                # Truncate long messages
                if len(content) > 300:
                    content = content[:300] + '...'
                exchanges.append(f'  USER: {content}')
        elif etype == 'assistant':
            content = entry.get('content', '')
            if isinstance(content, list):
                content = ' '.join(
                    p.get('text', '') for p in content
                    if isinstance(p, dict) and p.get('type') == 'text'
                )
            if content:
                if len(content) > 300:
                    content = content[:300] + '...'
                exchanges.append(f'  ASST: {content}')
        elif etype == 'tool_result':
            # Note errors
            is_error = entry.get('is_error', False)
            if is_error:
                content = entry.get('content', '')
                if isinstance(content, str) and content:
                    if len(content) > 200:
                        content = content[:200] + '...'
                    exchanges.append(f'  TOOL_ERROR: {content}')

    if not exchanges:
        continue

    print(f'--- SESSION: {key} (age: {age_min}m, tokens: {tokens}) ---')
    for ex in exchanges[-20:]:  # Last 20 exchanges max
        print(ex)
    print()
"
