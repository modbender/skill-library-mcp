#!/usr/bin/env python3
"""
List all available personalities.
Usage: python3 list_personalities.py
"""

import sys
import json
from pathlib import Path

# Add scripts dir to path for utils import
sys.path.insert(0, str(Path(__file__).parent))
from utils import get_workspace, get_personalities_dir, list_personalities

def main():
    workspace = get_workspace()
    personalities_dir = get_personalities_dir(workspace)
    
    personalities = list_personalities(personalities_dir, workspace)
    
    response = {
        "status": "success",
        "personalities": personalities,
        "message": f"Found {len(personalities)} personality(ies)."
    }
    
    print(json.dumps(response))

if __name__ == "__main__":
    main()
