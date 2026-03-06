#!/usr/bin/env python3
"""🧠 Configuration loader for Intrusive Thoughts."""

import json
import os
from pathlib import Path

# Get the directory where this script is located
BASE_DIR = Path(__file__).parent

def load_config():
    """Load configuration with fallback to example config."""
    config_file = BASE_DIR / "config.json"
    example_config_file = BASE_DIR / "config.example.json"
    
    if config_file.exists():
        try:
            with open(config_file) as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config.json: {e}")
            print("Falling back to config.example.json")
    
    # Fallback to example config
    if example_config_file.exists():
        try:
            with open(example_config_file) as f:
                config = json.load(f)
                print("⚠️  Using config.example.json - copy to config.json and customize!")
                return config
        except Exception as e:
            print(f"Error loading config.example.json: {e}")
    
    # Last resort - minimal config
    print("⚠️  No config found! Using minimal defaults.")
    return {
        "human": {"name": "Human", "timezone": "UTC"},
        "agent": {"name": "Agent", "emoji": "🤖"},
        "system": {"data_dir": str(BASE_DIR), "dashboard_port": 3117},
        "integrations": {"moltbook": {"enabled": False}, "telegram": {"enabled": False}}
    }

def get_data_dir():
    """Get the data directory path, expanding ~ if needed."""
    config = load_config()
    data_dir = Path(config["system"]["data_dir"]).expanduser()
    return data_dir

def get_file_path(filename):
    """Get full path to a data file."""
    return get_data_dir() / filename

# Global config instance
CONFIG = load_config()

def get(key_path, default=None):
    """Get config value using dot notation (e.g., 'human.name')."""
    try:
        keys = key_path.split('.')
        value = CONFIG
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default

def get_human_name():
    """Get the human's name."""
    return get('human.name', 'Human')

def get_agent_name():
    """Get the agent's name.""" 
    return get('agent.name', 'Agent')

def get_agent_emoji():
    """Get the agent's emoji."""
    return get('agent.emoji', '🤖')

def get_telegram_target():
    """Get Telegram target username."""
    return get('human.telegram_target', '@human')

def get_dashboard_port():
    """Get dashboard port."""
    return get('system.dashboard_port', 3117)

def is_integration_enabled(integration):
    """Check if an integration is enabled."""
    return get(f'integrations.{integration}.enabled', False)

def get_timezone():
    """Get the timezone."""
    return get('human.timezone', 'UTC')

if __name__ == "__main__":
    # Test config loading
    print("🧠 Intrusive Thoughts Configuration Test")
    print("=" * 40)
    print(f"Human: {get_human_name()}")
    print(f"Agent: {get_agent_name()} {get_agent_emoji()}")
    print(f"Data dir: {get_data_dir()}")
    print(f"Telegram target: {get_telegram_target()}")
    print(f"Dashboard port: {get_dashboard_port()}")
    print(f"Moltbook enabled: {is_integration_enabled('moltbook')}")
    print(f"Telegram enabled: {is_integration_enabled('telegram')}")
    print("\nConfig keys available:")
    def print_keys(obj, prefix=""):
        for key, value in obj.items():
            if isinstance(value, dict):
                print_keys(value, f"{prefix}{key}.")
            else:
                print(f"  {prefix}{key}")
    print_keys(CONFIG)