#!/usr/bin/env python3
"""
Manage tweet-summarizer configuration.

Usage:
    config.py --show
    config.py --set key value
    config.py --check-credentials
"""

import sys
import json
import os
from pathlib import Path

CONFIG_FILE = Path.home() / '.openclaw' / 'workspace' / '.tweet-summarizer-lite.json'

def load_config():
    """Load configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        'show_summary': True,
        'auto_detect_urls': True,
        'default_mode': 'single'
    }

def save_config(config):
    """Save configuration."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def check_credentials():
    """Check if Twitter credentials are set."""
    auth_token = os.getenv('AUTH_TOKEN')
    ct0 = os.getenv('CT0')
    
    print("🔐 Twitter Credentials Status:")
    print(f"  AUTH_TOKEN: {'✅ Set' if auth_token else '❌ Not set'}")
    print(f"  CT0: {'✅ Set' if ct0 else '❌ Not set'}")
    
    if not (auth_token and ct0):
        print("\n⚠️  To use tweet-summarizer, you need:")
        print("   1. Log into Twitter in your browser")
        print("   2. Open Developer Tools (F12)")
        print("   3. Go to Application → Cookies → twitter.com")
        print("   4. Copy 'auth_token' value")
        print("   5. Copy 'ct0' value")
        print("   6. Set in your shell:")
        print("      export AUTH_TOKEN='...your-token...'")
        print("      export CT0='...your-ct0...'")
        return False
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  config.py --show")
        print("  config.py --set key value")
        print("  config.py --check-credentials")
        sys.exit(1)
    
    command = sys.argv[1]
    config = load_config()
    
    if command == '--show':
        print("⚙️  Configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")
    
    elif command == '--set' and len(sys.argv) > 3:
        key = sys.argv[2]
        value = sys.argv[3]
        
        # Parse boolean values
        if value.lower() in ('true', 'yes', '1'):
            value = True
        elif value.lower() in ('false', 'no', '0'):
            value = False
        
        config[key] = value
        save_config(config)
        print(f"✅ Set {key} = {value}")
    
    elif command == '--check-credentials':
        check_credentials()
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
