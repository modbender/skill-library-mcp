#!/usr/bin/env python3
"""
Test script for the unified authentication utility
"""

import os
import sys
import subprocess

def test_auth_utility():
    """Test the authentication utility"""
    print("🧪 Testing Authentication Utility")
    print("="*50)
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    auth_script = os.path.join(script_dir, "scripts", "auth_utility.py")
    
    if not os.path.exists(auth_script):
        print(f"❌ Authentication utility not found: {auth_script}")
        return False
    
    print(f"✅ Found authentication utility: {auth_script}")
    
    # Use virtual environment Python if available
    venv_python = os.path.join(script_dir, "venv", "bin", "python")
    if os.path.exists(venv_python):
        python_cmd = venv_python
        print(f"✅ Using virtual environment Python: {python_cmd}")
    else:
        python_cmd = sys.executable
        print(f"⚠️  Using system Python: {python_cmd}")
    
    # Test 1: Check status
    print("\n1. Testing --check option...")
    result = subprocess.run(
        [python_cmd, auth_script, "--check"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Status check successful")
        print(f"Output:\n{result.stdout}")
    else:
        print(f"❌ Status check failed: {result.stderr}")
    
    # Test 2: Test help
    print("\n2. Testing help option...")
    result = subprocess.run(
        [python_cmd, auth_script, "--help"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Help display successful")
        # Don't print full help output
    else:
        print(f"❌ Help display failed: {result.stderr}")
    
    # Test 3: Test script structure
    print("\n3. Testing script structure...")
    with open(auth_script, 'r') as f:
        content = f.read()
    
    required_classes = ['AuthUtility', 'main']
    missing_classes = []
    
    for class_name in required_classes:
        if class_name not in content:
            missing_classes.append(class_name)
    
    if not missing_classes:
        print("✅ Script structure valid")
    else:
        print(f"❌ Missing classes: {missing_classes}")
    
    # Test 4: Test imports (skip if virtual environment not activated)
    print("\n4. Testing imports...")
    if python_cmd == venv_python:
        try:
            # Try to import the module using subprocess
            test_import = f"""
import sys
sys.path.insert(0, '{os.path.join(script_dir, "scripts")}')
try:
    import auth_utility
    print('SUCCESS: Import successful')
    if hasattr(auth_utility, 'AuthUtility'):
        print('SUCCESS: AuthUtility class found')
    else:
        print('ERROR: AuthUtility class not found')
except ImportError as e:
    print(f'ERROR: {{e}}')
"""
            
            result = subprocess.run(
                [python_cmd, "-c", test_import],
                capture_output=True,
                text=True
            )
            
            if "SUCCESS" in result.stdout:
                print("✅ Imports successful")
                print(result.stdout.strip())
            else:
                print(f"❌ Import test failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Import test error: {e}")
    else:
        print("⚠️  Skipping import test (not using virtual environment)")
    
    print("\n" + "="*50)
    print("✅ Authentication utility tests completed")
    print("\n📋 Next steps:")
    print("1. Run: python scripts/auth_utility.py --check")
    print("2. If tokens expired: python scripts/auth_utility.py --auth")
    print("3. Test connection: python scripts/auth_utility.py --test")
    
    return True

if __name__ == "__main__":
    success = test_auth_utility()
    sys.exit(0 if success else 1)