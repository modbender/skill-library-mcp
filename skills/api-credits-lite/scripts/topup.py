#!/usr/bin/env python3
"""
Add credits to a provider (record a top-up).

Usage:
    topup.py <provider> <amount>

Example:
    topup.py anthropic 25
"""

import os
import json
import sys
from datetime import datetime

# Supported providers (lite version)
SUPPORTED_PROVIDERS = ['anthropic', 'openai', 'openrouter', 'mistral', 'groq']

def load_config():
    """Load config from the skill directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '..', 'config.json')
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'providers': {}, 'thresholds': {'warning': 50, 'critical': 25}}

def save_config(config):
    """Save config back to file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '..', 'config.json')
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

def topup(provider: str, amount: float):
    """
    Add credits to a provider.
    
    Args:
        provider: Provider name
        amount: Amount to add
    """
    config = load_config()
    provider_key = provider.lower().replace('-', '_')
    
    # Check if supported
    if provider_key not in SUPPORTED_PROVIDERS:
        print(f"❌ Provider '{provider}' not supported in lite version.")
        print(f"   Supported: {', '.join(SUPPORTED_PROVIDERS)}")
        sys.exit(1)
    
    if provider_key not in config.get('providers', {}):
        print(f"❌ Provider '{provider}' not configured. Run sync_provider.py first.")
        sys.exit(1)
    
    old_balance = config['providers'][provider_key].get('current_credits', 0)
    old_max = config['providers'][provider_key].get('max_credits', 0)
    
    new_balance = old_balance + amount
    new_max = old_max + amount  # Also increase max since we added credits
    
    config['providers'][provider_key]['current_credits'] = new_balance
    config['providers'][provider_key]['max_credits'] = new_max
    config['providers'][provider_key]['last_sync'] = datetime.now().astimezone().isoformat()
    
    save_config(config)
    
    print(f"✅ Added ${amount:.2f} to {provider}")
    print(f"   Old balance: ${old_balance:.2f} / ${old_max:.2f}")
    print(f"   New balance: ${new_balance:.2f} / ${new_max:.2f}")
    
    return {
        'status': 'topped_up',
        'provider': provider_key,
        'amount_added': amount,
        'old_balance': old_balance,
        'new_balance': new_balance,
        'new_max': new_max
    }

if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] in ['-h', '--help']:
        print("Usage: topup.py <provider> <amount>")
        print("\nSupported providers: anthropic, openai, openrouter, mistral, groq")
        print("\nExample:")
        print("  topup.py anthropic 25")
        sys.exit(0)
    
    provider = sys.argv[1]
    amount = float(sys.argv[2])
    
    topup(provider, amount)
