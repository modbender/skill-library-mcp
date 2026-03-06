#!/usr/bin/env python3
"""
Universal Agent Memory CLI v1.6
簡化版通用記憶系統命令行介面
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/qst-memory')

from agent_memory import (
    save_memory_content, 
    tree_search, 
    semantic_search,
    load_config,
    load_memories,
    get_agent_config,
    get_memory_file
)

def print_basic_tree(agent_name: str):
    """顯示 agent 的樹狀結構"""
    config = load_config()
    agent_config = get_agent_config(agent_name, config)
    tree = agent_config.get('tree', {})
    
    print(f"\n📁 Agent: {agent_name} 記憶樹結構")
    print()
    
    def print_tree(node, prefix="", level=1):
        for i, (name, data) in enumerate(node.items()):
            is_last = i == len(node) - 1
            connector = "└" if is_last else "├"
            
            print(f"{prefix}{connector} 📂 L{level} {name}")
            
            children = data.get('children', {})
            if children:
                new_prefix = prefix + ("  " if is_last else "│ ")
                print_tree(children, new_prefix, level + 1)
    
    print_tree(tree)
    
    # Show memory stats
    memories = load_memories(agent_name)
    print(f"\n💾 記憶文件: {get_memory_file(agent_name)}")
    print(f"📊 記憶數量: {len(memories)} 條")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal Agent Memory v1.6")
    parser.add_argument('--agent', '-a', required=True, 
                       help='Agent name: qst, mengtian, lisi, or custom')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # save command
    save_p = subparsers.add_parser('save', help='Save memory')
    save_p.add_argument('content', help='Content to save')
    save_p.add_argument('--category', '-c', help='Category (auto-detected if not specified)')
    save_p.add_argument('--source', '-s', help='Source reference')
    
    # search command
    search_p = subparsers.add_parser('search', help='Search memories')
    search_p.add_argument('query', help='Search query')
    search_p.add_argument('--method', '-m', choices=['tree', 'semantic'], 
                          default='tree', help='Search method')
    
    # tree command
    tree_p = subparsers.add_parser('tree', help='Show memory tree structure')
    
    # stats command
    stats_p = subparsers.add_parser('stats', help='Show statistics')
    
    args = parser.parse_args()
    
    if args.command == 'save':
        result = save_memory_content(
            agent_name=args.agent,
            content=args.content,
            category=args.category,
            source=args.source
        )
        print(f"✅ 已保存到 {args.agent} 記憶庫")
        print(f"   ID: {result}")
    
    elif args.command == 'search':
        if args.method == 'tree':
            config = load_config()
            result = tree_search(args.query, args.agent, config)
            print(f"\n📁 路徑: {' → '.join(result['path'])}")
            print(f"📊 找到 {result['count']} 條記憶\n")
            for i, mem in enumerate(result['results'][:5], 1):
                print(f"--- 記憶 {i} ---")
                print(mem[:200] + "..." if len(mem) > 200 else mem)
                print()
        else:  # semantic
            result = semantic_search(args.query, args.agent)
            print(f"\n🔍 {result['method']} 搜索")
            print(f"📊 找到 {result['count']} 條記憶\n")
    
    elif args.command == 'tree':
        print_basic_tree(args.agent)
    
    elif args.command == 'stats':
        from agent_memory import show_stats
        show_stats(args.agent)
    
    else:
        parser.print_help()
