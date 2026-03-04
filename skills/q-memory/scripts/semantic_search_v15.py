#!/usr/bin/env python3
"""
Semantic Search v1.5 - 增強版語義搜索
引入相似度算法、上下文感知、權重調整

改進：
1. 詞頻-逆文檔頻率 (TF-IDF) 相似度
2. 上下文感知搜索
3. 記憶權重與年齡調整
4. 語義等價映射擴展

Usage:
    python semantic_search_v15.py "暗物質計算"
    python semantic_search_v15.py "ARM 芯片" --context "技術討論"
"""

import json
import re
import yaml
import math
from pathlib import Path
from typing import Optional, Set, List, Dict, Tuple
from collections import Counter
from datetime import datetime

SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "config.yaml"
MEMORY_FILE = SKILL_DIR / "data" / "qst_memories.md"  # 獨立存儲


def load_config() -> dict:
    """載入配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {"tree": {}, "search": {}}


def load_memory() -> List[dict]:
    """
    載入記憶並解析元數據
    
    Returns:
        [{"content": "...", "weight": "N", "created": datetime, "category": "..."}]
    """
    memories = []
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            entries = re.split(r'\n---+\n', content)
            
            for entry in entries:
                if not entry.strip():
                    continue
                
                # 解析權重標籤
                weight = "N"
                weight_match = re.search(r'\[([CIN])\]', entry)
                if weight_match:
                    weight = weight_match.group(1)
                
                # 解析日期
                created = datetime.now()
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', entry)
                if date_match:
                    try:
                        created = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                    except:
                        pass
                
                # 解析分類標籤
                category = "General"
                cat_match = re.search(r'\[([A-Za-z_]+)\]', entry)
                if cat_match and cat_match.group(1) not in ['C', 'I', 'N']:
                    category = cat_match.group(1)
                
                memories.append({
                    "content": entry.strip(),
                    "weight": weight,
                    "created": created,
                    "category": category
                })
    
    return memories


def calculate_tf(tokens: List[str]) -> Dict[str, float]:
    """計算詞頻 (TF)"""
    counter = Counter(tokens)
    total = len(tokens)
    return {word: count / total for word, count in counter.items()}


def calculate_idf(documents: List[List[str]]) -> Dict[str, float]:
    """計算逆文檔頻率 (IDF)"""
    doc_count = len(documents)
    all_words = set(word for doc in documents for word in doc)
    
    idf = {}
    for word in all_words:
        docs_with_word = sum(1 for doc in documents if word in doc)
        idf[word] = math.log(doc_count / (1 + docs_with_word)) + 1
    
    return idf


def tokenize(text: str) -> List[str]:
    """
    分詞（簡化版）
    支援中英文混合
    """
    # 移除標點符號
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
    # 分割
    tokens = text.lower().split()
    # 中文單字分割
    chinese_tokens = []
    for token in tokens:
        if re.match(r'^[\u4e00-\u9fff]+$', token):
            chinese_tokens.extend(list(token))
        else:
            chinese_tokens.append(token)
    
    return chinese_tokens


def cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    """計算餘弦相似度"""
    common_words = set(vec1.keys()) & set(vec2.keys())
    
    if not common_words:
        return 0.0
    
    dot_product = sum(vec1[w] * vec2[w] for w in common_words)
    norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def get_weight_multiplier(weight: str, age_days: float, config: dict) -> float:
    """
    根據權重和年齡計算調整係數
    
    Args:
        weight: 記憶權重 (C/I/N)
        age_days: 記憶年齡（天）
        config: 配置
    
    Returns:
        調整係數 (0.1 - 2.0)
    """
    decay = config.get("decay", {})
    
    if weight == "C":
        # Critical: 永不衰減，增強權重
        return 2.0
    elif weight == "I":
        # Important: 慢衰減
        decay_rate = decay.get("important", 0.1)
        return max(0.5, 1.5 - age_days * decay_rate / 365)
    else:
        # Normal: 快衰減
        decay_rate = decay.get("normal", 0.5)
        return max(0.1, 1.0 - age_days * decay_rate / 30)


# 語義等價映射（擴展版）
SEMANTIC_EQUIVALENCES = {
    # 動漫相關
    "那個動漫": ["Dragon Ball", "龍珠", "悟空", "Dragon", "Ball"],
    "動漫": ["Dragon Ball", "龍珠", "anime", "動畫"],
    
    # 人物指代
    "他": ["用戶", "秦王", "陛下", "King", "user"],
    "她": ["用戶", "user"],
    "你": ["丞相", "李斯", "Li Si", "assistant"],
    "朕": ["秦王", "陛下", "King", "user"],
    
    # 記憶相關
    "之前說過": ["MEMORY.md", "記憶", "memory", "之前"],
    "記得嗎": ["記憶", "memory", "recall"],
    "喜歡什麼": ["偏好", "preference", "喜歡", "like"],
    
    # QST 相關
    "QST暗物質": ["FSCA", "暗物質", "dark matter", "torsion", "幾何撓率"],
    "暗物質理論": ["FSCA", "dark matter", "QST", "torsion"],
    "粒子物理": ["E8", "particle", "Standard Model", "標準模型"],
    
    # 技術相關
    "ARM芯片": ["Tech", "芯片", "chip", "CPU", "processor", "技術"],
    "ARM 芯片": ["Tech", "芯片", "chip", "CPU", "processor", "技術"],
    "芯片": ["chip", "CPU", "processor", "Tech", "技術"],
    "模型配置": ["Tech_Config_Model", "model", "配置", "GLM", "Gemini"],
    
    # 邊防相關
    "邊防": ["Border", "Security", "VPN", "firewall", "安全"],
    "監控": ["Monitor", "monitor", "CPU", "memory", "系統"],
    
    # 外交相關
    "論壇": ["HKGBook", "forum", "外交", "帖子"],
    "帖子": ["post", "article", "HKGBook", "發表"],
}


def expand_semantic_query(query: str) -> Tuple[str, List[str]]:
    """
    擴展語義等價詞
    
    Returns:
        (expanded_query, added_terms)
    """
    expanded = query
    added = []
    
    for phrase, equivalents in SEMANTIC_EQUIVALENCES.items():
        if phrase.lower() in query.lower():
            for eq in equivalents:
                if eq.lower() not in query.lower():
                    expanded += " " + eq
                    added.append(eq)
    
    return expanded, added


def expand_by_keywords(query: str, config: dict) -> Set[str]:
    """根據關鍵詞擴展分類"""
    categories = set()
    tree = config.get("tree", {})
    query_lower = query.lower()
    
    def scan_nodes(data: dict, path: str = ""):
        for name, node in data.items():
            keywords = node.get("keywords", [])
            for kw in keywords:
                if kw.lower() in query_lower:
                    categories.add(name)
                    categories.update(node.get("related", []))
                    break
            
            children = node.get("children", {})
            if children:
                scan_nodes(children, f"{path}/{name}" if path else name)
    
    scan_nodes(tree)
    
    return categories


def get_related_categories(primary: str, config: dict) -> Set[str]:
    """獲取相關分類"""
    related = set()
    tree = config.get("tree", {})
    
    def find_node(data: dict, target: str):
        for name, node in data.items():
            if name == target or target.lower() in name.lower():
                related.update(node.get("related", []))
            
            children = node.get("children", {})
            if children:
                find_node(children, target)
    
    find_node(tree, primary)
    related.add(primary)
    
    return related


def semantic_search_enhanced(
    query: str,
    context: Optional[List[str]] = None,
    expand: bool = True,
    min_relevance: float = 0.1
) -> dict:
    """
    增強版語義搜索
    
    Args:
        query: 搜索查詢
        context: 上下文（最近對話）
        expand: 是否擴展相關分類
        min_relevance: 最小相關度閾值
    
    Returns:
        {
            "primary": "FSCA",
            "path": ["QST", "Physics", "FSCA"],
            "related": ["QST_Computation", "QST_Audit"],
            "keywords": [...],
            "results": [{"content": "...", "score": 0.85, ...}],
            "stats": {...}
        }
    """
    config = load_config()
    memories = load_memory()
    
    # 1. 擴展語義
    expanded_query, added_terms = expand_semantic_query(query)
    
    # 2. 合併上下文
    if context:
        context_str = " ".join(context[-3:])
        expanded_query = f"{context_str} {expanded_query}"
    
    # 3. 識別分類
    categories = expand_by_keywords(expanded_query, config)
    
    if not categories:
        categories = {"General"}
    
    primary = list(categories)[0]
    
    # 4. 擴展相關分類
    if expand:
        related = get_related_categories(primary, config)
        categories.update(related)
    else:
        related = set()
    
    # 5. 構建搜索索引
    query_tokens = tokenize(expanded_query)
    query_tf = calculate_tf(query_tokens)
    
    # 構建文檔集合
    all_docs = [tokenize(m["content"]) for m in memories]
    idf = calculate_idf(all_docs + [query_tokens])
    
    # 計算查詢 TF-IDF 向量
    query_tfidf = {word: query_tf.get(word, 0) * idf.get(word, 1) for word in query_tokens}
    
    # 6. 搜索記憶並計算相似度
    results = []
    
    for memory in memories:
        # 分類過濾
        if memory["category"] not in categories and memory["category"] != "General":
            continue
        
        # 計算相似度
        mem_tokens = tokenize(memory["content"])
        mem_tf = calculate_tf(mem_tokens)
        mem_tfidf = {word: mem_tf.get(word, 0) * idf.get(word, 1) for word in mem_tokens}
        
        similarity = cosine_similarity(query_tfidf, mem_tfidf)
        
        # 權重調整
        age_days = (datetime.now() - memory["created"]).days
        weight_mult = get_weight_multiplier(memory["weight"], age_days, config)
        
        adjusted_score = similarity * weight_mult
        
        if adjusted_score >= min_relevance:
            results.append({
                "content": memory["content"],
                "score": round(adjusted_score, 3),
                "similarity": round(similarity, 3),
                "weight": memory["weight"],
                "weight_multiplier": round(weight_mult, 2),
                "category": memory["category"],
                "age_days": age_days
            })
    
    # 7. 排序
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # 8. 構建路徑
    path = build_category_path(primary, config)
    
    return {
        "primary": primary,
        "path": path,
        "related": list(related - {primary}),
        "keywords": query_tokens[:10],
        "added_terms": added_terms,
        "results": results[:10],
        "count": len(results),
        "stats": {
            "total_memories": len(memories),
            "categories_searched": len(categories),
            "query_expanded": len(added_terms) > 0,
            "context_used": context is not None
        }
    }


def build_category_path(category: str, config: dict) -> List[str]:
    """構建分類路徑"""
    tree = config.get("tree", {})
    path = []
    
    def search(data: dict, target: str, current_path: List[str]) -> bool:
        for name, node in data.items():
            new_path = current_path + [name]
            
            if name == target:
                path.extend(new_path)
                return True
            
            children = node.get("children", {})
            if children and search(children, target, new_path):
                return True
        
        return False
    
    search(tree, category, [])
    
    return path if path else [category]


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Semantic Search v1.5")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--context", "-c", help="Context (comma-separated)")
    parser.add_argument("--expand", action="store_true", help="Expand related categories")
    parser.add_argument("--min-relevance", type=float, default=0.1, help="Minimum relevance")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    context = args.context.split(",") if args.context else None
    
    result = semantic_search_enhanced(
        args.query,
        context=context,
        expand=args.expand,
        min_relevance=args.min_relevance
    )
    
    print(f"\n🎯 Primary: {result['primary']}")
    print(f"📁 Path: {' → '.join(result['path'])}")
    print(f"🔗 Related: {', '.join(result['related'][:5])}")
    
    if result['added_terms']:
        print(f"➕ Added terms: {', '.join(result['added_terms'])}")
    
    print(f"📊 Found: {result['count']} memories")
    print(f"📈 Stats: {result['stats']}")
    
    if args.verbose:
        print("\n--- Results ---")
        for i, r in enumerate(result['results'][:5], 1):
            print(f"\n[{i}] Score: {r['score']} (sim: {r['similarity']}, w: {r['weight']}x{r['weight_multiplier']})")
            print(f"Category: {r['category']} | Age: {r['age_days']} days")
            print(r['content'][:200] + "..." if len(r['content']) > 200 else r['content'])
