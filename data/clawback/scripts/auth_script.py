#!/usr/bin/env python3
"""
Simple script to authenticate with E*TRADE for ClawBack
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from clawback.etrade_adapter import ETradeAdapter
import json

# Load config
config_path = os.path.expanduser('~/.clawback/config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

# Initialize adapter
adapter = ETradeAdapter(config)

print("🔐 Starting E*TRADE Authentication")
print("=" * 50)

# Get authorization URL
auth_url = adapter.get_auth_url()
if not auth_url:
    print("❌ Failed to get authorization URL")
    sys.exit(1)

print(f"\n✅ Authorization URL generated!")
print(f"\n📋 Please visit this URL in your browser:")
print(f"\n{auth_url}")
print(f"\n🔗 Or click: {auth_url}")
print("\n" + "=" * 50)
print("\n📝 After authorizing, you'll get a verification code.")
print("Enter the verification code below:")

# Get verification code
verifier_code = input("Verification code: ").strip()

# Complete authentication
if adapter.authenticate(verifier_code):
    print("\n✅ Authentication successful!")
    print("🎉 You can now use ClawBack with E*TRADE")
else:
    print("\n❌ Authentication failed")
    print("Please check your verification code and try again")