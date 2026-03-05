#!/usr/bin/env python3
"""
Moltbook submolts management tool
Usage: python submolts.py [--list] [--search KEYWORD] [--info NAME]
                        [--subscribe NAME] [--unsubscribe NAME]
"""

import argparse
import json

WORKSPACE = r'C:\Users\10405\.openclaw\workspace'
CONFIG_FILE = WORKSPACE + r'\configs\moltbook.json'

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def get_headers(api_key):
    return {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

def list_submolts(headers):
    """List all submolts"""
    import requests
    
    r = requests.get(
        'https://www.moltbook.com/api/v1/submolts',
        headers=headers
    )
    
    if r.status_code != 200:
        return {'success': False, 'error': f'Failed to list submolts: {r.status_code}'}
    
    submolts = r.json().get('submolts', [])
    
    result = {
        'success': True,
        'count': len(submolts),
        'submolts': []
    }
    
    for sm in submolts:
        result['submolts'].append({
            'id': sm.get('id', '')[:8],
            'name': sm.get('name', ''),
            'display_name': sm.get('display_name', ''),
            'description': sm.get('description', '')[:100],
            'subscribers': sm.get('subscriber_count', 0)
        })
    
    return result

def search_submolts(keyword, headers):
    """Search submolts"""
    import requests
    
    r = requests.get(
        f'https://www.moltbook.com/api/v1/submolts?search={keyword}',
        headers=headers
    )
    
    if r.status_code != 200:
        return {'success': False, 'error': f'Search failed: {r.status_code}'}
    
    submolts = r.json().get('submolts', [])
    
    result = {
        'success': True,
        'keyword': keyword,
        'count': len(submolts),
        'submolts': []
    }
    
    for sm in submolts:
        result['submolts'].append({
            'id': sm.get('id', '')[:8],
            'name': sm.get('name', ''),
            'display_name': sm.get('display_name', ''),
            'description': sm.get('description', '')[:100]
        })
    
    return result

def get_submolt_info(name, headers):
    """Get submolt info"""
    import requests
    
    r = requests.get(
        f'https://www.moltbook.com/api/v1/submolts/{name}',
        headers=headers
    )
    
    if r.status_code != 200:
        return {'success': False, 'error': f'Submolt not found: {name}'}
    
    sm = r.json().get('submolt', {})
    
    result = {
        'success': True,
        'submolt': {
            'id': sm.get('id', '')[:8],
            'name': sm.get('name', ''),
            'display_name': sm.get('display_name', ''),
            'description': sm.get('description', ''),
            'subscribers': sm.get('subscriber_count', 0),
            'created_at': sm.get('created_at', ''),
            'url': f"https://moltbook.com/m/{sm.get('name', '')}"
        }
    }
    
    return result

def subscribe_submolt(name, headers):
    """Subscribe to submolt"""
    import requests
    
    r = requests.post(
        f'https://www.moltbook.com/api/v1/submolts/{name}/subscribe',
        headers=headers
    )
    
    if r.status_code == 200:
        print(f"[OK] Subscribed to m/{name}")
        return {'success': True, 'action': 'subscribed', 'name': name}
    
    elif r.status_code == 400:
        print(f"[WARN] Already subscribed to m/{name}")
        return {'success': False, 'error': 'Already subscribed'}
    
    else:
        error = r.json().get('error', 'Unknown error')
        print(f"[ERROR] Failed: {error}")
        return {'success': False, 'error': error}

def unsubscribe_submolt(name, headers):
    """Unsubscribe from submolt"""
    import requests
    
    r = requests.post(
        f'https://www.moltbook.com/api/v1/submolts/{name}/unsubscribe',
        headers=headers
    )
    
    if r.status_code == 200:
        print(f"[OK] Unsubscribed from m/{name}")
        return {'success': True, 'action': 'unsubscribed', 'name': name}
    
    else:
        error = r.json().get('error', 'Unknown error')
        print(f"[ERROR] Failed: {error}")
        return {'success': False, 'error': error}

def print_submolts(result):
    """Print submolts list"""
    print(f"\n=== Submolts ({result.get('count', 0)}) ===\n")
    
    for sm in result.get('submolts', []):
        print(f"[m/{sm['name']}] {sm['display_name']}")
        if sm.get('description'):
            print(f"   {sm['description']}")
        print(f"   Subscribers: {sm.get('subscribers', 0)}\n")

def main():
    parser = argparse.ArgumentParser(description='Moltbook Submolts Management')
    parser.add_argument('--list', action='store_true', help='List all submolts')
    parser.add_argument('--search', metavar='KEYWORD', help='Search submolts')
    parser.add_argument('--info', metavar='NAME', help='Get submolt info')
    parser.add_argument('--subscribe', metavar='NAME', help='Subscribe to submolt')
    parser.add_argument('--unsubscribe', metavar='NAME', help='Unsubscribe from submolt')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    
    args = parser.parse_args()
    
    config = load_config()
    headers = get_headers(config['api_key'])
    
    if args.list:
        result = list_submolts(headers)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_submolts(result)
    
    elif args.search:
        result = search_submolts(args.search, headers)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n=== Search: \"{args.search}\" ({result.get('count', 0)}) ===\n")
            for sm in result.get('submolts', []):
                print(f"[m/{sm['name']}] {sm['display_name']}")
                if sm.get('description'):
                    print(f"   {sm['description']}\n")
    
    elif args.info:
        result = get_submolt_info(args.info, headers)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result['success']:
                sm = result.get('submolt', {})
                print(f"\n=== m/{sm.get('name', '')} ===")
                print(f"Name: {sm.get('display_name', '')}")
                print(f"Description: {sm.get('description', '')}")
                print(f"Subscribers: {sm.get('subscribers', 0)}")
                print(f"URL: {sm.get('url', '')}")
            else:
                print(f"[ERROR] {result.get('error')}")
    
    elif args.subscribe:
        result = subscribe_submolt(args.subscribe, headers)
        return 0 if result['success'] else 1
    
    elif args.unsubscribe:
        result = unsubscribe_submolt(args.unsubscribe, headers)
        return 0 if result['success'] else 1
    
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python submolts.py --list")
        print("  python submolts.py --search memory")
        print("  python submolts.py --info general")
        print("  python submolts.py --subscribe memory")

if __name__ == '__main__':
    exit(main())
