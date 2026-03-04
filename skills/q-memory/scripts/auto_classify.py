#!/usr/bin/env python3
"""
Auto Classify v1.5 - 自動分類引擎
根據內容自動推斷最適合的分類

功能：
1. 關鍵詞提取
2. 分類相似度計算
3. 自動建議分類
4. 置信度評估

Usage:
    python auto_classify.py "QST暗物質計算使用FSCA理論"
    python auto_classify.py --memory-file memory.txt
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import Counter

SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "config.yaml"


def load_config() -> dict:
    """載入配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def load_tree() -> dict:
    """載入分類樹"""
    config = load_config()
    return config.get("tree", {})


def extract_keywords(content: str) -> List[str]:
    """
    提取內容關鍵詞
    
    支援：
    - 英文單詞
    - 中文字符串
    - 標籤格式 [Category]
    - 代碼/配置項
    """
    keywords = []
    
    # 提取標籤
    tags = re.findall(r'\[([A-Za-z_]+)\]', content)
    keywords.extend(tags)
    
    # 提取英文單詞
    english = re.findall(r'\b[a-zA-Z]{2,}\b', content)
    keywords.extend(english)
    
    # 提取中文詞彙（2-4字）
    chinese = re.findall(r'[\u4e00-\u9fff]{2,4}', content)
    keywords.extend(chinese)
    
    # 提取配置項
    configs = re.findall(r'(?:API|config|model|key|token|cron)\s*\w+', content, re.IGNORECASE)
    keywords.extend(configs)
    
    # 去重，保留頻率
    keyword_freq = Counter(k.lower() for k in keywords)
    
    return [kw for kw, _ in keyword_freq.most_common(20)]


def calculate_category_score(keywords: List[str], category: str, tree: dict) -> Tuple[float, int, List[str]]:
    """
    計算關鍵詞與分類的匹配分數
    
    Returns:
        (score, match_count, matched_keywords)
    """
    score = 0.0
    matched = []
    
    def search_node(data: dict, depth: int = 0):
        nonlocal score, matched
        
        for name, node in data.items():
            if name.lower() in [k.lower() for k in keywords]:
                # 直接匹配分類名稱
                weight = 10.0 / (depth + 1)
                score += weight
                matched.append(name)
            
            # 匹配關鍵詞
            node_keywords = node.get("keywords", [])
            for kw in node_keywords:
                if kw.lower() in [k.lower() for k in keywords]:
                    weight = 5.0 / (depth + 1)
                    score += weight
                    matched.append(kw)
            
            # 遞歸搜索子節點
            children = node.get("children", {})
            if children:
                search_node(children, depth + 1)
    
    search_node(tree)
    
    return score, len(set(matched)), list(set(matched))


def get_category_keywords(category: str, tree: dict) -> List[str]:
    """獲取分類的所有關鍵詞"""
    keywords = []
    
    def search(data: dict):
        for name, node in data.items():
            if name == category:
                keywords.extend(node.get("keywords", []))
                # 遞歸獲取子關鍵詞
                for child in node.get("children", {}).values():
                    keywords.extend(child.get("keywords", []))
            
            children = node.get("children", {})
            if children:
                search(children)
    
    search(tree)
    
    return keywords


