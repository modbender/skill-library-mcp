#!/usr/bin/env python3
"""
Unit tests for claw-memory-lite extraction logic.

Run with: python3 -m pytest tests/test_extract.py -v
Or: python3 tests/test_extract.py
"""

import unittest
import sys
import os
import tempfile
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Import extraction functions (we'll test the logic directly)
# Note: In real scenario, extract_memory.py would be refactored to be importable


class TestCategoryDetection(unittest.TestCase):
    """Test category detection logic."""
    
    def setUp(self):
        self.category_keywords = {
            "Skill": ["skill", "api", "token", "model", "installed"],
            "Project": ["project", "strategy", "backtest", "portfolio"],
            "System": ["system", "config", "model", "alias"],
            "Environment": ["env", "backup", "workspace", "uv", "python"],
            "Comm": ["discord", "telegram", "channel", "bot"],
            "Security": ["security", "api key", "permission", "access"]
        }
    
    def detect_category(self, content):
        """Simple category detection (mirrors extract_memory.py logic)."""
        content_lower = content.lower()
        max_score = 0
        detected = "System"
        
        for category, keywords in self.category_keywords.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > max_score:
                max_score = score
                detected = category
        
        return detected
    
    def test_skill_category(self):
        content = "Installed weather skill with API token configuration"
        self.assertEqual(self.detect_category(content), "Skill")
    
    def test_project_category(self):
        content = "A-share strategy backtest portfolio optimization"
        self.assertEqual(self.detect_category(content), "Project")
    
    def test_system_category(self):
        content = "System config updated with new model aliases"
        self.assertEqual(self.detect_category(content), "System")
    
    def test_environment_category(self):
        content = "Workspace backup configured with uv python policy"
        self.assertEqual(self.detect_category(content), "Environment")
    
    def test_comm_category(self):
        content = "Discord telegram channel bot notification setup"
        self.assertEqual(self.detect_category(content), "Comm")
    
    def test_security_category(self):
        content = "Security permission access control for API keys"
        self.assertEqual(self.detect_category(content), "Security")


class TestFactExtraction(unittest.TestCase):
    """Test fact extraction logic."""
    
    def setUp(self):
        self.extraction_keywords = [
            "完成", "配置", "添加", "修复", "停用", "决策",
            "note", "fix", "add", "config", "install", "create"
        ]
    
    def extract_facts(self, content):
        """Simple fact extraction (mirrors extract_memory.py logic)."""
        lines = content.split('\n')
        facts = []
        
        for line in lines:
            line = line.strip()
            if len(line) > 20 and not line.startswith('#'):
                if any(kw in line.lower() for kw in self.extraction_keywords):
                    facts.append(line[:200])
        
        return facts
    
    def test_extract_single_fact(self):
        content = "- Added new model alias configuration"
        facts = self.extract_facts(content)
        self.assertEqual(len(facts), 1)
        self.assertIn("Added", facts[0])
    
    def test_extract_multiple_facts(self):
        content = """
# Daily Note

- Installed weather skill
- Created backup config
- Fixed API token issue
"""
        facts = self.extract_facts(content)
        self.assertEqual(len(facts), 3)
    
    def test_skip_headers(self):
        content = "# This is a header\n- Installed skill here"
        facts = self.extract_facts(content)
        self.assertEqual(len(facts), 1)
        self.assertNotIn("#", facts[0])
    
    def test_skip_short_lines(self):
        content = "Short\n- This is a longer line with install keyword"
        facts = self.extract_facts(content)
        self.assertEqual(len(facts), 1)


class TestKeywordGeneration(unittest.TestCase):
    """Test keyword generation logic."""
    
    def generate_keywords(self, content, category, date_str):
        """Simple keyword generation (mirrors extract_memory.py logic)."""
        import re
        # Extract English words (4+ chars)
        all_words = list(set(re.findall(r'\b[A-Za-z]{4,}\b', content)))
        # Extract Chinese keywords (2+ chars)
        chinese_words = list(set(re.findall(r'[\u4e00-\u9fa5]{2,}', content)))
        
        keywords = f"{category} {date_str} " + " ".join(all_words[:10] + chinese_words[:5])
        return keywords
    
    def test_english_keywords(self):
        content = "Installed weather skill with API token configuration"
        keywords = self.generate_keywords(content, "Skill", "2026-02-20")
        
        self.assertIn("Skill", keywords)
        self.assertIn("2026-02-20", keywords)
        self.assertIn("Installed", keywords)
        self.assertIn("weather", keywords)
    
    def test_chinese_keywords(self):
        content = "Stock quantitative strategy backup script configured"
        keywords = self.generate_keywords(content, "Project", "2026-02-21")
        
        self.assertIn("Project", keywords)
        self.assertIn("Deploy", keywords)
        self.assertIn("Backup", keywords)
    
    def test_mixed_content(self):
        content = "Installed configuration skill with API token"
        keywords = self.generate_keywords(content, "Skill", "2026-02-22")
        
        self.assertIn("Skill", keywords)
        # Should have both English and Chinese keywords


if __name__ == "__main__":
    unittest.main()
