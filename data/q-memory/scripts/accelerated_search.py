#!/usr/bin/env python3
"""
QST Memory Accelerated Search v1.2
Implements Selection Rule for 90% token reduction.

原理：QST Matrix Selection Rule ($C_{ab}=1$ 當幾何鄰近)
目標：只讀取相關記憶，跳過大部分
"""
import re
from typing import List, Tuple

# Selection Rule Keywords - 定義查詢類別與相關關鍵詞
SELECTION_RULES = {
    "QST_Physics": {
        "keywords": ["QST", "暗物質", "dark matter", "雙縫", "double slit",
                     "FSCA", "E8", "DSI", "ICT", "FSU", "Hydro",
                     "暗能量", "dark energy", "宇宙", "cosmology"],
        "skip": ["用戶偏好", "閒聊", "日常"]
    },
    "User_Identity": {
        "keywords": ["我是誰", "who am I", "身份", "identity",
                     "界王", "龍珠", "Dragon Ball", "偏好", "preference"],
        "skip": ["技術配置", "HKGBook", "OpenClaw"]
    },
    "Recent_Conversation": {
        "keywords": ["上次", "上次討論", "之前說過", "recent",
                     "今日", "今天", "today", "對話"],
        "skip": ["歷史歸檔", "系統配置"]
    },
    "Tech_Config": {
        "keywords": ["OpenClaw", "配置", "config", "API", "模型", "model",
                     "記憶", "memory", "技能", "skill"],
        "skip": ["用戶偏好", "閒聊"]
    },
    "HKGBook": {
        "keywords": ["HKGBook", "論壇", "forum", "外交", "diplomacy",
                     "巡邏", "patrol", "討論串", "thread"],
        "skip": ["QST理論", "物理"]
    },
    "Default": {
        "keywords": [],
        "skip": []
    }
}


def analyze_intent(query: str) -> List[str]:
    """
    分析用戶意圖，返回相關記憶類別
    """
    query_lower = query.lower()
    selected_categories = []

    for category, rules in SELECTION_RULES.items():
        if category == "Default":
            continue

        # 檢查是否匹配關鍵詞
        for keyword in rules["keywords"]:
            if keyword.lower() in query_lower:
                selected_categories.append(category)
                break

    # 如果沒有匹配，返回 Default（只讀取 critical 記憶）
    if not selected_categories:
        selected_categories = ["Default"]

    return selected_categories


def filter_memories(query: str, memory_lines: List[str]) -> Tuple[List[str], int]:
    """
    根據 Selection Rule 過濾記憶
    返回：(過濾後的記憶, 估計節省的 tokens)
    """
    selected_categories = analyze_intent(query)
    filtered = []
    skipped = 0

    # 定義跳過的關鍵詞
    skip_keywords = set()
    for cat in SELECTION_RULES.values():
        for kw in cat.get("skip", []):
            skip_keywords.add(kw.lower())

    for line in memory_lines:
        line_lower = line.lower()

        # 保留所有 Critical 記憶
        if "[C]" in line or "[Critical]" in line:
            filtered.append(line)
            continue

        # 跳過 Normal 記憶（除非相關）
        if "[N]" in line or "[Normal]" in line:
            is_relevant = any(kw in line_lower for kw in skip_keywords)
            if not is_relevant:
                skipped += 1
                continue

        # Important 記憶：根據類別選擇
        if "[I]" in line or "[Important]" in line:
            is_relevant = any(cat in line for cat in selected_categories)
            if is_relevant:
                filtered.append(line)
            else:
                skipped += 1
            continue

        # 無標籤記憶：預設保留
        filtered.append(line)

    # 計算節省的 tokens（假設每行 ~50 tokens）
    tokens_saved = skipped * 50

    return filtered, tokens_saved


def accelerated_search(query: str, memory_content: str) -> dict:
    """
    加速搜索主函數
    """
    lines = memory_content.split("\n")
    filtered, tokens_saved = filter_memories(query, lines)

    # 估算
    original_tokens = len(lines) * 50
    new_tokens = len(filtered) * 50
    reduction = (tokens_saved / original_tokens * 100) if original_tokens > 0 else 0

    return {
        "query": query,
        "categories": analyze_intent(query),
        "original_tokens": original_tokens,
        "new_tokens": new_tokens,
        "tokens_saved": tokens_saved,
        "reduction_percent": round(reduction, 1),
        "filtered_content": "\n".join(filtered[:20]),  # 只返回前20行
        "status": "success"
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"Query: {query}")
        print("\nAnalyzing intent...")
        categories = analyze_intent(query)
        print(f"Selected categories: {categories}")
    else:
        print("Usage: python accelerated_search.py <query>")
        print("\nExample: python accelerated_search.py QST暗物質是什麼")
