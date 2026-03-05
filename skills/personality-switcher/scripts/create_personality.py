#!/usr/bin/env python3
"""
Create a new personality from description.
Usage: python3 create_personality.py "Description of personality" [--name personality-name]

The script creates the personality folder. The agent then fills in SOUL.md and IDENTITY.md.

If --name is provided, uses that as the personality name.
If --name is not provided, generates a name from the description (legacy behavior).
"""

import sys
import json
from pathlib import Path

# Add scripts dir to path for utils import
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    get_workspace, get_personalities_dir, generate_personality_name,
    validate_personality_name, personality_name_unique, get_utc_timestamp
)

def create_personality(description, personality_name=None):
    """Create new personality folder with templates."""
    
    if not description or len(description.strip()) == 0:
        return {
            "status": "error",
            "message": "Description cannot be empty.",
            "code": "empty_description"
        }
    
    workspace = get_workspace()
    personalities_dir = get_personalities_dir(workspace)
    
    # Generate or use provided personality name
    if personality_name is None:
        personality_name = generate_personality_name(description)
    else:
        personality_name = personality_name.lower().strip()
    
    # Validate name
    is_valid, error_msg = validate_personality_name(personality_name)
    if not is_valid:
        return {
            "status": "error",
            "message": f"Personality name invalid: {error_msg}",
            "code": "invalid_name"
        }
    
    # Check uniqueness
    if not personality_name_unique(personalities_dir, personality_name):
        return {
            "status": "error",
            "message": f"Personality '{personality_name}' already exists.",
            "code": "already_exists"
        }
    
    # Create personality folder
    try:
        personality_folder = personalities_dir / personality_name
        personality_folder.mkdir(parents=True, exist_ok=True)
        
    except Exception as e:
        return {
            "status": "error",
            "message": "Failed to create personality folder.",
            "error_detail": str(e),
            "code": "creation_failed"
        }
    
    return {
        "status": "success",
        "personality": personality_name,
        "message": f"Personality '{personality_name}' folder created.",
        "folder": str(personality_folder),
        "description": description,
        "note": "Folder ready. Agent will now fill in SOUL.md and IDENTITY.md.",
        "ready": f"Use /personality {personality_name} to activate when ready"
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "message": "Usage: python3 create_personality.py \"Description of personality\" [--name personality-name]",
            "code": "missing_argument"
        }))
        return
    
    # Parse arguments
    args = sys.argv[1:]
    description = None
    personality_name = None
    
    # Look for --name flag
    if "--name" in args:
        name_idx = args.index("--name")
        if name_idx + 1 < len(args):
            personality_name = args[name_idx + 1]
            # Description is everything except --name and its value
            description_parts = args[:name_idx] + args[name_idx+2:]
            description = " ".join(description_parts).strip()
        else:
            print(json.dumps({
                "status": "error",
                "message": "--name flag requires a value",
                "code": "invalid_args"
            }))
            return
    else:
        # No --name flag, description is all args
        description = " ".join(args).strip()
    
    if not description:
        print(json.dumps({
            "status": "error",
            "message": "Usage: python3 create_personality.py \"Description of personality\" [--name personality-name]",
            "code": "missing_argument"
        }))
        return
    
    result = create_personality(description, personality_name)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
