#!/usr/bin/env python3
"""
Simple authentication test
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from clawback.etrade_adapter import ETradeAdapter

def main():
    print("=== Simple Authentication Test ===")
    
    # Load config
    config_path = os.path.expanduser('~/.clawback/config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print(f"Config loaded from {config_path}")
    print(f"Environment: {config.get('broker', {}).get('environment', 'sandbox')}")
    
    # Create adapter
    adapter = ETradeAdapter(config)
    
    print("\n1. Testing get_auth_url()...")
    auth_url = adapter.get_auth_url()
    if auth_url:
        print(f"✅ Success! Auth URL: {auth_url}")
        print(f"   Request token: {adapter.request_token[:30]}...")
        print(f"   Request secret: {adapter.request_secret[:30]}...")
        
        # Save tokens for later use
        token_file = os.path.expanduser('~/.clawback/.test_tokens.json')
        tokens = {
            'request_token': adapter.request_token,
            'request_secret': adapter.request_secret
        }
        with open(token_file, 'w') as f:
            json.dump(tokens, f)
        print(f"✅ Tokens saved to {token_file}")
        
        print(f"\n📋 Please visit: {auth_url}")
        print("   Authorize and get verification code")
        
        # Get verification code
        verifier_code = input("\nEnter verification code: ").strip()
        
        print(f"\n2. Testing authenticate() with code: {verifier_code}")
        result = adapter.authenticate(verifier_code)
        
        if result:
            print("✅ Authentication successful!")
            print(f"   Access token: {adapter.access_token[:30]}...")
            print(f"   Access secret: {adapter.access_secret[:30]}...")
            
            # Save access tokens
            access_file = os.path.expanduser('~/.clawback/.access_tokens.json')
            access_tokens = {
                'access_token': adapter.access_token,
                'access_secret': adapter.access_secret
            }
            with open(access_file, 'w') as f:
                json.dump(access_tokens, f)
            print(f"✅ Access tokens saved to {access_file}")
            
            # Test connection
            print("\n3. Testing connection...")
            try:
                accounts = adapter.get_accounts()
                if accounts:
                    print(f"✅ Connected! Found {len(accounts)} account(s)")
                else:
                    print("⚠️  Connected but no accounts found")
            except Exception as e:
                print(f"❌ Connection test failed: {e}")
        else:
            print("❌ Authentication failed")
            print("   Possible issues:")
            print("   - Incorrect verification code")
            print("   - Authorization expired")
            print("   - Token mismatch")
    else:
        print("❌ Failed to get auth URL")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())