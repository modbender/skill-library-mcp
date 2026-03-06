#!/usr/bin/env python3
"""
JarvisOne Knowledge Base Query Tool
Usage: python3 query.py <command> [args]

Commands:
  search <term>              - Full-text search across all content
  contact <phone|name>       - Look up a contact
  groups <phone>             - List groups a contact is in
  members <group_name>       - List members of a group
  conv <title>               - Search ChatGPT conversations by title
  chatgpt <term>             - Search ChatGPT message content
  doc <term>                 - Search documents
  stats                      - Show database statistics
  sql <query>                - Run raw SQL
"""
import sqlite3
import sys
from pathlib import Path

# Find workspace root
def find_workspace():
    candidates = [
        Path(__file__).parent.parent.parent.parent,  # skills/knowledge-base/scripts/ -> workspace
        Path.home() / ".openclaw" / "workspace",
        Path.cwd(),
    ]
    for p in candidates:
        if (p / "db" / "jarvis.db").exists():
            return p
    return candidates[0]

DB_PATH = find_workspace() / "db" / "jarvis.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def cmd_search(term: str):
    """Search across all content"""
    conn = get_conn()
    
    print(f"🔍 Searching for: {term}\n")
    
    # Contacts
    results = conn.execute("""
        SELECT phone, name, source FROM contacts 
        WHERE phone LIKE ? OR name LIKE ?
        LIMIT 5
    """, (f"%{term}%", f"%{term}%")).fetchall()
    if results:
        print("📇 Contacts:")
        for phone, name, source in results:
            print(f"  {phone} - {name or '(no name)'} [{source}]")
        print()
    
    # Groups
    results = conn.execute("""
        SELECT jid, name, participant_count FROM wa_groups 
        WHERE name LIKE ?
        LIMIT 5
    """, (f"%{term}%",)).fetchall()
    if results:
        print("👥 WhatsApp Groups:")
        for jid, name, count in results:
            print(f"  {name} ({count} members)")
        print()
    
    # Documents
    results = conn.execute("""
        SELECT title, path, SUBSTR(content, 1, 100) FROM documents 
        WHERE content LIKE ? OR title LIKE ?
        LIMIT 5
    """, (f"%{term}%", f"%{term}%")).fetchall()
    if results:
        print("📄 Documents:")
        for title, path, snippet in results:
            print(f"  {title} ({path})")
            print(f"    ...{snippet[:80]}...")
        print()
    
    # ChatGPT
    try:
        results = conn.execute("""
            SELECT c.title, m.role, SUBSTR(m.content, 1, 150)
            FROM chatgpt_fts f
            JOIN chatgpt_messages m ON m.conversation_id = f.conv_id AND m.content = f.content
            JOIN chatgpt_conversations c ON c.id = m.conversation_id
            WHERE chatgpt_fts MATCH ?
            LIMIT 5
        """, (term,)).fetchall()
    except:
        results = conn.execute("""
            SELECT c.title, m.role, SUBSTR(m.content, 1, 150)
            FROM chatgpt_messages m
            JOIN chatgpt_conversations c ON c.id = m.conversation_id
            WHERE m.content LIKE ?
            LIMIT 5
        """, (f"%{term}%",)).fetchall()
    
    if results:
        print("💬 ChatGPT Messages:")
        for title, role, snippet in results:
            print(f"  [{role}] {title}")
            print(f"    {snippet}...")
        print()
    
    conn.close()

def cmd_contact(query: str):
    """Look up contact by phone or name"""
    conn = get_conn()
    results = conn.execute("""
        SELECT phone, name, source, notes FROM contacts 
        WHERE phone LIKE ? OR name LIKE ?
    """, (f"%{query}%", f"%{query}%")).fetchall()
    
    if not results:
        print(f"No contacts found matching '{query}'")
        return
    
    for phone, name, source, notes in results:
        print(f"📱 {phone}")
        print(f"   Name: {name or '(unknown)'}")
        print(f"   Source: {source}")
        if notes:
            print(f"   Notes: {notes}")
        
        # Get groups
        groups = conn.execute("""
            SELECT g.name, m.is_admin FROM wa_memberships m
            JOIN wa_groups g ON g.jid = m.group_jid
            WHERE m.phone = ?
            ORDER BY g.name
        """, (phone,)).fetchall()
        
        if groups:
            print(f"   Groups ({len(groups)}):")
            for gname, is_admin in groups[:10]:
                admin = "👑" if is_admin else ""
                print(f"     {admin} {gname}")
            if len(groups) > 10:
                print(f"     ... and {len(groups) - 10} more")
        print()
    
    conn.close()

def cmd_groups(phone: str):
    """List all groups a phone number is in"""
    conn = get_conn()
    
    # Normalize phone
    if not phone.startswith("+"):
        phone = "+" + phone
    
    results = conn.execute("""
        SELECT g.name, g.participant_count, m.is_admin
        FROM wa_memberships m
        JOIN wa_groups g ON g.jid = m.group_jid
        WHERE m.phone = ?
        ORDER BY g.participant_count DESC
    """, (phone,)).fetchall()
    
    if not results:
        print(f"No groups found for {phone}")
        return
    
    print(f"👥 Groups for {phone}: {len(results)}\n")
    for name, count, is_admin in results:
        admin = "👑" if is_admin else "  "
        print(f"  {admin} {name} ({count})")
    
    conn.close()

