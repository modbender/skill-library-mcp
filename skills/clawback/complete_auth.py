#!/usr/bin/env python3
"""
Complete E*TRADE OAuth authentication with verification code
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from clawback.etrade_adapter import ETradeAdapter
import json

def main():
    # Load config
    config_path = os.path.expanduser('~/.clawback/config.json')
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        return 1
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print("🔧 Loading E*TRADE configuration...")
    
    # Create adapter
    adapter = ETradeAdapter(config)
    
    # Check if we need to complete OAuth
    print("\n📋 Current authentication status:")
    
    # Check for existing tokens
    token_file = os.path.expanduser('~/.clawback/.access_tokens.json')
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            tokens = json.load(f)
        
        if 'access_token' in tokens:
            print("✅ Access token already exists")
            print(f"   Token: {tokens['access_token'][:30]}...")
            print(f"   Expires: {tokens.get('expires_at', 'Unknown')}")
            return 0
    
    print("❌ No access token found")
    print("\n🔐 To complete authentication, we need to:")
    print("1. Generate an authorization URL")
    print("2. You visit that URL and authorize")
    print("3. You get a verification code")
    print("4. We exchange the code for tokens")
    
    print(f"\n📝 You provided verification code: Y1XL9")
    
    # Try to use the verification code
    print("\n🔄 Attempting to exchange verification code for tokens...")
    
    # Note: The actual implementation would call adapter.complete_oauth(verification_code)
    # But we need to see how the adapter is implemented
    
    print("\n⚠️  This script needs to be completed with the actual OAuth flow")
    print("   The verification code Y1XL9 should be used in the OAuth callback")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())