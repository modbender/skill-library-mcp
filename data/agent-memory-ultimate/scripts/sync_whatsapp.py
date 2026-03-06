#!/usr/bin/env python3
"""
Sync WhatsApp messages from Baileys store to knowledge base.
Run periodically via cron to keep message history searchable.
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

BAILEYS_STORE = Path.home() / ".openclaw/credentials/whatsapp/default/baileys_store_multi.json"
DB_PATH = Path.home() / ".openclaw/workspace/db/jarvis.db"

def ensure_table(conn: sqlite3.Connection):
    """Create wa_messages table if not exists"""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS wa_messages (
            id TEXT PRIMARY KEY,
            chat_id TEXT,
            chat_name TEXT,
            sender_phone TEXT,
            sender_name TEXT,
            content TEXT,
            is_group INTEGER DEFAULT 0,
            timestamp TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_wa_messages_chat ON wa_messages(chat_id);
        CREATE INDEX IF NOT EXISTS idx_wa_messages_sender ON wa_messages(sender_phone);
        CREATE INDEX IF NOT EXISTS idx_wa_messages_timestamp ON wa_messages(timestamp);
        
        -- FTS for message search
        CREATE VIRTUAL TABLE IF NOT EXISTS wa_messages_fts USING fts5(
            content, chat_name, sender_name
        );
    """)
    conn.commit()

def extract_message_text(msg: dict) -> str:
    """Extract text content from WhatsApp message object"""
    if not isinstance(msg, dict):
        return ""
    message = msg.get("message")
    if not message or not isinstance(message, dict):
        return ""
    
    # Try different message types
    if "conversation" in message:
        return message["conversation"]
    if "extendedTextMessage" in message:
        return message["extendedTextMessage"].get("text", "")
    if "imageMessage" in message:
        return f"[Image] {message['imageMessage'].get('caption', '')}"
    if "videoMessage" in message:
        return f"[Video] {message['videoMessage'].get('caption', '')}"
    if "documentMessage" in message:
        return f"[Document] {message['documentMessage'].get('fileName', '')}"
    if "audioMessage" in message:
        return "[Voice note]"
    if "stickerMessage" in message:
        return "[Sticker]"
    if "reactionMessage" in message:
        return f"[Reaction: {message['reactionMessage'].get('text', '')}]"
    if "pollCreationMessage" in message:
        return f"[Poll] {message['pollCreationMessage'].get('name', '')}"
    
    return ""

def sync_messages():
    """Sync messages from Baileys store to database"""
    if not BAILEYS_STORE.exists():
        print(f"⚠️  Baileys store not found: {BAILEYS_STORE}")
        return
    
    if not DB_PATH.exists():
        print(f"⚠️  Database not found: {DB_PATH}")
        print("   Run init_db.py first")
        return
    
    print(f"📥 Syncing WhatsApp messages from Baileys store")
    
    # Load Baileys store
    with open(BAILEYS_STORE) as f:
        store = json.load(f)
    
    chats = store.get("chats", {})
    messages_by_chat = store.get("messages", {})
    
    print(f"   Found {len(chats)} chats, {len(messages_by_chat)} message groups")
    
    conn = sqlite3.connect(DB_PATH)
    ensure_table(conn)
    
    new_count = 0
    total_count = 0
    
    for chat_id, msgs_dict in messages_by_chat.items():
        # Messages are stored as dict with message_id as key
        if isinstance(msgs_dict, dict):
            msgs = list(msgs_dict.values())
        elif isinstance(msgs_dict, list):
            msgs = msgs_dict
        else:
            continue
        
        # Get chat info
        chat_info = chats.get(chat_id, {})
        chat_name = chat_info.get("name", "") or chat_info.get("subject", "")
        is_group = "@g.us" in chat_id
        
        for msg in msgs:
            total_count += 1
            # Message ID can be in key.id or the dict key itself
            msg_id = msg.get("key", {}).get("id", "") if isinstance(msg, dict) else ""
            if not msg_id:
                continue
            
            # Check if already exists
            existing = conn.execute(
                "SELECT id FROM wa_messages WHERE id = ?", (msg_id,)
            ).fetchone()
            
            if existing:
                continue
            
            # Extract message content
            content = extract_message_text(msg)
            if not content:
                continue
            
            # Get sender info
            key = msg.get("key", {})
            sender_id = key.get("participant", "") or key.get("remoteJid", "")
            sender_phone = sender_id.split("@")[0] if "@" in sender_id else sender_id
            if sender_phone and not sender_phone.startswith("+"):
                sender_phone = "+" + sender_phone
            
            # Get timestamp
            timestamp = msg.get("messageTimestamp")
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp).isoformat()
            elif isinstance(timestamp, dict):
                # Handle protobuf Long format
                low = timestamp.get("low", 0)
                timestamp = datetime.fromtimestamp(low).isoformat()
            else:
                timestamp = datetime.now().isoformat()
            
            # Insert message
            try:
                conn.execute("""
                    INSERT INTO wa_messages 
                    (id, chat_id, chat_name, sender_phone, content, is_group, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (msg_id, chat_id, chat_name, sender_phone, content, 1 if is_group else 0, timestamp))
                new_count += 1
            except Exception as e:
                print(f"  Error inserting {msg_id}: {e}")
    
    # Rebuild FTS
    if new_count > 0:
        try:
            conn.execute("DELETE FROM wa_messages_fts")
            conn.execute("""
                INSERT INTO wa_messages_fts(content, chat_name, sender_name)
                SELECT content, chat_name, sender_phone FROM wa_messages
            """)
        except:
            pass  # FTS table might not exist yet
    
    conn.commit()
    
    # Stats
    total_stored = conn.execute("SELECT COUNT(*) FROM wa_messages").fetchone()[0]
    
    print(f"\n✅ Sync complete:")
    print(f"   Processed: {total_count} messages")
    print(f"   New: {new_count}")
    print(f"   Total in DB: {total_stored}")
    
    conn.close()

if __name__ == "__main__":
    sync_messages()