def suggest_category(content: str, top_k: int = 3) -> List[Dict]:
    """
    建議最佳分類
    
    Args:
        content: 內容
        top_k: 返回前 k 個建議
    
    Returns:
        [{"category": "QST_Physics_FSCA", "score": 8.5, "reasoning": "...", "confidence": "high"}]
    """
    config = load_config()
    tree = load_tree()
    
    # 提取關鍵詞
    keywords = extract_keywords(content)
    
    if not keywords:
        return [{
            "category": "General",
            "score": 1.0,
            "reasoning": "No keywords extracted, default to General",
            "confidence": "low",
            "keywords": []
        }]
    
    # 計算所有分類的分數
    scores = []
    
    def evaluate_node(data: dict, parent_path: str = "", depth: int = 0):
        for name, node in data.items():
            path = f"{parent_path}/{name}" if parent_path else name
            
            category_score, match_count, matched = calculate_category_score(
                keywords, name, {name: node}
            )
            
            # 考慮深度懲罰
            depth_penalty = 1.0 / (depth + 1)
            
            # 考慮權重
            auto_weight = node.get("auto_weight", "N")
            weight_bonus = {"C": 2.0, "I": 1.5, "N": 1.0}.get(auto_weight, 1.0)
            
            final_score = category_score * depth_penalty * weight_bonus
            
            scores.append({
                "category": path,
                "score": round(final_score, 2),
                "match_count": match_count,
                "matched_keywords": matched,
                "reasoning": build_reasoning(keywords, matched, name),
                "confidence": "high" if match_count >= 3 else ("medium" if match_count >= 1 else "low")
            })
            
            # 遞歸評估子節點
            children = node.get("children", {})
            if children:
                evaluate_node(children, path, depth + 1)
    
    evaluate_node(tree)
    
    # 去重，保留最高分數
    seen = {}
    for s in scores:
        base = s["category"].split("/")[-1]
        if base not in seen or s["score"] > seen[base]["score"]:
            seen[base] = s
    
    scores = list(seen.values())
    
    # 排序
    scores.sort(key=lambda x: x["score"], reverse=True)
    
    # 添加 General 作為兜底
    if not scores or scores[0]["score"] < 1.0:
        scores.insert(0, {
            "category": "General",
            "score": 1.0,
            "match_count": 0,
            "matched_keywords": [],
            "reasoning": "No matching category found",
            "confidence": "low"
        })
    
    return scores[:top_k]


def build_reasoning(keywords: List[str], matched: List[str], category: str) -> str:
    """構建推理說明"""
    if not matched:
        return f"No direct keyword match with {category}"
    
    return f"Matched keywords: {', '.join(matched)}"


def auto_classify(content: str) -> Dict:
    """
    自動分類主函數
    
    Args:
        content: 內容
    
    Returns:
        {
            "suggested_category": "QST_Physics_FSCA",
            "confidence": "high",
            "alternatives": [...],
            "keywords": [...],
            "reasoning": "..."
        }
    """
    keywords = extract_keywords(content)
    suggestions = suggest_category(content, top_k=5)
    
    best = suggestions[0] if suggestions else {
        "category": "General",
        "score": 1.0,
        "reasoning": "No keywords found"
    }
    
    return {
        "suggested_category": best["category"],
        "confidence": best["confidence"],
        "primary_score": best["score"],
        "reasoning": best["reasoning"],
        "keywords": keywords,
        "alternatives": [
            {"category": s["category"], "score": s["score"], "confidence": s["confidence"]}
            for s in suggestions[1:]
        ],
        "all_suggestions": suggestions
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto Classify for QST Memory v1.5")
    parser.add_argument("content", nargs="?", help="Content to classify")
    parser.add_argument("--file", "-f", help="File containing content")
    parser.add_argument("--top-k", type=int, default=3, help="Top K suggestions")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # 獲取內容
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    elif args.content:
        content = args.content
    else:
        content = input("Enter content to classify: ")
    
    result = auto_classify(content)
    
    print(f"\n📊 Auto Classification Result")
    print(f"{'='*50}")
    print(f"🏷️ Suggested: {result['suggested_category']}")
    print(f"📈 Confidence: {result['confidence']}")
    print(f"🎯 Score: {result['primary_score']}")
    print(f"💡 Reasoning: {result['reasoning']}")
    
    print(f"\n🔑 Keywords: {', '.join(result['keywords'][:10])}")
    
    if result['alternatives']:
        print(f"\n🔄 Alternatives:")
        for alt in result['alternatives']:
            print(f"  • {alt['category']} ({alt['score']}) - {alt['confidence']}")
    
    if args.verbose:
        print(f"\n📋 All Suggestions:")
        for s in result['all_suggestions']:
            print(f"  • {s['category']}: {s['score']} ({s['confidence']}) - {s['reasoning']}")
