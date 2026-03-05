#!/usr/bin/env python3
"""
Add Category v1.4 - Agent 新增分類
動態擴充分類，僅定立指引

Usage:
    python add_category.py --name "QST_Physics_Lattice" --parent "QST_Physics"
    python add_category.py --name "Tech_Config_Database" --keywords "database DB"
"""

import json
import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional

SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "config.yaml"
CATEGORY_LOG = SKILL_DIR / "category_history.json"


def load_config() -> dict:
    """載入配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {"tree": {}, "add_category": {}}


def save_config(config: dict):
    """保存配置"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)


def load_history() -> list:
    """載入分類歷史"""
    if CATEGORY_LOG.exists():
        with open(CATEGORY_LOG, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_history(history: list):
    """保存分類歷史"""
    with open(CATEGORY_LOG, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def validate_name(name: str, config: dict) -> tuple:
    """
    驗證分類名稱
    
    Returns:
        (valid: bool, message: str)
    """
    rules = config.get("add_category", {})
    pattern = rules.get("naming_pattern", "^[A-Z][a-zA-Z0-9_]*$")
    max_depth = rules.get("max_depth", 3)
    
    # 檢查命名規範
    if not re.match(pattern, name):
        return False, f"命名不符合規範: {pattern}"
    
    # 檢查層級深度
    parts = name.split("_")
    if len(parts) > max_depth:
        return False, f"層級超過限制: 最多 {max_depth} 層"
    
    # 檢查是否已存在
    tree = config.get("tree", {})
    if category_exists(name, tree):
        return False, "分類已存在"
    
    return True, "驗證通過"


def category_exists(name: str, tree: dict) -> bool:
    """檢查分類是否存在"""
    for node_name, node_data in tree.items():
        if node_name == name:
            return True
        children = node_data.get("children", {})
        if category_exists(name, children):
            return True
    return False


def find_parent_node(parent_path: str, tree: dict) -> Optional[dict]:
    """
    尋找父節點
    
    Args:
        parent_path: 例如 "QST_Physics" 或 "QST.Physics"
    
    Returns:
        父節點字典或 None
    """
    # 支援兩種分隔符
    parts = parent_path.replace(".", "_").split("_")
    
    current = tree
    for part in parts:
        if part in current:
            current = current[part]
        elif "children" in current and part in current["children"]:
            current = current["children"][part]
        else:
            return None
    
    return current


def add_category(
    name: str,
    parent: Optional[str] = None,
    description: str = "",
    keywords: list = None,
    auto_weight: str = "N",
    related: list = None
) -> dict:
    """
    新增分類
    
    Args:
        name: 分類名稱
        parent: 父分類路徑
        description: 描述
        keywords: 關鍵詞列表
        auto_weight: 自動權重 (C/I/N)
        related: 相關分類
    
    Returns:
        {
            "success": bool,
            "message": str,
            "category": dict
        }
    """
    config = load_config()
    
    # 驗證名稱
    valid, msg = validate_name(name, config)
    if not valid:
        return {"success": False, "message": msg, "category": None}
    
    # 準備新分類數據
    new_category = {
        "description": description,
        "keywords": keywords or [],
        "auto_weight": auto_weight,
        "related": related or [],
        "children": {}
    }
    
    # 添加到樹中
    tree = config.get("tree", {})
    
    if parent:
        # 尋找父節點
        parent_node = find_parent_node(parent, tree)
        if not parent_node:
            return {"success": False, "message": f"父分類不存在: {parent}", "category": None}
        
        if "children" not in parent_node:
            parent_node["children"] = {}
        
        parent_node["children"][name] = new_category
    else:
        # 添加為根節點
        tree[name] = new_category
    
    config["tree"] = tree
    save_config(config)
    
    # 記錄歷史
    history = load_history()
    history.append({
        "name": name,
        "parent": parent,
        "timestamp": datetime.now().isoformat(),
        "description": description
    })
    save_history(history)
    
    return {
        "success": True,
        "message": f"分類 {name} 已添加",
        "category": new_category
    }


def suggest_category(keywords: list, config: dict) -> dict:
    """
    根據關鍵詞建議分類
    
    Returns:
        {
            "suggested_name": str,
            "suggested_parent": str,
            "reasoning": str
        }
    """
    tree = config.get("tree", {})
    
    # 計算關鍵詞與現有分類的匹配度
    matches = {}
    
    def scan_for_matches(data: dict, path: str = ""):
        for name, node in data.items():
            node_keywords = node.get("keywords", [])
            common = set(keywords) & set(node_keywords)
            if common:
                full_path = f"{path}.{name}" if path else name
                matches[full_path] = len(common)
            
            children = node.get("children", {})
            if children:
                scan_for_matches(children, name)
    
    scan_for_matches(tree)
    
    if matches:
        best_match = max(matches, key=matches.get)
        parent = ".".join(best_match.split(".")[:-1]) if "." in best_match else best_match
        
        return {
            "suggested_name": None,
            "suggested_parent": best_match,
            "reasoning": f"關鍵詞與 {best_match} 匹配度最高 ({matches[best_match]} 個)"
        }
    
    return {
        "suggested_name": None,
        "suggested_parent": None,
        "reasoning": "未找到匹配分類，建議新增根分類"
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Add Category to QST Memory")
    parser.add_argument("--name", required=True, help="Category name")
    parser.add_argument("--parent", help="Parent category path")
    parser.add_argument("--description", default="", help="Category description")
    parser.add_argument("--keywords", default="", help="Comma-separated keywords")
    parser.add_argument("--weight", default="N", choices=["C", "I", "N"], help="Auto weight")
    parser.add_argument("--related", default="", help="Comma-separated related categories")
    
    args = parser.parse_args()
    
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    related = [r.strip() for r in args.related.split(",") if r.strip()]
    
    result = add_category(
        name=args.name,
        parent=args.parent,
        description=args.description,
        keywords=keywords,
        auto_weight=args.weight,
        related=related
    )
    
    if result["success"]:
        print(f"\n✅ {result['message']}\n")
        print(f"📁 分類: {args.name}")
        print(f"🔗 父節點: {args.parent or 'Root'}")
        print(f"🔑 關鍵詞: {', '.join(keywords)}")
        print(f"⚖️ 權重: {args.weight}")
    else:
        print(f"\n❌ {result['message']}\n")
