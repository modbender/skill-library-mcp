#!/usr/bin/env python3
"""
WhatsApp Intelligent Context Manager - Installation Verification
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
        'whatsapp_context_manager.py',
        'examples_whatsapp.py',
        'test_whatsapp.py',
        'README_WHATSAPP.md',
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
        from whatsapp_context_manager import (
            ContextManager, Order, Customer, Message,
            MessagePriority, CustomerSentiment, MessageCategory
        )
        print("✅ Module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import module: {e}")
        return False

def run_quick_test():
    """Run a quick functionality test"""
    print("\nRunning quick functionality test...")
    try:
        from whatsapp_context_manager import ContextManager
        import os
        
        # Create test database
        test_db = "install_check_test.db"
        manager = ContextManager(test_db)
        
        # Process a test message
        context = manager.process_incoming_message(
            phone="+1234567890",
            message_content="Hello, this is a test",
            agent_id="test_agent"
        )
        
        # Verify context was created
        assert context is not None
        assert context.customer.phone == "+1234567890"
        assert context.sentiment is not None
        assert context.priority is not None
        
        # Clean up
        if os.path.exists(test_db):
            os.remove(test_db)
        
        print("✅ Quick functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        # Clean up on failure
        test_db = "install_check_test.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        return False

def main():
    """Main installation check"""
    print("="*60)
    print("WHATSAPP INTELLIGENT CONTEXT MANAGER")
    print("Installation Verification")
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
        print("  1. Run: python test_whatsapp.py")
        print("  2. Run: python examples_whatsapp.py")
        print("  3. Read: README_WHATSAPP.md")
        print("  4. Start integrating with your WhatsApp system!")
    else:
        print("❌ INSTALLATION INCOMPLETE")
        print("\nPlease ensure all files are present and Python 3.8+ is installed.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
