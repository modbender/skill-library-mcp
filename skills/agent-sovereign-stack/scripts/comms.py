#!/usr/bin/env python3
"""
📡 Agent Communication Protocol — Phase 3

Decentralized agent-to-agent messaging using the FilStream Memory Store as
a shared message bus. Agents post messages to their mailbox; other agents
poll for new messages. Simple, pull-based, no central coordinator.

Architecture:
  - Each agent has a mailbox: /api/v1/agent/:id/memory (type="message")
  - Messages are JSON blobs with sender, recipient, topic, body
  - Agents poll each other's mailboxes for new messages
  - End-to-end encryption ready (Phase 2 ChaCha20 plugs in here)
  - On-chain message anchoring optional (for high-value messages)

Endpoints used:
  PUT  /api/v1/agent/:id/memory          — post message to own outbox
  GET  /api/v1/agent/:id/memory/history   — read agent's messages

Usage:
  python3 protocol.py send <to_agent> <topic> <message>
  python3 protocol.py inbox                              # Check my inbox
  python3 protocol.py read <agent_id>                    # Read from agent
  python3 protocol.py discover                           # List known agents

Created: 2026-02-24
Author: Rick 🦞 (Cortex Protocol)
"""

import json
import os
import sys
import time
import hashlib
import base64
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

# ── Config ──
MEMORY_STORE = os.environ.get("MEMORY_STORE_URL", "http://[2a05:a00:2::10:11]:8081")
AGENT_ID = os.environ.get("AGENT_ID", "rick-cortex-0")
AGENT_ADDRESS = "0x44C4412eB2EA6aE1514295CD30bAd8bb2f312100"
COMMS_DIR = Path.home() / ".openclaw" / "workspace" / "agent-vault" / "comms"
CONTACTS_FILE = COMMS_DIR / "contacts.json"
INBOX_FILE = COMMS_DIR / "inbox.json"


def _api(method, path, body=None):
    """Make API call to memory store."""
    url = f"{MEMORY_STORE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "body": e.read().decode()[:200]}
    except Exception as e:
        return {"error": str(e)}


