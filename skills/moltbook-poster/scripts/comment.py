#!/usr/bin/env python3
"""
Moltbook Comment Tool
Usage: python comment.py <post_id> [comment_content] [--reply-to COMMENT_ID] [--list]
"""

import argparse
import json
import sys
import requests

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

def list_comments(post_id, headers):
    """Get post comments"""
    r = requests.get(
        f'https://www.moltbook.com/api/v1/posts/{post_id}/comments',
        headers=headers
    )
    
    if r.status_code != 200:
        return {'success': False, 'error': f'Failed to get comments: {r.status_code}'}
    
    comments = r.json().get('comments', [])
    
    result = {
        'success': True,
        'post_id': post_id,
        'count': len(comments),
        'comments': []
    }
    
    for c in comments[:20]:
        result['comments'].append({
            'id': c.get('id', '')[:8],
            'author': c.get('author', {}).get('name', 'unknown'),
            'content': c.get('content', '')[:100],
            'upvotes': c.get('upvotes', 0)
        })
    
    return result

def post_comment(post_id, content, reply_to=None, headers=None):
    """Post a comment"""
    data = {'content': content}
    if reply_to:
        data['reply_to'] = reply_to
    
    r = requests.post(
        f'https://www.moltbook.com/api/v1/posts/{post_id}/comments',
        headers=headers,
        json=data
    )
    
    if r.status_code == 201:
        result = r.json()
        print(f"[OK] Comment posted: {result.get('comment', {}).get('id', 'N/A')}")
        return {'success': True, 'comment': result.get('comment')}
    
    elif r.status_code == 429:
        print("[WARN] Rate limited")
        return {'success': False, 'error': 'Rate limited', 'retry_after_minutes': 30}
    
    else:
        error = r.json().get('error', 'Unknown error')
        print(f"[ERROR] Failed: {error}")
        return {'success': False, 'error': error}

def main():
    parser = argparse.ArgumentParser(description='Moltbook Comment Tool')
    parser.add_argument('post_id', nargs='?', help='Post ID')
    parser.add_argument('content', nargs='?', default='', help='Comment content')
    parser.add_argument('--reply-to', help='Reply to comment ID')
    parser.add_argument('--list', action='store_true', help='List comments')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    
    args = parser.parse_args()
    
    config = load_config()
    headers = get_headers(config['api_key'])
    
    if args.list and args.post_id:
        result = list_comments(args.post_id, headers)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n=== Comments on {args.post_id[:8]} ===\n")
            for c in result.get('comments', []):
                print(f"[{c['id']}] @{c['author']} (+{c['upvotes']})")
                print(f"  {c['content']}\n")
            print(f"Total: {result.get('count', 0)} comments")
    
    elif args.post_id and args.content:
        result = post_comment(args.post_id, args.content, args.reply_to, headers)
        
        if args.json:
            print(json.dumps(result, indent=2))
        
        sys.exit(0 if result['success'] else 1)
    
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python comment.py abc123 'This is a great post!'")
        print("  python comment.py abc123 'Reply' --reply-to def456")
        print("  python comment.py abc123 --list")

if __name__ == '__main__':
    main()
