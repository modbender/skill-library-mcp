#!/usr/bin/env python3
"""
🧠 FilStream Agent Memory Store — Client Library

Upload, retrieve, and manage encrypted agent memories on FilStream.
Phase 1: Basic upload/retrieve with content-addressing.
Phase 2 will add ChaCha20-Poly1305 encryption.

Usage:
  python3 client.py upload <file>              # Upload a memory file
  python3 client.py upload-all                 # Upload all memory/*.md files
  python3 client.py latest                     # Get latest memory CID
  python3 client.py history                    # List all stored memories
  python3 client.py retrieve <cid>             # Download a specific memory

Created: 2026-02-24
Author: Rick 🦞 (Cortex Protocol / FilStream)
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
WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
IDENTITY_DIR = WORKSPACE / "identity"
STORE_DIR = WORKSPACE / "agent-vault" / "memory-store"
STORE_STATE = STORE_DIR / "store-state.json"

# FilStream index server
FILSTREAM_INDEX = os.environ.get("FILSTREAM_INDEX", "http://[2a05:a00:2::10:11]:8080")

# Agent identity
AGENT_ID = "rick-cortex-0"  # Token #0
AGENT_ADDRESS = "0x44C4412eB2EA6aE1514295CD30bAd8bb2f312100"


def content_hash(data):
    """SHA-256 content hash for addressing."""
    return hashlib.sha256(data).hexdigest()


def load_state():
    """Load memory store state."""
    if STORE_STATE.exists():
        try:
            return json.loads(STORE_STATE.read_text())
        except json.JSONDecodeError:
            pass
    return {"memories": [], "latest_cid": None, "total_bytes": 0}


def save_state(state):
    """Save memory store state."""
    STORE_STATE.parent.mkdir(parents=True, exist_ok=True)
    STORE_STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def upload_to_filstream(data_bytes, filename, metadata=None):
    """Upload memory to FilStream index server."""
    try:
        # Try the agent memory API endpoint first
        payload = json.dumps({
            "agent_id": AGENT_ID,
            "filename": filename,
            "content": base64.b64encode(data_bytes).decode(),
            "content_hash": content_hash(data_bytes),
            "timestamp": int(time.time()),
            "type": metadata.get("type", "memory") if metadata else "memory",
            "size_bytes": len(data_bytes),
        }).encode()

        for endpoint in ["/api/v1/agent/memory", "/api/upload", "/api/v0/add"]:
            try:
                req = urllib.request.Request(
                    f"{FILSTREAM_INDEX}{endpoint}",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    result = json.loads(resp.read())
                    cid = result.get("cid") or result.get("Hash") or result.get("IpfsHash")
                    if cid:
                        return {"cid": cid, "endpoint": endpoint}
            except urllib.error.HTTPError:
                continue
            except Exception:
                continue

        # Fallback: content-addressed local store
        cid = f"mem-{content_hash(data_bytes)[:16]}"
        local_path = STORE_DIR / "cache" / f"{cid}.json"
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(payload)
        return {"cid": cid, "endpoint": "local", "local_path": str(local_path)}

    except Exception as e:
        return {"error": str(e)}


def upload_file(filepath):
    """Upload a single memory file."""
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return None

    data = filepath.read_bytes()
    filename = filepath.name
    file_type = "identity_snapshot" if "identity" in filename else "daily_log" if filename.endswith(".md") else "memory"

    print(f"📤 Uploading: {filename} ({len(data)} bytes, type={file_type})")
    result = upload_to_filstream(data, filename, {"type": file_type})

    if "error" in result:
        print(f"   ❌ {result['error']}")
        return None

    cid = result["cid"]
    endpoint = result["endpoint"]
    print(f"   ✅ CID: {cid} (via {endpoint})")

    # Update state
    state = load_state()
    record = {
        "filename": filename,
        "cid": cid,
        "content_hash": content_hash(data),
        "size_bytes": len(data),
        "type": file_type,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
    }
    state["memories"].append(record)
    state["latest_cid"] = cid
    state["total_bytes"] += len(data)
    save_state(state)
    return record


def upload_all_memories():
    """Upload all memory files + identity snapshot."""
    print("🧠 FilStream Agent Memory Store — Bulk Upload")
    print(f"   Agent: {AGENT_ID}")
    print(f"   FilStream: {FILSTREAM_INDEX}")
    print()

    files_to_upload = []

    # Identity snapshot
    id_path = IDENTITY_DIR / "current_identity.json"
    if id_path.exists():
        files_to_upload.append(id_path)

    # Memory markdown files (last 7 days)
    if MEMORY_DIR.is_dir():
        md_files = sorted(MEMORY_DIR.glob("*.md"), reverse=True)[:7]
        files_to_upload.extend(md_files)

    # Key workspace files
    for fname in ["MEMORY.md", "SOUL.md"]:
        fp = WORKSPACE / fname
        if fp.exists():
            files_to_upload.append(fp)

    print(f"📦 {len(files_to_upload)} files to upload")
    print()

    uploaded = 0
    total_bytes = 0
    for fp in files_to_upload:
        result = upload_file(fp)
        if result:
            uploaded += 1
            total_bytes += result["size_bytes"]

    print(f"\n{'='*50}")
    print(f"🧠 Bulk upload complete!")
    print(f"   Uploaded: {uploaded}/{len(files_to_upload)} files")
    print(f"   Total: {total_bytes / 1024:.1f} KB")
    print(f"{'='*50}")


def show_history():
    """Show memory store history."""
    state = load_state()
    mems = state.get("memories", [])
    print(f"🧠 Memory Store — {len(mems)} items ({state.get('total_bytes', 0) / 1024:.1f} KB total)")
    print(f"   Agent: {AGENT_ID}")
    print(f"   Latest CID: {state.get('latest_cid', 'none')}")
    print()
    for m in mems[-15:]:
        ts = m.get("uploaded_at", "?")[:19]
        print(f"   [{ts}] {m.get('filename', '?'):30s} {m.get('size_bytes', 0):>6d}B → {m.get('cid', '?')[:20]}...")


def show_latest():
    """Show latest memory."""
    state = load_state()
    print(f"Latest CID: {state.get('latest_cid', 'none')}")
    mems = state.get("memories", [])
    if mems:
        m = mems[-1]
        print(f"File: {m.get('filename')}")
        print(f"Type: {m.get('type')}")
        print(f"Size: {m.get('size_bytes')} bytes")
        print(f"Uploaded: {m.get('uploaded_at')}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "history":
        show_history()
    elif args[0] == "latest":
        show_latest()
    elif args[0] == "upload" and len(args) > 1:
        upload_file(args[1])
    elif args[0] == "upload-all":
        upload_all_memories()
    else:
        print("Usage:")
        print("  python3 client.py history              # List stored memories")
        print("  python3 client.py latest               # Show latest CID")
        print("  python3 client.py upload <file>         # Upload a file")
        print("  python3 client.py upload-all            # Upload all recent memories")
