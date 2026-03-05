#!/usr/bin/env python3
"""
Delete a personality.
Usage: python3 delete_personality.py <personality-name>

If deleting active personality, automatically switches to "default" first.
"""

import sys
import json
import shutil
from pathlib import Path

# Add scripts dir to path for utils import
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    get_workspace, get_personalities_dir, read_state,
    personality_exists, copy_personality_to_workspace,
    write_state, copy_workspace_to_personality
)

def delete_personality(personality_name):
    """Delete personality folder."""
    
    workspace = get_workspace()
    personalities_dir = get_personalities_dir(workspace)
    
    # Validate input
    if not personality_name:
        return {
            "status": "error",
            "message": "Personality name is required.",
            "code": "missing_argument"
        }
    
    # Prevent deleting "default"
    if personality_name == "default":
        return {
            "status": "error",
            "message": "Cannot delete 'default' personality.",
            "code": "cannot_delete_default"
        }
    
    # Verify personality exists
    if not personality_exists(personalities_dir, personality_name):
        return {
            "status": "error",
            "message": f"Personality '{personality_name}' not found.",
            "code": "personality_not_found"
        }
    
    current_active = read_state(workspace)
    
    # If deleting active personality, switch to default first
    if current_active == personality_name:
        try:
            default_folder = personalities_dir / "default"
            if not copy_personality_to_workspace(default_folder, workspace):
                raise Exception("Failed to load default personality")
            
            write_state(workspace, "default", previous_personality=personality_name)
        except Exception as e:
            return {
                "status": "error",
                "message": "Failed to switch to default before deletion.",
                "error_detail": str(e),
                "code": "switch_failed"
            }
    
    # Delete personality folder
    try:
        personality_folder = personalities_dir / personality_name
        shutil.rmtree(personality_folder)
    except Exception as e:
        return {
            "status": "error",
            "message": "Failed to delete personality folder.",
            "error_detail": str(e),
            "code": "deletion_failed"
        }
    
    response = {
        "status": "success",
        "message": f"Personality '{personality_name}' deleted."
    }
    
    if current_active == personality_name:
        response["switched_to"] = "default"
        response["note"] = "Switched to default personality before deletion."
    
    return response

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "message": "Usage: python3 delete_personality.py <personality-name>",
            "code": "missing_argument"
        }))
        return
    
    personality_name = sys.argv[1]
    result = delete_personality(personality_name)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
