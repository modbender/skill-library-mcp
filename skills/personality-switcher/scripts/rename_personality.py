#!/usr/bin/env python3
"""
Rename a personality.
Usage: python3 rename_personality.py <old-name> <new-name>
"""

import sys
import json
from pathlib import Path

# Add scripts dir to path for utils import
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    get_workspace, get_personalities_dir, read_state, write_state,
    validate_personality_name, personality_exists, personality_name_unique
)

def rename_personality(old_name, new_name):
    """Rename personality folder."""
    
    workspace = get_workspace()
    personalities_dir = get_personalities_dir(workspace)
    
    # Validate inputs
    if not old_name or not new_name:
        return {
            "status": "error",
            "message": "Both old and new names are required.",
            "code": "missing_argument"
        }
    
    # Prevent renaming "default"
    if old_name == "default":
        return {
            "status": "error",
            "message": "Cannot rename 'default' personality.",
            "code": "cannot_rename_default"
        }
    
    # Verify old personality exists
    if not personality_exists(personalities_dir, old_name):
        return {
            "status": "error",
            "message": f"Personality '{old_name}' not found.",
            "code": "personality_not_found"
        }
    
    # Validate new name
    is_valid, error_msg = validate_personality_name(new_name)
    if not is_valid:
        return {
            "status": "error",
            "message": f"Invalid new name: {error_msg}",
            "code": "invalid_name"
        }
    
    # Check new name is unique
    if not personality_name_unique(personalities_dir, new_name):
        return {
            "status": "error",
            "message": f"Personality '{new_name}' already exists.",
            "code": "already_exists"
        }
    
    # Rename folder
    try:
        old_folder = personalities_dir / old_name
        new_folder = personalities_dir / new_name
        old_folder.rename(new_folder)
    except Exception as e:
        return {
            "status": "error",
            "message": "Failed to rename personality folder.",
            "error_detail": str(e),
            "code": "rename_failed"
        }
    
    # Update state if renaming active personality
    current_active = read_state(workspace)
    if current_active == old_name:
        try:
            write_state(workspace, new_name, previous_personality=old_name)
        except Exception as e:
            # Attempt to revert folder rename
            try:
                new_folder.rename(old_folder)
            except:
                pass
            return {
                "status": "error",
                "message": "Failed to update personality state.",
                "error_detail": str(e),
                "code": "state_update_failed"
            }
    
    return {
        "status": "success",
        "message": f"Renamed '{old_name}' to '{new_name}'.",
        "old_name": old_name,
        "new_name": new_name,
        "folder": str(personalities_dir / new_name)
    }

def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "status": "error",
            "message": "Usage: python3 rename_personality.py <old-name> <new-name>",
            "code": "missing_argument"
        }))
        return
    
    old_name = sys.argv[1]
    new_name = sys.argv[2]
    result = rename_personality(old_name, new_name)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
