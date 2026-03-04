#!/usr/bin/env python3
"""
Check Moltbook API rate limit status
"""

import json
import os
import time

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
CONFIG_FILE = os.path.join(WORKSPACE, "configs", "moltbook.json")
DRAFT_FILE = os.path.join(WORKSPACE, "configs", "moltbook-post.json")

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def check_rate_limit():
    """Check recent posts to estimate rate limit"""
    import requests
    
    config = load_config()
    api_key = config['api_key']
    headers = {'Authorization': f'Bearer {api_key}'}
    
    # Get my posts
    r = requests.get(
        'https://www.moltbook.com/api/v1/posts/me?limit=20',
        headers=headers
    )
    
    if r.status_code != 200:
        print(f"✗ Failed to fetch posts: {r.status_code}")
        return
    
    posts = r.json().get('posts', [])
    
    print("=== Rate Limit Status ===\n")
    print(f"Total posts found: {len(posts)}\n")
    
    # Analyze recent posts
    now = time.time()
    recent_posts = []
    
    for p in posts:
        created = p.get('created_at', '')
        if created:
            try:
                ts = time.mktime(time.strptime(created, '%Y-%m-%dT%H:%M:%S+00:00'))
                age = now - ts
                if age < 3600:  # Within 1 hour
                    recent_posts.append((p, age))
            except:
                pass
    
    print(f"Posts in last hour: {len(recent_posts)}")
    
    if recent_posts:
        print("\nRecent posts:")
        for p, age in sorted(recent_posts, key=lambda x: x[1]):
            mins = int(age / 60)
            title = p.get('title', 'Untitled')[:40]
            print(f"  - {mins}m ago: {title}")
    
    # Check draft file
    if os.path.exists(DRAFT_FILE):
        with open(DRAFT_FILE, 'r') as f:
            try:
                drafts = json.load(f)
                print(f"\nDrafts pending: {len(drafts)}")
                for d in drafts[-3:]:
                    print(f"  - {d.get('title', 'Untitled')[:30]}")
            except:
                pass
    
    print("\n=== Recommendations ===")
    if len(recent_posts) >= 5:
        print("⚠ High posting frequency detected")
        print("  Suggestion: Wait 2-3 minutes between posts")
    elif len(recent_posts) >= 3:
        print("⚡ Moderate posting frequency")
        print("  Suggestion: Wait 60 seconds between posts")
    else:
        print("✓ Low posting frequency - safe to post")

if __name__ == '__main__':
    check_rate_limit()