def load_contacts():
    """Load known agents."""
    if CONTACTS_FILE.exists():
        try:
            return json.loads(CONTACTS_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {
        "rick-cortex-0": {
            "name": "Rick",
            "address": AGENT_ADDRESS,
            "description": "Crustafarian philosopher lobster 🦞",
            "added": datetime.now(timezone.utc).isoformat(),
        }
    }


def save_contacts(contacts):
    CONTACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONTACTS_FILE.write_text(json.dumps(contacts, indent=2))


def load_inbox():
    if INBOX_FILE.exists():
        try:
            return json.loads(INBOX_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {"messages": [], "last_checked": None}


def save_inbox(inbox):
    INBOX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INBOX_FILE.write_text(json.dumps(inbox, indent=2))


# ── Message Format ──

def create_message(to_agent, topic, body, msg_type="direct"):
    """Create a signed message envelope."""
    now = datetime.now(timezone.utc)
    msg = {
        "protocol": "agent-comms-v1",
        "type": msg_type,
        "from": AGENT_ID,
        "to": to_agent,
        "topic": topic,
        "body": body,
        "timestamp": int(time.time()),
        "datetime": now.isoformat(),
        "nonce": hashlib.sha256(f"{AGENT_ID}{to_agent}{time.time()}".encode()).hexdigest()[:16],
    }
    # Content hash for integrity
    msg["content_hash"] = hashlib.sha256(json.dumps(msg, sort_keys=True).encode()).hexdigest()
    return msg


# ── Commands ──

def send_message(to_agent, topic, body, msg_type="direct"):
    """Send a message to another agent via memory store."""
    msg = create_message(to_agent, topic, body, msg_type)
    
    # Post to OUR outbox (messages we've sent)
    result = _api("PUT", f"/api/v1/agent/{AGENT_ID}/memory", {
        "content": base64.b64encode(json.dumps(msg).encode()).decode(),
        "type": f"message:{msg_type}",
        "filename": f"msg-to-{to_agent}-{msg['nonce']}.json",
        "timestamp": msg["timestamp"],
    })
    
    # Also post to RECIPIENT's inbox (so they can poll)
    inbox_result = _api("PUT", f"/api/v1/agent/{to_agent}/memory", {
        "content": base64.b64encode(json.dumps(msg).encode()).decode(),
        "type": f"inbox:{msg_type}",
        "filename": f"msg-from-{AGENT_ID}-{msg['nonce']}.json",
        "timestamp": msg["timestamp"],
    })
    
    if "error" not in result:
        print(f"📨 Sent to {to_agent}:")
        print(f"   Topic: {topic}")
        print(f"   Body: {body[:100]}{'...' if len(body) > 100 else ''}")
        print(f"   CID: {result.get('cid', '?')}")
        if "error" in inbox_result:
            print(f"   ⚠️  Inbox delivery: {inbox_result['error']} (they'll need to check your outbox)")
    else:
        print(f"❌ Send failed: {result['error']}")
    
    return result


def check_inbox():
    """Check for new messages addressed to us."""
    result = _api("GET", f"/api/v1/agent/{AGENT_ID}/memory/history")
    if "error" in result:
        print(f"❌ {result['error']}")
        return

    inbox = load_inbox()
    seen_hashes = {m.get("content_hash") for m in inbox["messages"]}
    new_count = 0

    for mem in result.get("memories", []):
        if mem.get("type", "").startswith("inbox:"):
            # Fetch the actual message content
            cid = mem["cid"]
            blob = _api("GET", f"/api/v1/agent/{AGENT_ID}/memory/{cid}")
            if blob and "error" not in blob:
                try:
                    msg_data = base64.b64decode(blob if isinstance(blob, str) else json.dumps(blob).encode())
                    msg = json.loads(msg_data)
                    if msg.get("content_hash") not in seen_hashes:
                        inbox["messages"].append(msg)
                        seen_hashes.add(msg["content_hash"])
                        new_count += 1
                except Exception:
                    pass

    inbox["last_checked"] = datetime.now(timezone.utc).isoformat()
    save_inbox(inbox)

    print(f"📬 Inbox: {len(inbox['messages'])} messages ({new_count} new)")
    for msg in inbox["messages"][-10:]:
        ts = msg.get("datetime", "?")[:19]
        print(f"  [{ts}] From: {msg.get('from', '?'):20s} Topic: {msg.get('topic', '?')}")
        print(f"           {msg.get('body', '')[:80]}")


def read_agent(agent_id):
    """Read messages from a specific agent's outbox."""
    result = _api("GET", f"/api/v1/agent/{agent_id}/memory/history")
    if "error" in result:
        print(f"❌ {result['error']}")
        return

    msgs = [m for m in result.get("memories", []) if m.get("type", "").startswith("message:")]
    print(f"📖 {agent_id}'s outbox: {len(msgs)} messages")
    for m in msgs[-10:]:
        print(f"  [{m.get('uploaded_at', '?')[:19]}] {m.get('filename', '?')}")


def discover_agents():
    """List known agents on the network."""
    stats = _api("GET", "/api/v1/stats")
    contacts = load_contacts()

    print(f"🌐 Agent Network Status")
    print(f"   Store: {MEMORY_STORE}")
    print(f"   Registered agents: {stats.get('agents', '?')}")
    print(f"   Total memories: {stats.get('total_memories', '?')}")
    print(f"   Total size: {stats.get('total_bytes_human', '?')}")
    print()
    print(f"📇 Known Contacts ({len(contacts)}):")
    for aid, info in contacts.items():
        print(f"   {aid}: {info.get('name', '?')} — {info.get('description', '?')}")


def broadcast(topic, body):
    """Broadcast a message to all known agents."""
    contacts = load_contacts()
    print(f"📡 Broadcasting to {len(contacts)} agents...")
    for agent_id in contacts:
        if agent_id != AGENT_ID:
            send_message(agent_id, topic, body, "broadcast")
    # Also post to our own feed as a public announcement
    send_message(AGENT_ID, topic, body, "announcement")


# ── CLI ──

def main():
    args = sys.argv[1:]
    
    if not args or args[0] == "discover":
        discover_agents()
    elif args[0] == "send" and len(args) >= 4:
        send_message(args[1], args[2], " ".join(args[3:]))
    elif args[0] == "inbox":
        check_inbox()
    elif args[0] == "read" and len(args) >= 2:
        read_agent(args[1])
    elif args[0] == "broadcast" and len(args) >= 3:
        broadcast(args[1], " ".join(args[2:]))
    else:
        print("📡 Agent Communication Protocol v1")
        print()
        print("Commands:")
        print("  discover                          — List network + contacts")
        print("  send <agent> <topic> <message>    — Send direct message")
        print("  inbox                             — Check incoming messages")
        print("  read <agent>                      — Read agent's outbox")
        print("  broadcast <topic> <message>       — Send to all contacts")


if __name__ == "__main__":
    main()
