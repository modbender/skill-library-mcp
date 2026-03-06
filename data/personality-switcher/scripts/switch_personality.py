#!/usr/bin/env python3
"""
Switch to a personality.
Usage: python3 switch_personality.py <personality_name>

Implements atomic switching with backup and rollback.
"""

import sys
import json
from pathlib import Path

# Add scripts dir to path for utils import
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    get_workspace, get_personalities_dir, read_state, write_state,
    backup_personality_files, restore_backup, verify_personality_folder,
    personality_exists, copy_personality_to_workspace, copy_workspace_to_personality,
    cleanup_old_backups
)

def switch_personality(personality_name):
    """Perform atomic personality switch."""
    
    workspace = get_workspace()
    personalities_dir = get_personalities_dir(workspace)
    target_folder = personalities_dir / personality_name
    
    # ===== PRE-SWITCH CHECKLIST =====
    
    # Check target exists
    if not personality_exists(personalities_dir, personality_name):
        return {
            "status": "error",
            "message": f"Personality '{personality_name}' not found.",
            "code": "personality_not_found"
        }
    
    # Verify target folder integrity
    is_valid, error_msg = verify_personality_folder(target_folder)
    if not is_valid:
        return {
            "status": "error",
            "message": f"Personality '{personality_name}' is invalid: {error_msg}",
            "code": "invalid_personality"
        }
    
    # Get current active personality
    current_active = read_state(workspace) or "default"
    
    # Prevent switching to already-active personality
    if current_active == personality_name:
        return {
            "status": "success",
            "message": f"Already using personality '{personality_name}'.",
            "personality": personality_name
        }
    
    # ===== STEP 1: PRESERVE CURRENT STATE (BACKUP) =====
    try:
        backup_location = backup_personality_files(workspace, prefix="current")
    except Exception as e:
        return {
            "status": "error",
            "message": "Failed to create backup before switch.",
            "error_detail": str(e),
            "code": "backup_failed"
        }
    
    # ===== STEP 2: PERSIST CURRENT PERSONALITY CHANGES =====
    try:
        current_personality_folder = personalities_dir / current_active
        current_personality_folder.mkdir(parents=True, exist_ok=True)
        
        if not copy_workspace_to_personality(workspace, current_personality_folder):
            raise Exception("Failed to copy workspace files to current personality folder")
    except Exception as e:
        restore_backup(workspace, backup_location)
        return {
            "status": "error",
            "message": "Failed to persist current personality changes.",
            "error_detail": str(e),
            "code": "persist_failed",
            "previous_personality": current_active,
            "backup_restored": True
        }
    
    # ===== STEP 3: LOAD NEW PERSONALITY =====
    try:
        if not copy_personality_to_workspace(target_folder, workspace):
            raise Exception("Failed to copy personality files to workspace")
    except Exception as e:
        restore_backup(workspace, backup_location)
        return {
            "status": "error",
            "message": "Failed to load new personality.",
            "error_detail": str(e),
            "code": "load_failed",
            "previous_personality": current_active,
            "backup_restored": True
        }
    
    # ===== STEP 4: UPDATE STATE =====
    try:
        write_state(workspace, personality_name, previous_personality=current_active)
    except Exception as e:
        # Critical failure - restore everything
        restore_backup(workspace, backup_location)
        return {
            "status": "error",
            "message": "Failed to update personality state.",
            "error_detail": str(e),
            "code": "state_write_failed",
            "previous_personality": current_active,
            "backup_restored": True
        }
    
    # ===== STEP 5: VERIFY (INTEGRITY CHECK) =====
    try:
        is_valid, error_msg = verify_personality_folder(target_folder)
        if not is_valid:
            raise Exception(f"Personality integrity check failed: {error_msg}")
        
        # Check files exist in workspace
        soul_file = workspace / "SOUL.md"
        identity_file = workspace / "IDENTITY.md"
        
        if not soul_file.exists() or not identity_file.exists():
            raise Exception("Personality files not found in workspace after switch")
    except Exception as e:
        # Integrity check failed - rollback
        restore_backup(workspace, backup_location)
        write_state(workspace, current_active)  # Restore old state
        return {
            "status": "error",
            "message": "Personality integrity check failed. Rolled back.",
            "error_detail": str(e),
            "code": "integrity_check_failed",
            "previous_personality": current_active,
            "backup_restored": True
        }
    
    # ===== SUCCESS =====
    # Clean up old backups (keep last 10)
    cleanup_count, cleanup_error = cleanup_old_backups(workspace, keep_count=10)
    
    response = {
        "status": "success",
        "message": f"Switched to personality '{personality_name}'.",
        "personality": personality_name,
        "previous": current_active,
        "backup": {
            "location": str(backup_location),
            "note": "Backup of previous personality state"
        }
    }
    
    if cleanup_count > 0:
        response["cleanup"] = {
            "deleted_backups": cleanup_count,
            "note": "Old backups automatically cleaned up"
        }
    
    if cleanup_error:
        response["cleanup_warning"] = cleanup_error
    
    return response

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "message": "Usage: python3 switch_personality.py <personality_name>",
            "code": "missing_argument"
        }))
        return
    
    personality_name = sys.argv[1]
    result = switch_personality(personality_name)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
