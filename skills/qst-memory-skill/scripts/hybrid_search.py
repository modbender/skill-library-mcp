#!/usr/bin/env python3
"""
Hybrid Search v1.5 - 混合搜索引擎
融合樹狀搜索 + Selection Rule + 語義搜索

原理：
1. 先用 Tree Search 精確定位分類
2. 再用 Selection Rule (幾何鄰近) 擴展
3. 最後用 Semantic Search 智能補充

Usage:
    python hybrid_search.py "暗物質計算"
    python hybrid_search.py "ARM芯片" --methods tree,semantic
"""

import sys
from pathlib import Path
from typing import Dict, List, Set, Optional

# 添加腳本目錄到路徑
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from tree_search import tree_search as ts
from bfs_search import bfs_search as bs
from semantic_search import semantic_search as ss
from semantic_search_v15 import semantic_search_enhanced


def load_config() -> dict:
    """載入配置"""
    import yaml
    config_file = Path(__file__).parent.parent / "config.yaml"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


# Selection Rule 幾何鄰近映射
# C_ab = 1 when geometric neighbors
SELECTION_RULES = {
    # QST 物理相關
    "QST_Physics": ["QST_Computation", "QST_Audit"],
    "QST_Computation": ["QST_Physics", "QST_Audit"],
    "QST_Audit": ["QST_Physics", "QST_Computation", "Tech_Config"],
    
    # FSCA 生態系統
    "QST_Physics_FSCA": ["QST_Computation", "QST_Audit", "QST_Physics_E8"],
    
    # 技術配置相關
    "Tech_Config": ["Tech_Discussion", "Tech_Skills"],
    "Tech_Config_API": ["Tech_Config_Cron", "Tech_Config_Model"],
    "Tech_Config_Cron": ["Tech_Config_API", "Tech_Config_Model"],
    "Tech_Config_Model": ["Tech_Config_API", "Tech_Discussion"],
    
    # 邊防相關
    "Border_Security": ["Border_Monitor", "Border_Email"],
    "Border_Monitor": ["Border_Security", "Tech_Config"],
    "Border_Email": ["Border_Security", "General_Chat"],
    
    # 用戶相關
    "User_Identity": ["User_Intent", "User_Projects"],
    "User_Intent": ["User_Identity", "General_Chat"],
    "User_Projects": ["User_Identity", "Tech_Discussion"],
    
    # HKGBook 相關
    "HK_Forum_Posts": ["HK_Forum_Replies", "HK_Forum_Users"],
    "HK_Forum_Replies": ["HK_Forum_Posts", "General_Chat"],
    
    # 一般話題
    "General_Chat": ["General_History", "General_Dragon_Ball"],
    "General_Dragon_Ball": ["General_Chat", "QST_Physics"],
    
    # General 兜底
    "General": []
}


def get_selection_neighbors(category: str) -> Set[str]:
    """
    根據 Selection Rule 獲取幾何鄰近分類
    
    原理：C_ab = 1 when geometric neighbors
    
    Returns:
        相關分類集合
    """
    neighbors = set()
    
    # 直接查找
    if category in SELECTION_RULES:
        neighbors.update(SELECTION_RULES[category])
    
    # 部分匹配
    for rule_cat, rule_neighbors in SELECTION_RULES.items():
        if category in rule_neighbors or category.lower() in rule_cat.lower():
            neighbors.update(rule_neighbors)
            neighbors.add(rule_cat)
    
    return neighbors


def tree_search_step(query: str) -> Dict:
    """第一步：Tree Search 精確定位"""
    return ts(query, None)


def selection_rule_step(primary_category: str, tree_result: Dict) -> Set[str]:
    """
    第二步：Selection Rule 幾何鄰近擴展
    
    原理：C_ab = 1 when geometric neighbors
    
    Args:
        primary_category: 主要分類
        tree_result: Tree Search 結果
    
    Returns:
        擴展後的分類集合
    """
    # 從 Tree Search 獲取分類
    categories = set()
    
    if tree_result.get('path'):
        if isinstance(tree_result['path'], list):
            categories.add(tree_result['path'][-1] if tree_result['path'] else 'General')
        else:
            categories.add(tree_result['path'])
    
    if tree_result.get('primary'):
        categories.add(tree_result['primary'])
    
    # 應用 Selection Rule 擴展
    expanded = set(categories)
    for cat in categories:
        neighbors = get_selection_neighbors(cat)
        expanded.update(neighbors)
    
    return expanded


def semantic_step(query: str, categories: Set[str], context: Optional[List[str]] = None) -> Dict:
    """
    第三步：Semantic Search 智能補充
    
    使用 v1.5 增強版語義搜索
    """
    return semantic_search_enhanced(
        query,
        context=context,
        expand=True,
        min_relevance=0.1
    )


