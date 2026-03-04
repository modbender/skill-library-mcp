#!/usr/bin/env python3
"""
Save Memory v1.5 - 智能記憶保存系統
自動分類 + 權重標記 + 記憶寫入

功能：
1. 自動推斷分類
2. 智能標記權重
3. 保存到 MEMORY.md
4. 返回記憶索引

Usage:
    python save_memory.py "這是一個重要發現"
    python save_memory.py "一般對話" --weight N
    python save_memory.py --file memory.txt --auto
"""

import re
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# 添加腳本目錄到路徑
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from auto_classify import auto_classify as do_auto_classify

SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "config.yaml"
MEMORY_FILE = SKILL_DIR / "data" / "qst_memories.md"  # 獨立存儲，避免與 MEMORY.md 衝突


def load_config() -> dict:
    """載入配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def suggest_weight(content: str) -> str:
    """
    智能建議權重
    
    規則：
    - [C] Critical: 決策、配置、密鑰、重要偏好
    - [I] Important: 專案、約定、觀點
    - [N] Normal: 一般對話、閒聊、問候
    """
    content_lower = content.lower()
    
    # Critical 關鍵詞
    critical_keywords = [
        "密鑰", "key", "token", "密碼", "password", "配置", "config",
        "決策", "決定", "系統配置", "api key", "管理密鑰",
        "重要", "critical", "絕對", "必須", "永不"
    ]
    
    # Important 關鍵詞
    important_keywords = [
        "專案", "project", "計劃", "plan", "約定", "答應",
        "偏好", "喜歡", "不喜歡", "想", "目標",
        "討論", "分析", "比較", "結論", "觀點"
    ]
    
    for kw in critical_keywords:
        if kw.lower() in content_lower:
            return "C"
    
    for kw in important_keywords:
        if kw.lower() in content_lower:
            return "I"
    
    return "N"


def format_memory(
    content: str,
    category: str = "General",
    weight: str = "N",
    auto_classified: bool = False
) -> str:
    """
    格式化記憶
    
    格式：
    ---
    # Memory Title (自動生成或第一行)
    
    [Category] [Weight]
    Date: YYYY-MM-DD
    
    Content...
    
    Tags: tag1, tag2
    """
    lines = content.strip().split('\n')
    title = lines[0][:50] if lines else "Memory Entry"
    
    # 構建記憶塊
    memory = f"""# {title}

[{category}] [{weight}]
Date: {datetime.now().strftime("%Y-%m-%d")}

"""
    
    # 添加自動分類標記
    if auto_classified:
        memory += f"*Auto-classified by QST Memory v1.5*\n\n"
    
    # 添加內容
    memory += content
    
    # 自動標籤
    tags = extract_tags(content)
    if tags:
        memory += f"\n\nTags: {', '.join(tags)}"
    
    return memory


def extract_tags(content: str) -> List[str]:
    """提取標籤"""
    tags = []
    
    # 提取 #標籤
    hash_tags = re.findall(r'#(\w+)', content)
    tags.extend(hash_tags)
    
    return list(set(tags))


def save_memory(
    content: str,
    category: Optional[str] = None,
    weight: Optional[str] = None,
    auto_classify: bool = True,
    auto_weight: bool = True
) -> Dict:
    """
    保存記憶主函數
    
    Args:
        content: 記憶內容
        category: 指定分類 (可選)
        weight: 指定權重 (可選)
        auto_classify: 是否自動分類
        auto_weight: 是否自動標記權重
    
    Returns:
        {
            "success": True,
            "category": "QST_Physics",
            "weight": "I",
            "index": 42,
            "formatted": "..."
        }
    """
    config = load_config()
    
    # 1. 自動分類
    if auto_classify and not category:
        classification = do_auto_classify(content)
        category = classification["suggested_category"]
        auto_classified = True
        reasoning = classification["reasoning"]
    else:
        category = category or "General"
        auto_classified = False
        reasoning = "Manual category specified"
    
    # 2. 自動權重
    if auto_weight and not weight:
        weight = suggest_weight(content)
    weight = weight or "N"
    
    # 3. 格式化
    formatted = format_memory(content, category, weight, auto_classified)
    
    # 4. 讀取現有記憶
    existing = []
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            content_all = f.read()
            existing = re.split(r'\n---\n', content_all)
            existing = [e.strip() for e in existing if e.strip()]
    
    # 5. 添加新記憶
    existing.append(formatted)
    
    # 6. 寫回文件
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        f.write('\n---\n\n'.join(existing))
        f.write('\n')
    
    return {
        "success": True,
        "category": category,
        "weight": weight,
        "index": len(existing),
        "auto_classified": auto_classified,
        "reasoning": reasoning,
        "formatted": formatted[:200] + "...",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Save Memory v1.5")
    parser.add_argument("content", nargs="?", help="Memory content")
    parser.add_argument("--file", "-f", help="File containing content")
    parser.add_argument("--category", "-c", help="Category (auto if not specified)")
    parser.add_argument("--weight", "-w", choices=["C", "I", "N"], help="Weight")
    parser.add_argument("--no-auto-classify", action="store_true", help="Disable auto-classify")
    parser.add_argument("--no-auto-weight", action="store_true", help="Disable auto-weight")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # 獲取內容
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    elif args.content:
        content = args.content
    else:
        content = input("Enter memory content: ")
    
    result = save_memory(
        content,
        category=args.category,
        weight=args.weight,
        auto_classify=not args.no_auto_classify,
        auto_weight=not args.no_auto_weight
    )
    
    print(f"\n💾 Memory Saved")
    print(f"{'='*50}")
    print(f"✅ Success: {result['success']}")
    print(f"🏷️ Category: {result['category']}")
    print(f"⚖️ Weight: {result['weight']}")
    print(f"📝 Index: {result['index']}")
    print(f"🤖 Auto-classified: {result['auto_classified']}")
    print(f"💡 Reasoning: {result['reasoning']}")
    print(f"🕐 Timestamp: {result['timestamp']}")
    
    if args.verbose:
        print(f"\n📄 Formatted Preview:")
        print("-" * 50)
        print(result['formatted'])