def cmd_members(group_name: str):
    """List members of a group"""
    conn = get_conn()
    
    # Find group
    group = conn.execute("""
        SELECT jid, name, participant_count FROM wa_groups 
        WHERE name LIKE ?
        LIMIT 1
    """, (f"%{group_name}%",)).fetchone()
    
    if not group:
        print(f"No group found matching '{group_name}'")
        return
    
    jid, name, count = group
    print(f"👥 {name} ({count} members)\n")
    
    # Get members
    members = conn.execute("""
        SELECT m.phone, c.name, m.is_admin
        FROM wa_memberships m
        LEFT JOIN contacts c ON c.phone = m.phone
        WHERE m.group_jid = ?
        ORDER BY m.is_admin DESC, c.name
    """, (jid,)).fetchall()
    
    for phone, cname, is_admin in members:
        admin = "👑" if is_admin else "  "
        display = cname or phone
        print(f"  {admin} {display}")
    
    conn.close()

def cmd_chatgpt(term: str):
    """Search ChatGPT messages"""
    conn = get_conn()
    
    try:
        results = conn.execute("""
            SELECT DISTINCT c.id, c.title, c.message_count
            FROM chatgpt_fts f
            JOIN chatgpt_conversations c ON c.id = f.conv_id
            WHERE chatgpt_fts MATCH ?
            LIMIT 20
        """, (term,)).fetchall()
    except:
        results = conn.execute("""
            SELECT DISTINCT c.id, c.title, c.message_count
            FROM chatgpt_messages m
            JOIN chatgpt_conversations c ON c.id = m.conversation_id
            WHERE m.content LIKE ?
            LIMIT 20
        """, (f"%{term}%",)).fetchall()
    
    if not results:
        print(f"No ChatGPT messages matching '{term}'")
        return
    
    print(f"💬 ChatGPT conversations mentioning '{term}':\n")
    for conv_id, title, msg_count in results:
        print(f"  📝 {title} ({msg_count} messages)")
    
    conn.close()

def cmd_stats():
    """Show database statistics"""
    conn = get_conn()
    
    print("📊 JarvisOne Knowledge Base Statistics\n")
    
    tables = [
        ("Contacts", "SELECT COUNT(*) FROM contacts"),
        ("Contacts with names", "SELECT COUNT(*) FROM contacts WHERE name IS NOT NULL"),
        ("WhatsApp Groups", "SELECT COUNT(*) FROM wa_groups"),
        ("Group Memberships", "SELECT COUNT(*) FROM wa_memberships"),
        ("Documents", "SELECT COUNT(*) FROM documents"),
        ("ChatGPT Conversations", "SELECT COUNT(*) FROM chatgpt_conversations"),
        ("ChatGPT Messages", "SELECT COUNT(*) FROM chatgpt_messages"),
    ]
    
    for label, query in tables:
        count = conn.execute(query).fetchone()[0]
        print(f"  {label}: {count:,}")
    
    # Total text
    doc_chars = conn.execute("SELECT SUM(LENGTH(content)) FROM documents").fetchone()[0] or 0
    chat_chars = conn.execute("SELECT SUM(LENGTH(content)) FROM chatgpt_messages").fetchone()[0] or 0
    total = doc_chars + chat_chars
    print(f"\n  Total indexed text: {total:,} chars ({total/1024/1024:.1f} MB)")
    
    # DB size
    db_size = DB_PATH.stat().st_size
    print(f"  Database file: {db_size/1024:.1f} KB")
    
    conn.close()

def cmd_sql(query: str):
    """Run raw SQL"""
    conn = get_conn()
    try:
        results = conn.execute(query).fetchall()
        for row in results:
            print(row)
    except Exception as e:
        print(f"Error: {e}")
    conn.close()

def cmd_wa(term: str):
    """Search WhatsApp message archive"""
    conn = get_conn()
    
    try:
        # Try FTS first
        results = conn.execute("""
            SELECT DISTINCT m.sender_phone, m.chat_name, SUBSTR(m.content, 1, 150), m.timestamp
            FROM wa_messages_fts f
            JOIN wa_messages m ON m.content = f.content
            WHERE wa_messages_fts MATCH ?
            ORDER BY m.timestamp DESC
            LIMIT 20
        """, (term,)).fetchall()
    except:
        # Fall back to LIKE
        results = conn.execute("""
            SELECT sender_phone, chat_name, SUBSTR(content, 1, 150), timestamp
            FROM wa_messages
            WHERE content LIKE ?
            ORDER BY timestamp DESC
            LIMIT 20
        """, (f"%{term}%",)).fetchall()
    
    if not results:
        print(f"No WhatsApp messages matching '{term}'")
        return
    
    print(f"📱 WhatsApp messages matching '{term}':\n")
    for sender, chat, content, ts in results:
        date = ts[:10] if ts else "?"
        print(f"  [{date}] {sender or 'unknown'}")
        print(f"    {content}...")
        print()
    
    conn.close()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    args = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
    
    commands = {
        "search": cmd_search,
        "contact": cmd_contact,
        "groups": cmd_groups,
        "members": cmd_members,
        "chatgpt": cmd_chatgpt,
        "wa": cmd_wa,
        "stats": lambda _: cmd_stats(),
        "sql": cmd_sql,
    }
    
    if cmd in commands:
        commands[cmd](args)
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == "__main__":
    main()
