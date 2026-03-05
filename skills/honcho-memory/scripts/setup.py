#!/usr/bin/env python3
"""
Honcho Memory — Setup script.
Creates workspace and peers in Honcho.

Usage:
  python3 scripts/setup.py --workspace "my-workspace" --peers "j,axel,axobotl"
  python3 scripts/setup.py --workspace "my-workspace" --peers "user,assistant" --credentials ~/.config/honcho/credentials.json
"""

import argparse
import json
import os
import sys

def main():
    parser = argparse.ArgumentParser(description='Honcho Memory Setup')
    parser.add_argument('--workspace', required=True, help='Workspace name/ID')
    parser.add_argument('--peers', required=True, help='Comma-separated peer names')
    parser.add_argument('--credentials', default=os.path.expanduser('~/.config/honcho/credentials.json'),
                        help='Path to credentials file')
    
    args = parser.parse_args()
    
    # Load credentials
    if not os.path.exists(args.credentials):
        print(f"Error: Credentials file not found at {args.credentials}")
        print("Create it with: {\"api_key\": \"your-key\", \"organization\": \"your-org\"}")
        sys.exit(1)
    
    with open(args.credentials) as f:
        creds = json.load(f)
    
    if not creds.get('api_key'):
        print("Error: api_key not found in credentials file")
        sys.exit(1)
    
    try:
        from honcho import Honcho
    except ImportError:
        print("Error: honcho-ai not installed. Run: pip install honcho-ai")
        sys.exit(1)
    
    # Initialize
    honcho = Honcho(workspace_id=args.workspace, api_key=creds['api_key'])
    
    peer_names = [p.strip() for p in args.peers.split(',') if p.strip()]
    peers = {}
    
    for name in peer_names:
        peers[name] = honcho.peer(name)
        print(f"  Created peer: {name}")
    
    # Update credentials with workspace info
    creds['workspace_id'] = args.workspace
    creds['peers'] = peer_names
    
    os.makedirs(os.path.dirname(args.credentials), exist_ok=True)
    with open(args.credentials, 'w') as f:
        json.dump(creds, f, indent=2)
    
    print(f"\nSetup complete: workspace={args.workspace}, {len(peers)} peers created")
    print(f"Credentials updated at {args.credentials}")

if __name__ == '__main__':
    main()
