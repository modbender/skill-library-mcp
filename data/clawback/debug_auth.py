#!/usr/bin/env python3
"""
Debug authentication to understand the exact flow
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from clawback.etrade_adapter import ETradeAdapter

def main():
    print("=== DEBUG AUTHENTICATION FLOW ===")
    
    # Load config
    config_path = os.path.expanduser('~/.clawback/config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print("\n1. Creating adapter instance...")
    adapter = ETradeAdapter(config)
    
    print(f"   Environment: {adapter.environment}")
    print(f"   API Key: {adapter.api_key[:10]}...")
    print(f"   Request token: {adapter.request_token}")
    print(f"   Request secret: {adapter.request_secret}")
    
    print("\n2. Calling get_auth_url()...")
    auth_url = adapter.get_auth_url()
    print(f"   Auth URL: {auth_url}")
    print(f"   Request token after: {adapter.request_token}")
    print(f"   Request secret after: {adapter.request_secret}")
    
    # Extract token from URL
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(auth_url)
    query_params = parse_qs(parsed.query)
    url_token = query_params.get('token', [''])[0]
    
    print(f"\n3. Token from URL: {url_token}")
    print(f"   Token in adapter: {adapter.request_token}")
    
    print("\n4. Checking if tokens match...")
    if url_token == adapter.request_token:
        print("   ✅ Tokens match!")
    else:
        print("   ❌ Tokens DON'T match!")
        print(f"   URL encoded: {url_token}")
        print(f"   Adapter raw: {adapter.request_token}")
        # Try decoding
        from urllib.parse import unquote
        decoded = unquote(url_token)
        print(f"   URL decoded: {decoded}")
        if decoded == adapter.request_token:
            print("   ✅ After decoding: Tokens match!")
        else:
            print("   ❌ Still don't match after decoding")
    
    print("\n5. Testing authentication with a dummy code...")
    try:
        # This should fail but show us the error
        result = adapter.authenticate("DUMMYCODE123")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== DEBUG COMPLETE ===")

if __name__ == "__main__":
    main()