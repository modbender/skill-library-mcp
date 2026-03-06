#!/usr/bin/env python3
import sqlite3
import redis
import argparse
import os
import sys
import hashlib
import datetime
from pathlib import Path

# Config
DB_PATH = os.path.expanduser("~/.openclaw/memory/main.sqlite")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "../assets/schema.sql")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PREFIX = "mema:mental"

def get_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with open(SCHEMA_PATH, 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    print(f"✓ Database initialized at {DB_PATH}")

def index_doc(path, title=None, tag=None):
    if not path:
        print("Error: Path required")
        sys.exit(1)
    
    doc_id = hashlib.sha256(path.encode()).hexdigest()[:16]
    title = title or os.path.basename(path)
    
    conn = get_db()
    conn.execute("""
        INSERT INTO documents (document_id, path, title, tag, updated_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        ON CONFLICT(document_id) DO UPDATE SET
            path=excluded.path, title=excluded.title, 
            tag=excluded.tag, updated_at=datetime('now')
    """, (doc_id, path, title, tag))
    conn.commit()
    print(f"✓ Indexed: {title} ({doc_id})")

def list_docs(tag=None, since=None):
    query = "SELECT document_id, title, tag, updated_at FROM documents WHERE 1=1"
    params = []
    if tag:
        query += " AND tag LIKE ?"
        params.append(f"%{tag}%")
    if since:
        query += " AND updated_at >= ?"
        params.append(since)
    
    query += " ORDER BY updated_at DESC"
    
    conn = get_db()
    cursor = conn.execute(query, params)
    for row in cursor:
        print(f"[{row['updated_at']}] {row['title']} ({row['tag'] or 'no-tag'}) - ID: {row['document_id']}")

def mental_op(action, key=None, value=None, ttl=21600):
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    
    if action == "set":
        if not key:
            print("Error: key is required for 'set' action", file=sys.stderr)
            return False
        if value is None:
            print("Error: value is required for 'set' action", file=sys.stderr)
            return False
        full_key = f"{REDIS_PREFIX}:{key}"
        r.set(full_key, value, ex=ttl)
        print(f"✓ Set {key} (TTL: {ttl}s)")
        return True
    elif action == "get":
        if not key:
            print("Error: key is required for 'get' action", file=sys.stderr)
            return False
        full_key = f"{REDIS_PREFIX}:{key}"
        val = r.get(full_key)
        print(val if val else "(nil)")
        return True
    elif action == "list":
        for k in r.scan_iter(match=f"{REDIS_PREFIX}:*"):
            print(k.replace(f"{REDIS_PREFIX}:", ""))
        return True
    elif action == "clear":
        if key:
            full_key = f"{REDIS_PREFIX}:{key}"
            r.delete(full_key)
            print(f"✓ Cleared {key}")
        else:
            keys_to_delete = list(r.scan_iter(match=f"{REDIS_PREFIX}:*"))
            if keys_to_delete:
                r.delete(*keys_to_delete)
            print("✓ Cleared all mental state")
        return True
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mema Brain v2")
    subparsers = parser.add_subparsers(dest="command")
    
    # Init
    subparsers.add_parser("init")
    
    # Index
    p_idx = subparsers.add_parser("index")
    p_idx.add_argument("path")
    p_idx.add_argument("--title")
    p_idx.add_argument("--tag")
    
    # List
    p_list = subparsers.add_parser("list")
    p_list.add_argument("--tag")
    p_list.add_argument("--since")
    
    # Mental
    p_mental = subparsers.add_parser("mental")
    p_mental.add_argument("action", choices=["set", "get", "list", "clear"])
    p_mental.add_argument("key", nargs="?")
    p_mental.add_argument("value", nargs="?")
    p_mental.add_argument("--ttl", type=int, default=21600)

    args = parser.parse_args()
    
    try:
        if args.command == "init":
            init_db()
        elif args.command == "index":
            index_doc(args.path, args.title, args.tag)
        elif args.command == "list":
            list_docs(args.tag, args.since)
        elif args.command == "mental":
            # Fix args for mental
            if args.action in ["set", "get", "clear"]:
                # If args.key is actually action arg (argparse weirdness with subparsers)
                if not args.key and len(sys.argv) > 3:
                     args.key = sys.argv[3]
                if args.action == "set" and not args.value and len(sys.argv) > 4:
                     args.value = " ".join(sys.argv[4:])
            
            success = mental_op(args.action, args.key, args.value, args.ttl)
            if not success:
                sys.exit(1)
        else:
            parser.print_help()
    except redis.RedisError as e:
        print(f"Redis Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
