#!/usr/bin/env python3
"""
Soul Memory Module C: Dynamic Classifier
Auto-learning category classification

Dynamically learns categories from memory content.
No hardcoded categories.

Author: Soul Memory System
Date: 2026-02-17
"""

import os
import json
import re
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
from collections import Counter


@dataclass
class Category:
    """Memory category"""
    name: str
    keywords: Set[str] = field(default_factory=set)
    count: int = 0


class DynamicClassifier:
    """
    Dynamic Category Classifier
    
    Automatically learns categories from memory content.
    Supports custom category rules.
    """
    
    # Default categories (generic, neutral)
    DEFAULT_CATEGORIES = {
        "User_Identity": {"user", "preferences", "identity", "用戶", "喜好", "身份"},
        "Tech_Config": {"config", "api", "ssh", "key", "設定", "配置"},
        "Project": {"project", "task", "work", "專案", "項目", "工作"},
        "Science": {"theory", "physics", "science", "理論", "物理", "科學"},
        "History": {"history", "past", "before", "歷史", "之前"},
        "Memory": {"memory", "remember", "記憶", "記住"},
        "General": {"general", "chat", "日常", "閒聊"}
    }
    
    def __init__(self, cache_path: Optional[Path] = None):
        self.categories: Dict[str, Category] = {}
        self.cache_path = cache_path or Path(__file__).parent.parent / "cache"
        self.cache_path.mkdir(exist_ok=True)
        
        # Load or initialize categories
        self._load_categories()
    
    def _load_categories(self):
        """Load categories from cache or use defaults"""
        cache_file = self.cache_path / "categories.json"
        
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for name, kw_list in data.get('categories', {}).items():
                self.categories[name] = Category(
                    name=name,
                    keywords=set(kw_list)
                )
        else:
            # Use defaults
            for name, keywords in self.DEFAULT_CATEGORIES.items():
                self.categories[name] = Category(name=name, keywords=keywords)
    
    def _save_categories(self):
        """Save categories to cache"""
        cache_file = self.cache_path / "categories.json"
        data = {
            'categories': {
                name: list(cat.keywords)
                for name, cat in self.categories.items()
            }
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def classify(self, text: str) -> str:
        """Classify text into a category"""
        text_lower = text.lower()
        
        scores = {}
        for name, cat in self.categories.items():
            score = sum(1 for kw in cat.keywords if kw in text_lower)
            if score > 0:
                scores[name] = score
        
        if scores:
            return max(scores.keys(), key=lambda x: scores[x])
        
        return "General"
    
    def learn(self, text: str, category: str):
        """Learn new category association"""
        if category not in self.categories:
            self.categories[category] = Category(name=category)
        
        # Extract keywords (words >= 3 chars)
        words = re.findall(r'\w{3,}', text.lower())
        for word in words:
            self.categories[category].keywords.add(word)
        
        self.categories[category].count += 1
        self._save_categories()
    
    def add_category(self, name: str, keywords: List[str]):
        """Add a new category with keywords"""
        self.categories[name] = Category(
            name=name,
            keywords=set(keywords)
        )
        self._save_categories()
    
    def get_categories(self) -> List[str]:
        """Get all category names"""
        return list(self.categories.keys())


if __name__ == "__main__":
    # Test
    classifier = DynamicClassifier()
    
    test_texts = [
        "User prefers dark mode and likes coffee",
        "API endpoint is configured at localhost:8080",
        "The physics theory explains quantum mechanics",
        "Remember to check the project status"
    ]
    
    for text in test_texts:
        category = classifier.classify(text)
        print(f"'{text[:40]}...' -> {category}")
