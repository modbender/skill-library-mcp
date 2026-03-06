#!/usr/bin/env python3
"""
Simple, fast credit display - just reads config and shows health bars.
No complex processing, designed for quick viewing.
"""

import json
import os
import sys
from datetime import datetime
from render_healthbar import format_credits

# Supported providers in lite version
SUPPORTED_PROVIDERS = ['anthropic', 'openai', 'openrouter', 'mistral', 'groq']

def show_credits():
    """Read config and display all enabled providers."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '..', 'config.json')
    
    if not os.path.exists(config_path):
        print("⚠️ No config.json found. Copy config.example.json and edit it.")
        return 1
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print('💰 API Credit Health')
    print('━━━━━━━━━━━━━━━━━━━━━')
    print()
    
    warnings = []
    thresholds = config.get('thresholds', {'warning': 50, 'critical': 25})
    
    # Show each enabled provider (lite version: 5 core providers only)
    for provider_name, provider_config in config['providers'].items():
        if provider_name.lower() not in SUPPORTED_PROVIDERS:
            continue
        
        if not provider_config.get('enabled', False):
            continue
        
        provider_display = provider_name.title()
        current = provider_config.get('current_credits', provider_config['max_credits'])
        max_credits = provider_config['max_credits']
        last_sync = provider_config.get('last_sync')
        
        # Format last sync time
        sync_str = None
        if last_sync:
            try:
                sync_time = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
                now = datetime.now(sync_time.tzinfo)
                diff = now - sync_time
                
                if diff.total_seconds() < 60:
                    sync_str = 'just now'
                elif diff.total_seconds() < 3600:
                    mins = int(diff.total_seconds() / 60)
                    sync_str = f'{mins}m ago'
                elif diff.total_seconds() < 86400:
                    hours = int(diff.total_seconds() / 3600)
                    sync_str = f'{hours}h ago'
                else:
                    days = int(diff.total_seconds() / 86400)
                    sync_str = f'{days}d ago'
            except:
                sync_str = 'recently'
        
        print(format_credits(provider_display, current, max_credits, last_sync=sync_str))
        print()
        
        # Check thresholds
        pct = (current / max_credits * 100) if max_credits > 0 else 0
        if pct <= thresholds['critical']:
            warnings.append(f'🚨 {provider_display} is critical!')
        elif pct <= thresholds['warning']:
            warnings.append(f'⚠️ {provider_display} is low')
    
    # Show warnings
    if warnings:
        print('━━━━━━━━━━━━━━━━━━━━━')
        for w in warnings:
            print(w)
    
    return 0

if __name__ == "__main__":
    sys.exit(show_credits())
