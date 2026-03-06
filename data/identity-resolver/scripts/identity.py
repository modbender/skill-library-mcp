#!/usr/bin/env python3
"""
identity.py - Canonical user identity resolution for OpenClaw

Resolves multi-channel user identities (Telegram, WhatsApp, Discord, web)
to canonical user IDs, preventing state fragmentation across channels.

Author: OpenClaw Agent <agent@openclaw.local>
License: MIT
"""

import json
import os
import re
import fcntl
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict

# Default workspace detection
def _get_workspace(workspace: Optional[str] = None) -> Path:
    """Get workspace path (auto-detect if not provided)."""
    if workspace:
        return Path(workspace).resolve()
    
    # Try environment variable
    if os.getenv("OPENCLAW_WORKSPACE"):
        return Path(os.getenv("OPENCLAW_WORKSPACE")).resolve()
    
    # Default: current directory
    return Path.cwd()

def _get_identity_map_path(workspace: Path) -> Path:
    """Get identity map file path."""
    # Try data/identity-map.json first (new standard)
    data_path = workspace / "data" / "identity-map.json"
    if data_path.exists():
        return data_path
    
    # Fallback: memory/identity-map.json (legacy)
    memory_path = workspace / "memory" / "identity-map.json"
    if memory_path.exists():
        return memory_path
    
    # Default: create in data/
    data_path.parent.mkdir(parents=True, exist_ok=True)
    return data_path

def _sanitize_canonical_id(canonical_id: str) -> str:
    """
    Sanitize canonical ID to prevent path traversal and injection attacks.
    
    Only allows: lowercase letters, numbers, hyphens, underscores
    Max length: 64 characters
    """
    # Remove all non-alphanumeric except - and _
    sanitized = re.sub(r'[^a-z0-9\-_]', '', canonical_id.lower())
    
    # Remove leading/trailing hyphens or underscores
    sanitized = sanitized.strip('-_')
    
    # Limit length
    sanitized = sanitized[:64]
    
    # Prevent empty or dangerous patterns
    if not sanitized or sanitized.startswith('.') or '/' in sanitized:
        raise ValueError(f"Invalid canonical_id: {canonical_id}")
    
    return sanitized

def _load_owner_numbers(workspace: Path) -> List[str]:
    """Load owner contact numbers from USER.md."""
    user_md = workspace / "USER.md"
    if not user_md.exists():
        return []
    
    content = user_md.read_text()
    numbers = []
    
    # Extract numbers from contact-related lines
    for line in content.splitlines():
        if any(kw in line for kw in ["Contact", "WhatsApp", "Telegram", "Phone", "Mobile", "Other"]):
            # Extract all patterns: +digits or just long digit sequences
            # Handles: +1234567890, 123456789, +9876543210, +5555555555
            matches = re.findall(r'\+?\d{7,}', line)
            numbers.extend(matches)
    
    return list(set(numbers))  # Deduplicate

def _load_identity_map(workspace: Path) -> Dict:
    """
    Load identity map with file locking (thread-safe read).
    
    Returns:
        dict with structure:
        {
            "version": "1.0",
            "identities": {
                "canonical_id": {
                    "canonical_id": str,
                    "is_owner": bool,
                    "display_name": str,
                    "channels": [list of "channel:user_id"],
                    "created_at": ISO timestamp,
                    "updated_at": ISO timestamp
                }
            }
        }
    """
    map_path = _get_identity_map_path(workspace)
    
    if not map_path.exists():
        # Initialize empty map
        return {"version": "1.0", "identities": {}}
    
    try:
        with open(map_path, 'r') as f:
            # Shared lock for reading
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Validate structure
        if "identities" not in data:
            data = {"version": "1.0", "identities": {}}
        
        return data
    except (json.JSONDecodeError, IOError):
        return {"version": "1.0", "identities": {}}

def _save_identity_map(data: Dict, workspace: Path):
    """
    Save identity map with file locking (thread-safe write).
    """
    map_path = _get_identity_map_path(workspace)
    map_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Atomic write with exclusive lock
    temp_path = map_path.with_suffix('.tmp')
    try:
        with open(temp_path, 'w') as f:
            # Exclusive lock for writing
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(data, f, indent=2, sort_keys=True)
                f.flush()
                os.fsync(f.fileno())
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Atomic rename
        temp_path.replace(map_path)
    finally:
        if temp_path.exists():
            temp_path.unlink()

