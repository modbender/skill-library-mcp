#!/usr/bin/env python3
"""
Foxcode OpenClaw Interactive Configuration Wizard

Guides users through setting up Foxcode endpoints in OpenClaw with an
interactive, beginner-friendly approach.

Usage:
    python3 scripts/configure_foxcode.py
"""

import json
import os
import re
import sys
from getpass import getpass
from pathlib import Path
from typing import Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Endpoint definitions
ENDPOINTS = {
    "official": {
        "name": "Claude Code 官方专用线路 (Official)",
        "url": "https://code.newcli.com/claude",
        "description": "Highest reliability, standard pricing",
        "reliability": "★★★★★",
        "cost": "$$$"
    },
    "super": {
        "name": "Super特价Claude Code",
        "url": "https://code.newcli.com/claude/super",
        "description": "Cost efficient, 20-30% savings",
        "reliability": "★★★★☆",
        "cost": "$$"
    },
    "ultra": {
        "name": "Ultra特价Claude Code",
        "url": "https://code.newcli.com/claude/ultra",
        "description": "Maximum savings, 40-50% discount",
        "reliability": "★★★☆☆",
        "cost": "$"
    },
    "aws": {
        "name": "AWS特价Claude Code",
        "url": "https://code.newcli.com/claude/aws",
        "description": "Fastest response, AWS infrastructure",
        "reliability": "★★★★★",
        "cost": "$$$"
    },
    "aws-thinking": {
        "name": "AWS特价Claude Code（思考）",
        "url": "https://code.newcli.com/claude/droid",
        "description": "Extended thinking for complex tasks",
        "reliability": "★★★★★",
        "cost": "$$$"
    }
}

# Available models
MODELS = {
    "claude-opus-4-5-20251101": {
        "name": "Claude Opus",
        "description": "Most capable, best for complex tasks",
        "speed": "Slower",
        "cost": "Highest"
    },
    "claude-sonnet-4-5-20251101": {
        "name": "Claude Sonnet",
        "description": "Balanced - recommended for daily use",
        "speed": "Fast",
        "cost": "Medium"
    },
    "claude-haiku-4-5-20251101": {
        "name": "Claude Haiku",
        "description": "Fast and cheap, good for quick tasks",
        "speed": "Fastest",
        "cost": "Lowest"
    }
}

# Default config paths
DEFAULT_CONFIG_PATHS = [
    Path.home() / ".openclaw" / "openclaw.json",
]


def print_header(text: str):
    """Print a formatted header."""
    print()
    print("=" * 60)
    print(f"  {text}")
    print("=" * 60)
    print()


def print_step(number: int, text: str):
    """Print a step indicator."""
    print(f"\n▶ Step {number}: {text}")
    print("-" * 40)


def get_config_path() -> Path:
    """Find or create the OpenClaw config path."""
    # Try to find existing config
    for path in DEFAULT_CONFIG_PATHS:
        if path.exists():
            print(f"✓ Found existing config: {path}")
            return path

    # Default to first path if none found
    default_path = DEFAULT_CONFIG_PATHS[0]
    print(f"ℹ Will create new config at: {default_path}")
    return default_path


def validate_api_token(token: str) -> bool:
    """Validate API token format."""
    if not token:
        return False
    # Foxcode tokens typically start with sk-foxcode-
    if not re.match(r'^sk-[a-zA-Z0-9_-]+$', token):
        return False
    return len(token) > 20  # Minimum length check


def test_endpoint(url: str, token: str, timeout: int = 15) -> Dict:
    """Test if endpoint is accessible with the given token."""
    try:
        # Try a simple models endpoint or HEAD request
        req = Request(url, method="HEAD")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("User-Agent", "Foxcode-Configurator/1.0")

        with urlopen(req, timeout=timeout) as response:
            return {
                "success": True,
                "status_code": response.getcode(),
                "error": None
            }
    except HTTPError as e:
        # 401 means token was received but invalid
        if e.code == 401:
            return {
                "success": False,
                "status_code": e.code,
                "error": "Invalid API token"
            }
        # 404/405 means endpoint exists but doesn't support HEAD
        if e.code in [404, 405]:
            return {
                "success": True,
                "status_code": e.code,
                "error": None
            }
        return {
            "success": False,
            "status_code": e.code,
            "error": str(e)
        }
    except URLError as e:
        return {
            "success": False,
            "status_code": None,
            "error": f"Cannot reach endpoint: {e.reason}"
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": None,
            "error": str(e)
        }


