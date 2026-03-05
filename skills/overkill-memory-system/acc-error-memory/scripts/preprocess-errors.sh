#!/bin/bash
# Preprocess session transcripts to extract user+assistant exchanges for ACC analysis
# Finds pairs where user might be correcting/frustrated with the assistant
#
# Usage:
#   preprocess-errors.sh                # Process exchanges after watermark
#   preprocess-errors.sh --full         # Process ALL exchanges (ignore watermark)
#   preprocess-errors.sh --limit N      # Limit to last N exchanges
#
# Output: pending-errors.json with exchanges to analyze

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
AGENT_ID="${AGENT_ID:-main}"
TRANSCRIPT_DIR="$HOME/.openclaw/agents/$AGENT_ID/sessions"
OUTPUT="$WORKSPACE/memory/pending-errors.json"
WATERMARK_FILE="$WORKSPACE/memory/acc-watcher-watermark.json"

# Parse arguments
FULL_MODE=false
LIMIT=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --full) FULL_MODE=true; shift ;;
        --limit) LIMIT="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# Count session files
SESSION_COUNT=$(ls "$TRANSCRIPT_DIR"/*.jsonl 2>/dev/null | wc -l | tr -d ' ')
if [ "$SESSION_COUNT" -eq 0 ]; then
    echo "No session transcripts found in $TRANSCRIPT_DIR"
    exit 1
fi

echo "⚡ ACC Preprocess: Extracting exchanges from $SESSION_COUNT session files"
echo "Mode: $([ "$FULL_MODE" = true ] && echo 'FULL' || echo 'incremental')"

export TRANSCRIPT_DIR OUTPUT WATERMARK_FILE FULL_MODE LIMIT

python3 << 'PYTHON_SCRIPT'
import os
import sys
import json
from datetime import datetime
from glob import glob

transcript_dir = os.environ.get('TRANSCRIPT_DIR', '')
output_file = os.environ.get('OUTPUT', '')
watermark_file = os.environ.get('WATERMARK_FILE', '')
full_mode = os.environ.get('FULL_MODE', 'false') == 'true'
limit_str = os.environ.get('LIMIT', '')
limit = int(limit_str) if limit_str and limit_str.isdigit() else None

# Get watermark timestamp
watermark_ts = None
if not full_mode and os.path.exists(watermark_file):
    try:
        with open(watermark_file, 'r') as f:
            wm = json.load(f)
        ts_str = wm.get('timestamp')
        if ts_str:
            watermark_ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
            print(f"Watermark: {ts_str}")
    except:
        pass

if watermark_ts is None and not full_mode:
    print("Watermark: (none - starting fresh)")

# Collect all messages from all sessions
all_messages = []
session_files = glob(os.path.join(transcript_dir, '*.jsonl'))

for session_file in session_files:
    session_name = os.path.basename(session_file)
    line_num = 0
    try:
        with open(session_file, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line_num += 1
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                
                if data.get('type') != 'message':
                    continue
                
                msg = data.get('message', {})
                role = msg.get('role', '')
                if role not in ('user', 'assistant'):
                    continue
                
                ts_str = data.get('timestamp', '')
                if not ts_str:
                    continue
                
                try:
                    ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                except:
                    continue
                
                # Filter by watermark
                if not full_mode and watermark_ts and ts <= watermark_ts:
                    continue
                
                # Extract text
                content = msg.get('content', [])
                text = ''
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            text = item.get('text', '')
                            break
                elif isinstance(content, str):
                    text = content
                
                # Clean and limit
                text = text[:1000].strip()
                if len(text) < 5:
                    continue
                
                # Skip system/cron messages
                if text.startswith('System:') and 'Cron:' in text:
                    continue
                
                all_messages.append({
                    'timestamp': ts_str,
                    'ts_parsed': ts,
                    'role': role,
                    'text': text,
                    'session': session_name,
                    'line': line_num
                })
    except Exception as e:
        continue

# Sort by timestamp
all_messages.sort(key=lambda x: x['ts_parsed'])

# Extract exchanges (assistant followed by user)
exchanges = []
for i, msg in enumerate(all_messages):
    if msg['role'] == 'assistant' and i + 1 < len(all_messages):
        next_msg = all_messages[i + 1]
        if next_msg['role'] == 'user':
            exchanges.append({
                'assistant_text': msg['text'][:500],
                'user_text': next_msg['text'][:500],
                'timestamp': next_msg['timestamp'],
                'session': next_msg['session'],
                'line': next_msg['line']
            })

# Apply limit
if limit and len(exchanges) > limit:
    exchanges = exchanges[-limit:]

# Write output
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(exchanges, f, indent=2, ensure_ascii=False)

print(f"Found {len(exchanges)} exchanges to analyze")
if exchanges:
    print(f"Latest: {exchanges[-1]['timestamp']}")
PYTHON_SCRIPT
