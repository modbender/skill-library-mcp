#!/usr/bin/env python3
"""
Stats Panel v1.5 - 記憶統計面板
可視化記憶狀態

Usage:
    python stats_panel.py
    python stats_panel.py --json
"""

import json
import re
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "config.yaml"
MEMORY_DIR = SKILL_DIR.parent / "memory"
MEMORY_FILE = SKILL_DIR / "data" / "qst_memories.md"  # 獨立存儲


def load_config() -> dict:
    """載入配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def count_categories(config: dict) -> dict:
    """統計分類數量"""
    counts = {
        "roots": 0,
        "level1": 0,
        "level2": 0,
        "level3": 0,
        "total": 0
    }
    
    tree = config.get("tree", {})
    
    def scan(data: dict, depth: int = 0):
        nonlocal counts
        for name, node in data.items():
            counts["total"] += 1
            if depth == 0:
                counts["roots"] += 1
            elif depth == 1:
                counts["level1"] += 1
            elif depth == 2:
                counts["level2"] += 1
            else:
                counts["level3"] += 1
            
            children = node.get("children", {})
            if children:
                scan(children, depth + 1)
    
    scan(tree)
    
    return counts


def count_memories() -> dict:
    """統計記憶數量"""
    counts = {
        "critical": 0,
        "important": 0,
        "normal": 0,
        "total": 0
    }
    
    # 從獨立存儲讀取
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            
            counts["critical"] += content.count("[C]")
            counts["important"] += content.count("[I]")
            counts["normal"] += content.count("[N]")
    
    counts["total"] = counts["critical"] + counts["important"] + counts["normal"]
    
    return counts


def estimate_token_usage() -> dict:
    """估算 Token 使用"""
    counts = count_memories()
    
    # 估算每條記憶的平均 token 數
    avg_tokens = {
        "critical": 100,  # Critical 記憶較詳細
        "important": 50,
        "normal": 30
    }
    
    return {
        "critical": counts["critical"] * avg_tokens["critical"],
        "important": counts["important"] * avg_tokens["important"],
        "normal": counts["normal"] * avg_tokens["normal"],
        "total": counts["critical"] * avg_tokens["critical"] +
                 counts["important"] * avg_tokens["important"] +
                 counts["normal"] * avg_tokens["normal"]
    }


def get_recent_activity(days: int = 7) -> dict:
    """獲取最近活動"""
    activity = {
        "files": [],
        "memories": 0
    }
    
    cutoff = datetime.now() - timedelta(days=days)
    
    memory_files = list(MEMORY_DIR.glob("*.md"))
    
    for mf in sorted(memory_files, reverse=True):
        mtime = datetime.fromtimestamp(mf.stat().st_mtime)
        
        if mtime >= cutoff:
            activity["files"].append({
                "name": mf.name,
                "modified": mtime.strftime("%Y-%m-%d %H:%M")
            })
            
            with open(mf, 'r', encoding='utf-8') as f:
                content = f.read()
                activity["memories"] += content.count("## ")
    
    return activity


def get_category_distribution(config: dict) -> dict:
    """獲取分類分佈"""
    tree = config.get("tree", {})
    distribution = {}
    
    for root_name, root_data in tree.items():
        count = count_nodes(root_data)
        distribution[root_name] = count
    
    return distribution


def count_nodes(data: dict) -> int:
    """統計節點數量（包括子節點）"""
    count = 1  # 當前節點
    
    for child in data.get("children", {}).values():
        count += count_nodes(child)
    
    return count


def stats_panel(output: str = "text") -> dict:
    """
    統計面板主函數
    
    Returns:
        統計結果字典
    """
    config = load_config()
    
    stats = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.4",
        "categories": count_categories(config),
        "memories": count_memories(),
        "tokens": estimate_token_usage(),
        "recent_activity": get_recent_activity(),
        "distribution": get_category_distribution(config)
    }
    
    if output == "json":
        return stats
    
    # 格式化輸出
    output_lines = [
        "=" * 50,
        "📊 QST Memory v1.5 統計面板",
        "=" * 50,
        "",
        f"⏰ 統計時間: {stats['timestamp']}",
        "",
        "─" * 50,
        "🌳 分類結構",
        "─" * 50,
        f"  根分類 (L1): {stats['categories']['roots']}",
        f"  二級分類 (L2): {stats['categories']['level1']}",
        f"  三級分類 (L3): {stats['categories']['level2']}",
        f"  ─────────────────────",
        f"  總計: {stats['categories']['total']} 個分類",
        "",
        "─" * 50,
        "💾 記憶統計",
        "─" * 50,
        f"  [C] Critical: {stats['memories']['critical']}",
        f"  [I] Important: {stats['memories']['important']}",
        f"  [N] Normal: {stats['memories']['normal']}",
        f"  ────────────────",
        f"  總計: {stats['memories']['total']} 條",
        "",
        "─" * 50,
        "🔢 Token 估算",
        "─" * 50,
        f"  Critical: ~{stats['tokens']['critical']:,} tokens",
        f"  Important: ~{stats['tokens']['important']:,} tokens",
        f"  Normal: ~{stats['tokens']['normal']:,} tokens",
        f"  ──────────────────────",
        f"  總計: ~{stats['tokens']['total']:,} tokens",
        "",
        "─" * 50,
        "📁 分類分佈",
        "─" * 50,
    ]
    
    for cat, count in sorted(stats["distribution"].items(), key=lambda x: -x[1]):
        output_lines.append(f"  {cat}: {count}")
    
    output_lines.extend([
        "",
        "─" * 50,
        "🕐 最近活動 (7天內)",
        "─" * 50,
    ])
    
    for f in stats["recent_activity"]["files"][:5]:
        output_lines.append(f"  📄 {f['name']} ({f['modified']})")
    
    output_lines.extend([
        "",
        f"  新增記憶: {stats['recent_activity']['memories']} 條",
        "",
        "=" * 50,
    ])
    
    return "\n".join(output_lines)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="QST Memory Stats Panel")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    result = stats_panel(output="json" if args.json else "text")
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)
