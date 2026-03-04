#!/usr/bin/env python3
"""
Provider Setup Wizard
Interactive setup for token tracking providers
"""

import sys
from pathlib import Path
from config import Config


def setup_anthropic():
    """Setup Anthropic (Claude) provider."""
    print("\n🤖 Anthropic (Claude) Setup\n")
    
    api_key = input("API Key (oder Enter für env var ANTHROPIC_API_KEY): ").strip()
    
    models = [
        "claude-opus-4-5",
        "claude-sonnet-4-5",
        "claude-sonnet-4",
        "claude-3-5-sonnet-20241022"
    ]
    
    print("\nVerfügbare Models:")
    for i, model in enumerate(models, 1):
        print(f"  {i}. {model}")
    
    choice = input(f"\nModel wählen (1-{len(models)}, default: 2): ").strip()
    
    if choice and choice.isdigit() and 1 <= int(choice) <= len(models):
        model = models[int(choice) - 1]
    else:
        model = models[1]  # default: sonnet-4-5
    
    config = {
        "model": model
    }
    
    if api_key:
        config["api_key"] = api_key
    
    return config


def setup_openai():
    """Setup OpenAI (GPT) provider."""
    print("\n🧠 OpenAI (GPT) Setup\n")
    
    api_key = input("API Key (oder Enter für env var OPENAI_API_KEY): ").strip()
    
    models = [
        "gpt-4-turbo",
        "gpt-4",
        "gpt-4-32k",
        "gpt-3.5-turbo"
    ]
    
    print("\nVerfügbare Models:")
    for i, model in enumerate(models, 1):
        print(f"  {i}. {model}")
    
    choice = input(f"\nModel wählen (1-{len(models)}, default: 1): ").strip()
    
    if choice and choice.isdigit() and 1 <= int(choice) <= len(models):
        model = models[int(choice) - 1]
    else:
        model = models[0]  # default: gpt-4-turbo
    
    config = {
        "model": model
    }
    
    if api_key:
        config["api_key"] = api_key
    
    return config


def setup_gemini():
    """Setup Google Gemini provider."""
    print("\n✨ Google Gemini Setup\n")
    
    api_key = input("API Key (oder Enter für env var GOOGLE_API_KEY): ").strip()
    
    models = [
        "gemini-pro",
        "gemini-pro-vision",
        "gemini-ultra"
    ]
    
    print("\nVerfügbare Models:")
    for i, model in enumerate(models, 1):
        print(f"  {i}. {model}")
    
    choice = input(f"\nModel wählen (1-{len(models)}, default: 1): ").strip()
    
    if choice and choice.isdigit() and 1 <= int(choice) <= len(models):
        model = models[int(choice) - 1]
    else:
        model = models[0]  # default: gemini-pro
    
    config = {
        "model": model
    }
    
    if api_key:
        config["api_key"] = api_key
    
    return config


def main():
    """Main setup wizard."""
    print("=" * 60)
    print("Token Alert - Provider Setup")
    print("=" * 60)
    
    config_manager = Config()
    
    providers = {
        "1": ("anthropic", "Anthropic (Claude)", setup_anthropic),
        "2": ("openai", "OpenAI (GPT)", setup_openai),
        "3": ("gemini", "Google Gemini", setup_gemini)
    }
    
    print("\n📊 Welchen Provider möchtest du tracken?\n")
    for key, (_, name, _) in providers.items():
        print(f"  {key}. {name}")
    
    choice = input("\nWahl (1-3): ").strip()
    
    if choice not in providers:
        print("❌ Ungültige Auswahl!")
        return 1
    
    provider_type, provider_name, setup_func = providers[choice]
    
    try:
        config = setup_func()
        config_manager.add_provider(provider_type, config)
        
        print(f"\n✅ {provider_name} erfolgreich konfiguriert!")
        print(f"📁 Config gespeichert: {config_manager.config_path}")
        
        # Show current providers
        print("\n📋 Aktive Provider:")
        for p in config_manager.get_providers():
            enabled = "✅" if p.get("enabled", True) else "❌"
            print(f"  {enabled} {p['type']} - {p['config'].get('model', 'default')}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup abgebrochen.")
        return 1
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