def select_endpoints() -> List[str]:
    """Interactive multi-endpoint selection."""
    print("Available Foxcode Endpoints:")
    print()

    for key, endpoint in ENDPOINTS.items():
        print(f"  [{key}]")
        print(f"    Name: {endpoint['name']}")
        print(f"    Description: {endpoint['description']}")
        print(f"    Reliability: {endpoint['reliability']} | Cost: {endpoint['cost']}")
        print()

    print("Select one or more endpoints (comma-separated, e.g., 'official,super,aws')")
    print("Or type 'all' to add all endpoints.")
    print()
    print("Recommendations:")
    print("  • Beginners: 'official' - most reliable")
    print("  • Cost-conscious: 'super' - good savings")
    print("  • Maximum savings: 'ultra' - lowest cost")
    print("  • Speed priority: 'aws' - fastest response")
    print("  • Complex tasks: 'aws-thinking' - extended reasoning")
    print()

    while True:
        choice = input("Select endpoints (default: official): ").strip().lower()

        if not choice:
            choice = "official"

        if choice == "all":
            return list(ENDPOINTS.keys())

        selected = [c.strip() for c in choice.split(",")]
        valid = [s for s in selected if s in ENDPOINTS]

        if valid:
            return valid

        print("❌ Invalid choice. Please try again.")


def select_primary_model() -> str:
    """Interactive primary model selection."""
    print("Available Models:")
    print()

    for key, model in MODELS.items():
        print(f"  [{key}]")
        print(f"    Name: {model['name']}")
        print(f"    Description: {model['description']}")
        print(f"    Speed: {model['speed']} | Cost: {model['cost']}")
        print()

    print("Recommendations:")
    print("  • Daily use: 'claude-sonnet-4-5-20251101' - best balance")
    print("  • Complex tasks: 'claude-opus-4-5-20251101' - most capable")
    print("  • Quick tasks: 'claude-haiku-4-5-20251101' - fastest/cheapest")
    print()

    while True:
        choice = input("Select primary model (default: claude-sonnet-4-5-20251101): ").strip()

        if not choice:
            choice = "claude-sonnet-4-5-20251101"

        if choice in MODELS:
            return choice

        print("❌ Invalid model. Please try again.")


def select_fallback_models(primary: str) -> List[str]:
    """Interactive fallback model selection."""
    print()
    print("Fallback models provide backup if the primary is unavailable.")
    print("You can select 0-2 fallback models.")
    print()

    available_fallbacks = [k for k in MODELS.keys() if k != primary]
    fallbacks = []

    print("Available fallback options:")
    for i, key in enumerate(available_fallbacks, 1):
        model = MODELS[key]
        print(f"  {i}. {key} - {model['description']}")

    print()

    # First fallback
    choice = input("Select first fallback (1-2, or press Enter to skip): ").strip()
    if choice == "1":
        fallbacks.append(available_fallbacks[0])
    elif choice == "2":
        fallbacks.append(available_fallbacks[1])

    # Second fallback (if first was selected)
    if fallbacks:
        remaining = [k for k in available_fallbacks if k != fallbacks[0]]
        if remaining:
            print(f"\nRemaining option: {remaining[0]}")
            choice = input("Add as second fallback? (y/n): ").strip().lower()
            if choice == 'y':
                fallbacks.append(remaining[0])

    return fallbacks


def create_config(
    endpoint_keys: List[str],
    api_token: str,
    primary_model: str,
    fallback_models: List[str],
    default_endpoint: str
) -> Dict:
    """Create the configuration dictionary with multiple endpoint providers.
    
    Note: OpenClaw uses auth-profiles.json for API keys, NOT openclaw.json.
    The apiKey is stored separately in ~/.openclaw/agents/main/agent/auth-profiles.json
    """
    
    # Build models list (all 3 models, with primary first)
    all_models = [primary_model]
    for model_id in MODELS.keys():
        if model_id != primary_model and model_id not in all_models:
            all_models.append(model_id)
    
    models_list = []
    for model_id in all_models:
        model_info = MODELS.get(model_id, {})
        models_list.append({
            "id": model_id,
            "name": model_info.get("name", model_id),
            "contextWindow": 200000,
            "maxTokens": 4096
        })
    
    # Build providers for each selected endpoint
    # NOTE: No apiKey here - OpenClaw reads from auth-profiles.json
    providers = {}
    
    for endpoint_key in endpoint_keys:
        endpoint = ENDPOINTS[endpoint_key]
        provider_name = f"foxcode-{endpoint_key}" if endpoint_key != "official" else "foxcode"
        
        providers[provider_name] = {
            "baseUrl": endpoint["url"],
            "api": "anthropic-messages",
            "models": models_list
        }
    
    # OpenClaw uses camelCase and nested providers structure
    config = {
        "models": {
            "providers": providers
        }
    }
    
    # Set default agent model to the default endpoint's primary model
    default_provider = f"foxcode-{default_endpoint}" if default_endpoint != "official" else "foxcode"
    config["agents"] = {
        "defaults": {
            "model": f"{default_provider}/{primary_model}"
        }
    }
    
    return config


