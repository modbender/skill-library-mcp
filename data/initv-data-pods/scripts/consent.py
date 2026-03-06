#!/usr/bin/env python3
"""
Consent Layer v0.1 - Agent consent management for Data Pods
Usage: consent.py <command> [options]
"""

import sqlite3
import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import uuid

CONSENT_DIR = Path.home() / ".openclaw" / "consent"
PODS_DIR = Path.home() / ".openclaw" / "data-pods"

def ensure_dir():
    CONSENT_DIR.mkdir(parents=True, exist_ok=True)
    db_path = CONSENT_DIR / "consent.db"
    if not db_path.exists():
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            agent TEXT,
            pods_allowed TEXT,
            created_at TEXT,
            expires_at TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            session_id TEXT,
            pod TEXT,
            query TEXT,
            rows INTEGER
        )''')
        conn.commit()
        conn.close()

def list_pods():
    """List available pods."""
    if not PODS_DIR.exists():
        print("No pods found.")
        return []
    pods = []
    for d in PODS_DIR.iterdir():
        if d.is_dir():
            pods.append(d.name)
    return pods

def status(session_id: str = None):
    """Show consent status."""
    ensure_dir()
    db_path = CONSENT_DIR / "consent.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    if session_id:
        c.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = c.fetchone()
        if row:
            print(f"Session: {row[0]}")
            print(f"Agent: {row[1]}")
            print(f"Pods allowed: {row[2]}")
            print(f"Created: {row[3]}")
            print(f"Expires: {row[4]}")
        else:
            print(f"No session: {session_id}")
    else:
        c.execute("SELECT id, agent, pods_allowed, expires_at FROM sessions")
        rows = c.fetchall()
        if rows:
            print("Active sessions:")
            for row in rows:
                print(f"  [{row[0][:8]}...] {row[1]} -> {row[2]} (expires: {row[3]})")
        else:
            print("No active sessions.")
    conn.close()

def grant(pods: list, agent: str = "unknown", duration_minutes: int = 60):
    """Grant consent to pods for a session."""
    ensure_dir()
    session_id = str(uuid.uuid4())
    created = datetime.now()
    expires = created + timedelta(minutes=duration_minutes)
    
    db_path = CONSENT_DIR / "consent.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO sessions VALUES (?, ?, ?, ?, ?)",
              (session_id, agent, ",".join(pods), created.isoformat(), expires.isoformat()))
    conn.commit()
    conn.close()
    
    print(f"Granted {len(pods)} pods to agent '{agent}'")
    print(f"  Session: {session_id}")
    print(f"  Pods: {', '.join(pods)}")
    print(f"  Expires: {expires.strftime('%H:%M')}")
    return session_id

def revoke(session_id: str):
    """Revoke consent for a session."""
    ensure_dir()
    db_path = CONSENT_DIR / "consent.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()
    print(f"Revoked session: {session_id}")

def audit_logs(session_id: str = None, today: bool = False):
    """Show audit logs."""
    ensure_dir()
    db_path = CONSENT_DIR / "consent.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    if session_id:
        c.execute("SELECT * FROM audit WHERE session_id = ?", (session_id,))
    else:
        c.execute("SELECT * FROM audit ORDER BY timestamp DESC LIMIT 20")
    
    rows = c.fetchall()
    if rows:
        for row in rows:
            print(f"[{row[1]}] {row[3]}: {row[4][:50]}... ({row[5]} rows)")
    else:
        print("No audit logs.")
    conn.close()

def check_consent(session_id: str, pod: str) -> bool:
    """Check if session has consent for pod."""
    ensure_dir()
    db_path = CONSENT_DIR / "consent.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT pods_allowed, expires_at FROM sessions WHERE id = ?", (session_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return False
    
    pods_allowed = row[0].split(",")
    expires = datetime.fromisoformat(row[1])
    
    if datetime.now() > expires:
        return False
    
    return pod in pods_allowed

def log_access(session_id: str, pod: str, query: str, rows: int):
    """Log a pod access."""
    ensure_dir()
    db_path = CONSENT_DIR / "consent.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO audit VALUES (NULL, ?, ?, ?, ?, ?)",
              (datetime.now().isoformat(), session_id, pod, query, rows))
    conn.commit()
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Consent Layer v0.1")
    sub = parser.add_subparsers(dest="cmd")
    
    sub.add_parser("list", help="List available pods")
    sub.add_parser("status", help="Show consent status")
    
    grant_p = sub.add_parser("grant", help="Grant consent to pods")
    grant_p.add_argument("pods", nargs="+", help="Pod names to allow")
    grant_p.add_argument("--agent", default="cli", help="Agent name")
    grant_p.add_argument("--duration", type=int, default=60, help="Minutes until expiry")
    
    revoke_p = sub.add_parser("revoke", help="Revoke consent")
    revoke_p.add_argument("session", help="Session ID")
    
    audit_p = sub.add_parser("audit", help="Show audit logs")
    audit_p.add_argument("--session", help="Filter by session")
    
    args = parser.parse_args()
    
    if args.cmd == "list":
        pods = list_pods()
        if pods:
            print("Available pods:")
            for p in pods:
                print(f"  - {p}")
        else:
            print("No pods found.")
    elif args.cmd == "status":
        status()
    elif args.cmd == "grant":
        grant(args.pods, args.agent, args.duration)
    elif args.cmd == "revoke":
        revoke(args.session)
    elif args.cmd == "audit":
        audit_logs(args.session)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
