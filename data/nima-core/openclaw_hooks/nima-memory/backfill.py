#!/usr/bin/env python3
"""
NIMA Graph Memory Backfill
==========================
Ingests existing session transcripts into the SQLite graph.
Extracts input/contemplation/output layers from each assistant turn.

Usage: python3 backfill.py [session_file] [--dry-run]
"""

import sqlite3
import json
import sys
import os
import re
import time
from datetime import datetime
from pathlib import Path

GRAPH_DB = os.path.expanduser("~/.nima/memory/graph.sqlite")
SESSIONS_DIR = os.path.expanduser("~/.openclaw/agents/main/sessions")


def summarize(text, max_len=80):
    """Compress text to short summary."""
    if not text:
        return ""
    clean = re.sub(r'\n+', ' ', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    if len(clean) <= max_len:
        return clean
    return clean[:max_len - 3] + "..."


def extract_sender(text):
    """Extract sender name from message format."""
    match = re.search(r'\[(?:Telegram|Discord|Signal|SMS)\s+(.+?)\s+id:', text)
    if match:
        return match.group(1)
    return "unknown"


def parse_transcript(filepath):
    """Parse a session transcript and yield (user_msg, assistant_msg) pairs."""
    pairs = []
    messages = []
    
    with open(filepath, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get('type') == 'message':
                    messages.append(entry.get('message', {}))
            except (json.JSONDecodeError, KeyError):
                continue

    # Walk through messages finding user→assistant pairs
    i = 0
    while i < len(messages):
        msg = messages[i]
        
        if msg.get('role') == 'user':
            # Look for next assistant message
            j = i + 1
            while j < len(messages) and messages[j].get('role') != 'assistant':
                j += 1
            
            if j < len(messages):
                pairs.append((msg, messages[j]))
                i = j + 1
            else:
                i += 1
        else:
            i += 1
    
    return pairs


def extract_layers(user_msg, assistant_msg):
    """Extract three layers from a message pair."""
    # Input
    content = user_msg.get('content', '')
    if isinstance(content, list):
        input_text = ' '.join(c.get('text', '') for c in content if c.get('type') == 'text')
    else:
        input_text = str(content)
    
    who = extract_sender(input_text)
    
    # Contemplation + Output
    thinking_text = ""
    output_text = ""
    a_content = assistant_msg.get('content', '')
    
    if isinstance(a_content, list):
        for block in a_content:
            if block.get('type') == 'thinking' and block.get('thinking'):
                thinking_text += block['thinking'] + "\n"
            elif block.get('type') == 'text' and block.get('text'):
                output_text += block['text'] + "\n"
    else:
        output_text = str(a_content)
    
    # Get timestamp
    timestamp = assistant_msg.get('timestamp')
    if isinstance(timestamp, str):
        try:
            timestamp = int(datetime.fromisoformat(timestamp).timestamp() * 1000)
        except:
            timestamp = int(time.time() * 1000)
    elif isinstance(timestamp, (int, float)):
        # If seconds (not ms), convert
        if timestamp < 1e12:
            timestamp = int(timestamp * 1000)
        else:
            timestamp = int(timestamp)
    else:
        timestamp = int(time.time() * 1000)
    
    return {
        'input': {'text': input_text.strip(), 'who': who},
        'contemplation': {'text': thinking_text.strip()},
        'output': {'text': output_text.strip()},
        'timestamp': timestamp,
    }


def store_turn(db, layers, session_key=""):
    """Store a complete turn to the graph."""
    ts = layers['timestamp']
    turn_id = f"turn_{ts}"
    affect_json = "{}"  # Historical turns don't have affect data
    
    # Skip empty turns
    if not layers['input']['text'] and not layers['output']['text']:
        return False
    
    # Skip heartbeats and no-replies
    output = layers['output']['text']
    if output in ('HEARTBEAT_OK', 'NO_REPLY', ''):
        return False
    
    # Check if turn already exists
    existing = db.execute("SELECT id FROM memory_turns WHERE turn_id = ?", (turn_id,)).fetchone()
    if existing:
        return False
    
    # Insert nodes
    cur = db.execute(
        "INSERT INTO memory_nodes (timestamp, layer, text, summary, who, affect_json, session_key, turn_id) VALUES (?, 'input', ?, ?, ?, ?, ?, ?)",
        (ts, layers['input']['text'], summarize(layers['input']['text']), layers['input']['who'], affect_json, session_key, turn_id)
    )
    input_id = cur.lastrowid
    
    cur = db.execute(
        "INSERT INTO memory_nodes (timestamp, layer, text, summary, who, affect_json, session_key, turn_id) VALUES (?, 'contemplation', ?, ?, 'self', ?, ?, ?)",
        (ts, layers['contemplation']['text'], summarize(layers['contemplation']['text'], 120), affect_json, session_key, turn_id)
    )
    contemp_id = cur.lastrowid
    
    cur = db.execute(
        "INSERT INTO memory_nodes (timestamp, layer, text, summary, who, affect_json, session_key, turn_id) VALUES (?, 'output', ?, ?, 'self', ?, ?, ?)",
        (ts, layers['output']['text'], summarize(layers['output']['text'], 100), affect_json, session_key, turn_id)
    )
    output_id = cur.lastrowid
    
    # Create edges
    db.execute("INSERT INTO memory_edges (source_id, target_id, relation, weight) VALUES (?, ?, 'triggered', 1.0)", (input_id, contemp_id))
    db.execute("INSERT INTO memory_edges (source_id, target_id, relation, weight) VALUES (?, ?, 'produced', 1.0)", (contemp_id, output_id))
    db.execute("INSERT INTO memory_edges (source_id, target_id, relation, weight) VALUES (?, ?, 'responded_to', 1.0)", (output_id, input_id))
    
    # Create turn group
    db.execute(
        "INSERT INTO memory_turns (turn_id, input_node_id, contemplation_node_id, output_node_id, timestamp, affect_json) VALUES (?, ?, ?, ?, ?, ?)",
        (turn_id, input_id, contemp_id, output_id, ts, affect_json)
    )
    
    return True


def backfill(session_file=None, dry_run=False):
    """Backfill graph from session transcripts."""
    if session_file:
        files = [session_file]
    else:
        # Find all session transcripts
        files = sorted(Path(SESSIONS_DIR).glob("*.jsonl"))
        # Exclude deleted files
        files = [f for f in files if '.deleted.' not in str(f)]
    
    if not files:
        print("❌ No session files found")
        return
    
    print(f"📂 Found {len(files)} session file(s)")
    
    if not dry_run:
        db = sqlite3.connect(GRAPH_DB)
        db.execute("PRAGMA journal_mode=WAL")
    
    total_stored = 0
    total_skipped = 0
    
    for filepath in files:
        filepath = str(filepath)
        basename = os.path.basename(filepath)
        print(f"\n📄 Processing: {basename}")
        
        pairs = parse_transcript(filepath)
        print(f"   Found {len(pairs)} conversation turns")
        
        stored = 0
        skipped = 0
        
        for user_msg, assistant_msg in pairs:
            layers = extract_layers(user_msg, assistant_msg)
            
            if dry_run:
                who = layers['input']['who']
                inp = summarize(layers['input']['text'], 50)
                think = summarize(layers['contemplation']['text'], 50)
                out = summarize(layers['output']['text'], 50)
                print(f"   👂 {who}: {inp}")
                print(f"   💭 {think}")
                print(f"   💬 {out}")
                print()
                stored += 1
            else:
                if store_turn(db, layers, session_key=basename):
                    stored += 1
                else:
                    skipped += 1
        
        print(f"   ✅ Stored: {stored} | ⏭️ Skipped: {skipped}")
        total_stored += stored
        total_skipped += skipped
    
    if not dry_run:
        db.commit()
        
        # Print stats
        nodes = db.execute("SELECT COUNT(*) FROM memory_nodes").fetchone()[0]
        edges = db.execute("SELECT COUNT(*) FROM memory_edges").fetchone()[0]
        turns = db.execute("SELECT COUNT(*) FROM memory_turns").fetchone()[0]
        db.close()
        
        print(f"\n{'='*50}")
        print(f"📊 Backfill Complete")
        print(f"   New turns: {total_stored}")
        print(f"   Skipped: {total_skipped}")
        print(f"   Total graph: {nodes} nodes, {edges} edges, {turns} turns")
    else:
        print(f"\n🏃 Dry run: {total_stored} turns would be stored")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Backfill NIMA graph from transcripts")
    parser.add_argument("session_file", nargs="?", help="Specific session file (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without storing")
    args = parser.parse_args()
    
    backfill(session_file=args.session_file, dry_run=args.dry_run)
