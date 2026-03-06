#!/usr/bin/env bash
# list-sessions.sh — Scan Gemini CLI session files and output a session index.
#
# Usage:
#   ./list-sessions.sh <project-name> [--since <days>d]
#
# Gemini CLI stores sessions as JSON files in:
#   ~/.gemini/tmp/<sha256(project_root)>/chats/session-*.json
# The project root is hashed (SHA256), so we compute hashes of candidate
# directories and check for matching session directories.
#
# Output: JSON array to stdout with session metadata for matching projects.
# Requires: python3

set -euo pipefail

PROJECT="${1:-}"
SINCE_DAYS=""

shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --since) SINCE_DAYS="${2%d}"; shift 2 ;;
    *) echo "Unknown flag: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$PROJECT" ]]; then
  echo "Usage: list-sessions.sh <project-name> [--since Nd]" >&2
  exit 1
fi

GEMINI_HOME="${GEMINI_CLI_HOME:-$HOME/.gemini}"
TMP_ROOT="$GEMINI_HOME/tmp"

if [[ ! -d "$TMP_ROOT" ]]; then
  echo "[]"
  exit 0
fi

CUTOFF=0
if [[ -n "$SINCE_DAYS" ]]; then
  CUTOFF=$(date -v-"${SINCE_DAYS}"d +%s 2>/dev/null || date -d "${SINCE_DAYS} days ago" +%s 2>/dev/null || echo 0)
fi

exec python3 - "$PROJECT" "$TMP_ROOT" "$CUTOFF" << 'PYEOF'
import json
import hashlib
import os
import sys
import stat

project_name = sys.argv[1].lower()
tmp_root = sys.argv[2]
cutoff = int(sys.argv[3])

def sha256_hex(s):
    return hashlib.sha256(s.encode()).hexdigest()

def extract_text(content):
    """Extract plain text from a PartListUnion (string, Part, or Part[])."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, dict):
        return (content.get("text") or "").strip()
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict):
                t = p.get("text", "")
                if t:
                    parts.append(t)
        return " ".join(parts).strip()
    return ""

def clean_msg(text, max_len=200):
    """Clean message text for display."""
    text = " ".join(text.split())
    # Remove non-printable
    text = "".join(c for c in text if 32 <= ord(c) < 127 or c in "\t\n")
    text = text.strip()
    return text[:max_len]

# ── Phase 1: Collect candidate directories and compute hashes ──
home = os.path.expanduser("~")
base_dirs = [
    home,
    os.path.join(home, "dev"),
    os.path.join(home, "projects"),
    os.path.join(home, "src"),
    os.path.join(home, "code"),
    os.path.join(home, "work"),
    os.path.join(home, "Documents"),
    os.path.join(home, "repos"),
]

# Collect all existing hash dirs for quick lookup
existing_hashes = set()
try:
    for entry in os.scandir(tmp_root):
        if entry.is_dir() and len(entry.name) == 64:
            existing_hashes.add(entry.name)
except OSError:
    pass

# Map hash -> project_root for matching candidates
hash_to_path = {}

def register_candidate(path):
    """Register a directory as a candidate if its hash exists in gemini tmp."""
    abspath = os.path.abspath(path)
    h = sha256_hex(abspath)
    if h in existing_hashes:
        hash_to_path[h] = abspath

# Scan base directories up to 3 levels deep
for base in base_dirs:
    if not os.path.isdir(base):
        continue
    register_candidate(base)
    try:
        for e1 in os.scandir(base):
            if not e1.is_dir() or e1.name.startswith("."):
                continue
            register_candidate(e1.path)
            try:
                for e2 in os.scandir(e1.path):
                    if not e2.is_dir() or e2.name.startswith("."):
                        continue
                    register_candidate(e2.path)
                    try:
                        for e3 in os.scandir(e2.path):
                            if not e3.is_dir() or e3.name.startswith("."):
                                continue
                            register_candidate(e3.path)
                    except (PermissionError, OSError):
                        pass
            except (PermissionError, OSError):
                pass
    except (PermissionError, OSError):
        pass

# ── Phase 1b: Fallback — for any unmatched hash dirs, try to extract project
# root from tool call arguments in the first session file ──
unmatched = existing_hashes - set(hash_to_path.keys())
for h in unmatched:
    chats_dir = os.path.join(tmp_root, h, "chats")
    if not os.path.isdir(chats_dir):
        continue
    # Peek at the first session file for file paths in tool calls
    try:
        files = sorted(f for f in os.listdir(chats_dir) if f.startswith("session-") and f.endswith(".json"))
    except OSError:
        continue
    if not files:
        continue
    try:
        with open(os.path.join(chats_dir, files[0]), "r") as fh:
            data = json.load(fh)
        for msg in data.get("messages", []):
            if msg.get("type") != "gemini":
                continue
            for tc in msg.get("toolCalls", []):
                args = tc.get("args", {})
                if not isinstance(args, dict):
                    continue
                for key in ("file_path", "path", "directory"):
                    val = args.get(key, "")
                    if isinstance(val, str) and val.startswith("/"):
                        # Verify the hash matches
                        # Try progressively shorter path prefixes
                        parts = val.split("/")
                        for depth in range(len(parts), 1, -1):
                            candidate = "/".join(parts[:depth])
                            if sha256_hex(candidate) == h:
                                hash_to_path[h] = candidate
                                break
                        if h in hash_to_path:
                            break
                if h in hash_to_path:
                    break
            if h in hash_to_path:
                break
    except (json.JSONDecodeError, OSError, KeyError):
        continue

# ── Phase 2: Filter by project name ──
matched_hashes = {}
for h, path in hash_to_path.items():
    path_lower = path.lower()
    if project_name in path_lower:
        matched_hashes[h] = path

if not matched_hashes:
    print("[]")
    sys.exit(0)

# ── Phase 3: Scan session files and build index ──
results = []

for h, project_path in matched_hashes.items():
    chats_dir = os.path.join(tmp_root, h, "chats")
    if not os.path.isdir(chats_dir):
        continue

    try:
        session_files = sorted(
            f for f in os.listdir(chats_dir)
            if f.startswith("session-") and f.endswith(".json")
        )
    except OSError:
        continue

    for fname in session_files:
        fpath = os.path.join(chats_dir, fname)

        # Modification time
        try:
            st = os.stat(fpath)
            mod_epoch = int(st.st_mtime)
        except OSError:
            continue

        # Time filter
        if cutoff > 0 and mod_epoch < cutoff:
            continue

        # Parse session JSON
        try:
            with open(fpath, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (json.JSONDecodeError, OSError):
            continue

        messages = data.get("messages", [])
        if not messages:
            continue

        # last_updated from the file (prefer the field, fall back to mtime)
        last_updated = data.get("lastUpdated", "")
        if not last_updated:
            from datetime import datetime, timezone
            last_updated = datetime.fromtimestamp(mod_epoch, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Extract first and last user messages
        first_user = ""
        last_user = ""
        for msg in messages:
            if msg.get("type") == "user":
                text = extract_text(msg.get("content", ""))
                if text:
                    if not first_user:
                        first_user = clean_msg(text)
                    last_user = clean_msg(text)

        # Count "lines" as number of messages (analog of line count for JSONL)
        line_count = len(messages)

        results.append({
            "file": fpath,
            "platform": "gemini-cli",
            "project_slug": project_path,
            "modified": last_updated,
            "lines": line_count,
            "first_user_message": first_user,
            "last_user_message": last_user,
        })

# Sort by modified descending
results.sort(key=lambda x: x["modified"], reverse=True)
print(json.dumps(results, indent=2))
PYEOF
