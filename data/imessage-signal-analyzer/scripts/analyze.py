#!/usr/bin/env python3
"""Message analyzer - iMessage and Signal conversation analysis."""
import sys
import sqlite3
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

def get_imessage_handles(phone_or_handle):
    """Find all iMessage handles matching a phone number or handle."""
    db_path = os.path.expanduser("~/Library/Messages/chat.db")
    if not os.path.exists(db_path):
        print("Error: iMessage database not found. Is this macOS?")
        return []
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Try to match by phone or handle
    # Handle formats: +1234567890, 1234567890, some@email.com
    query = """
        SELECT DISTINCT id
        FROM handle
        WHERE id LIKE ? OR id = ?
    """
    search_pattern = f"%{phone_or_handle}%"
    c.execute(query, (search_pattern, phone_or_handle))
    handles = [row['id'] for row in c.fetchall()]
    
    conn.close()
    return list(set(handles))

def analyze_imessage(phone_or_handle, limit=0):
    """Analyze iMessage conversation."""
    handles = get_imessage_handles(phone_or_handle)
    if not handles:
        print(f"No handles found matching: {phone_or_handle}")
        print("\nTip: Use the full phone number including country code (e.g., +17279991234)")
        return
    
    print(f"Found {len(handles)} handle(s): {', '.join(handles)}")
    
    db_path = os.path.expanduser("~/Library/Messages/chat.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Build query
    placeholders = ','.join(['?' for _ in handles])
    query = f"""
        SELECT 
            message.ROWID,
            message.text,
            message.date,
            message.is_from_me,
            message.attributedBody
        FROM message
        JOIN chat_message_join cmj ON message.ROWID = cmj.message_id
        JOIN chat_handle_join chj ON cmj.chat_id = chj.chat_id
        JOIN handle ON chj.handle_id = handle.ROWID
        WHERE handle.id IN ({placeholders})
        ORDER BY message.date DESC
    """
    if limit:
        query += f" LIMIT {limit}"
    
    c.execute(query, handles)
    messages = c.fetchall()
    conn.close()
    
    if not messages:
        print("No messages found.")
        return
    
    analyze_messages(messages, "iMessage")

def analyze_signal(json_path, phone_or_name, limit=0):
    """Analyze Signal conversation from exported JSON."""
    if not os.path.exists(json_path):
        print(f"Error: Signal export not found at {json_path}")
        print("Run: signal-cli export --output ~/signal_export.json")
        return
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Find recipient
    recipient_id = None
    for recipient in data.get('recipients', []):
        if phone_or_name in recipient.get('number', '') or \
           phone_or_name.lower() in recipient.get('name', '').lower():
            recipient_id = recipient['id']
            recipient_name = recipient.get('name', recipient['id'])
            break
    
    if not recipient_id:
        print(f"No recipient found matching: {phone_or_name}")
        print("\nAvailable recipients:")
        for r in data.get('recipients', [])[:10]:
            print(f"  - {r.get('name', 'Unknown')} ({r.get('number', 'no number')})")
        return
    
    print(f"Analyzing Signal conversation with: {recipient_name or recipient_id}")
    
    # Extract messages
    messages = []
    for convo in data.get('conversations', []):
        if convo.get('recipientId') == recipient_id or convo.get('source') == recipient_id:
            for msg in convo.get('messages', []):
                text = msg.get('text', '')
                if text:
                    messages.append({
                        'text': text,
                        'date': msg.get('timestamp', 0) / 1000,  # ms to seconds
                        'is_from_me': msg.get('type') == 'outgoing',
                    })
    
    messages.sort(key=lambda x: x['date'], reverse=True)
    
    if limit:
        messages = messages[:limit]
    
    if not messages:
        print("No messages found.")
        return
    
    analyze_messages(messages, "Signal")

def analyze_messages(messages, source):
    """Common message analysis."""
    print(f"\n{'='*60}")
    print(f"Message Analysis ({source})")
    print(f"{'='*60}")
    
    # Basic stats
    total = len(messages)
    from_me = sum(1 for m in messages if m['is_from_me'])
    from_them = total - from_me
    
    print(f"\nTotal messages: {total}")
    print(f"  From you: {from_me} ({100*from_me/total:.1f}%)")
    print(f"  From them: {from_them} ({100*from_them/total:.1f}%)")
    
    # Date range (iMessage uses Mac timestamps, Signal uses Unix)
    dates = []
    for m in messages:
        try:
            if source == "iMessage":
                # Mac timestamp (seconds from 2001-01-01)
                ts = datetime(2001, 1, 1) + timedelta(seconds=m['date'] or 0)
            else:
                ts = datetime.fromtimestamp(m['date'])
            dates.append(ts)
        except:
            pass
    
    if dates:
        print(f"\nDate range: {dates[-1].strftime('%Y-%m-%d')} to {dates[0].strftime('%Y-%m-%d')}")
    
    # Messages per year
    year_counts = defaultdict(int)
    for d in dates:
        year_counts[d.year] += 1
    
    print("\nMessages per year:")
    for year in sorted(year_counts.keys()):
        bar_len = int(50 * year_counts[year] / max(year_counts.values()))
        print(f"  {year}: {'█' * bar_len} {year_counts[year]}")
    
    # Find gaps (initiations)
    dates_sorted = sorted(dates)
    initiations = 0
    silence_gaps = []
    
    for i in range(1, len(dates_sorted)):
        gap = dates_sorted[i-1] - dates_sorted[i]
        if gap > timedelta(hours=4):
            if gap > timedelta(days=30):
                silence_gaps.append((dates_sorted[i], dates_sorted[i-1], gap.days))
            initiations += 1
    
    print(f"\nConversation initiations: ~{initiations}")
    
    if silence_gaps:
        print("\nNotable silences (>30 days):")
        for start, end, days in sorted(silence_gaps, key=lambda x: -x[2])[:5]:
            print(f"  {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}: {days} days")
    
    # Sample messages
    print("\nRecent messages:")
    for m in messages[:10]:
        text = (m['text'] or '')[:100] + "..." if len(m['text'] or '') > 100 else (m['text'] or '')
        sender = "You" if m['is_from_me'] else "Them"
        try:
            if source == "iMessage":
                ts = datetime(2001, 1, 1) + timedelta(seconds=m['date'] or 0)
            else:
                ts = datetime.fromtimestamp(m['date'])
            ts_str = ts.strftime('%Y-%m-%d')
        except:
            ts_str = "?"
        print(f"  [{ts_str}] {sender}: {text}")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  iMessage: python3 analyze.py imessage <phone> [--limit N]")
        print("  Signal:   python3 analyze.py signal <json_path> <phone_or_name> [--limit N]")
        sys.exit(1)
    
    source = sys.argv[1].lower()
    
    if source == "imessage" or source == "imessage":
        phone = sys.argv[2] if len(sys.argv) > 2 else input("Phone/Handle: ").strip()
        limit = 0
        if '--limit' in sys.argv:
            idx = sys.argv.index('--limit')
            if idx + 1 < len(sys.argv):
                limit = int(sys.argv[idx+1])
        analyze_imessage(phone, limit)
    
    elif source == "signal":
        if len(sys.argv) < 3:
            print("Usage: python3 analyze.py signal <json_path> <phone_or_name> [--limit N]")
            sys.exit(1)
        json_path = os.path.expanduser(sys.argv[2])
        phone = sys.argv[3] if len(sys.argv) > 3 else input("Phone/Name: ").strip()
        limit = 0
        if '--limit' in sys.argv:
            idx = sys.argv.index('--limit')
            if idx + 1 < len(sys.argv):
                limit = int(sys.argv[idx+1])
        analyze_signal(json_path, phone, limit)
    
    else:
        print(f"Unknown source: {source}")
        print("Use 'imessage' or 'signal'")

if __name__ == "__main__":
    main()
