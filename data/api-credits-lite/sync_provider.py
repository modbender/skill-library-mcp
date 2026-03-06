#!/usr/bin/env python3
"""
Manual sync for 5 core providers.
Use to update balance from provider console.

Usage:
    sync_provider.py <provider> <current_balance> [max_credits]

Examples:
    sync_provider.py anthropic 45.00
    sync_provider.py openai 95.00 100.00
"""

import os
import json
import sys
from datetime import datetime

# Supported providers (lite version)
PROVIDER_INFO = {
    'anthropic': {
        'console_url': 'https://console.anthropic.com',
        'notes': 'Check console.anthropic.com → Settings → Billing for current balance'
    },
    'openai': {
        'console_url': 'https://platform.openai.com/usage',
        'notes': 'Check platform.openai.com/usage for balance and usage'
    },
    'openrouter': {
        'console_url': 'https://openrouter.ai/activity',
        'notes': 'Check openrouter.ai/activity for current credits'
    },
    'mistral': {
        'console_url': 'https://console.mistral.ai/billing',
        'notes': 'Check console.mistral.ai → Billing for current balance'
    },
    'groq': {
        'console_url': 'https://console.groq.com/settings/billing',
        'notes': 'Check console.groq.com → Settings → Billing for usage'
    }
}

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

def sync_balance(provider: str, current_balance: float, max_credits: float = None):
    """
    Sync balance for a provider.
    
    Args:
        provider: Provider name (e.g., 'anthropic', 'openai')
        current_balance: Current balance from console
        max_credits: Optional max credits (creates if not exists)
    """
    config = load_config()
    
    # Normalize provider name
    provider_key = provider.lower().replace('-', '_')
    
    # Check if supported
    if provider_key not in PROVIDER_INFO:
        print(f"❌ Provider '{provider}' not supported in lite version.")
        print(f"   Supported: {', '.join(PROVIDER_INFO.keys())}")
        print(f"   Upgrade to Pro for 16+ providers.")
        sys.exit(1)
    
    info = PROVIDER_INFO[provider_key]
    
    # Check if provider exists in config
    if provider_key not in config.get('providers', {}):
        config.setdefault('providers', {})
        config['providers'][provider_key] = {
            'enabled': True,
            'max_credits': max_credits or current_balance,
            'current_credits': current_balance,
            'last_sync': datetime.now().astimezone().isoformat(),
            'notes': info.get('notes', f'Manual sync - check {provider} console')
        }
    else:
        config['providers'][provider_key]['current_credits'] = current_balance
        config['providers'][provider_key]['last_sync'] = datetime.now().astimezone().isoformat()
        config['providers'][provider_key]['enabled'] = True
        
        if max_credits:
            config['providers'][provider_key]['max_credits'] = max_credits
    
    save_config(config)
    
    result = {
        'status': 'synced',
        'provider': provider_key,
        'current_credits': current_balance,
        'max_credits': config['providers'][provider_key].get('max_credits'),
        'last_sync': config['providers'][provider_key]['last_sync'],
        'console_url': info['console_url']
    }
    
    return result

def list_providers():
    """List all supported providers with their console URLs."""
    print("Supported providers (Lite version):\n")
    for provider, info in sorted(PROVIDER_INFO.items()):
        print(f"  {provider}")
        print(f"    Console: {info.get('console_url', 'N/A')}")
        print(f"    Notes: {info.get('notes', 'N/A')}")
        print()
    print("\n💡 Need more providers? Upgrade to api-credits-pro")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print("Usage: sync_provider.py <provider> <current_balance> [max_credits]")
        print("       sync_provider.py --list")
        print("\nSupported providers: anthropic, openai, openrouter, mistral, groq")
        print("\nExamples:")
        print("  sync_provider.py anthropic 45.00")
        print("  sync_provider.py openai 85.00 100.00")
        print("\nUse --list to see all providers and their console URLs.")
        sys.exit(0)
    
    if sys.argv[1] == '--list':
        list_providers()
        sys.exit(0)
    
    if len(sys.argv) < 3:
        print("Error: Both provider and balance are required")
        print("Usage: sync_provider.py <provider> <current_balance> [max_credits]")
        sys.exit(1)
    
    provider = sys.argv[1]
    balance = float(sys.argv[2])
    max_credits = float(sys.argv[3]) if len(sys.argv) > 3 else None
    
    result = sync_balance(provider, balance, max_credits)
    print(json.dumps(result, indent=2))
