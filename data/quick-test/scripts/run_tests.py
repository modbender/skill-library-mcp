#!/usr/bin/env python3
"""
Quick test runner for OpenClaw system verification.
Usage: python3 run_tests.py
"""

import subprocess
import sys
from datetime import datetime, timezone

def run_command(cmd, description=""):
    """Run a command and return result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {
            'command': ' '.join(cmd),
            'description': description,
            'returncode': result.returncode,
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip()
        }
    except Exception as e:
        return {
            'command': ' '.join(cmd),
            'description': description,
            'returncode': -1,
            'stdout': '',
            'stderr': str(e)
        }

def main():
    print("🔍 Quick Test - OpenClaw System Verification")
    print("=" * 50)
    print(f"Started: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n")

    tests = []

    # Test 1: Python version
    tests.append(run_command(['python3', '--version'], 'Python version check'))
    
    # Test 2: Current directory
    tests.append(run_command(['pwd'], 'Current directory check'))
    
    # Test 3: Date
    tests.append(run_command(['date'], 'Date check'))
    
    # Test 4: Environment variables
    tests.append(run_command(['env', 'head -5'], 'Environment variables'))
    
    # Test 5: File system (ls)
    tests.append(run_command(['ls', '-la', '/home/zig/.openclaw/workspace/'], 'File system check'))
    
    # Test 6: Test file write
    tests.append(run_command(['echo', 'Quick test passed', '>', '/tmp/quick_test.txt'], 'File write test'))

    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Total tests: {len(tests)}")
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test['returncode'] == 0:
            print(f"✅ {test['description']}")
            print(f"   Command: {test['command']}")
            if test['stdout']:
                print(f"   Output: {test['stdout'][:100]}")
            passed += 1
        else:
            print(f"❌ {test['description']}")
            print(f"   Command: {test['command']}")
            print(f"   Error: {test['stderr'][:200]}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! System is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check system status.")

if __name__ == '__main__':
    main()
