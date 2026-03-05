#!/usr/bin/env python3
"""
BFS Search v1.4 - 廣度優先搜索
先搜同層，再搜下層，找到相關類別

Usage:
    python bfs_search.py "暗物質"
    python bfs_search.py --root "QST"
"""

import json
import re
import yaml
from pathlib import Path
from collections import deque
from typing import Optional

SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "config.yaml"
MEMORY_FILE = SKILL_DIR / "data" / "qst_memories.md"  # 獨立存儲


def load_config() -> dict:
    """載入配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {"tree": {}}


def load_memory() -> list:
    """載入記憶"""
    memories = []
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            entries = re.split(r'\n---+\n', content)
            for entry in entries:
                if entry.strip():
                    memories.append(entry.strip())
    return memories


def detect_root(query: str, config: dict) -> Optional[str]:
    """
    檢測查詢屬於哪個根節點
    
    例如: "暗物質" → "QST"
    """
    tree = config.get("tree", {})
    
    for root_name, root_data in tree.items():
        keywords = root_data.get("keywords", [])
        description = root_data.get("description", "").lower()
        
        query_lower = query.lower()
        
        for kw in keywords:
            if kw.lower() in query_lower:
                return root_name
        
        if description and description in query_lower:
            return root_name
    
    return None


def get_all_children(tree: dict, root: str) -> dict:
    """
    獲取根節點下的所有子節點
    
    返回 {路徑: 節點數據}
    """
    children = {}
    
    if root not in tree:
        return children
    
    root_data = tree[root]
    root_children = root_data.get("children", {})
    
    for child_name, child_data in root_children.items():
        path = f"{root}.{child_name}"
        children[path] = child_data
        
        # 孫節點
        grand_children = child_data.get("children", {})
        for grand_name, grand_data in grand_children.items():
            grand_path = f"{path}.{grand_name}"
            children[grand_path] = grand_data
    
    return children


def bfs_search(query: str, root: Optional[str] = None) -> dict:
    """
    廣度優先搜索
    
    Args:
        query: 搜索查詢
        root: 指定根節點 (可選)
    
    Returns:
        {
            "root": "QST",
            "matched_paths": ["QST.Physics", "QST.Physics.FSCA"],
            "keywords": [...],
            "results": [...],
            "count": 5
        }
    """
    config = load_config()
    memories = load_memory()
    tree = config.get("tree", {})
    
    # 檢測根節點
    if not root:
        root = detect_root(query, config)
    
    if not root:
        # 全局搜索
        return search_all_roots(query, config, memories)
    
    # 獲取所有子節點
    all_children = get_all_children(tree, root)
    
    # BFS 匹配
    matched_paths = []
    all_keywords = set()
    query_lower = query.lower()
    
    for path, node_data in all_children.items():
        keywords = node_data.get("keywords", [])
        for kw in keywords:
            if kw.lower() in query_lower:
                matched_paths.append(path)
                all_keywords.update(keywords)
                break
    
    # 如果沒有匹配，返回根節點下所有記憶
    if not matched_paths:
        matched_paths = [root]
    
    # 搜索記憶
    results = search_memories_by_paths(memories, matched_paths)
    
    return {
        "root": root,
        "matched_paths": matched_paths,
        "keywords": list(all_keywords),
        "results": results,
        "count": len(results)
    }


def search_all_roots(query: str, config: dict, memories: list) -> dict:
    """全局搜索所有根節點"""
    tree = config.get("tree", {})
    all_paths = []
    
    for root_name, root_data in tree.items():
        keywords = root_data.get("keywords", [])
        query_lower = query.lower()
        
        for kw in keywords:
            if kw.lower() in query_lower:
                all_paths.append(root_name)
                break
    
    results = search_memories_by_paths(memories, all_paths)
    
    return {
        "root": None,
        "matched_paths": all_paths,
        "results": results,
        "count": len(results)
    }


def search_memories_by_paths(memories: list, paths: list) -> list:
    """根據路徑列表搜索記憶"""
    results = []
    
    for memory in memories:
        for path in paths:
            path_parts = path.split(".")
            # 檢查標籤
            for part in path_parts:
                if f"[{part}]" in memory:
                    if memory not in results:
                        results.append(memory)
                    break
    
    return results[:10]


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="BFS Search for QST Memory")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--root", help="Specify root category")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    result = bfs_search(args.query, args.root)
    
    print(f"\n📁 Root: {result['root'] or 'All'}")
    print(f"🔗 Matched Paths: {', '.join(result['matched_paths'][:5])}")
    print(f"📊 Found: {result['count']} memories\n")
    
    if args.verbose:
        for i, r in enumerate(result['results'][:5], 1):
            print(f"--- Memory {i} ---")
            print(r[:200] + "..." if len(r) > 200 else r)
            print()
