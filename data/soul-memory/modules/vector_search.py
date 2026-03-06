#!/usr/bin/env python3
"""
Soul Memory Module B: Vector Search Engine (v2.2)
Local keyword-based semantic search with CJK support
Author: Soul Memory System
Date: 2026-02-18
"""
import json
import hashlib
import os
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class SearchResult:
    """Search result"""
    content: str
    score: float
    source: str
    line_number: int
    category: str = ""
    priority: str = "N"


@dataclass
class MemorySegment:
    """Memory segment"""
    id: str
    content: str
    source: str
    line_number: int
    category: str = ""
    priority: str = "N"
    keywords: List[str] = field(default_factory=list)


class VectorSearch:
    """
    Vector Search Engine v2.2
    - CJK intelligent segmentation (无需外部依赖)
    - Local keyword-based semantic search
    """
    
    VERSION = "2.3.0"
    
    # CJK Unicode ranges
    CJK_RANGES = [
        (0x4E00, 0x9FFF),
        (0x3400, 0x4DBF),
        (0x3040, 0x309F),
        (0x30A0, 0x30FF),
    ]
    
    SEMANTIC_EXPANSIONS = {
        "user": ["用戶", "user", "preferences"],
        "preferences": ["喜好", "偏好", "喜歡"],
        "config": ["配置", "設定", "settings"],
        "api": ["API", "接口", "endpoint"],
        "memory": ["記憶", "memory", "context"],
        "project": ["專案", "項目", "project"],
        "task": ["任務", "工作", "task"],
    }

    def __init__(self):
        self.segments: List[MemorySegment] = []
        self.keyword_index: Dict[str, List[str]] = {}

    def _is_cjk(self, char: str) -> bool:
        """Check if character is CJK"""
        code = ord(char)
        for start, end in self.CJK_RANGES:
            if start <= code <= end:
                return True
        return False

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords (v2.2 CJK智能分词)"""
        text = re.sub(r"[#*_`\[\](){}]", " ", text)
        
        result = []
        current_word = ""
        
        for char in text:
            if self._is_cjk(char):
                if current_word:
                    result.append(current_word)
                    current_word = ""
                result.append(char)
            elif char.isalnum():
                current_word += char
            else:
                if current_word:
                    result.append(current_word)
                    current_word = ""
        
        if current_word:
            result.append(current_word)
        
        keywords = []
        i = 0
        while i < len(result):
            word = result[i]
            if len(word) >= 1:
                keywords.append(word.lower())
            # Create bigram for adjacent CJK characters (single chars only)
            if i + 1 < len(result) and len(word) == 1 and len(result[i+1]) == 1:
                if self._is_cjk(word) and self._is_cjk(result[i+1]):
                    bigram = word + result[i+1]
                    keywords.append(bigram.lower())
            i += 1
        
        seen = set()
        filtered = []
        for k in keywords:
            if k not in seen and len(k) >= 1:
                seen.add(k)
                filtered.append(k)
        
        return filtered

    def _expand_query(self, query: str) -> List[str]:
        """Expand query with semantic synonyms"""
        keywords = self._extract_keywords(query)
        expanded = set(keywords)
        for kw in keywords:
            if kw in self.SEMANTIC_EXPANSIONS:
                expanded.update(self.SEMANTIC_EXPANSIONS[kw])
        return list(expanded)

    def add_segment(self, segment: Dict[str, Any]):
        """Add a memory segment"""
        ms = MemorySegment(
            id=segment.get('id', hashlib.md5(segment['content'].encode()).hexdigest()[:8]),
            content=segment['content'],
            source=segment.get('source', 'unknown'),
            line_number=segment.get('line_number', 0),
            category=segment.get('category', ''), 
            priority=segment.get('priority', 'N'),
            keywords=segment.get('keywords', self._extract_keywords(segment['content']))
        )
        self.segments.append(ms)
        
        for kw in ms.keywords:
            if kw not in self.keyword_index:
                self.keyword_index[kw] = []
            self.keyword_index[kw].append(ms.id)

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search memory with CJK support"""
        query_keywords = self._expand_query(query)
        scores = {}
        matches_count = {}  # 記錄每個 segment 匹配的關鍵詞數量

        # 計算每個 segment 的基礎分數（關鍵詞匹配數量，不是匹配次數）
        for seg in self.segments:
            matched_keywords = 0
            for kw in query_keywords:
                if kw in seg.keywords:
                    matched_keywords += 1

            if matched_keywords > 0:
                scores[seg.id] = matched_keywords
                matches_count[seg.id] = matched_keywords

        # 添加優先級加權
        for seg in self.segments:
            if seg.id in scores:
                priority_boost = {
                    'C': 3.0,  # Critical: +3 分
                    'I': 1.5,  # Important: +1.5 分
                    'N': 0.5,  # Normal: +0.5 分
                }.get(seg.priority, 0.5)
                scores[seg.id] += priority_boost

        # 排序：綜合分數優先，優先級其次
        def sort_key(item):
            seg_id, score = item
            seg = next((s for s in self.segments if s.id == seg_id), None)
            if seg:
                # 檢查記憶是否包含完整的查詢字符串（給予額外加權）
                exact_match_bonus = 0
                content_lower = seg.content.lower()
                query_lower = query.lower()
                if query_lower in content_lower:
                    exact_match_bonus = 2.0

                priority_weight = {'C': 10, 'I': 5, 'N': 0}.get(seg.priority, 0)
                # 總分 = 關鍵詞匹配 + 優先級加權 + 完整匹配加權
                total_score = scores[seg_id] + exact_match_bonus
                return (total_score, priority_weight, matches_count.get(seg.id, 0))
            return (scores[seg_id], 0, 0)

        sorted_scores = sorted(scores.items(), key=sort_key, reverse=True)
        results = []

        for seg_id, score in sorted_scores[:top_k]:
            seg = next((s for s in self.segments if s.id == seg_id), None)
            if seg:
                # 重新計算總分（包含完整匹配加權）
                content_lower = seg.content.lower()
                query_lower = query.lower()
                exact_match_bonus = 2.0 if query_lower in content_lower else 0.0
                final_score = scores[seg_id] + exact_match_bonus

                results.append(SearchResult(
                    content=seg.content,
                    score=final_score,
                    source=seg.source,
                    line_number=seg.line_number,
                    category=seg.category,
                    priority=seg.priority
                ))

        return results

    def index_file(self, file_path: Path):
        """Index a markdown file with block-level indexing"""
        if not file_path.exists():
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # 遇到標題（##）
            if stripped.startswith('##') and not stripped.startswith('###'):
                # 收集這個標題下方的內容，直到下一個 ## 標題
                block_content = []
                block_start = i + 1
                
                # 添加標題（移除 ##）
                title = stripped.lstrip('#').strip()
                block_content.append(title)
                i += 1
                
                # 收集內容行（跳過空行，直到下一個 ## 標題）
                while i < len(lines):
                    next_line = lines[i].strip()
                    
                    # 遇到下一個 ## 標題，停止
                    if next_line.startswith('##') and not next_line.startswith('###'):
                        break
                    
                    # 非空行才加入
                    if next_line:
                        block_content.append(next_line)
                    
                    i += 1
                
                # 將整個區塊合併為一個 segment
                full_content = ' | '.join(block_content)
                
                # 偵測優先級
                priority = 'N'
                if '[C]' in full_content:
                    priority = 'C'
                elif '[I]' in full_content:
                    priority = 'I'
                
                segment = {
                    'content': full_content,
                    'source': str(file_path),
                    'line_number': block_start,
                    'category': title,
                    'priority': priority
                }
                self.add_segment(segment)
            else:
                # 非標題行，單獨跳過
                i += 1

    def export_index(self) -> Dict[str, Any]:
        """Export index to dict"""
        return {
            'version': self.VERSION,
            'segments': [
                {
                    'id': s.id,
                    'content': s.content,
                    'source': s.source,
                    'line_number': s.line_number,
                    'category': s.category,
                    'priority': s.priority,
                    'keywords': s.keywords
                }
                for s in self.segments
            ]
        }

    def load_index(self, data: Dict[str, Any]):
        """Load index from dict"""
        self.segments = []
        self.keyword_index = {}
        for seg_data in data.get('segments', []):
            ms = MemorySegment(
                id=seg_data.get('id', ''),
                content=seg_data.get('content', ''),
                source=seg_data.get('source', ''),
                line_number=seg_data.get('line_number', 0),
                category=seg_data.get('category', ''),
                priority=seg_data.get('priority', 'N'),
                keywords=seg_data.get('keywords', [])
            )
            self.segments.append(ms)
            for kw in ms.keywords:
                if kw not in self.keyword_index:
                    self.keyword_index[kw] = []
                self.keyword_index[kw].append(ms.id)