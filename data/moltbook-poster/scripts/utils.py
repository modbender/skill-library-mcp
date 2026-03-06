"""Utility functions for Moltbook operations"""

import json
import os
import time

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
CONFIG_FILE = os.path.join(WORKSPACE, "configs", "moltbook.json")

def load_config():
    """Load Moltbook configuration"""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def get_api_key():
    """Get API key from config"""
    return load_config().get('api_key')

def get_headers():
    """Get API headers"""
    return {
        'Authorization': f'Bearer {get_api_key()}',
        'Content-Type': 'application/json'
    }

def format_wait_time(seconds):
    """Format seconds to human-readable wait time"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m"
    else:
        return f"{seconds // 3600}h {seconds % 3600 // 60}m"

def exponential_backoff(attempt, base=30, max_wait=300):
    """Calculate wait time with exponential backoff"""
    wait = min(base * (2 ** attempt), max_wait)
    # Add jitter
    import random
    wait += random.randint(0, 10)
    return wait

def save_post_history(post_info):
    """Save post to history for tracking"""
    history_file = os.path.join(WORKSPACE, "configs", "moltbook-post-history.json")
    
    history = []
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    
    history.append({
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        **post_info
    })
    
    # Keep only last 50
    history = history[-50:]
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)

def get_agent_info():
    """Get agent name and profile"""
    config = load_config()
    return {
        'name': config.get('agent_name'),
        'profile_url': config.get('profile_url'),
        'claim_url': config.get('claim_url')
    }
