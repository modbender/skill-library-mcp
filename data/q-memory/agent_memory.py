#!/usr/bin/env python3
"""
Universal Agent Memory System v1.6
通用記憶系統 - 支持多主題 Agents

Usage:
    python agent_memory.py --agent qst save "記憶內容"
    python agent_memory.py --agent mengtian save "防火牆規則更新"
    python agent_memory.py --agent lisi search "外交策略"

All agents share the same core but have independent:
- Storage files (data/{agent}_memories.md)
- Classification trees (defined in config_universal.yaml)
- Key patterns for indexing
"""

import argparse
import yaml
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# 路徑配置
SKILL_DIR = Path(__file__).parent
CONFIG_FILE = SKILL_DIR / "config_universal.yaml"
DATA_DIR = SKILL_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

def load_config() -> Dict[str, Any]:
    """載入通用配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}

def get_agent_config(agent_name: str, config: Dict) -> Dict:
    """獲取特定 agent 的配置"""
    agents = config.get('agents', {})
    return agents.get(agent_name, {})

def get_memory_file(agent_name: str) -> Path:
    """獲取 agent 的記憶文件路徑"""
    return DATA_DIR / f"{agent_name}_memories.md"

def load_memories(agent_name: str) -> List[str]:
    """載入指定 agent 的記憶"""
    memory_file = get_memory_file(agent_name)
    if memory_file.exists():
        content = memory_file.read_text(encoding='utf-8')
        entries = re.split(r'\n---+\n', content)
        return [e.strip() for e in entries if e.strip()]
    return []

def save_memory_content(agent_name: str, content: str, 
                       category: Optional[str] = None,
                       source: Optional[str] = None) -> str:
    """保存記憶到指定 agent 的存儲"""
    memory_file = get_memory_file(agent_name)
    
    # Auto-classify if no category provided
    if not category:
        category = auto_classify(content, agent_name)
    
    # Generate hash ID
    content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
    timestamp = datetime.now().isoformat()
    
    # Build memory entry
    lines = [
        f"# Agent: {agent_name} | ID: {content_hash}",
        f"- Timestamp: {timestamp}",
        f"- Category: {category}",
    ]
    if source:
        lines.append(f"- Source: {source}")
    lines.append("")
    lines.append(content)
    lines.append("")
    lines.append("---")
    
    entry = '\n'.join(lines)
    
    # Append to file
    with open(memory_file, 'a', encoding='utf-8') as f:
        f.write(entry + '\n')
    
    return content_hash

def auto_classify(content: str, agent_name: str) -> str:
    """自動分類到 agent 的樹狀結構"""
    config = load_config()
    agent_config = get_agent_config(agent_name, config)
    tree = agent_config.get('tree', {})
    
    content_lower = content.lower()
    
    # Traverse tree and find best match
    path = []
    current = tree
    
    while current:
        best_match = None
        best_score = 0
        
        for node_name, node_data in current.items():
            score = 0
            keywords = node_data.get('keywords', [])
            description = node_data.get('description', '').lower()
            
            # Check keywords
            for kw in keywords:
                if kw.lower() in content_lower:
                    score += 1
            
            # Check description match
            if description and description in content_lower:
                score += 2
            
            # Check node name
            if node_name.lower() in content_lower:
                score += 1
            
            if score > best_score:
                best_score = score
                best_match = node_name
        
        if best_match and best_score > 0:
            path.append(best_match)
            current = tree[best_match].get('children', {})
        else:
            break
    
    return '.'.join(path) if path else 'General'

def tree_search(query: str, agent_name: str, config: Dict) -> Dict[str, Any]:
    """樹狀搜索"""
    agent_config = get_agent_config(agent_name, config)
    tree = agent_config.get('tree', {})
    memories = load_memories(agent_name)
    
    # Find best path
    path = []
    current = tree
    content_lower = query.lower()
    
    while current:
        best_match = None
        best_score = 0
        
        for node_name, node_data in current.items():
            score = 0
            for kw in node_data.get('keywords', []):
                if kw.lower() in content_lower:
                    score += 1
            if node_name.lower() in content_lower:
                score += 1
            
            if score > best_score:
                best_score = score
                best_match = node_name
        
        if best_match and best_score > 0:
            path.append(best_match)
            current = tree[best_match].get('children', {})
        else:
            break
    
    # Filter memories by path
    path_str = '.'.join(path)
    results = []
    for mem in memories:
        if path_str in mem or any(p in mem for p in path):
            results.append(mem)
    
    return {
        'path': path,
        'count': len(results),
        'results': results[:10]
    }

def semantic_search(query: str, agent_name: str) -> Dict[str, Any]:
    """語義搜索（簡易版：關鍵詞匹配）"""
    memories = load_memories(agent_name)
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    scored = []
    for mem in memories:
        mem_lower = mem.lower()
        score = sum(1 for word in query_words if word in mem_lower)
        if score > 0:
            scored.append((score, mem))
    
    scored.sort(reverse=True, key=lambda x: x[0])
    results = [mem for _, mem in scored[:10]]
    
    return {
        'method': 'semantic',
        'count': len(results),
        'results': results
    }

def show_stats(agent_name: str) -> None:
    """顯示 agent 記憶統計"""
    memories = load_memories(agent_name)
    
    # Parse categories
    categories = {}
    sources = {}
    
    for mem in memories:
        # Extract category
        cat_match = re.search(r'- Category: (.+)', mem)
        if cat_match:
            cat = cat_match.group(1)
            categories[cat] = categories.get(cat, 0) + 1
        
        # Extract source
        src_match = re.search(r'- Source: (.+)', mem)
        if src_match:
            src = src_match.group(1)
            sources[src] = sources.get(src, 0) + 1
    
    print(f"\n📊 Agent: {agent_name}")
    print(f"   總記憶數: {len(memories)}")
    print(f"\n📁 分類分佈:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count}")
    
    if sources:
        print(f"\n📎 來源分佈:")
        for src, count in sorted(sources.items(), key=lambda x: -x[1])[:5]:
            print(f"   {src}: {count}")

def main():
    parser = argparse.ArgumentParser(
        description="Universal Agent Memory System v1.6"
    )
    parser.add_argument('--agent', '-a', required=True,
                       help='Agent name (e.g., qst, mengtian, lisi)')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Save command
    save_parser = subparsers.add_parser('save', help='Save memory')
    save_parser.add_argument('content', help='Memory content')
    save_parser.add_argument('--category', '-c', help='Category')
    save_parser.add_argument('--source', '-s', help='Source')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search memories')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--method', default='tree', choices=['tree', 'semantic'], help='Search method')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    args = parser.parse_args()
    
    if args.command == 'save':
        result = save_memory_content(
            agent_name=args.agent,
            content=args.content,
            category=args.category,
            source=args.source
        )
        print(f"Saved: {result}")
    
    elif args.command == 'search':
        config = load_config()
        if args.method == 'tree':
            result = tree_search(args.query, args.agent, config)
            print(f"Path: {' -> '.join(result['path'])}")
            print(f"Found: {result['count']}")
        else:
            result = semantic_search(args.query, args.agent)
            print(f"Found: {result['count']}")
    
    elif args.command == 'stats':
        show_stats(args.agent)
    
    else:
        parser.print_help()


if __name__ == "__main__":