#!/usr/bin/env python3
"""
Semantic Search v1.4 - 語義關聯搜索
根據關聯度擴展，搜索相關分類

例如: "暗物質" → FSCA → 也搜 QST_Computation, QST_Audit

Usage:
    python semantic_search.py "暗物質計算"
    python semantic_search.py --expand
"""

import json
import re
import yaml
from pathlib import Path
from typing import Optional, Set

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


def get_related_categories(primary: str, config: dict) -> Set[str]:
    """
    獲取相關分類
    
    從配置中讀取 related 欄位
    """
    related = set()
    tree = config.get("tree", {})
    
    # 遞歸搜索節點
    def find_node(data: dict, target: str):
        for name, node in data.items():
            if name == target or target in name.lower():
                node_related = node.get("related", [])
                related.update(node_related)
            
            children = node.get("children", {})
            if children:
                find_node(children, target)
    
    find_node(tree, primary)
    
    # 添加反向關聯
    related.add(primary)
    
    return related


def expand_by_keywords(query: str, config: dict) -> Set[str]:
    """
    根據關鍵詞擴展分類
    
    例如: "計算" + "暗物質" → QST_Computation + QST_Physics
    """
    categories = set()
    tree = config.get("tree", {})
    query_lower = query.lower()
    
    # 遞歸掃描所有節點
    def scan_nodes(data: dict):
        for name, node in data.items():
            keywords = node.get("keywords", [])
            for kw in keywords:
                if kw.lower() in query_lower:
                    categories.add(name)
                    # 添加相關分類
                    categories.update(node.get("related", []))
                    break
            
            children = node.get("children", {})
            if children:
                scan_nodes(children)
    
    scan_nodes(tree)
    
    return categories


def semantic_search(query: str, expand: bool = True) -> dict:
    """
    語義搜索主函數
    
    Args:
        query: 搜索查詢
        expand: 是否擴展相關分類
    
    Returns:
        {
            "primary": "FSCA",
            "related": ["QST_Computation", "QST_Audit"],
            "keywords": [...],
            "results": [...],
            "count": 5
        }
    """
    config = load_config()
    memories = load_memory()
    tree = config.get("tree", {})
    
    # 識別主要分類
    categories = expand_by_keywords(query, config)
    
    if not categories:
        categories = {"General"}
    
    primary = list(categories)[0] if categories else None
    
    # 擴展相關分類
    if expand and primary:
        related = get_related_categories(primary, config)
        categories.update(related)
    else:
        related = set()
    
    # 收集所有關鍵詞
    keywords = collect_keywords(categories, config)
    
    # 搜索記憶
    results = search_by_keywords(memories, keywords, categories)
    
    return {
        "primary": primary,
        "related": list(related - {primary}) if primary else [],
        "keywords": list(keywords)[:10],
        "results": results,
        "count": len(results)
    }


def collect_keywords(categories: Set[str], config: dict) -> Set[str]:
    """收集所有相關關鍵詞"""
    keywords = set()
    tree = config.get("tree", {})
    
    def find_keywords(data: dict):
        for name, node in data.items():
            if name in categories:
                keywords.update(node.get("keywords", []))
            
            children = node.get("children", {})
            if children:
                find_keywords(children)
    
    find_keywords(tree)
    
    return keywords


def search_by_keywords(memories: list, keywords: Set[str], categories: Set[str]) -> list:
    """根據關鍵詞搜索記憶"""
    results = []
    
    for memory in memories:
        # 檢查標籤
        has_tag = any(f"[{cat}]" in memory for cat in categories)
        
        # 檢查關鍵詞
        has_keyword = any(kw.lower() in memory.lower() for kw in keywords)
        
        if has_tag or has_keyword:
            results.append(memory)
    
    return results[:10]


# 語義等價映射
SEMANTIC_EQUIVALENCES = {
    "那個動漫": ["Dragon Ball", "龍珠"],
    "他": ["用戶", "秦王", "陛下"],
    "她": ["用戶"],
    "你": ["丞相", "李斯"],
    "之前說過": ["MEMORY.md", "記憶"],
    "喜歡什麼": ["偏好", "preference"],
    "QST暗物質": ["FSCA", "暗物質", "dark matter", "torsion"],
    "邊防": ["Border", "Security", "VPN", "firewall"],
}


def expand_semantic_query(query: str) -> str:
    """
    擴展語義等價詞
    
    例如: "那個動漫" → "那個動漫 Dragon Ball 龍珠"
    """
    expanded = query
    
    for phrase, equivalents in SEMANTIC_EQUIVALENCES.items():
        if phrase in query:
            expanded += " " + " ".join(equivalents)
    
    return expanded


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Semantic Search for QST Memory")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--expand", action="store_true", help="Expand related categories")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # 擴展語義
    expanded_query = expand_semantic_query(args.query)
    
    result = semantic_search(expanded_query, args.expand)
    
    print(f"\n🎯 Primary: {result['primary']}")
    print(f"🔗 Related: {', '.join(result['related'][:5])}")
    print(f"🔑 Keywords: {', '.join(result['keywords'][:5])}")
    print(f"📊 Found: {result['count']} memories\n")
    
    if args.verbose:
        for i, r in enumerate(result['results'][:5], 1):
            print(f"--- Memory {i} ---")
            print(r[:200] + "..." if len(r) > 200 else r)
            print()
