#!/usr/bin/env python3
"""
JarvisOne Knowledge Base v2 - Simpler approach without FTS triggers
"""
import sqlite3
import json
import hashlib
from pathlib import Path
from datetime import datetime

# Find workspace root (where db/ lives or should live)
def find_workspace():
    # Try common locations
    candidates = [
        Path(__file__).parent.parent.parent.parent,  # skills/knowledge-base/scripts/ -> workspace
        Path.home() / ".openclaw" / "workspace",
        Path.cwd(),
    ]
    for p in candidates:
        if (p / "AGENTS.md").exists() or (p / "db").exists():
            return p
    return candidates[0]

WORKSPACE = find_workspace()
DB_PATH = WORKSPACE / "db" / "jarvis.db"

def get_hash(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()

def init_schema(conn: sqlite3.Connection):
    """Create all tables"""
    conn.executescript("""
    -- Core documents table
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        path TEXT UNIQUE,
        title TEXT,
        content TEXT,
        hash TEXT,
        created_at TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT
    );

    -- Contacts table
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT UNIQUE,
        name TEXT,
        source TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- WhatsApp groups
    CREATE TABLE IF NOT EXISTS wa_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        jid TEXT UNIQUE NOT NULL,
        name TEXT,
        participant_count INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- Group memberships
    CREATE TABLE IF NOT EXISTS wa_memberships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_jid TEXT NOT NULL,
        phone TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0,
        UNIQUE(group_jid, phone)
    );

    -- ChatGPT conversations
    CREATE TABLE IF NOT EXISTS chatgpt_conversations (
        id TEXT PRIMARY KEY,
        title TEXT,
        created_at TEXT,
        updated_at TEXT,
        message_count INTEGER,
        model TEXT
    );

    -- ChatGPT messages
    CREATE TABLE IF NOT EXISTS chatgpt_messages (
        id TEXT PRIMARY KEY,
        conversation_id TEXT,
        role TEXT,
        content TEXT,
        created_at TEXT
    );

    -- Tags
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id INTEGER,
        tag TEXT
    );

    -- Schema version
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY,
        applied_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- Indexes
    CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
    CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(name);
    CREATE INDEX IF NOT EXISTS idx_wa_memberships_phone ON wa_memberships(phone);
    CREATE INDEX IF NOT EXISTS idx_wa_memberships_group ON wa_memberships(group_jid);
    CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(type);
    CREATE INDEX IF NOT EXISTS idx_chatgpt_messages_conv ON chatgpt_messages(conversation_id);
    """)
    
    # Create FTS tables separately (without triggers for now)
    try:
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                title, content, content='documents', content_rowid='id'
            )
        """)
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS chatgpt_fts USING fts5(content)
        """)
    except Exception as e:
        print(f"  FTS warning: {e}")
    
    conn.execute("INSERT OR IGNORE INTO schema_version (version) VALUES (2)")
    conn.commit()
    print("✅ Schema created")

def import_whatsapp_contacts(conn: sqlite3.Connection):
    """Import WhatsApp contacts and groups"""
    json_path = WORKSPACE / "bank" / "whatsapp-contacts-full.json"
    if not json_path.exists():
        print("⚠️  WhatsApp contacts file not found")
        return
    
    with open(json_path) as f:
        data = json.load(f)
    
    groups_added = 0
    for group in data.get("groups", []):
        try:
            conn.execute("""
                INSERT OR REPLACE INTO wa_groups (jid, name, participant_count)
                VALUES (?, ?, ?)
            """, (group["id"], group.get("subject", ""), group.get("participantCount", 0)))
            groups_added += 1
        except Exception as e:
            pass
    
    contacts_added = 0
    memberships_added = 0
    for contact in data.get("contacts", []):
        phone = contact.get("phone", "").replace("+", "")
        if not phone:
            continue
        if not phone.startswith("+"):
            phone = "+" + phone
        
        try:
            conn.execute("INSERT OR IGNORE INTO contacts (phone, source) VALUES (?, 'whatsapp')", (phone,))
            contacts_added += 1
        except:
            pass
        
        for group in contact.get("groups", []):
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO wa_memberships (group_jid, phone, is_admin)
                    VALUES (?, ?, ?)
                """, (group["id"], phone, 1 if group.get("isAdmin") else 0))
                memberships_added += 1
            except:
                pass
    
    conn.commit()
    print(f"✅ WhatsApp: {groups_added} groups, {contacts_added} contacts, {memberships_added} memberships")

def import_daily_logs(conn: sqlite3.Connection):
    """Import markdown files from memory/"""
    memory_dir = WORKSPACE / "memory"
    if not memory_dir.exists():
        return
    
    docs_added = 0
    for md_file in memory_dir.rglob("*.md"):
        try:
            content = md_file.read_text()
            title = md_file.stem
            rel_path = str(md_file.relative_to(WORKSPACE))
            content_hash = get_hash(content)
            
            if md_file.name.startswith("2026-") or md_file.name.startswith("2025-"):
                doc_type = "log"
            elif "project" in rel_path:
                doc_type = "project"
            else:
                doc_type = "note"
            
            conn.execute("""
                INSERT OR REPLACE INTO documents (type, path, title, content, hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (doc_type, rel_path, title, content, content_hash, datetime.now().isoformat()))
            docs_added += 1
        except:
            pass
    
    conn.commit()
    print(f"✅ Documents: {docs_added} markdown files")