def resolve_canonical_id(
    channel: str,
    provider_user_id: str,
    workspace: Optional[str] = None,
    owner_numbers: Optional[List[str]] = None
) -> str:
    """
    Resolve channel identity to canonical user ID.
    
    Args:
        channel: Provider name (telegram, whatsapp, discord, web, etc.)
        provider_user_id: User ID from provider
        workspace: Path to workspace (default: auto-detect)
        owner_numbers: List of owner contact IDs (default: load from USER.md)
    
    Returns:
        Canonical user ID (e.g., "alice") or
        "stranger:{channel}:{provider_user_id}" for unmapped users
    
    Auto-registers owner numbers from workspace/USER.md if provided.
    """
    ws = _get_workspace(workspace)
    identity_map = _load_identity_map(ws)
    
    # Build channel ID
    channel_id = f"{channel}:{provider_user_id}"
    
    # Check if already mapped
    for canonical_id, user_data in identity_map["identities"].items():
        if channel_id in user_data.get("channels", []):
            return canonical_id
    
    # Auto-registration for owner
    if owner_numbers is None:
        owner_numbers = _load_owner_numbers(ws)
    
    if provider_user_id in owner_numbers:
        # Find or create owner canonical ID
        owner_canonical = None
        for canonical_id, user_data in identity_map["identities"].items():
            if user_data.get("is_owner"):
                owner_canonical = canonical_id
                break
        
        if not owner_canonical:
            # Create owner identity (use "owner" or first name from USER.md)
            user_md = ws / "USER.md"
            if user_md.exists():
                content = user_md.read_text()
                name_match = re.search(r'\*\*Name:\*\*\s+(.+)', content)
                if name_match:
                    owner_canonical = _sanitize_canonical_id(name_match.group(1).split()[0])
                else:
                    owner_canonical = "owner"
            else:
                owner_canonical = "owner"
            
            # Create owner entry
            identity_map["identities"][owner_canonical] = {
                "canonical_id": owner_canonical,
                "is_owner": True,
                "display_name": owner_canonical.capitalize(),
                "channels": [],
                "created_at": datetime.now(timezone.utc).isoformat() + "Z",
                "updated_at": datetime.now(timezone.utc).isoformat() + "Z"
            }
        
        # Add channel to owner
        if channel_id not in identity_map["identities"][owner_canonical]["channels"]:
            identity_map["identities"][owner_canonical]["channels"].append(channel_id)
            identity_map["identities"][owner_canonical]["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
            _save_identity_map(identity_map, ws)
        
        return owner_canonical
    
    # Unmapped stranger
    return f"stranger:{channel}:{provider_user_id}"

def add_channel(
    canonical_id: str,
    channel: str,
    provider_user_id: str,
    workspace: Optional[str] = None,
    display_name: Optional[str] = None
):
    """
    Add channel mapping to a canonical user.
    
    Creates new canonical user if doesn't exist.
    Thread-safe (file locking).
    """
    ws = _get_workspace(workspace)
    canonical_id = _sanitize_canonical_id(canonical_id)
    identity_map = _load_identity_map(ws)
    
    channel_id = f"{channel}:{provider_user_id}"
    
    # Create user if doesn't exist
    if canonical_id not in identity_map["identities"]:
        identity_map["identities"][canonical_id] = {
            "canonical_id": canonical_id,
            "is_owner": False,
            "display_name": display_name or canonical_id.capitalize(),
            "channels": [],
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "updated_at": datetime.now(timezone.utc).isoformat() + "Z"
        }
    
    # Add channel if not already present
    if channel_id not in identity_map["identities"][canonical_id]["channels"]:
        identity_map["identities"][canonical_id]["channels"].append(channel_id)
        identity_map["identities"][canonical_id]["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
        _save_identity_map(identity_map, ws)

def remove_channel(
    canonical_id: str,
    channel: str,
    provider_user_id: str,
    workspace: Optional[str] = None
):
    """Remove channel mapping from canonical user."""
    ws = _get_workspace(workspace)
    canonical_id = _sanitize_canonical_id(canonical_id)
    identity_map = _load_identity_map(ws)
    
    channel_id = f"{channel}:{provider_user_id}"
    
    if canonical_id in identity_map["identities"]:
        user_data = identity_map["identities"][canonical_id]
        if channel_id in user_data["channels"]:
            user_data["channels"].remove(channel_id)
            user_data["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
            _save_identity_map(identity_map, ws)

def list_identities(workspace: Optional[str] = None) -> Dict:
    """Return all identity mappings."""
    ws = _get_workspace(workspace)
    return _load_identity_map(ws)["identities"]

def get_channels(canonical_id: str, workspace: Optional[str] = None) -> List[str]:
    """Get all channels for a canonical user."""
    ws = _get_workspace(workspace)
    canonical_id = _sanitize_canonical_id(canonical_id)
    identity_map = _load_identity_map(ws)
    
    if canonical_id in identity_map["identities"]:
        return identity_map["identities"][canonical_id].get("channels", [])
    return []

def is_owner(canonical_id: str, workspace: Optional[str] = None) -> bool:
    """Check if canonical ID is the owner."""
    ws = _get_workspace(workspace)
    canonical_id = _sanitize_canonical_id(canonical_id)
    identity_map = _load_identity_map(ws)
    
    if canonical_id in identity_map["identities"]:
        return identity_map["identities"][canonical_id].get("is_owner", False)
    return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 identity.py <channel> <user_id> [workspace]")
        sys.exit(1)
    
    channel = sys.argv[1]
    user_id = sys.argv[2]
    workspace = sys.argv[3] if len(sys.argv) > 3 else None
    
    canonical_id = resolve_canonical_id(channel, user_id, workspace)
    print(canonical_id)
