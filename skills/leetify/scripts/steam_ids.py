#!/usr/bin/env python3
"""
Manage Username -> Steam ID mappings
"""
import json
import os
import sys

STORAGE_FILE = os.path.join(os.path.dirname(__file__), '../data/steam_ids.json')


def ensure_storage():
    """Ensure storage directory and file exist"""
    os.makedirs(os.path.dirname(STORAGE_FILE), exist_ok=True)
    if not os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'w') as f:
            json.dump({}, f)


def normalize_username(username):
    """Normalize username (remove @ if present)"""
    return username.lstrip('@').lower()


def save_steam_id(username, steam_id, name=None, telegram_id=None):
    """Save Steam ID for a username"""
    ensure_storage()
    
    with open(STORAGE_FILE, 'r') as f:
        data = json.load(f)
    
    key = normalize_username(username)
    
    data[key] = {
        'steam_id': steam_id,
        'name': name or username,
        'username': username.lstrip('@')
    }
    
    if telegram_id:
        data[key]['telegram_id'] = telegram_id
    
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return True


def get_steam_id(username):
    """Get Steam ID for a username"""
    ensure_storage()
    
    with open(STORAGE_FILE, 'r') as f:
        data = json.load(f)
    
    key = normalize_username(username)
    user_data = data.get(key)
    
    if user_data:
        return user_data.get('steam_id')
    return None


def get_user_data(username):
    """Get all data for a username"""
    ensure_storage()
    
    with open(STORAGE_FILE, 'r') as f:
        data = json.load(f)
    
    key = normalize_username(username)
    return data.get(key)


def list_all():
    """List all stored mappings"""
    ensure_storage()
    
    with open(STORAGE_FILE, 'r') as f:
        data = json.load(f)
    
    return data


def delete_steam_id(username):
    """Delete Steam ID mapping for a username"""
    ensure_storage()
    
    with open(STORAGE_FILE, 'r') as f:
        data = json.load(f)
    
    key = normalize_username(username)
    
    if key in data:
        del data[key]
        
        with open(STORAGE_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    
    return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage Username -> Steam ID mappings')
    parser.add_argument('action', choices=['save', 'get', 'list', 'delete'], help='Action to perform')
    parser.add_argument('--username', help='Telegram username (with or without @)')
    parser.add_argument('--telegram-id', help='Telegram user ID (optional, for backward compat)')
    parser.add_argument('--steam-id', help='Steam ID')
    parser.add_argument('--name', help='Display name (optional)')
    parser.add_argument('--json', action='store_true', help='JSON output')
    
    args = parser.parse_args()
    
    # Backward compatibility: if --telegram-id provided but no --username, use telegram-id as username
    if args.telegram_id and not args.username:
        args.username = args.telegram_id
    
    if args.action == 'save':
        if not args.username or not args.steam_id:
            print("Error: --username and --steam-id required for save", file=sys.stderr)
            return 1
        
        save_steam_id(args.username, args.steam_id, args.name, args.telegram_id)
        
        if args.json:
            print(json.dumps({'success': True, 'username': args.username, 'steam_id': args.steam_id}))
        else:
            print(f"Saved: @{args.username} -> Steam {args.steam_id}")
    
    elif args.action == 'get':
        if not args.username:
            print("Error: --username required for get", file=sys.stderr)
            return 1
        
        user_data = get_user_data(args.username)
        
        if args.json:
            if user_data:
                print(json.dumps(user_data))
            else:
                print(json.dumps({'success': False, 'steam_id': None}))
        else:
            if user_data:
                print(user_data['steam_id'])
            else:
                print(f"No Steam ID found for @{args.username}", file=sys.stderr)
                return 1
    
    elif args.action == 'list':
        data = list_all()
        
        if args.json:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            if data:
                print("Saved mappings:")
                for username, user in data.items():
                    name = user.get('name', username)
                    print(f"  @{username} ({name}) -> Steam {user['steam_id']}")
            else:
                print("No mappings saved")
    
    elif args.action == 'delete':
        if not args.username:
            print("Error: --username required for delete", file=sys.stderr)
            return 1
        
        success = delete_steam_id(args.username)
        
        if args.json:
            print(json.dumps({'success': success}))
        else:
            if success:
                print(f"Deleted mapping for @{args.username}")
            else:
                print(f"No mapping found for @{args.username}", file=sys.stderr)
                return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