def import_chatgpt(conn: sqlite3.Connection):
    """Import ChatGPT conversations"""
    export_path = WORKSPACE / "chatgpt-export" / "chatgpt-export-2026-02-06.json"
    if not export_path.exists():
        print("⚠️  ChatGPT export not found")
        return
    
    with open(export_path) as f:
        data = json.load(f)
    
    conversations = data.get("conversations", [])
    
    convs_added = 0
    msgs_added = 0
    
    for conv in conversations:
        conv_id = conv.get("id", "")
        title = conv.get("title", "Untitled")
        created = conv.get("created", "")
        messages = conv.get("messages", [])
        
        conn.execute("""
            INSERT OR REPLACE INTO chatgpt_conversations 
            (id, title, created_at, message_count)
            VALUES (?, ?, ?, ?)
        """, (conv_id, title, created, len(messages)))
        convs_added += 1
        
        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            text = msg.get("text", "")
            time = msg.get("time", "")
            
            if not text.strip():
                continue
            
            msg_id = f"{conv_id}_{i}"
            
            conn.execute("""
                INSERT OR REPLACE INTO chatgpt_messages
                (id, conversation_id, role, content, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (msg_id, conv_id, role, text, time))
            msgs_added += 1
    
    conn.commit()
    print(f"✅ ChatGPT: {convs_added} conversations, {msgs_added} messages")

def rebuild_fts(conn: sqlite3.Connection):
    """Rebuild FTS indexes"""
    try:
        # Documents FTS
        conn.execute("INSERT INTO documents_fts(documents_fts) VALUES('rebuild')")
        
        # ChatGPT FTS - simple approach
        conn.execute("DROP TABLE IF EXISTS chatgpt_fts")
        conn.execute("CREATE VIRTUAL TABLE chatgpt_fts USING fts5(conv_id, role, content)")
        conn.execute("""
            INSERT INTO chatgpt_fts(conv_id, role, content)
            SELECT conversation_id, role, content FROM chatgpt_messages
        """)
        conn.commit()
        print("✅ FTS indexes rebuilt")
    except Exception as e:
        print(f"⚠️  FTS rebuild: {e}")

def print_stats(conn: sqlite3.Connection):
    """Print database statistics"""
    print("\n📊 Database Statistics:")
    
    tables = [
        ("contacts", "SELECT COUNT(*) FROM contacts"),
        ("wa_groups", "SELECT COUNT(*) FROM wa_groups"),
        ("wa_memberships", "SELECT COUNT(*) FROM wa_memberships"),
        ("documents", "SELECT COUNT(*) FROM documents"),
        ("chatgpt_conversations", "SELECT COUNT(*) FROM chatgpt_conversations"),
        ("chatgpt_messages", "SELECT COUNT(*) FROM chatgpt_messages"),
    ]
    
    for name, query in tables:
        try:
            count = conn.execute(query).fetchone()[0]
            print(f"  {name}: {count:,}")
        except:
            print(f"  {name}: 0")
    
    db_size = DB_PATH.stat().st_size / 1024
    print(f"\n  Database size: {db_size:.1f} KB")

def test_search(conn: sqlite3.Connection):
    """Test search functionality"""
    print("\n🔍 Testing search...")
    
    # Test contact search
    result = conn.execute("SELECT phone FROM contacts WHERE phone LIKE '%659418%' LIMIT 3").fetchall()
    print(f"  Contacts matching '659418': {len(result)}")
    
    # Test document search
    try:
        result = conn.execute("""
            SELECT title, SUBSTR(content, 1, 50) FROM documents_fts WHERE documents_fts MATCH 'project' LIMIT 3
        """).fetchall()
        print(f"  Documents matching 'project': {len(result)}")
    except:
        result = conn.execute("""
            SELECT title, SUBSTR(content, 1, 50) FROM documents WHERE content LIKE '%project%' LIMIT 3
        """).fetchall()
        print(f"  Documents matching 'project' (LIKE): {len(result)}")
    
    # Test ChatGPT search
    try:
        result = conn.execute("""
            SELECT conv_id, SUBSTR(content, 1, 50) FROM chatgpt_fts WHERE chatgpt_fts MATCH 'Bashar' LIMIT 3
        """).fetchall()
        print(f"  ChatGPT messages matching 'Bashar': {len(result)}")
        for conv_id, snippet in result:
            print(f"    - {snippet}...")
    except Exception as e:
        print(f"  ChatGPT FTS: {e}")

def main():
    print(f"🗄️  JarvisOne Knowledge Base v2")
    print(f"   Database: {DB_PATH}\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    init_schema(conn)
    import_whatsapp_contacts(conn)
    import_daily_logs(conn)
    import_chatgpt(conn)
    rebuild_fts(conn)
    print_stats(conn)
    test_search(conn)
    
    conn.close()
    print("\n✅ Knowledge Base ready!")

if __name__ == "__main__":
    main()
