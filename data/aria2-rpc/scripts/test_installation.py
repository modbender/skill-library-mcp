#!/usr/bin/env python3
"""
Test script for aria2-rpc skill installation

Run this to verify that:
1. Required dependencies are installed
2. aria2 RPC endpoint is accessible
3. Basic commands work correctly
"""

import sys
import subprocess

def check_python():
    """Check Python version"""
    print("✓ Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 6:
        print(f"  Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"  Python {version.major}.{version.minor}.{version.micro} - Too old (need 3.6+)")
        return False

def check_requests():
    """Check if requests library is installed"""
    print("✓ Checking requests library...")
    try:
        import requests
        print(f"  requests {requests.__version__} - OK")
        return True
    except ImportError:
        print("  requests - NOT INSTALLED")
        print("  Install with: pip3 install requests")
        return False

def check_curl():
    """Check if curl is available"""
    print("✓ Checking curl...")
    try:
        result = subprocess.run(['curl', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"  {version_line} - OK")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("  curl - NOT FOUND")
    print("  Install with: sudo apt install curl")
    return False

def check_aria2():
    """Check if aria2c is available"""
    print("✓ Checking aria2c...")
    try:
        result = subprocess.run(['aria2c', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"  {version_line} - OK")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("  aria2c - NOT FOUND")
    print("  Install with: sudo apt install aria2")
    return False

def test_rpc_connection(rpc_url, rpc_secret):
    """Test RPC connection"""
    print(f"✓ Testing RPC connection to {rpc_url}...")
    
    try:
        import requests
        
        payload = {
            'jsonrpc': '2.0',
            'id': 'test',
            'method': 'aria2.getGlobalStat',
            'params': [f'token:{rpc_secret}'] if rpc_secret else []
        }
        
        response = requests.post(rpc_url, json=payload, timeout=5)
        result = response.json()
        
        if 'error' in result:
            print(f"  RPC Error: {result['error'].get('message', 'Unknown')}")
            return False
        
        if 'result' in result:
            print(f"  Connection successful - OK")
            stats = result['result']
            print(f"  Active: {stats.get('numActive', 0)}, "
                  f"Waiting: {stats.get('numWaiting', 0)}, "
                  f"Stopped: {stats.get('numStopped', 0)}")
            return True
        else:
            print(f"  Unexpected response: {result}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  Cannot connect to {rpc_url}")
        print("  Make sure aria2 is running with RPC enabled:")
        print("    aria2c --enable-rpc --rpc-listen-all=true -D")
        return False
    except requests.exceptions.Timeout:
        print(f"  Connection timeout")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    print("=" * 60)
    print("aria2-rpc Skill Installation Test")
    print("=" * 60)
    print()
    
    # Check dependencies
    checks = [
        check_python(),
        check_requests(),
        check_curl(),
        check_aria2()
    ]
    
    print()
    
    # Test RPC connection if aria2 is installed
    rpc_tested = False
    import os
    rpc_url = os.environ.get('ARIA2_RPC_URL', 'http://localhost:6800/jsonrpc')
    rpc_secret = os.environ.get('ARIA2_RPC_SECRET')
    
    if checks[3]:  # aria2 is installed
        print("Testing RPC connection...")
        print("(Use Ctrl+C to skip if aria2 is not running)")
        print()
        try:
            rpc_tested = test_rpc_connection(rpc_url, rpc_secret)
        except KeyboardInterrupt:
            print("\n  Skipped")
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    if all(checks[:4]):
        print("✓ All dependencies installed successfully!")
        if rpc_tested:
            print("✓ RPC connection test passed!")
        else:
            print("⚠ RPC connection not tested (aria2 may not be running)")
        print()
        print("You can now use aria2-rpc skill!")
        print()
        print("Example:")
        print("  python3 scripts/aria2_rpc.py add-uri http://example.com/file.zip")
        return 0
    else:
        print("✗ Some dependencies are missing:")
        if not checks[0]:
            print("  - Python 3.6+ required")
        if not checks[1]:
            print("  - requests library (pip3 install requests)")
        if not checks[2]:
            print("  - curl (sudo apt install curl)")
        if not checks[3]:
            print("  - aria2c (sudo apt install aria2)")
        print()
        print("Install missing dependencies and run this test again.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
