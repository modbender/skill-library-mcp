#!/usr/bin/env python3
"""
Honcho Memory — On-demand query.
Ask Honcho anything about a peer's context mid-conversation.

Usage:
  python3 scripts/query.py "What is CoShip?"
  python3 scripts/query.py "What are J's priorities?" --peer j
  python3 scripts/query.py "Deep analysis of project status" --level high
"""

import argparse
import json
import os
import sys

def main():
    parser = argparse.ArgumentParser(description='Query Honcho Memory')
    parser.add_argument('question', help='Question to ask Honcho')
    parser.add_argument('--peer', default='j', help='Peer to query about (default: j)')
    parser.add_argument('--level', default='low', 
                        choices=['minimal', 'low', 'medium', 'high', 'max'],
                        help='Reasoning level (default: low)')
    parser.add_argument('--credentials', default=os.path.expanduser('~/.config/honcho/credentials.json'))
    
    args = parser.parse_args()
    
    with open(args.credentials) as f:
        creds = json.load(f)
    
    from honcho import Honcho
    honcho = Honcho(workspace_id=creds.get('workspace_id', 'default'), api_key=creds['api_key'])
    
    peer = honcho.peer(args.peer)
    answer = peer.chat(args.question, reasoning_level=args.level)
    
    if answer:
        print(answer)
    else:
        print(f"No context found for peer '{args.peer}' on this topic.")

if __name__ == '__main__':
    main()
