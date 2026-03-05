#!/usr/bin/env python3
"""
Test the full authentication flow step by step
"""
import sys
import os
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from clawback.etrade_adapter import ETradeAdapter

def main():
    print("=== FULL AUTHENTICATION FLOW TEST ===")
    
    # Load config
    config_path = os.path.expanduser('~/.clawback/config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print("\n1. Creating adapter...")
    adapter = ETradeAdapter(config)
    
    print("\n2. Getting authorization URL...")
    auth_url = adapter.get_auth_url()
    if not auth_url:
        print("❌ Failed to get authorization URL")
        return False
    
    print(f"✅ URL: {auth_url}")
    print(f"   Request token: {adapter.request_token}")
    print(f"   Request secret: {adapter.request_secret}")
    
    print("\n" + "="*60)
    print("⚠️  MANUAL STEP REQUIRED:")
    print(f"1. Visit: {auth_url}")
    print("2. Authorize the application")
    print("3. Get the verification code")
    print("="*60)
    
    # Get verification code from user
    verifier_code = input("\nEnter verification code: ").strip()
    
    print(f"\n3. Attempting authentication with code: {verifier_code}")
    print(f"   Code length: {len(verifier_code)}")
    print(f"   Code looks like: {verifier_code}")
    
    # Try authentication
    start_time = time.time()
    result = adapter.authenticate(verifier_code)
    elapsed = time.time() - start_time
    
    print(f"\n4. Authentication result after {elapsed:.2f}s:")
    if result:
        print("✅ SUCCESS!")
        print(f"   Access token: {adapter.access_token[:30]}...")
        print(f"   Access secret: {adapter.access_secret[:30]}...")
        
        # Save tokens
        token_path = os.path.expanduser('~/.clawback/.access_tokens.json')
        tokens = {
            'access_token': adapter.access_token,
            'access_secret': adapter.access_secret
        }
        with open(token_path, 'w') as f:
            json.dump(tokens, f)
        print(f"✅ Tokens saved to {token_path}")
        
        # Test connection
        print("\n5. Testing connection...")
        try:
            accounts = adapter.get_accounts()
            if accounts:
                print(f"✅ Connected! Found {len(accounts)} account(s)")
                for acc in accounts:
                    print(f"   - {acc.get('accountId', 'Unknown')}: {acc.get('accountType', 'Unknown')}")
            else:
                print("⚠️  Connected but no accounts found")
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            
    else:
        print("❌ FAILED")
        print("   Possible issues:")
        print("   - Verification code incorrect")
        print("   - Authorization session expired")
        print("   - Token mismatch")
        print("   - E*TRADE API issue")
    
    return result

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)