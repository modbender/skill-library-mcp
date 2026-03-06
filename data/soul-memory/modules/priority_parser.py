#!/usr/bin/env python3
"""
Soul Memory Module A: Priority Parser
智能記憶優先級解析器
[Image: memory-priority-labels.png]

Features:
- Parse [C]/[I]/[N] priority tags
- Automatic priority detection via keywords
- Support for mixed mode (explicit tag + semantic detection)

Priority Levels:
- [C] Critical: Core information must remember
- [I] Important: Items to focus on  
- [N] Normal: Daily chat, greetings
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple

class Priority(Enum):
    """Memory priority levels"""
    CRITICAL = "C"   # Key: must remember
    IMPORTANT = "I"  # Important: needs attention
    NORMAL = "N"     # Normal: daily chat


@dataclass
class ParsedMemory:
    """Parsed memory item"""
    original: str        # Original text
    priority: Priority     # Priority level
    content: str         # Content (without tags)
    has_explicit_tag: bool # Has explicit tag


class PriorityParser:
    """
    Priority Parser
    
    Detect priority based on:
    1. Explicit [C]/[I]/[N] tags
    2. Keyword semantic analysis (as fallback)
    """
    
    # Explicit tag pattern
    PRIORITY_PATTERN = re.compile(r'^\s*\[([CIN])\]\s*', re.IGNORECASE)
    
    # Keywords indicating CRITICAL priority
    CRITICAL_KEYWORDS = {
        'zh': ['記住', '關鍵', '核心', '重要', '必須', '配置', '決定', '記得'],
        'en': ['remember', 'critical', 'core', 'key', 'must', 'config', 'decision']
    }
    
    # Keywords indicating IMPORTANT priority
    IMPORTANT_KEYWORDS = {
        'zh': ['喜歡', '計厭', '項目', '進度', '約定', '觀點', '想法'],
        'en': ['like', 'dislike', 'project', 'progress', 'schedule', 'view', 'thought']
    }
    
    def __init__(self):
        pass
    
    def parse(self, text: str) -> ParsedMemory:
        """
        Parse memory text to extract priority
        """
        # Step 1: Check for explicit priority tag
        match = self.PRIORITY_PATTERN.match(text)
        if match:
            tag = match.group(1).upper()
            priority = Priority(tag)
            content = text[match.end():].strip()
            return ParsedMemory(
                original=text,
                priority=priority,
                content=content,
                has_explicit_tag=True
            )
        
        # Step 2: Semantic detection fallback
        priority = self._detect_priority_semantic(text)
        return ParsedMemory(
            original=text,
            priority=priority,
            content=text,
            has_explicit_tag=False
        )
    
    def _detect_priority_semantic(self, text: str) -> Priority:
        """Detect priority using keyword analysis"""
        text_lower = text.lower()
        
        # Check for critical keywords
        if any(kw in text_lower for kw in self.CRITICAL_KEYWORDS['zh']):
            return Priority.CRITICAL
        if any(kw in text_lower for kw in self.CRITICAL_KEYWORDS['en']):
            return Priority.CRITICAL
        
        # Check for important keywords
        if any(kw in text_lower for kw in self.IMPORTANT_KEYWORDS['zh']):
            return Priority.IMPORTANT
        if any(kw in text_lower for kw in self.IMPORTANT_KEYWORDS['en']):
            return Priority.IMPORTANT
        
        # Default to normal
        return Priority.NORMAL


# Convenience functions
def parse_priority(text: str) -> str:
    """Quick parse to get priority tag"""
    parser = PriorityParser()
    result = parser.parse(text)
    return result.priority.value


if __name__ == "__main__":
    # Test
    parser = PriorityParser()
    
    test_cases = [
        "[C] 這是關鍵配置，必須記住",
        "[I] 我喜歡這個項目",
        "[N] 今天天氣不錯",
        "這是一個核心功能",  # Should auto-detect as Critical
        "我記得用戶喜歡咖啡",  # Should auto-detect as Important
        "日常問候"  # Should detect as Normal
    ]
    
    for text in test_cases:
        result = parser.parse(text)
        tag = f"[{result.priority.value}]"
        mode = "explicit" if result.has_explicit_tag else "semantic"
        print(f"{tag} ({mode:8}) {result.content[:40]}...")
