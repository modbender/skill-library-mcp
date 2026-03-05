#!/usr/bin/env python3
"""
ProductAI Setup Helper

Initialize ProductAI integration with API credentials.
"""

import json
import sys
from pathlib import Path

CONFIG_PATH = Path.home() / '.openclaw' / 'workspace' / 'productai' / 'config.json'

def setup():
    """Interactive setup for ProductAI integration."""
    print("ProductAI Setup")
    print("=" * 60)
    print()
    
    # Check if config already exists
    if CONFIG_PATH.exists():
        print(f"Configuration already exists at {CONFIG_PATH}")
        response = input("Overwrite? [y/N]: ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            sys.exit(0)
        print()
    
    # Gather configuration
    print("Enter your ProductAI API credentials:")
    print("(Get your API key from ProductAI dashboard when available)")
    print()
    
    api_key = input("API Key: ").strip()
    if not api_key:
        print("Error: API key is required", file=sys.stderr)
        sys.exit(1)
    
    api_endpoint = input("API Endpoint [https://api.productai.photo/v1]: ").strip()
    if not api_endpoint:
        api_endpoint = "https://api.productai.photo/v1"
    
    default_model = input("Default Model [nano-banana-2]: ").strip()
    if not default_model:
        default_model = "nano-banana-2"
    
    default_resolution = input("Default Resolution [1024x1024]: ").strip()
    if not default_resolution:
        default_resolution = "1024x1024"
    
    plan = input("Your Plan (basic/standard/pro) [standard]: ").strip().lower()
    if not plan:
        plan = "standard"
    
    # Create config
    config = {
        "api_key": api_key,
        "api_endpoint": api_endpoint,
        "default_model": default_model,
        "default_resolution": default_resolution,
        "plan": plan
    }
    
    # Save config
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Secure the config file
    CONFIG_PATH.chmod(0o600)
    
    print()
    print("=" * 60)
    print(f"✓ Configuration saved to {CONFIG_PATH}")
    print()
    print("You're ready to use ProductAI!")
    print()
    print("Next steps:")
    print("  1. Test the integration:")
    print("     scripts/generate_photo.py --image product.jpg --prompt 'white background' --output test.png")
    print()
    print("  2. Read the documentation:")
    print("     cat SKILL.md")
    print("     cat references/API.md")
    print()

def main():
    try:
        setup()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
