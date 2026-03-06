#!/usr/bin/env python3
"""
Honcho Hourly Feed — Run by cron alongside the memory sync.
Feeds new conversation messages from all active agent sessions to Honcho.
Tracks position to avoid duplicates.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

STATE_FILE = os.path.expanduser('~/.config/honcho/feed-state.json')

def get_honcho():
    from honcho import Honcho
    with open(os.path.expanduser('~/.config/honcho/credentials.json')) as f:
        creds = json.load(f)
    return Honcho(workspace_id=creds.get('workspace_id', 'default'), api_key=creds['api_key'])

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def parse_transcript_messages(path, j_peer, agent_peer, skip_lines=0):
    """Parse a JSONL transcript into Honcho messages, skipping already-synced lines."""
    messages = []
    line_count = 0
    
    with open(path) as f:
        for i, line in enumerate(f):
            line_count = i + 1
            if i < skip_lines:
                continue
            try:
                event = json.loads(line.strip())
            except:
                continue
            if event.get('type') != 'message':
                continue
            msg = event.get('message', event)
            role = msg.get('role', '')
            if role not in ('user', 'assistant'):
                continue
            content = msg.get('content', '')
            if isinstance(content, list):
                texts = [b.get('text', '') for b in content if isinstance(b, dict) and b.get('type') == 'text']
                content = ' '.join(texts)
            if not content or len(content.strip()) < 10:
                continue
            if len(content) > 8000:
                content = content[:8000]
            peer = j_peer if role == 'user' else agent_peer
            messages.append(peer.message(content))
    
    return messages, line_count

def main():
    honcho = get_honcho()
    peers = {name: honcho.peer(name) for name in ['j', 'axel', 'axobotl', 'larry', 'clarity', 'wire', 'drift']}
    j = peers['j']
    
    agents = {
        'main': 'axel',
        'axobotl': 'axobotl',
        'larry': 'larry',
        'clarity': 'clarity',
        'wire': 'wire',
        'drift': 'drift',
    }
    
    state = load_state()
    total_new = 0
    
    for agent_dir, agent_name in agents.items():
        sessions_dir = Path(f'/home/ubuntu/.openclaw/agents/{agent_dir}/sessions/')
        if not sessions_dir.exists():
            continue
        
        # Get most recent transcript
        transcripts = sorted(sessions_dir.glob('*.jsonl'), key=os.path.getmtime, reverse=True)[:1]
        
        for path in transcripts:
            path_str = str(path)
            skip = state.get(path_str, {}).get('lines_synced', 0)
            
            agent_peer = peers[agent_name]
            messages, total_lines = parse_transcript_messages(path, j, agent_peer, skip_lines=skip)
            
            if not messages:
                continue
            
            session = honcho.session(f'full-sync-{agent_name}')
            session.add_peers([j, agent_peer])
            
            for i in range(0, len(messages), 20):
                batch = messages[i:i+20]
                session.add_messages(batch)
            
            state[path_str] = {
                'lines_synced': total_lines,
                'last_sync': datetime.now(timezone.utc).isoformat(),
                'agent': agent_name,
                'total_messages': state.get(path_str, {}).get('total_messages', 0) + len(messages)
            }
            
            total_new += len(messages)
            print(f'{agent_name}: +{len(messages)} new messages')
    
    save_state(state)
    print(f'Total: {total_new} new messages fed to Honcho')

if __name__ == '__main__':
    main()
