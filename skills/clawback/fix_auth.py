#!/usr/bin/env python3
"""
Fixed authentication script for ClawBack
This script maintains token state between URL generation and code entry
"""
import sys
import os
import json
import pickle
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from clawback.etrade_adapter import ETradeAdapter

# Token storage file
TOKEN_STORE = os.path.expanduser('~/.clawback/.auth_tokens.pkl')

def save_tokens(adapter):
    """Save request tokens for later use"""
    tokens = {
        'request_token': adapter.request_token,
        'request_secret': adapter.request_secret,
        'api_key': adapter.api_key,
        'api_secret': adapter.api_secret,
        'environment': adapter.environment
    }
    with open(TOKEN_STORE, 'wb') as f:
        pickle.dump(tokens, f)
    print(f"✅ Tokens saved to {TOKEN_STORE}")

def load_tokens():
    """Load saved tokens"""
    if os.path.exists(TOKEN_STORE):
        with open(TOKEN_STORE, 'rb') as f:
            return pickle.load(f)
    return None

def main():
    print("🔐 FIXED E*TRADE Authentication")
    print("=" * 50)
    
    # Load config
    config_path = os.path.expanduser('~/.clawback/config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Check if we have saved tokens
    saved_tokens = load_tokens()
    
    if saved_tokens:
        print("\n📋 Found saved authentication session")
        print(f"   Request token: {saved_tokens['request_token'][:20]}...")
        print(f"   Environment: {saved_tokens['environment']}")
        
        use_saved = input("\nUse saved tokens? (y/n): ").strip().lower()
        if use_saved == 'y':
            # Create adapter with saved tokens
            adapter = ETradeAdapter(config)
            adapter.request_token = saved_tokens['request_token']
            adapter.request_secret = saved_tokens['request_secret']
            
            # Get verification code
            verifier_code = input("\nEnter verification code: ").strip()
            
            print(f"\n🔐 Attempting authentication with saved tokens...")
            if adapter.authenticate(verifier_code):
                print("✅ Authentication successful!")
                os.remove(TOKEN_STORE)  # Clean up
                return True
            else:
                print("❌ Authentication failed with saved tokens")
                print("   Generating new authorization URL...")
                # Continue to generate new URL
    
    # Generate new authorization URL
    print("\n🔄 Generating new authorization URL...")
    adapter = ETradeAdapter(config)
    auth_url = adapter.get_auth_url()
    
    if not auth_url:
        print("❌ Failed to get authorization URL")
        return False
    
    print(f"\n✅ Authorization URL generated!")
    print(f"\n📋 Please visit this URL in your browser:")
    print(f"\n{auth_url}")
    print(f"\n🔗 Or click: {auth_url}")
    
    # Save tokens for later use
    save_tokens(adapter)
    
    print("\n" + "=" * 50)
    print("\n📝 After authorizing, you'll get a verification code.")
    print("⚠️  IMPORTANT: Use this SAME script to enter the code!")
    print("   Run: python fix_auth.py")
    
    # Option to enter code now
    enter_now = input("\nEnter code now? (y/n): ").strip().lower()
    if enter_now == 'y':
        verifier_code = input("Verification code: ").strip()
        
        print(f"\n🔐 Attempting authentication...")
        if adapter.authenticate(verifier_code):
            print("✅ Authentication successful!")
            os.remove(TOKEN_STORE)  # Clean up
            return True
        else:
            print("❌ Authentication failed")
            print("   The code may be incorrect or expired.")
            print("   You can try again with: python fix_auth.py")
            return False
    else:
        print("\n📋 To complete authentication later:")
        print("   1. Visit the URL above and authorize")
        print("   2. Get the verification code")
        print("   3. Run: python fix_auth.py")
        print("   4. Enter the code when prompted")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Authentication cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)