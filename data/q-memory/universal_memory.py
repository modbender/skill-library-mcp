#!/usr/bin/env python3
"""
Universal Agent Memory System v1.6.1
通用記憶系統 - 支持多主題 Agents + 加密

Usage:
    python universal_memory.py --agent qst save "記憶內容"
    python universal_memory.py --agent qst save "敏感數據" --encrypt
    python universal_memory.py --agent mengtian search "防火牆"
"""

import argparse
import yaml
import re
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import sys

SKILL_DIR = Path(__file__).parent
CONFIG_FILE = SKILL_DIR / "config_universal.yaml"
DATA_DIR = SKILL_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# 導入加密模組
sys.path.insert(0, str(SKILL_DIR / "scripts"))
try:
    from crypto import MemoryCrypto
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️ crypto.py 未找到，加密功能不可用")

def load_config() -> Dict[str, Any]:
    """載入通用配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}

def get_agent_tree(agent_name: str, config: Dict) -> Dict:
    """獲取特定 agent 的分類樹"""
    agents = config.get('agents', {})
    agent = agents.get(agent_name, {})
    return agent.get('tree', {})

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

def auto_classify(content: str, tree: Dict) -> str:
    """自動分類到樹狀結構"""
    content_lower = content.lower()
    path = []
    current_level = tree
    
    while current_level:
        best_match = None
        best_score = 0
        
        for node_name, node_data in current_level.items():
            score = 0
            keywords = node_data.get('keywords', [])
            
            for kw in keywords:
                if kw.lower() in content_lower:
                    score += 1
            
            if node_name.lower() in content_lower:
                score += 1
            
            if score > best_score:
                best_score = score
                best_match = node_name
        
        if best_match and best_score > 0:
            path.append(best_match)
            # 正確獲取子節點
            current_level = current_level[best_match].get('children', {})
        else:
            break
    
    return '.'.join(path) if path else 'General'

def save_memory(agent_name: str, content: str, 
                category: Optional[str] = None,
                source: Optional[str] = None,
                encrypt: bool = False) -> str:
    """保存記憶（可選加密）"""
    config = load_config()
    tree = get_agent_tree(agent_name, config)
    
    # Auto-classify
    if not category:
        category = auto_classify(content, tree)
    
    # 加密選項
    if encrypt and CRYPTO_AVAILABLE:
        crypto = MemoryCrypto()
        content = crypto.encrypt(content)
        if not source:
            source = "encrypted"
        else:
            source = f"{source} (encrypted)"
    
    # Generate ID
    content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
    timestamp = datetime.now().isoformat()
    
    # Build entry
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
    
    # Append
    memory_file = get_memory_file(agent_name)
    with open(memory_file, 'a', encoding='utf-8') as f:
        f.write(entry + '\n')
    
    return content_hash

def tree_search(agent_name: str, query: str) -> dict:
    """樹狀搜索 - 結合路徑分類 + 內容匹配"""
    config = load_config()
    tree = get_agent_tree(agent_name, config)
    memories = load_memories(agent_name)
    
    # Find path based on tree keywords
    content_lower = query.lower()
    path = []
    current_level = tree
    
    while current_level:
        best_match = None
        best_score = 0
        
        for node_name, node_data in current_level.items():
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
            current_level = current_level[best_match].get('children', {})
        else:
            break
    
    # Filter memories by BOTH path AND content
    path_str = '.'.join(path)
    results = []
    query_words = set(query.lower().split())
    
    for mem in memories:
        mem_lower = mem.lower()
        
        # 條件1：路徑匹配 OR 內容匹配
        path_match = path_str and (path_str in mem or any(p.lower() in mem_lower for p in path))
        
        # 條件2：內容匹配（至少一個查詢詞）
        content_match = any(word in mem_lower for word in query_words)
        
        # 必須滿足內容匹配
        if content_match:
            results.append(mem)
    
    return {
        'path': path,
        'count': len(results),
        'results': results[:10]
    }

def semantic_search(agent_name: str, query: str) -> dict:
    """語義搜索"""
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
        'count': len(results),
        'results': results
    }

def print_tree_structure(agent_name: str):
    """顯示樹狀結構"""
    config = load_config()
    tree = get_agent_tree(agent_name, config)
    
    print(f"\n📁 Agent: {agent_name} 記憶樹結構")
    print()
    
    def print_tree_node(node, prefix="", level=1):
        items = list(node.items())
        for i, (name, data) in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└" if is_last else "├"
            
            desc = data.get('description', '')
            print(f"{prefix}{connector} 📂 L{level} {name} - {desc[:30]}...")
            
            children = data.get('children', {})
            if children:
                new_prefix = prefix + ("  " if is_last else "│ ")
                print_tree_node(children, new_prefix, level + 1)
    
    print_tree_node(tree)
    
    memories = load_memories(agent_name)
    print(f"\n💾 記憶文件: {get_memory_file(agent_name)}")
    print(f"📊 記憶數量: {len(memories)} 條")

def show_stats(agent_name: str):
    """顯示統計"""
    memories = load_memories(agent_name)
    print(f"\n📊 Agent: {agent_name} 統計")
    print(f"   總記憶數: {len(memories)}")
    
    categories = {}
    for mem in memories:
        match = re.search(r'- Category: ([^\n]+)', mem)
        if match:
            cat = match.group(1)
            categories[cat] = categories.get(cat, 0) + 1
    
    if categories:
        print(f"\n📁 分類分佈:")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"   {cat}: {count}")

def main():
    parser = argparse.ArgumentParser(description="Universal Agent Memory v1.6")
    parser.add_argument('--agent', '-a', required=True,
                       help='Agent: qst, mengtian, lisi, or custom')
    
    subparsers = parser.add_subparsers(dest='command')
    
    # Save
    save_p = subparsers.add_parser('save', help='Save memory')
    save_p.add_argument('content')
    save_p.add_argument('--category', '-c')
    save_p.add_argument('--source', '-s')
    save_p.add_argument('--encrypt', '-e', action='store_true', 
                       help='Encrypt sensitive content')
    
    # Search
    search_p = subparsers.add_parser('search', help='Search memories')
    search_p.add_argument('query')
    search_p.add_argument('--method', '-m', choices=['tree', 'semantic'], 
                         default='tree')
    
    # Tree
    subparsers.add_parser('tree', help='Show tree structure')
    
    # Stats
    subparsers.add_parser('stats', help='Show statistics')
    
    # Decrypt
    decrypt_p = subparsers.add_parser('decrypt', help='Decrypt encrypted memory')
    decrypt_p.add_argument('memory_id', help='Memory ID to decrypt')
    
    # Doing - State management
    doing_p = subparsers.add_parser('doing', help='Task state management (start/update/pause/resume/complete)')
    doing_p.add_argument('action', choices=['start', 'update', 'pause', 'resume', 'complete', 'status', 'events'],
                        help='State action')
    doing_p.add_argument('--task', '-t', help='Task description (for start)')
    doing_p.add_argument('--type', choices=['Development', 'Analysis', 'Patrol', 'Debug', 'Research'],
                        default='Development', help='Task type')
    doing_p.add_argument('--template', choices=['Development', 'Research', 'Analytics', 'Support', 'Custom'],
                        help='Task template (v1.8.4)')
    doing_p.add_argument('--progress', '-p', type=int, help='Progress percentage (0-100)')
    doing_p.add_argument('--context', '-c', help='Context info as JSON string')
    doing_p.add_argument('--reason', '-r', help='Reason for pause/fail')
    doing_p.add_argument('--result', help='Result for complete')
    
    args = parser.parse_args()
    
    if args.command == 'save':
        result = save_memory(
            agent_name=args.agent,
            content=args.content,
            category=args.category,
            source=args.source,
            encrypt=args.encrypt
        )
        print(f"✅ 已保存到 {args.agent} 記憶庫")
        print(f"   ID: {result}")
    
    elif args.command == 'search':
        if args.method == 'tree':
            result = tree_search(args.agent, args.query)
            print(f"\n📁 路徑: {' → '.join(result['path'])}")
            print(f"📊 找到 {result['count']} 條記憶\n")
            for i, mem in enumerate(result['results'][:3], 1):
                print(f"--- 記憶 {i} ---")
                print(mem[:200] + "..." if len(mem) > 200 else mem)
                print()
        else:
            result = semantic_search(args.agent, args.query)
            print(f"\n🔍 語義搜索")
            print(f"📊 找到 {result['count']} 條記憶\n")
    
    elif args.command == 'tree':
        print_tree_structure(args.agent)
    
    elif args.command == 'stats':
        show_stats(args.agent)
    
    elif args.command == 'doing':
        from scripts.agent_state import AgentState
        state_mgr = AgentState(args.agent)
        
        if args.action == 'start':
            if not args.task:
                print("❌ 请提供任务描述: --task '任务名称'")
            else:
                ctx = json.loads(args.context) if args.context else {}
                template_name = getattr(args, 'template', None)
                state = state_mgr.start(args.task, args.type, context=ctx, template=template_name)
                print(f"✅ 任务开始: {state['task']}")
                print(f"   状态: {state['status']} | 进度: {state['progress']}%")
                if template_name:
                    print(f"   模板: {template_name}")
        
        elif args.action == 'update':
            ctx = json.loads(args.context) if args.context else {}
            state = state_mgr.update(args.progress, ctx)
            print(f"✅ 进度更新: {state['task']} ({state['progress']}%)")
        
        elif args.action == 'pause':
            state = state_mgr.pause(args.reason)
            print(f"⏸️ 任务暂停: {state['task']}")
            if args.reason:
                print(f"   原因: {args.reason}")
        
        elif args.action == 'resume':
            state = state_mgr.resume()
            print(f"▶️ 任务恢复: {state['task']}")
        
        elif args.action == 'complete':
            state = state_mgr.complete(args.result)
            print(f"✅ 任务完成: {state['task']}")
            if args.result:
                print(f"   结果: {args.result}")
        
        elif args.action == 'status':
            state = state_mgr.get_status()
            print(f"\n📊 Agent: {args.agent} 当前状态")
            print(f"   状态: {state['status'].upper()}")
            if state['task']:
                print(f"   任务: {state['task']}")
                print(f"   类型: {state['type']}")
                print(f"   进度: {state['progress']}%")
                if state.get('context'):
                    print(f"   上下文: {state['context']}")
            print()
        
        elif args.action == 'events':
            events = state_mgr.get_events(10)
            print(f"\n📜 最近事件 ({len(events)} 条)")
            for e in events[-5:]:
                print(f"   [{e['timestamp'][11:19]}] {e['event_type']}: {e['description'][:40]}...")
            print()
    
    elif args.command == 'decrypt':
        if not CRYPTO_AVAILABLE:
            print("❌ 加密模組不可用")
            return
        
        memories = load_memories(args.agent)
        crypto = MemoryCrypto()
        
        for mem in memories:
            if args.memory_id in mem:
                # 找到記憶，解密內容
                lines = mem.split('\n')
                for line in lines:
                    if line.startswith("ENC::"):
                        decrypted = crypto.decrypt(line)
                        print(f"\n🔓 解密記憶 {args.memory_id}:")
                        print(decrypted)
                        break
                break
        else:
            print(f"❌ 找不到記憶 ID: {args.memory_id}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
