#!/usr/bin/env python3
"""
Soul Memory Module F: Auto-Trigger
Pre-response memory retrieval

Automatically searches relevant memories before responding.
Based on query type selection rules.

Author: Soul Memory System
Date: 2026-02-17
"""

import os
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Ensure module path
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class TriggerResult:
    """Auto-trigger result"""
    query: str
    detected_category: str
    memories: List[Dict[str, Any]]
    context_summary: str


# Selection Rules - Generic query type mapping
SELECTION_RULES = {
    # Physics/Science
    "physics": "Science",
    "science": "Science",
    "理論": "Science",
    "物理": "Science",
    
    # User identity
    "user": "User_Identity",
    "我是誰": "User_Identity",
    "身份": "User_Identity",
    "preferences": "User_Identity",
    "喜好": "User_Identity",
    
    # Technical config
    "config": "Tech_Config",
    "ssh": "Tech_Config",
    "api": "Tech_Config",
    "key": "Tech_Config",
    "配置": "Tech_Config",
    
    # Projects
    "project": "Project",
    "專案": "Project",
    "項目": "Project",
    
    # History
    "history": "History",
    "歷史": "History",
    "之前": "History",
    
    # General
    "記憶": "Memory",
    "memory": "Memory",
}


class AutoTrigger:
    """
    Auto-Trigger System
    
    Pre-response memory retrieval based on query type.
    """
    
    def __init__(self, memory_system=None):
        self.memory_system = memory_system
    
    def _detect_category(self, query: str) -> str:
        """Detect query category"""
        query_lower = query.lower()
        
        for keyword, category in SELECTION_RULES.items():
            if keyword in query_lower:
                return category
        
        return "General"
    
    def trigger(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Auto-trigger memory search
        
        Returns relevant memories for the query.
        """
        category = self._detect_category(query)
        
        if self.memory_system:
            results = self.memory_system.search(query, top_k=top_k)
            memories = [
                {
                    'content': r.content,
                    'score': r.score,
                    'priority': r.priority,
                    'category': r.category
                }
                for r in results
            ]
        else:
            memories = []
        
        # Build context summary
        if memories:
            context = f"Found {len(memories)} relevant memories in category '{category}'"
        else:
            context = f"No memories found for query in category '{category}'"
        
        return {
            'query': query,
            'category': category,
            'memories': memories,
            'context': context
        }


def auto_trigger(query: str, top_k: int = 5) -> Dict[str, Any]:
    """Convenience function for auto-trigger"""
    trigger = AutoTrigger()
    return trigger.trigger(query, top_k)


def get_memory_context(query: str) -> str:
    """Get memory context as string"""
    result = auto_trigger(query)
    return result.get('context', '')


if __name__ == "__main__":
    # Test
    trigger = AutoTrigger()
    
    test_queries = [
        "What are my preferences?",
        "How does the physics theory work?",
        "What's the API configuration?",
        "Tell me about history"
    ]
    
    for q in test_queries:
        result = trigger.trigger(q)
        print(f"Query: {q}")
        print(f"  Category: {result['category']}")
        print(f"  Context: {result['context']}")
        print()
