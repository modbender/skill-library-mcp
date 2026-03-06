#!/usr/bin/env python3
"""Aura Memory Management Script for OpenClaw Integration.

Provides memory lifecycle commands for AI agents:
  - Write to memory tiers (/pad, /episodic, /fact)
  - List compiled memory shards  
  - Prune old/unwanted memories
  - Show storage usage

Security Manifest:
    Environment Variables: None
    External Endpoints: None
    Local Files Read: ~/.aura/memory/ (memory shards)
    Local Files Written: ~/.aura/memory/ (memory shards, WAL)

Usage:
    python memory.py write <namespace> <content>
    python memory.py list
    python memory.py prune --before 2026-01-01
    python memory.py usage
    python memory.py end-session
"""

import sys
import argparse
from aura.memory import AuraMemoryOS


def main():
    parser = argparse.ArgumentParser(
        description='Aura Memory Management for OpenClaw',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Namespaces:
    /pad       Working notes, scratch space
    /episodic  Session logs, conversation history
    /fact      Verified facts, persistent knowledge

Examples:
    python memory.py write pad "User prefers dark mode"
    python memory.py write fact "API key rotates monthly"
    python memory.py list
    python memory.py usage
    python memory.py prune --before 2026-01-01
    python memory.py end-session
"""
    )
    
    subparsers = parser.add_subparsers(dest='action', help='Memory actions')
    
    # Write
    write_parser = subparsers.add_parser('write', help='Write to a memory tier')
    write_parser.add_argument('namespace', choices=['pad', 'episodic', 'fact'],
                             help='Memory namespace')
    write_parser.add_argument('content', type=str, help='Content to remember')
    write_parser.add_argument('--source', type=str, default='agent',
                             help='Source of the memory (default: agent)')
    write_parser.add_argument('--tags', type=str, nargs='*', default=[],
                             help='Optional tags for classification')
    
    # List
    subparsers.add_parser('list', help='List all memory shards')
    
    # Prune
    prune_parser = subparsers.add_parser('prune', help='Prune memory shards')
    prune_parser.add_argument('--before', type=str, help='Delete shards before date (YYYY-MM-DD)')
    prune_parser.add_argument('--id', type=str, help='Delete specific shard by ID')
    
    # Usage
    subparsers.add_parser('usage', help='Show memory storage usage')
    
    # End session
    subparsers.add_parser('end-session', help='End current session and flush WALs')
    
    # Query
    query_parser = subparsers.add_parser('query', help='Search memory')
    query_parser.add_argument('query_text', type=str, help='Search query')
    query_parser.add_argument('--namespace', type=str, default=None,
                             help='Limit search to namespace')
    query_parser.add_argument('--top-k', type=int, default=5,
                             help='Number of results (default: 5)')
    
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        sys.exit(1)
    
    memory = AuraMemoryOS()
    
    if args.action == 'write':
        entry = memory.write(
            namespace=args.namespace,
            content=args.content,
            source=args.source,
            tags=args.tags
        )
        print(f"✅ Written to /{args.namespace}: {entry.entry_id}")
    
    elif args.action == 'list':
        memory.list_shards()
    
    elif args.action == 'prune':
        if args.before:
            memory.prune_shards(before_date=args.before)
        elif args.id:
            memory.prune_shards(shard_ids=[args.id])
        else:
            print("Specify --before DATE or --id SHARD_ID")
            sys.exit(1)
    
    elif args.action == 'usage':
        memory.show_usage()
    
    elif args.action == 'end-session':
        memory.end_session()
    
    elif args.action == 'query':
        results = memory.query(
            query_text=args.query_text,
            namespace=args.namespace,
            top_k=args.top_k
        )
        if results:
            print(f"🔍 Found {len(results)} result(s):\n")
            for i, r in enumerate(results, 1):
                print(f"  {i}. [{r['namespace']}] (score: {r['score']:.2f})")
                print(f"     {r['content'][:120]}...")
                print(f"     Source: {r['source']}  |  {r['timestamp']}")
                print()
        else:
            print("No results found.")


if __name__ == "__main__":
    main()
