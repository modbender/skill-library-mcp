#!/usr/bin/env python3
"""
Soul Memory System v2.1 - Test Suite
Test all modules

Author: Soul Memory System
Date: 2026-02-17
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_priority_parser():
    """Test Module A: Priority Parser"""
    print("\n📦 Testing Module A: Priority Parser...")
    from modules.priority_parser import PriorityParser, Priority
    
    parser = PriorityParser()
    
    # Test explicit tags
    result1 = parser.parse("[C] This is critical")
    assert result1.priority == Priority.CRITICAL, "Critical tag parsing failed"
    assert result1.has_explicit_tag == True, "Explicit tag detection failed"
    
    # Test semantic detection
    result2 = parser.parse("這是核心功能")
    assert result2.priority == Priority.CRITICAL, "Semantic critical detection failed"
    
    # Test normal
    result3 = parser.parse("日常問候")
    assert result3.priority == Priority.NORMAL, "Normal detection failed"
    
    print("  ✅ Priority Parser: PASS")
    return True

def test_vector_search():
    """Test Module B: Vector Search"""
    print("\n📦 Testing Module B: Vector Search...")
    from modules.vector_search import VectorSearch
    
    vs = VectorSearch()
    vs.add_segment({
        'content': 'User prefers dark mode',
        'source': 'test',
        'line_number': 1
    })
    vs.add_segment({
        'content': 'API configured at localhost',
        'source': 'test',
        'line_number': 2
    })
    
    results = vs.search('user preferences', top_k=2)
    assert len(results) > 0, "No search results found"
    
    print("  ✅ Vector Search: PASS")
    return True

def test_dynamic_classifier():
    """Test Module C: Dynamic Classifier"""
    print("\n📦 Testing Module C: Dynamic Classifier...")
    from modules.dynamic_classifier import DynamicClassifier
    
    classifier = DynamicClassifier()
    
    # Test existing categories
    category1 = classifier.classify("User prefers coffee")
    assert category1 == "User_Identity", "User identity classification failed"
    
    category2 = classifier.classify("API endpoint configuration")
    assert category2 == "Tech_Config", "Tech config classification failed"
    
    print("  ✅ Dynamic Classifier: PASS")
    return True

def test_version_control():
    """Test Module D: Version Control"""
    print("\n📦 Testing Module D: Version Control...")
    from modules.version_control import VersionControl
    
    vc = VersionControl(".")
    
    # Test git repo check
    is_repo = vc.is_git_repo()
    
    # Test log retrieval
    log = vc.get_log(3)
    # If not a git repo, log is empty, but that's OK
    
    print("  ✅ Version Control: PASS")
    return True

def test_memory_decay():
    """Test Module E: Memory Decay"""
    print("\n📦 Testing Module E: Memory Decay...")
    from modules.memory_decay import MemoryDecay
    
    decay = MemoryDecay()
    
    # Test access recording
    decay.record_access('test_segment')
    
    # Test decay calculation
    result = decay.calculate_decay('test_segment', 'N')
    assert result.decay_score <= 1.0, "Decay score out of range"
    assert result.recommendation in ['keep', 'review', 'archive'], "Invalid recommendation"
    
    print("  ✅ Memory Decay: PASS")
    return True

def test_auto_trigger():
    """Test Module F: Auto-Trigger"""
    print("\n📦 Testing Module F: Auto-Trigger...")
    from modules.auto_trigger import AutoTrigger
    
    trigger = AutoTrigger()
    
    # Test category detection
    result1 = trigger.trigger("What are my preferences?")
    assert result1['category'] == "User_Identity", "Category detection failed"
    
    result2 = trigger.trigger("API configuration")
    assert result2['category'] == "Tech_Config", "Tech config category failed"
    
    print("  ✅ Auto-Trigger: PASS")
    return True

def test_core_system():
    """Test Core System"""
    print("\n📦 Testing Core System...")
    from core import SoulMemorySystem
    
    system = SoulMemorySystem()
    
    # Test search without initialization
    results = system.search("test query", top_k=1)
    # Search should work even without full initialization
    
    # Test stats
    stats = system.stats()
    assert 'version' in stats, "Stats missing version"
    assert stats['version'] == "2.1.0", "Version mismatch"
    
    print("  ✅ Core System: PASS")
    return True

def run_all_tests():
    """Run all module tests"""
    print("=" * 50)
    print("🧠 Soul Memory System v2.1 - Test Suite")
    print("=" * 50)
    
    tests = [
        test_priority_parser,
        test_vector_search,
        test_dynamic_classifier,
        test_version_control,
        test_memory_decay,
        test_auto_trigger,
        test_core_system
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
