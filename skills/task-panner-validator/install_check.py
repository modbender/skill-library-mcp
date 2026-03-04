#!/usr/bin/env python3
"""
Task Planner and Validator - Installation Verification Script
Run this after installation to verify everything works correctly.
"""

import sys
import os

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.8+")
        return False

def check_files():
    """Check if all required files exist"""
    print("\nChecking required files...")
    required_files = [
        'task_planner.py',
        'examples.py',
        'test_basic.py',
        'README.md',
        'QUICKSTART.md',
        'API.md',
        'SKILL.md',
        'LICENSE'
    ]
    
    missing_files = []
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✅ {filename}")
        else:
            print(f"❌ {filename} - MISSING")
            missing_files.append(filename)
    
    return len(missing_files) == 0

def test_import():
    """Test if the module can be imported"""
    print("\nTesting module import...")
    try:
        from task_planner import TaskPlanner, TaskStatus, StepStatus
        print("✅ Module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import module: {e}")
        return False

def run_quick_test():
    """Run a quick functionality test"""
    print("\nRunning quick functionality test...")
    try:
        from task_planner import TaskPlanner
        
        # Create a simple plan
        planner = TaskPlanner()
        steps = [{
            "description": "Test step",
            "action": "test_action",
            "parameters": {"test": True},
            "expected_output": "Test output"
        }]
        
        plan = planner.create_plan("Test Plan", "Testing", steps)
        
        # Validate
        is_valid, warnings = planner.validate_plan(plan)
        
        if is_valid:
            print("✅ Basic functionality test passed")
            return True
        else:
            print("❌ Basic functionality test failed")
            return False
            
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

def main():
    """Main installation check"""
    print("="*60)
    print("TASK PLANNER AND VALIDATOR - Installation Check")
    print("="*60 + "\n")
    
    checks = [
        check_python_version(),
        check_files(),
        test_import(),
        run_quick_test()
    ]
    
    print("\n" + "="*60)
    if all(checks):
        print("✅ INSTALLATION SUCCESSFUL!")
        print("\nNext steps:")
        print("  1. Read QUICKSTART.md to get started")
        print("  2. Run: python examples.py")
        print("  3. Run: python test_basic.py")
        print("  4. Check README.md for full documentation")
    else:
        print("❌ INSTALLATION INCOMPLETE")
        print("\nPlease ensure all files are present and Python 3.8+ is installed.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
