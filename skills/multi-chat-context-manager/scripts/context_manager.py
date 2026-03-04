#!/usr/bin/env python3
"""
Multi-Chat Context Manager
Store, retrieve, and clear conversation contexts per channel/user.
"""

import json
import os
import sys
import argparse
from pathlib import Path

DEFAULT_STORAGE_PATH = str(Path(__file__).parent.parent / 'data' / 'contexts.json')

def load_contexts():
    """Load contexts from JSON file."""
    try:
        with open(DEFAULT_STORAGE_PATH, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_contexts(contexts):
    """Save contexts to JSON file."""
    os.makedirs(os.path.dirname(DEFAULT_STORAGE_PATH), exist_ok=True)
    with open(DEFAULT_STORAGE_PATH, 'w') as f:
        json.dump(contexts, f, indent=2)

def get_context_key(channel_id, user_id=None, thread_id=None):
    """Generate a unique key for a context."""
    key = f"channel:{channel_id}"
    if user_id:
        key += f":user:{user_id}"
    if thread_id:
        key += f":thread:{thread_id}"
    return key

def store_context(channel_id, user_id=None, thread_id=None, message=None, response=None, max_history=10):
    """Store a message/response pair in context."""
    contexts = load_contexts()
    key = get_context_key(channel_id, user_id, thread_id)
    
    if key not in contexts:
        contexts[key] = {
            'channel_id': channel_id,
            'user_id': user_id,
            'thread_id': thread_id,
            'history': []
        }
    
    entry = contexts[key]
    if message is not None and response is not None:
        entry['history'].append({
            'message': message,
            'response': response,
            'timestamp': os.path.getmtime(__file__)  # placeholder, could use datetime
        })
        # Keep only last N entries
        if len(entry['history']) > max_history:
            entry['history'] = entry['history'][-max_history:]
    
    save_contexts(contexts)
    return entry

def retrieve_context(channel_id, user_id=None, thread_id=None):
    """Retrieve context for a channel/user/thread."""
    contexts = load_contexts()
    key = get_context_key(channel_id, user_id, thread_id)
    return contexts.get(key, {})

def clear_context(channel_id=None, user_id=None, thread_id=None):
    """Clear context(s). If no IDs provided, clear all."""
    contexts = load_contexts()
    if channel_id is None:
        contexts.clear()
    else:
        key = get_context_key(channel_id, user_id, thread_id)
        if key in contexts:
            del contexts[key]
        # Also clear any sub-contexts? For simplicity, just exact match.
    save_contexts(contexts)
    return {'cleared': True}

def list_contexts():
    """List all stored contexts."""
    contexts = load_contexts()
    return contexts

def main():
    parser = argparse.ArgumentParser(description='Multi-Chat Context Manager')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # store
    store_parser = subparsers.add_parser('store', help='Store a message/response pair')
    store_parser.add_argument('--channel', required=True, help='Channel ID')
    store_parser.add_argument('--user', help='User ID')
    store_parser.add_argument('--thread', help='Thread ID')
    store_parser.add_argument('--message', required=True, help='User message')
    store_parser.add_argument('--response', required=True, help='Agent response')
    store_parser.add_argument('--max-history', type=int, default=10, help='Maximum history entries to keep')
    
    # retrieve
    retrieve_parser = subparsers.add_parser('retrieve', help='Retrieve context')
    retrieve_parser.add_argument('--channel', required=True, help='Channel ID')
    retrieve_parser.add_argument('--user', help='User ID')
    retrieve_parser.add_argument('--thread', help='Thread ID')
    
    # clear
    clear_parser = subparsers.add_parser('clear', help='Clear context(s)')
    clear_parser.add_argument('--channel', help='Channel ID')
    clear_parser.add_argument('--user', help='User ID')
    clear_parser.add_argument('--thread', help='Thread ID')
    
    # list
    subparsers.add_parser('list', help='List all contexts')
    
    args = parser.parse_args()
    
    if args.command == 'store':
        result = store_context(
            channel_id=args.channel,
            user_id=args.user,
            thread_id=args.thread,
            message=args.message,
            response=args.response,
            max_history=args.max_history
        )
        print(json.dumps(result, indent=2))
    
    elif args.command == 'retrieve':
        result = retrieve_context(
            channel_id=args.channel,
            user_id=args.user,
            thread_id=args.thread
        )
        print(json.dumps(result, indent=2))
    
    elif args.command == 'clear':
        result = clear_context(
            channel_id=args.channel,
            user_id=args.user,
            thread_id=args.thread
        )
        print(json.dumps(result, indent=2))
    
    elif args.command == 'list':
        result = list_contexts()
        print(json.dumps(result, indent=2))
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
