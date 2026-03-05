#!/usr/bin/env python3
"""
Test script to verify the trading bot setup
"""
import os
import sys
import json

def test_config():
    """Test configuration file"""
    print("Testing configuration...")

    config_path = 'config/config.json'

    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        return False

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Check required fields
        required = ['broker', 'trading', 'congress', 'logging']
        for field in required:
            if field not in config:
                print(f"❌ Missing config section: {field}")
                return False

        # Check broker adapter
        broker = config.get('broker', {})
        adapter = broker.get('adapter', '')
        if adapter:
            print(f"✅ Broker adapter: {adapter}")
        else:
            print("❌ No broker adapter specified")
            return False

        # Check credentials
        creds = broker.get('credentials', {})
        if creds.get('apiKey'):
            print("✅ API key found")
        else:
            print("⚠️  API key not set")

        print("✅ Configuration test passed")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing config: {e}")
        return False

def test_directories():
    """Test required directories"""
    print("\nTesting directories...")
    
    required_dirs = ['config', 'logs', 'src']
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ Directory exists: {dir_name}")
        else:
            print(f"❌ Directory missing: {dir_name}")
            return False
    
    return True

def test_python_modules():
    """Test Python module imports"""
    print("\nTesting Python modules...")
    
    modules = [
        'requests',
        'requests_oauthlib',
        'pandas',
        'schedule',
        'bs4'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ Module available: {module}")
        except ImportError:
            print(f"❌ Module missing: {module}")
            all_ok = False
    
    return all_ok

def test_source_files():
    """Test source code files"""
    print("\nTesting source files...")

    source_files = [
        'src/broker_adapter.py',
        'src/etrade_adapter.py',
        'src/congress_tracker.py',
        'src/trade_engine.py',
        'src/main.py',
        'src/requirements.txt'
    ]

    all_ok = True
    for file_path in source_files:
        if os.path.exists(file_path):
            print(f"✅ Source file exists: {file_path}")
        else:
            print(f"❌ Source file missing: {file_path}")
            all_ok = False

    return all_ok

def test_broker_credentials():
    """Test if broker credentials are configured"""
    print("\nTesting broker credentials...")

    config_path = 'config/config.json'

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        broker = config.get('broker', {})
        creds = broker.get('credentials', {})

        api_key = creds.get('apiKey', '')
        api_secret = creds.get('apiSecret', '')

        if api_key and not api_key.startswith('${'):
            print("✅ API key configured")
        elif api_key.startswith('${'):
            print("⚠️  API key uses environment variable placeholder")
        else:
            print("❌ No API key configured")
            return False

        if api_secret and not api_secret.startswith('${'):
            print("✅ API secret configured")
        elif api_secret.startswith('${'):
            print("⚠️  API secret uses environment variable placeholder")
        else:
            print("❌ No API secret configured")
            return False

        return True

    except Exception as e:
        print(f"❌ Error testing broker credentials: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("ClawBack - Congressional Trade Mirror - Setup Test")
    print("="*60)
    
    tests = [
        ("Configuration", test_config),
        ("Directories", test_directories),
        ("Python Modules", test_python_modules),
        ("Source Files", test_source_files),
        ("Broker Credentials", test_broker_credentials)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary:")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Setup is complete.")
        print("\nNext steps:")
        print("1. Run: python src/main.py auth")
        print("2. Follow authentication prompts")
        print("3. Test with: python src/main.py interactive")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please fix issues before proceeding.")
    
    print("="*60)

if __name__ == "__main__":
    main()