#!/usr/bin/env python3
"""
Variflight API wrapper - Universal version
Supports: OpenClaw, Claude Code, Cursor, and other AI clients

Configuration priority:
1. Command line --api-key
2. Environment variable VARIFLIGHT_API_KEY
3. ./.variflight.json (project config)
4. ~/.variflight.json (user config)
5. ~/.config/variflight/config.json (XDG standard)
"""

import sys
import os
import json
import urllib.request
import urllib.error
import argparse

BASE_URL = 'https://ai.variflight.com/api/v1/mcp/data'

def find_config_file():
    """Find config file in standard locations"""
    paths = [
        './.variflight.json',  # Project config
        os.path.expanduser('~/.variflight.json'),  # User config
        os.path.expanduser('~/.config/variflight/config.json'),  # XDG standard
    ]
    
    # Also check OpenClaw path for backward compatibility
    openclaw_path = os.path.expanduser('~/.openclaw/workspace/.env.variflight')
    if os.path.exists(openclaw_path):
        return openclaw_path
    
    for path in paths:
        if os.path.exists(path):
            return path
    return None

def load_api_key(args_api_key=None):
    """Load API key from various sources"""
    # 1. Command line argument (highest priority)
    if args_api_key:
        return args_api_key
    
    # 2. Environment variable
    if os.environ.get('VARIFLIGHT_API_KEY'):
        return os.environ.get('VARIFLIGHT_API_KEY')
    
    # 3. Config file
    config_path = find_config_file()
    if config_path:
        try:
            if config_path.endswith('.json'):
                with open(config_path) as f:
                    config = json.load(f)
                    if config.get('api_key'):
                        return config['api_key']
            elif config_path.endswith('.env.variflight'):
                # Legacy OpenClaw format
                with open(config_path) as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            key, val = line.strip().split('=', 1)
                            if key == 'VARIFLIGHT_API_KEY':
                                return val
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}", file=sys.stderr)
    
    return None

def make_request(endpoint, params, api_key):
    """Make API request to Variflight"""
    body = json.dumps({
        "endpoint": endpoint,
        "params": params
    }).encode('utf-8')
    
    req = urllib.request.Request(
        BASE_URL,
        data=body,
        headers={
            'X-VARIFLIGHT-KEY': api_key,
            'Content-Type': 'application/json'
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}

def parse_args_with_api_key():
    """Parse arguments, extracting --api-key if present"""
    api_key = None
    remaining = []
    
    i = 0
    while i < len(sys.argv):
        if sys.argv[i] in ('--api-key', '-k') and i + 1 < len(sys.argv):
            api_key = sys.argv[i + 1]
            i += 2
        elif sys.argv[i].startswith('--api-key='):
            api_key = sys.argv[i].split('=', 1)[1]
            i += 1
        else:
            remaining.append(sys.argv[i])
            i += 1
    
    return api_key, remaining

def main():
    # Parse --api-key from anywhere in args
    args_api_key, remaining_args = parse_args_with_api_key()
    
    if len(remaining_args) < 2:
        print("Usage: variflight.py [--api-key KEY] <endpoint> [key=value ...]")
        print("\nExamples:")
        print("  variflight.py flights dep=PEK arr=SHA date=2025-02-15")
        print("  variflight.py --api-key sk-xxxx flight fnum=MU2157 date=2025-02-15")
        sys.exit(1)
    
    endpoint = remaining_args[1]
    params = {}
    
    for arg in remaining_args[2:]:
        if '=' in arg:
            key, val = arg.split('=', 1)
            params[key] = val
    
    api_key = load_api_key(args_api_key)
    
    if not api_key:
        print("Error: VARIFLIGHT_API_KEY not found", file=sys.stderr)
        print("\nPlease configure using one of:", file=sys.stderr)
        print("  1. export VARIFLIGHT_API_KEY=sk-xxxx", file=sys.stderr)
        print("  2. echo '{\"api_key\": \"sk-xxxx\"}' > ~/.variflight.json", file=sys.stderr)
        print("  3. Use --api-key flag", file=sys.stderr)
        sys.exit(1)
    
    result = make_request(endpoint, params, api_key)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
