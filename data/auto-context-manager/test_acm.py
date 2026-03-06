#!/usr/bin/env python3
"""Test suite for Auto Context Manager"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from auto_context_manager import AutoContextManager
import json

def test_init():
    """Test initialization"""
    acm = AutoContextManager()
    assert acm.data_dir.exists(), "Data directory should exist"
    assert acm.projects_file.exists(), "Projects file should exist"
    print("[PASS] test_init")

def test_load_projects():
    """Test loading projects"""
    acm = AutoContextManager()
    projects = acm.load_projects()
    assert "projects" in projects, "Should have projects key"
    assert "current_project" in projects, "Should have current_project key"
    assert "default" in projects["projects"], "Should have default project"
    print("[PASS] test_load_projects")

def test_detect_project():
    """Test project detection"""
    acm = AutoContextManager()

    # Test default keywords
    proj, conf = acm.detect_project("hello there")
    assert proj == "default", f"Expected 'default', got '{proj}'"

    # Test help keyword
    proj, conf = acm.detect_project("I need help with something")
    assert proj == "default", f"Expected 'default', got '{proj}'"

    # Test status keyword
    proj, conf = acm.detect_project("check status please")
    assert proj == "default", f"Expected 'default', got '{proj}'"

    # Test no match - should return default
    proj, conf = acm.detect_project("xyz random message abc")
    assert proj == "default", f"Expected 'default' for unknown, got '{proj}'"

    print("[PASS] test_detect_project")

def test_switch_project():
    """Test project switching"""
    acm = AutoContextManager()

    # Create a test project first
    acm.create_project("test-proj", "Test Project", ["test"], "A test")

    result = acm.switch_project("test-proj")
    assert "test-proj" in result, f"Switch message should mention 'test-proj'"

    current = acm.get_current_project()
    assert current == "test-proj", f"Current should be 'test-proj', got '{current}'"

    # Switch back to default
    acm.switch_project("default")
    print("[PASS] test_switch_project")

def test_list_projects():
    """Test listing projects"""
    acm = AutoContextManager()
    output = acm.list_projects()

    assert "Available Projects" in output, "Should have header"
    assert "default" in output, "Should list default project"
    print("[PASS] test_list_projects")

def test_cli():
    """Test CLI wrapper"""
    import subprocess
    os.chdir(os.path.dirname(__file__))

    # Test detect with default project
    result = subprocess.run(
        [sys.executable, "acm.py", "detect", "hello world"],
        capture_output=True, text=True, encoding='utf-8'
    )
    assert result.returncode == 0, f"CLI detect failed: {result.stderr}"
    assert "default" in result.stdout, f"Expected 'default' in output: {result.stdout}"

    # Test list
    result = subprocess.run(
        [sys.executable, "acm.py", "list"],
        capture_output=True, text=True, encoding='utf-8'
    )
    assert result.returncode == 0, f"CLI list failed: {result.stderr}"

    # Test current
    result = subprocess.run(
        [sys.executable, "acm.py", "current"],
        capture_output=True, text=True, encoding='utf-8'
    )
    assert result.returncode == 0, f"CLI current failed: {result.stderr}"

    print("[PASS] test_cli")

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("Auto Context Manager - Test Suite")
    print("=" * 50)
    print()

    tests = [
        test_init,
        test_load_projects,
        test_detect_project,
        test_switch_project,
        test_list_projects,
        test_cli,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test.__name__}: {e}")
            failed += 1

    print()
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)