#!/usr/bin/env python3
import json
import sys
import os
from pathlib import Path

CONFIG_FILE = Path(__file__).parent.parent / "config" / "models.json"
EXAMPLE_CONFIG = Path(__file__).parent.parent / "config" / "models.example.json"

class ConfigManager:
    @staticmethod
    def get_default_model():
        """Get a sensible default model, checking common env vars"""
        # Check common environment variables used by different agent systems
        return (
            os.environ.get('DEFAULT_MODEL') or
            os.environ.get('MODEL') or
            'google/gemini-3-flash-preview'  # Fallback to a widely available model
        )

    @staticmethod
    def load():
        # If config file doesn't exist, use sensible defaults
        if not CONFIG_FILE.exists():
            default_model = ConfigManager.get_default_model()
            return {
                "pro_model": default_model,
                "preprocess_model": default_model,
                "zettel_dir": "~/Documents/Obsidian/Zettelkasten",
                "output_dir": "~/Documents/Obsidian/Inbox",
                "search_skill": "web_search",
                "link_depth": 2,
                "max_links": 10
            }

        try:
            config = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
            # Fallback to default model if specific models aren't configured
            default_model = ConfigManager.get_default_model()
            if not config.get('pro_model'):
                config['pro_model'] = default_model
            if not config.get('preprocess_model'):
                config['preprocess_model'] = default_model
            # Fallback for research settings
            if not config.get('search_skill'):
                config['search_skill'] = 'web_search'
            if not config.get('link_depth'):
                config['link_depth'] = 2
            if not config.get('max_links'):
                config['max_links'] = 10
            return config
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in configuration file at {CONFIG_FILE}")
            sys.exit(1)

    @staticmethod
    def save(config):
        # Ensure config directory exists
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding='utf-8')
        print(f"Configuration saved to {CONFIG_FILE}")

    @staticmethod
    def load_defaults():
        if EXAMPLE_CONFIG.exists():
            return json.loads(EXAMPLE_CONFIG.read_text(encoding='utf-8'))
        return {
            "pro_model": "openai/gpt-5.2",
            "preprocess_model": "openrouter/x-ai/kimi-k2.5",
            "zettel_dir": "~/Documents/Obsidian/Zettelkasten",
            "output_dir": "~/Documents/Obsidian/Inbox",
            "search_skill": "web_search",
            "link_depth": 2,
            "max_links": 10
        }


    @staticmethod
    def save(config):
        # Ensure config directory exists
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding='utf-8')
        print(f"Configuration saved to {CONFIG_FILE}")

    @staticmethod
    def load_defaults():
        if EXAMPLE_CONFIG.exists():
            return json.loads(EXAMPLE_CONFIG.read_text(encoding='utf-8'))
        return {
            "pro_model": "openai/gpt-5.2",
            "preprocess_model": "openrouter/x-ai/kimi-k2.5",
            "zettel_dir": "~/Documents/Obsidian/Zettelkasten",
            "output_dir": "~/Documents/Obsidian/Inbox"
        }
