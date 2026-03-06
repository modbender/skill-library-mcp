#!/usr/bin/env python3
"""
Shared utilities for personality-switcher skill.
Handles file I/O, backups, validation, state management.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime, timezone
import hashlib


def get_utc_timestamp():
    """Return current UTC timestamp in ISO format with Z suffix."""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def get_workspace():
    """Return workspace root path."""
    return Path.home() / ".openclaw" / "workspace"


def get_personalities_dir(workspace):
    """Return personalities directory path."""
    personalities_dir = workspace / "personalities"
    personalities_dir.mkdir(parents=True, exist_ok=True)
    return personalities_dir


def get_backups_dir(workspace):
    """Return personality backups directory path."""
    backups_dir = workspace / "personalities" / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)
    return backups_dir


def read_state(workspace):
    """Read _personality_state.json. Return active personality name or None."""
    personalities_dir = get_personalities_dir(workspace)
    state_file = personalities_dir / "_personality_state.json"
    if not state_file.exists():
        return None
    try:
        with open(state_file, 'r') as f:
            data = json.load(f)
            return data.get("active_personality")
    except Exception:
        return None


def write_state(workspace, personality_name, previous_personality=None):
    """Write _personality_state.json with active personality."""
    personalities_dir = get_personalities_dir(workspace)
    state_file = personalities_dir / "_personality_state.json"
    state = {
        "active_personality": personality_name,
        "timestamp": get_utc_timestamp(),
        "previous_personality": previous_personality,
        "note": "Tracks which personality is currently active across session boundaries"
    }
    state_file.write_text(json.dumps(state, indent=2))


def backup_personality_files(workspace, prefix="backup"):
    """
    Create timestamped backup of SOUL.md and IDENTITY.md in personalities/backups/.
    Includes personality name in backup directory for easy identification.
    Return path to backup directory.
    """
    timestamp = get_utc_timestamp().replace(':', '-').replace('Z', '')
    
    # Get current active personality to include in backup name
    active_personality = read_state(workspace)
    if not active_personality:
        active_personality = "unknown"
    
    backups_dir = get_backups_dir(workspace)
    # Format: from-<personality>_<timestamp> or backup-<personality>_<timestamp>
    backup_dir = backups_dir / f"{prefix}-from-{active_personality}_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    soul_file = workspace / "SOUL.md"
    identity_file = workspace / "IDENTITY.md"
    
    if soul_file.exists():
        shutil.copy2(soul_file, backup_dir / "SOUL.md")
    if identity_file.exists():
        shutil.copy2(identity_file, backup_dir / "IDENTITY.md")
    
    return backup_dir


def restore_backup(workspace, backup_location):
    """Restore SOUL.md and IDENTITY.md from backup location."""
    try:
        soul_backup = Path(backup_location) / "SOUL.md"
        identity_backup = Path(backup_location) / "IDENTITY.md"
        
        if soul_backup.exists():
            shutil.copy2(soul_backup, workspace / "SOUL.md")
        if identity_backup.exists():
            shutil.copy2(identity_backup, workspace / "IDENTITY.md")
        
        return True
    except Exception:
        return False


def _extract_backup_timestamp(backup_name):
    """
    Extract timestamp from backup directory name.
    Handles both old and new formats:
    - Old: "current_2026-02-08T17-19-13.100517"
    - New: "current-from-aelindor_2026-02-08T17-19-13.100517"
    
    Return timestamp string (ISO format with colons restored) or None if unparseable.
    """
    try:
        # Find the last underscore - everything after is the timestamp
        parts = backup_name.rsplit('_', 1)
        if len(parts) != 2:
            return None
        
        timestamp_str = parts[1]  # e.g., "2026-02-08T17-19-13.100517"
        
        # Convert back to ISO format: "2026-02-08T17:19:13.100517Z"
        if 'T' in timestamp_str:
            date_part, time_part = timestamp_str.split('T')
            # Reconstruct time with colons: "17-19-13" → "17:19:13"
            time_components = time_part.split('.')
            if len(time_components) == 2:
                time_hms = time_components[0]  # "17-19-13"
                fractional = time_components[1]  # "100517"
                restored = f"{date_part}T{time_hms.replace('-', ':')}.{fractional}Z"
                return restored
        
        return None
    except Exception:
        return None


def cleanup_old_backups(workspace, keep_count=10, max_age_days=None):
    """
    Clean up old backups in personalities/backups/.
    Keep the most recent `keep_count` backups.
    Optionally delete backups older than `max_age_days` days.
    
    Return (deleted_count, error_message or None).
    """
    try:
        backups_dir = get_backups_dir(workspace)
        
        if not backups_dir.exists():
            return 0, None
        
        # List all backup directories
        backups = []
        for item in backups_dir.iterdir():
            if item.is_dir():
                try:
                    timestamp_str = _extract_backup_timestamp(item.name)
                    if timestamp_str:
                        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        backups.append((dt, item))
                except Exception:
                    # Skip unparseable backup directories
                    continue
        
        if not backups:
            return 0, None
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x[0], reverse=True)
        
        deleted_count = 0
        now = datetime.now(timezone.utc)
        
        for i, (timestamp, backup_dir) in enumerate(backups):
            should_delete = False
            
            # Delete if beyond keep_count
            if i >= keep_count:
                should_delete = True
            
            # Delete if older than max_age_days
            if max_age_days is not None:
                age_days = (now - timestamp).days
                if age_days > max_age_days:
                    should_delete = True
            
            if should_delete:
                try:
                    shutil.rmtree(backup_dir)
                    deleted_count += 1
                except Exception as e:
                    return deleted_count, f"Failed to delete backup {backup_dir.name}: {str(e)}"
        
        return deleted_count, None
    
    except Exception as e:
        return 0, f"Cleanup failed: {str(e)}"


def get_backup_info(workspace):
    """
    Get information about current backups.
    Return list of dicts: [{"name": "...", "from_personality": "...", "timestamp": "...", "age_days": ...}, ...]
    """
    try:
        backups_dir = get_backups_dir(workspace)
        
        if not backups_dir.exists():
            return []
        
        backups = []
        now = datetime.now(timezone.utc)
        
        for item in sorted(backups_dir.iterdir(), reverse=True):
            if item.is_dir():
                try:
                    timestamp_str = _extract_backup_timestamp(item.name)
                    if timestamp_str:
                        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        age_days = (now - dt).days
                        
                        # Extract personality name from backup directory name
                        # Format: "current-from-aelindor_2026-02-08T..." or "backup-from-default_..."
                        from_personality = "unknown"
                        if "from-" in item.name:
                            parts = item.name.split("from-")
                            if len(parts) == 2:
                                personality_part = parts[1].rsplit('_', 1)[0]  # Remove timestamp
                                from_personality = personality_part
                        
                        backups.append({
                            "name": item.name,
                            "from_personality": from_personality,
                            "timestamp": timestamp_str,
                            "age_days": age_days
                        })
                except Exception:
                    continue
        
        return backups
    
    except Exception:
        return []


def verify_personality_folder(personality_folder):
    """
    Verify personality folder contains SOUL.md and IDENTITY.md.
    (USER.md must remain in workspace root, never in personality folders)
    Return (is_valid, error_message).
    """
    personality_folder = Path(personality_folder)
    
    if not personality_folder.exists():
        return False, "Personality folder does not exist"
    
    soul_file = personality_folder / "SOUL.md"
    identity_file = personality_folder / "IDENTITY.md"
    
    if not soul_file.exists():
        return False, "Missing SOUL.md"
    if not identity_file.exists():
        return False, "Missing IDENTITY.md"
    
    try:
        soul_file.read_text()
        identity_file.read_text()
    except Exception as e:
        return False, f"Cannot read personality files: {str(e)}"
    
    return True, None


def list_personalities(personalities_dir, workspace):
    """
    List all personalities.
    Return list of dicts: [{"name": "...", "active": True/False}, ...]
    """
    if not personalities_dir.exists():
        return []
    
    active = read_state(workspace)
    personalities = []
    
    for item in sorted(personalities_dir.iterdir()):
        if item.is_dir():
            is_valid, _ = verify_personality_folder(item)
            if is_valid:
                personalities.append({
                    "name": item.name,
                    "active": (item.name == active)
                })
    
    return personalities


def validate_personality_name(name):
    """
    Validate personality name format.
    Return (is_valid, error_message).
    Rules: no spaces, lowercase, alphanumeric + hyphens only.
    """
    if not name:
        return False, "Name cannot be empty"
    
    if " " in name:
        return False, "Name cannot contain spaces (use hyphens)"
    
    if name.lower() != name:
        return False, "Name must be lowercase"
    
    if not all(c.isalnum() or c == '-' for c in name):
        return False, "Name can only contain letters, numbers, and hyphens"
    
    if name == "default":
        return False, "Cannot use 'default' as custom name"
    
    return True, None


def generate_personality_name(description):
    """
    Generate personality name from description.
    Example: "A stoic dwarf" → "stoic-dwarf"
    """
    # Take first few words, lowercase, spaces to hyphens
    words = description.lower().split()[:3]
    name = "-".join(words)
    
    # Remove non-alphanumeric except hyphens
    name = "".join(c if c.isalnum() or c == '-' else '' for c in name)
    
    # Clean up multiple hyphens
    while "--" in name:
        name = name.replace("--", "-")
    
    name = name.strip('-')
    return name if name else "personality"


def personality_exists(personalities_dir, name):
    """Check if personality folder exists and is valid."""
    personality_folder = personalities_dir / name
    is_valid, _ = verify_personality_folder(personality_folder)
    return is_valid


def personality_name_unique(personalities_dir, name):
    """Check if personality name doesn't already exist."""
    personality_folder = personalities_dir / name
    return not personality_folder.exists()


def copy_personality_to_workspace(personality_folder, workspace):
    """Copy SOUL.md and IDENTITY.md from personality folder to workspace."""
    try:
        soul_src = personality_folder / "SOUL.md"
        identity_src = personality_folder / "IDENTITY.md"
        
        soul_dst = workspace / "SOUL.md"
        identity_dst = workspace / "IDENTITY.md"
        
        if soul_src.exists():
            shutil.copy2(soul_src, soul_dst)
        if identity_src.exists():
            shutil.copy2(identity_src, identity_dst)
        
        return True
    except Exception as e:
        print(f"Error copying personality: {str(e)}")
        return False


def copy_workspace_to_personality(workspace, personality_folder):
    """Copy SOUL.md and IDENTITY.md from workspace to personality folder."""
    try:
        soul_src = workspace / "SOUL.md"
        identity_src = workspace / "IDENTITY.md"
        
        soul_dst = personality_folder / "SOUL.md"
        identity_dst = personality_folder / "IDENTITY.md"
        
        if soul_src.exists():
            shutil.copy2(soul_src, soul_dst)
        if identity_src.exists():
            shutil.copy2(identity_src, identity_dst)
        
        return True
    except Exception as e:
        print(f"Error copying to personality folder: {str(e)}")
        return False