def create_auth_profile(api_token: str) -> Dict:
    """Create auth profile entry for Foxcode.
    
    OpenClaw stores API keys in auth-profiles.json, not openclaw.json.
    """
    return {
        "type": "api_key",
        "provider": "foxcode",
        "key": api_token
    }


def save_config(config: Dict, config_path: Path) -> bool:
    """Save configuration to file."""
    try:
        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        # Set restrictive permissions
        os.chmod(config_path, 0o600)

        return True
    except Exception as e:
        print(f"❌ Error saving config: {e}")
        return False


def get_auth_profiles_path() -> Path:
    """Get the path to auth-profiles.json."""
    return Path.home() / ".openclaw" / "agents" / "main" / "agent" / "auth-profiles.json"


def update_auth_profiles(api_token: str, endpoint_keys: List[str]) -> bool:
    """Update auth-profiles.json with Foxcode API key for ALL selected endpoints.
    
    OpenClaw stores API keys in auth-profiles.json, not openclaw.json.
    Each provider (foxcode, foxcode-super, foxcode-aws, etc.) needs its own auth profile.
    """
    auth_path = get_auth_profiles_path()
    
    try:
        # Load existing auth-profiles
        if auth_path.exists():
            with open(auth_path, 'r') as f:
                auth_data = json.load(f)
        else:
            auth_data = {"version": 1, "profiles": {}, "lastGood": {}, "usageStats": {}}
        
        # Create auth profile for each selected endpoint provider
        for endpoint_key in endpoint_keys:
            provider_name = f"foxcode-{endpoint_key}" if endpoint_key != "official" else "foxcode"
            profile_key = f"{provider_name}:default"
            
            # Add profile
            auth_data["profiles"][profile_key] = {
                "type": "api_key",
                "provider": provider_name,
                "key": api_token
            }
            
            # Update lastGood
            auth_data["lastGood"][provider_name] = profile_key
            
            # Update usageStats
            if profile_key not in auth_data.get("usageStats", {}):
                auth_data["usageStats"][profile_key] = {
                    "lastUsed": 0,
                    "errorCount": 0
                }
        
        # Ensure directory exists
        auth_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save
        with open(auth_path, 'w') as f:
            json.dump(auth_data, f, indent=2)
        
        os.chmod(auth_path, 0o600)
        
        return True
    except Exception as e:
        print(f"❌ Error updating auth-profiles: {e}")
        return False