def hybrid_search(
    query: str,
    methods: List[str] = ["tree", "selection", "semantic"],
    context: Optional[List[str]] = None
) -> Dict:
    """
    混合搜索主函數
    
    融合：
    1. Tree Search - 精確定位
    2. Selection Rule - 幾何鄰近擴展
    3. Semantic Search - 智能補充
    
    Args:
        query: 搜索查詢
        methods: 使用的搜索方法
        context: 上下文
    
    Returns:
        融合結果
    """
    result = {
        "query": query,
        "methods_used": [],
        "categories": set(),
        "primary_category": None,
        "results": [],
        "stats": {
            "tree_matches": 0,
            "selection_expansion": 0,
            "semantic_matches": 0,
            "total_results": 0
        }
    }
    
    # 方法1: Tree Search
    if "tree" in methods:
        tree_result = tree_search_step(query)
        result["methods_used"].append("tree")
        result["stats"]["tree_matches"] = tree_result.get("count", 0)
        
        if tree_result.get("path"):
            path = tree_result["path"]
            if isinstance(path, list):
                result["primary_category"] = path[-1] if path else "General"
            else:
                result["primary_category"] = path
        
        result["tree_result"] = tree_result
    
    # 方法2: Selection Rule
    if "selection" in methods and result["primary_category"]:
        selection_categories = selection_rule_step(
            result["primary_category"],
            tree_result if "tree" in methods else {}
        )
        result["methods_used"].append("selection")
        result["categories"] = selection_categories
        result["stats"]["selection_expansion"] = len(selection_categories)
        
        # 從 Tree 結果收集關鍵詞
        if "tree" in methods:
            keywords = tree_result.get("keywords", [])
            if keywords:
                result["keywords"] = keywords
    
    # 方法3: Semantic Search (v1.5 增強版)
    if "semantic" in methods:
        semantic_result = semantic_step(query, result["categories"], context)
        result["methods_used"].append("semantic")
        result["stats"]["semantic_matches"] = semantic_result.get("count", 0)
        
        # 融合結果
        tree_results = result.get("tree_result", {}).get("results", [])
        semantic_results = semantic_result.get("results", [])
        
        # 合併去重
        seen = set()
        merged = []
        
        for r in tree_results:
            if isinstance(r, dict):
                content = r.get("content", str(r))
            else:
                content = str(r)
            if content not in seen:
                seen.add(content)
                merged.append({"content": content, "source": "tree"})
        
        for r in semantic_results:
            content_preview = r["content"][:100]
            if content_preview not in seen:
                seen.add(content_preview)
                merged.append({**r, "source": "semantic"})
        
        # 按分數排序
        def get_score(item):
            if item["source"] == "tree":
                return 1.0
            return item.get("score", 0.5)
        
        merged.sort(key=get_score, reverse=True)
        result["results"] = merged[:10]
        result["stats"]["total_results"] = len(merged)
        
        result["semantic_result"] = semantic_result
    
    # 構建最終分類路徑
    if result["primary_category"]:
        result["path"] = build_path(result["primary_category"])
    
    return result


def build_path(category: str) -> List[str]:
    """構建分類路徑"""
    config = load_config()
    tree = config.get("tree", {})
    path = []
    
    def search(data: dict, current_path: List[str]):
        for name, node in data.items():
            if name == category or name.lower() == category.lower():
                path.extend(current_path + [name])
                return True
            
            children = node.get("children", {})
            if children and search(children, current_path + [name]):
                return True
        
        return False
    
    search(tree, [])
    return path if path else [category]


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Hybrid Search v1.5")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--methods", "-m", default="tree,semantic",
                       help="Methods to use (comma-separated: tree,selection,semantic)")
    parser.add_argument("--context", "-c", help="Context (comma-separated)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    methods = [m.strip() for m in args.methods.split(",")]
    context = args.context.split(",") if args.context else None
    
    result = hybrid_search(args.query, methods=methods, context=context)
    
    print(f"\n🔍 Hybrid Search Result")
    print(f"{'='*50}")
    print(f"Query: {result['query']}")
    print(f"Methods: {', '.join(result['methods_used'])}")
    
    if result.get('primary_category'):
        print(f"\n🎯 Primary: {result['primary_category']}")
        print(f"📁 Path: {' → '.join(result.get('path', []))}")
    
    if result.get('categories'):
        print(f"\n🔗 Selection Categories ({len(result['categories'])}):")
        print(f"  {', '.join(sorted(result['categories']))}")
    
    print(f"\n📊 Stats:")
    print(f"  Tree matches: {result['stats']['tree_matches']}")
    print(f"  Selection expansion: {result['stats']['selection_expansion']}")
    print(f"  Semantic matches: {result['stats']['semantic_matches']}")
    print(f"  Total results: {result['stats']['total_results']}")
    
    if args.verbose and result.get('results'):
        print(f"\n--- Results ---")
        for i, r in enumerate(result['results'][:5], 1):
            source = r.get('source', 'unknown')
            score = r.get('score', 'N/A')
            print(f"[{i}] ({source}) Score: {score}")
            content = r.get('content', '')[:150]
            print(f"    {content}...")
