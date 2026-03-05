#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Self-Healing Skill - Usage Examples
"""

from openclaw_memory import OpenClawMemory


def example_1_basic_diagnosis():
    """Example 1: Basic problem diagnosis"""
    print("Example 1: Basic Diagnosis")
    print("-" * 60)
    
    memory = OpenClawMemory()
    
    # Simulate a gateway error
    result = memory.diagnose_and_fix(
        error_text="Gateway service crashed and cannot start",
        error_logs="Error: Gateway process exited with code 1"
    )
    
    print(f"Fixed: {result['fixed']}")
    print(f"Problem Type: {result['problem_type']}")
    print(f"Report: {result['report_file']}")
    print(f"BAT Files: {result['bat_files']}")
    print()


def example_2_search_case():
    """Example 2: Search repair case library"""
    print("Example 2: Search Case Library")
    print("-" * 60)
    
    memory = OpenClawMemory()
    
    # Search for memory-related issues
    case = memory.search_case_library("memory search function broken")
    
    if case:
        print(f"Found Case: {case['title']}")
        print(f"Solution: {case['solution'][:100]}...")
    else:
        print("No matching case found")
    print()


def example_3_add_record():
    """Example 3: Add repair record"""
    print("Example 3: Add Repair Record")
    print("-" * 60)
    
    memory = OpenClawMemory()
    
    # Add a successful repair record
    result = memory.add_record(
        error_text="Custom error that was fixed",
        solution="Ran openclaw gateway restart",
        success=True,
        error_code="CUSTOM_001"
    )
    
    print(f"Record added: {result['added']}")
    print(f"Updated: {result['updated']}")
    print(f"Signature: {result['signature']}")
    print()


def example_4_list_all_cases():
    """Example 4: List all repair cases"""
    print("Example 4: All Repair Cases")
    print("-" * 60)
    
    memory = OpenClawMemory()
    
    for case in memory.cases.get("cases", []):
        print(f"[{case['id']}] {case['title']}")
        print(f"   Success Rate: {case.get('success_rate', 'N/A')}")
        print(f"   Keywords: {', '.join(case.get('keywords', []))}")
        print()


def example_5_different_problem_types():
    """Example 5: Test different problem types"""
    print("Example 5: Problem Type Classification")
    print("-" * 60)
    
    memory = OpenClawMemory()
    
    test_cases = [
        "Memory search is not working",
        "Gateway service failed to start",
        "API rate limit exceeded error 429",
        "Configuration file corrupted",
        "Permission denied when accessing files"
    ]
    
    for error in test_cases:
        problem_type = memory._classify_problem(error)
        print(f"Error: {error[:40]}...")
        print(f"  → Type: {problem_type}")
        print()


if __name__ == "__main__":
    print("=" * 60)
    print("OpenClaw Self-Healing Skill - Usage Examples")
    print("=" * 60)
    print()
    
    # Run examples
    example_2_search_case()
    example_5_different_problem_types()
    example_4_list_all_cases()
    
    print("=" * 60)
    print("Examples completed!")
    print("=" * 60)
