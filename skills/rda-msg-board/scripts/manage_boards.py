#!/usr/bin/env python3
"""Manage RDA MSG Board profiles."""

import argparse
import json
import os
import sys

def get_config_path():
    """Get the boards.yaml config file path."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'boards.yaml')

def load_profiles():
    """Load board profiles from boards.yaml."""
    config_path = get_config_path()
    if not os.path.exists(config_path):
        return {}
    try:
        import yaml
        with open(config_path) as f:
            return yaml.safe_load(f).get('profiles', {})
    except ImportError:
        print("Error: PyYAML not installed. Install with: pip install pyyaml")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading profiles: {e}")
        sys.exit(1)

def save_profiles(profiles):
    """Save board profiles to boards.yaml."""
    config_path = get_config_path()
    try:
        import yaml
        with open(config_path, 'w') as f:
            yaml.dump({'profiles': profiles}, f, default_flow_style=False)
    except ImportError:
        print("Error: PyYAML not installed. Install with: pip install pyyaml")
        sys.exit(1)
    except Exception as e:
        print(f"Error saving profiles: {e}")
        sys.exit(1)

def list_boards():
    """List all configured boards."""
    profiles = load_profiles()
    if not profiles:
        print("No board profiles configured.")
        return

    print("\n📟 Configured Board Profiles:")
    print("-" * 60)
    for name, config in profiles.items():
        print(f"\n  [{name}]")
        print(f"    IP:       {config.get('ip', 'N/A')}")
        print(f"    Username: {config.get('user', 'admin')}")
        print(f"    Password: {'*' * len(config.get('pass', ''))}")
    print()

def add_board(args):
    """Add a new board profile."""
    profiles = load_profiles()

    if args.name in profiles:
        if not args.force:
            print(f"Error: Profile '{args.name}' already exists. Use --force to overwrite.")
            sys.exit(1)

    profiles[args.name] = {
        'ip': args.ip,
        'user': args.user,
        'pass': args.password
    }

    save_profiles(profiles)
    print(f"✅ Board profile '{args.name}' added/updated successfully.")
    print(f"   IP: {args.ip}")
    print(f"   Use: python3 send_message.py \"Hello\" --profile {args.name}")

def remove_board(args):
    """Remove a board profile."""
    profiles = load_profiles()

    if args.name not in profiles:
        print(f"Error: Profile '{args.name}' not found.")
        list_boards()
        sys.exit(1)

    del profiles[args.name]
    save_profiles(profiles)
    print(f"✅ Board profile '{args.name}' removed successfully.")

def main():
    parser = argparse.ArgumentParser(description="Manage RDA MSG Board profiles")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List command
    subparsers.add_parser('list', help='List all board profiles')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new board profile')
    add_parser.add_argument('name', help='Profile name (e.g., home, office, lab)')
    add_parser.add_argument('--ip', required=True, help='Device IP address')
    add_parser.add_argument('--user', default='admin', help='Web interface username (default: admin)')
    add_parser.add_argument('--pass', dest='password', default='msgboard', help='Web interface password (default: msgboard)')
    add_parser.add_argument('--force', action='store_true', help='Overwrite existing profile')

    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove a board profile')
    remove_parser.add_argument('name', help='Profile name to remove')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'list':
        list_boards()
    elif args.command == 'add':
        add_board(args)
    elif args.command == 'remove':
        remove_board(args)

if __name__ == "__main__":
    main()