def main():
    print_header("Foxcode OpenClaw Configuration Wizard")

    print("This wizard will help you set up Foxcode AI models in OpenClaw.")
    print("Estimated time: 3-5 minutes")
    print()
    print("Before starting, make sure you have:")
    print("  • A Foxcode API token (from https://foxcode.rjj.cc/api-keys)")
    print("  • OpenClaw installed on your system")
    print()

    input("Press Enter to continue...")

    # Step 1: Get API Token
    print_step(1, "Enter Your Foxcode API Token")
    print("Get your token from: https://foxcode.rjj.cc/api-keys")
    print()
    print("Security: Your input will be hidden.")
    print()

    while True:
        api_token = getpass("API Token: ").strip()

        if not api_token:
            print("❌ API token is required. Please try again.")
            continue

        if not validate_api_token(api_token):
            print("⚠ Warning: Token format looks unusual. Expected format: sk-...")
            confirm = input("Continue anyway? (y/n): ").strip().lower()
            if confirm == 'y':
                break
        else:
            print("✓ Token format looks valid")
            break

    # Step 2: Select Endpoints
    print_step(2, "Select Endpoints")
    endpoint_keys = select_endpoints()
    
    # If multiple endpoints, ask which one should be default
    default_endpoint = endpoint_keys[0]
    if len(endpoint_keys) > 1:
        print(f"\nYou selected {len(endpoint_keys)} endpoints.")
        print("Which one should be your default?")
        for i, key in enumerate(endpoint_keys, 1):
            print(f"  {i}. {key} - {ENDPOINTS[key]['name']}")
        
        while True:
            choice = input(f"Select default (1-{len(endpoint_keys)}, default: 1): ").strip()
            if not choice:
                choice = "1"
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(endpoint_keys):
                    default_endpoint = endpoint_keys[idx]
                    break
            except ValueError:
                pass
            print("❌ Invalid choice. Please try again.")
    
    print(f"\n✓ Selected endpoints: {', '.join(endpoint_keys)}")
    print(f"✓ Default endpoint: {default_endpoint}")

    # Step 3: Select Primary Model
    print_step(3, "Select Primary Model")
    primary_model = select_primary_model()
    print(f"\n✓ Selected: {MODELS[primary_model]['name']}")

    # Step 4: Configure Fallbacks
    print_step(4, "Configure Fallback Models")
    fallback_models = select_fallback_models(primary_model)
    if fallback_models:
        print(f"✓ Fallbacks configured: {', '.join(fallback_models)}")
    else:
        print("ℹ No fallbacks configured (you can add later)")

    # Step 5: Test Connection
    print_step(5, "Test Connection")
    default_endpoint_obj = ENDPOINTS[default_endpoint]
    print(f"Testing default endpoint: {default_endpoint_obj['url']}")
    print("Please wait...")

    test_result = test_endpoint(default_endpoint_obj["url"], api_token)

    if test_result["success"]:
        print("✓ Connection successful!")
        if test_result["status_code"]:
            print(f"  Status code: {test_result['status_code']}")
    else:
        print("⚠ Connection test failed")
        print(f"  Error: {test_result['error']}")
        print()
        print("You can still save the configuration, but OpenClaw may not work.")
        confirm = input("Save configuration anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            print("\nConfiguration cancelled.")
            print("Please check:")
            print("  • Your API token is correct")
            print("  • The endpoint URL is accessible")
            print("  • Your network connection is working")
            return

    # Step 6: Save Configuration
    print_step(6, "Save Configuration")

    config_path = get_config_path()
    config = create_config(endpoint_keys, api_token, primary_model, fallback_models, default_endpoint)

    print(f"\nConfiguration to save:")
    print(f"  Config file: {config_path}")
    print(f"  Auth file: {get_auth_profiles_path()}")
    print(f"  Endpoints: {', '.join(endpoint_keys)}")
    print(f"  Default Endpoint: {default_endpoint}")
    print(f"  Primary Model: {primary_model}")
    print(f"  All Models: {', '.join(MODELS.keys())}")

    # Show config (no API key - stored separately)
    print(f"\nConfig contents (openclaw.json):")
    print(json.dumps(config, indent=2))

    print()
    confirm = input("Save this configuration? (y/n): ").strip().lower()

    if confirm == 'y':
        # Save openclaw.json
        if save_config(config, config_path):
            print("\n✓ Configuration saved!")
            print(f"  File: {config_path}")
            
            # Step 7: Update auth-profiles.json
            print_step(7, "Save API Key to auth-profiles.json")
            print("OpenClaw stores API keys in auth-profiles.json (not openclaw.json)")
            print(f"Creating auth profiles for: {', '.join(endpoint_keys)}")
            
            if update_auth_profiles(api_token, endpoint_keys):
                print(f"\n✓ API key saved to auth-profiles.json")
                print(f"  File: {get_auth_profiles_path()}")
                print(f"  Providers: {', '.join(['foxcode' if k == 'official' else f'foxcode-{k}' for k in endpoint_keys])}")
            else:
                print("\n⚠ Could not update auth-profiles.json")
                print("You may need to add the API key manually through OpenClaw.")

            print("\n" + "=" * 60)
            print("Setup Complete!")
            print("=" * 60)
            print("\nNext steps:")
            print("  1. Restart OpenClaw if it's running")
            print("  2. Run a test: 'openclaw' then ask a simple question")
            print("  3. Check status anytime: python3 scripts/check_status.py")
            print()
            print("Need to make changes? Just run this wizard again:")
            print("  python3 scripts/configure_foxcode.py")
        else:
            print("\n❌ Failed to save configuration")
            print(f"Please check if the directory exists and you have write permissions:")
            print(f"  {config_path.parent}")
    else:
        print("\nConfiguration cancelled. No changes were saved.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nConfiguration cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
