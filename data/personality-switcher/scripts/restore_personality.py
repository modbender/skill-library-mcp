#!/usr/bin/env python3
"""
Restore active personality to workspace (heartbeat restoration).
Usage: python3 restore_personality.py

Runs on every heartbeat to ensure personality survives session restart/compacting.
"""

import sys
import json
from pathlib import Path

# Add scripts dir to path for utils import
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    get_workspace, get_personalities_dir, read_state,
    verify_personality_folder, copy_personality_to_workspace
)

def restore_personality():
    """Restore active personality from state."""
    
    workspace = get_workspace()
    personalities_dir = get_personalities_dir(workspace)
    
    # Get active personality from state, default to "default"
    active_personality = read_state(workspace)
    if not active_personality:
        active_personality = "default"
    
    # Get personality folder
    personality_folder = personalities_dir / active_personality
    
    # Verify folder exists and is valid
    is_valid, error_msg = verify_personality_folder(personality_folder)
    if not is_valid:
        # Fallback to default if active personality is corrupted
        if active_personality != "default":
            personality_folder = personalities_dir / "default"
            is_valid, error_msg = verify_personality_folder(personality_folder)
            if not is_valid:
                return {
                    "status": "error",
                    "message": "Cannot restore personality: default is also corrupted.",
                    "error_detail": error_msg,
                    "code": "no_valid_personality"
                }
            active_personality = "default"
        else:
            return {
                "status": "error",
                "message": f"Cannot restore personality '{active_personality}': {error_msg}",
                "code": "personality_corrupted"
            }
    
    # Copy personality files to workspace
    try:
        if not copy_personality_to_workspace(personality_folder, workspace):
            raise Exception("Failed to copy files")
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to restore personality '{active_personality}'.",
            "error_detail": str(e),
            "code": "restore_failed"
        }
    
    return {
        "status": "success",
        "message": f"Restored personality '{active_personality}'.",
        "active_personality": active_personality
    }

def main():
    result = restore_personality()
    print(json.dumps(result))

if __name__ == "__main__":
    main()
