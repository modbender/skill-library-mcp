#!/usr/bin/env python3
"""
identity_cli.py - CLI tool for identity-resolver

Commands:
  init              Initialize identity map
  resolve           Resolve channel:user_id to canonical ID
  add              Add channel mapping
  remove           Remove channel mapping  
  list             List all identities
  channels         Get channels for canonical ID
  is-owner         Check if canonical ID is owner

Author: OpenClaw Agent <agent@openclaw.local>
License: MIT
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Import from local module
sys.path.insert(0, str(Path(__file__).parent))
from identity import (
    resolve_canonical_id,
    add_channel,
    remove_channel,
    list_identities,
    get_channels,
    is_owner,
    _get_workspace,
    _get_identity_map_path
)

def cmd_init(args):
    """Initialize identity map."""
    ws = _get_workspace(args.workspace)
    map_path = _get_identity_map_path(ws)
    
    if map_path.exists() and not args.force:
        print(f"✗ Identity map already exists at {map_path}")
        print("  Use --force to reinitialize")
        return 1
    
    # Create empty map
    map_path.parent.mkdir(parents=True, exist_ok=True)
    with open(map_path, 'w') as f:
        json.dump({"version": "1.0", "identities": {}}, f, indent=2)
    
    print(f"✓ Initialized identity map at {map_path}")
    
    # Try to detect owner from USER.md
    user_md = ws / "USER.md"
    if user_md.exists():
        content = user_md.read_text()
        import re
        name_match = re.search(r'\*\*Name:\*\*\s+(.+)', content)
        if name_match:
            owner_name = name_match.group(1).split()[0].lower()
            print(f"✓ Owner canonical ID: {owner_name}")
            print(f"✓ Owner will auto-register on first use")
    
    return 0

def cmd_resolve(args):
    """Resolve channel identity to canonical ID."""
    # Auto-detect from environment if not provided
    channel = args.channel or os.getenv("OPENCLAW_CHANNEL")
    user_id = args.user_id or os.getenv("OPENCLAW_USER_ID")
    
    if not channel or not user_id:
        print("✗ Error: --channel and --user-id required (or set OPENCLAW_CHANNEL, OPENCLAW_USER_ID)")
        return 1
    
    canonical_id = resolve_canonical_id(channel, user_id, args.workspace)
    
    if args.json:
        print(json.dumps({"canonical_id": canonical_id}))
    else:
        print(canonical_id)
    
    return 0

def cmd_add(args):
    """Add channel mapping."""
    if not args.canonical or not args.channel or not args.user_id:
        print("✗ Error: --canonical, --channel, and --user-id required")
        return 1
    
    add_channel(args.canonical, args.channel, args.user_id, args.workspace, args.display_name)
    
    if args.json:
        print(json.dumps({"status": "added", "canonical_id": args.canonical, "channel": f"{args.channel}:{args.user_id}"}))
    else:
        print(f"✓ Added {args.channel}:{args.user_id} → {args.canonical}")
    
    return 0

def cmd_remove(args):
    """Remove channel mapping."""
    if not args.canonical or not args.channel or not args.user_id:
        print("✗ Error: --canonical, --channel, and --user-id required")
        return 1
    
    remove_channel(args.canonical, args.channel, args.user_id, args.workspace)
    
    if args.json:
        print(json.dumps({"status": "removed", "canonical_id": args.canonical, "channel": f"{args.channel}:{args.user_id}"}))
    else:
        print(f"✓ Removed {args.channel}:{args.user_id} from {args.canonical}")
    
    return 0

def cmd_list(args):
    """List all identities."""
    identities = list_identities(args.workspace)
    
    if args.json:
        print(json.dumps(identities, indent=2))
    else:
        if not identities:
            print("No identities registered")
            return 0
        
        for canonical_id, data in sorted(identities.items()):
            owner_badge = " [OWNER]" if data.get("is_owner") else ""
            print(f"{canonical_id}{owner_badge}")
            if data.get("display_name"):
                print(f"  Display Name: {data['display_name']}")
            if data.get("channels"):
                print(f"  Channels:")
                for channel in sorted(data["channels"]):
                    print(f"    - {channel}")
            print()
    
    return 0

def cmd_channels(args):
    """Get channels for canonical ID."""
    if not args.canonical:
        print("✗ Error: --canonical required")
        return 1
    
    channels = get_channels(args.canonical, args.workspace)
    
    if args.json:
        print(json.dumps({"canonical_id": args.canonical, "channels": channels}))
    else:
        if not channels:
            print(f"No channels registered for {args.canonical}")
        else:
            for channel in sorted(channels):
                print(channel)
    
    return 0

def cmd_is_owner(args):
    """Check if canonical ID is owner."""
    if not args.canonical:
        print("✗ Error: --canonical required")
        return 1
    
    result = is_owner(args.canonical, args.workspace)
    
    if args.json:
        print(json.dumps({"canonical_id": args.canonical, "is_owner": result}))
    else:
        print("yes" if result else "no")
    
    return 0

def main():
    parser = argparse.ArgumentParser(
        description="Identity resolver CLI - Manage multi-channel user identities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize identity map
  identity init
  
  # Resolve identity (auto-detect from env)
  OPENCLAW_CHANNEL=telegram OPENCLAW_USER_ID=123456789 identity resolve
  
  # Resolve with explicit params
  identity resolve --channel telegram --user-id 123456789
  
  # Add channel mapping
  identity add --canonical alice --channel discord --user-id alice#1234
  
  # List all identities
  identity list
  
  # Get channels for user
  identity channels --canonical alice
  
  # Check owner status
  identity is-owner --canonical alice
"""
    )
    
    parser.add_argument('--workspace', help='Workspace path (default: auto-detect)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # init
    p_init = subparsers.add_parser('init', help='Initialize identity map')
    p_init.add_argument('--force', action='store_true', help='Overwrite existing map')
    
    # resolve
    p_resolve = subparsers.add_parser('resolve', help='Resolve channel:user_id to canonical ID')
    p_resolve.add_argument('--channel', help='Channel name (or set OPENCLAW_CHANNEL)')
    p_resolve.add_argument('--user-id', help='Provider user ID (or set OPENCLAW_USER_ID)')
    
    # add
    p_add = subparsers.add_parser('add', help='Add channel mapping')
    p_add.add_argument('--canonical', required=True, help='Canonical user ID')
    p_add.add_argument('--channel', required=True, help='Channel name')
    p_add.add_argument('--user-id', required=True, help='Provider user ID')
    p_add.add_argument('--display-name', help='Display name')
    
    # remove
    p_remove = subparsers.add_parser('remove', help='Remove channel mapping')
    p_remove.add_argument('--canonical', required=True, help='Canonical user ID')
    p_remove.add_argument('--channel', required=True, help='Channel name')
    p_remove.add_argument('--user-id', required=True, help='Provider user ID')
    
    # list
    subparsers.add_parser('list', help='List all identities')
    
    # channels
    p_channels = subparsers.add_parser('channels', help='Get channels for canonical ID')
    p_channels.add_argument('--canonical', required=True, help='Canonical user ID')
    
    # is-owner
    p_is_owner = subparsers.add_parser('is-owner', help='Check if canonical ID is owner')
    p_is_owner.add_argument('--canonical', required=True, help='Canonical user ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Dispatch to command handler
    commands = {
        'init': cmd_init,
        'resolve': cmd_resolve,
        'add': cmd_add,
        'remove': cmd_remove,
        'list': cmd_list,
        'channels': cmd_channels,
        'is-owner': cmd_is_owner
    }
    
    try:
        return commands[args.command](args)
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        if args.json:
            print(json.dumps({"error": str(e)}))
        return 1

if __name__ == "__main__":
    sys.exit(main())
