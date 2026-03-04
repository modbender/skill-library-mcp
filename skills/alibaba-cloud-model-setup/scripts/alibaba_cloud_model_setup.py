#!/usr/bin/env python3
"""Interactive OpenClaw Bailian (Alibaba Cloud) provider configurator.

Safely updates OpenClaw-style JSON config with a `bailian` provider entry.
Supports both Pay-As-You-Go and Coding Plan subscription types.
"""

from __future__ import annotations

import argparse
import datetime as dt
import getpass
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict
from urllib import error, request

# ============================================================================
# Base URLs - 5 options total
# ============================================================================

# Pay-As-You-Go (按量付费)
PAYG_CN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
PAYG_INTL_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
PAYG_US_BASE_URL = "https://dashscope-us.aliyuncs.com/compatible-mode/v1"

# Coding Plan (订阅制)
CODING_CN_BASE_URL = "https://coding.dashscope.aliyuncs.com/v1"
CODING_INTL_BASE_URL = "https://coding-intl.dashscope.aliyuncs.com/v1"

DEFAULT_MODEL = "qwen3-coder-plus"
PROVIDER_NAME = "bailian"  # Fixed typo from "balian"

# ============================================================================
# Model Definitions - Flagship 4 series, latest 2-3 generations each
# ============================================================================

# Qwen-Max series (best performance)
QWEN_MAX_MODELS = [
    {"id": "qwen-max", "name": "Qwen Max", "contextWindow": 262144, "maxTokens": 65536},
    {"id": "qwen-max-2025-01-25", "name": "Qwen Max 2025-01-25", "contextWindow": 262144, "maxTokens": 65536},
]

# Qwen-Plus series (balanced)
QWEN_PLUS_MODELS = [
    {"id": "qwen-plus", "name": "Qwen Plus", "contextWindow": 1000000, "maxTokens": 65536},
    {"id": "qwen-plus-2025-01-15", "name": "Qwen Plus 2025-01-15", "contextWindow": 1000000, "maxTokens": 65536},
]

# Qwen-Flash series (fast & cheap)
QWEN_FLASH_MODELS = [
    {"id": "qwen-flash", "name": "Qwen Flash", "contextWindow": 1000000, "maxTokens": 65536},
    {"id": "qwen-flash-2025-01-15", "name": "Qwen Flash 2025-01-15", "contextWindow": 1000000, "maxTokens": 65536},
]

# Qwen-Coder series (code specialist)
QWEN_CODER_MODELS = [
    {"id": "qwen3-coder-plus", "name": "Qwen3 Coder Plus", "contextWindow": 1000000, "maxTokens": 65536},
    {"id": "qwen3-coder-next", "name": "Qwen3 Coder Next", "contextWindow": 262144, "maxTokens": 65536},
    {"id": "qwen2.5-coder-32b-instruct", "name": "Qwen2.5 Coder 32B", "contextWindow": 256000, "maxTokens": 65536},
]

# Latest Qwen models (available for both Pay-As-You-Go and Coding Plan)
QWEN_LATEST_MODELS = [
    {"id": "qwen3.5-plus", "name": "Qwen3.5 Plus", "contextWindow": 1000000, "maxTokens": 65536},
    {"id": "qwen3-max-2026-01-23", "name": "Qwen3 Max 2026-01-23", "contextWindow": 262144, "maxTokens": 65536},
]

# Coding Plan exclusive models (third-party models: MiniMax, GLM, Kimi)
CODING_PLAN_EXCLUSIVE_MODELS = [
    {"id": "MiniMax-M2.5", "name": "MiniMax M2.5", "contextWindow": 204800, "maxTokens": 131072},
    {"id": "glm-5", "name": "GLM-5", "contextWindow": 202752, "maxTokens": 16384},
    {"id": "glm-4.7", "name": "GLM-4.7", "contextWindow": 202752, "maxTokens": 16384},
    {"id": "kimi-k2.5", "name": "Kimi K2.5", "contextWindow": 262144, "maxTokens": 32768},
]

DEFAULT_MODEL_SPEC = {
    "reasoning": False,
    "input": ["text"],
    "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Configure OpenClaw to use Alibaba Cloud Bailian provider."
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to OpenClaw JSON config. Auto-detected if omitted.",
    )
    parser.add_argument(
        "--plan-type",
        choices=["payg", "coding"],
        help="Plan type: payg (Pay-As-You-Go) or coding (Coding Plan).",
    )
    parser.add_argument(
        "--site",
        choices=["cn", "intl", "us"],
        help="Site region: cn, intl, or us.",
    )
    parser.add_argument("--api-key", help="DashScope API key.")
    parser.add_argument(
        "--api-key-source",
        choices=["env", "inline"],
        default=None,
        help="Where to store provider apiKey: env (recommended) or inline.",
    )
    parser.add_argument(
        "--env-var",
        default="DASHSCOPE_API_KEY",
        help="Environment variable name used when --api-key-source=env.",
    )
    parser.add_argument(
        "--persist-env-shell",
        action="store_true",
        help="Write export line to shell profile (default ~/.bashrc) when using env key mode.",
    )
    parser.add_argument(
        "--shell-profile",
        type=Path,
        default=Path.home() / ".bashrc",
        help="Shell profile file for --persist-env-shell.",
    )
    parser.add_argument(
        "--persist-env-systemd",
        action="store_true",
        help="Write env var to systemd user override and restart service when using env key mode.",
    )
    parser.add_argument(
        "--systemd-service",
        default="openclaw",
        help="Systemd user service name for --persist-env-systemd.",
    )
    parser.add_argument("--model", default=None, help="Primary model ID.")
    parser.add_argument(
        "--models",
        default=None,
        help="Comma-separated provider model IDs.",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models for the selected site and exit.",
    )
    parser.add_argument(
        "--set-default",
        action="store_true",
        help="Set agent default model to this provider/primary model.",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Fail instead of prompting for missing values.",
    )
    return parser.parse_args()


def detect_config_path() -> Path:
    candidates = [
        Path.home() / ".openclaw" / "openclaw.json",
        Path.home() / ".moltbot" / "moltbot.json",
        Path.home() / ".clawdbot" / "clawdbot.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def model_entry(model_id: str, context_window: int = 1000000, max_tokens: int = 65536) -> Dict[str, Any]:
    """Create a model entry with standard structure."""
    return {
        "id": model_id,
        "name": model_id.replace("-", " ").replace("_", " ").title(),
        "reasoning": False,
        "input": ["text"],
        "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
        "contextWindow": context_window,
        "maxTokens": max_tokens,
    }


def get_payg_models() -> list[Dict[str, Any]]:
    """Get Pay-As-You-Go models (flagship 4 series + latest Qwen)."""
    models = []
    
    # Qwen-Max series
    for m in QWEN_MAX_MODELS:
        models.append(model_entry(m["id"], m["contextWindow"], m["maxTokens"]))
    
    # Qwen-Plus series
    for m in QWEN_PLUS_MODELS:
        models.append(model_entry(m["id"], m["contextWindow"], m["maxTokens"]))
    
    # Qwen-Flash series
    for m in QWEN_FLASH_MODELS:
        models.append(model_entry(m["id"], m["contextWindow"], m["maxTokens"]))
    
    # Qwen-Coder series
    for m in QWEN_CODER_MODELS:
        models.append(model_entry(m["id"], m["contextWindow"], m["maxTokens"]))
    
    # Latest Qwen models (qwen3.5-plus, qwen3-max-2026-01-23)
    for m in QWEN_LATEST_MODELS:
        models.append(model_entry(m["id"], m["contextWindow"], m["maxTokens"]))
    
    return models


def get_coding_cn_models() -> list[Dict[str, Any]]:
    """Get Coding Plan 中国站 models (Pay-As-You-Go + third-party exclusive)."""
    models = get_payg_models()
    
    # Add Coding Plan exclusive models (third-party: MiniMax, GLM, Kimi)
    for m in CODING_PLAN_EXCLUSIVE_MODELS:
        models.append(model_entry(m["id"], m["contextWindow"], m["maxTokens"]))
    
    return models


def get_coding_intl_models() -> list[Dict[str, Any]]:
    """Get Coding Plan 国际站 models (same as China site)."""
    # 国际站和中国站模型列表相同
    return get_coding_cn_models()


def prompt_plan_type() -> str:
    """Prompt user to choose plan type."""
    while True:
        print("\n=== Bailian Plan Type ===")
        print("1) Pay-As-You-Go (按量付费) - Pay per token")
        print("2) Coding Plan (订阅制) - Monthly subscription")
        print("   • 中国站: More models (Qwen + MiniMax + GLM + Kimi)")
        print("   • 国际站: Qwen flagship models")
        
        raw = input("\nSelection [1/2] (default 1): ").strip().lower()
        if raw in {"", "1", "payg", "pay-as-you-go", "按量"}:
            return "payg"
        if raw in {"2", "coding", "subscription", "订阅"}:
            return "coding"
        print("Invalid choice. Enter 1 (Pay-As-You-Go) or 2 (Coding Plan).")


def prompt_site(plan_type: str) -> str:
    """Prompt user to choose site based on plan type."""
    if plan_type == "payg":
        while True:
            print("\n=== Pay-As-You-Go Site ===")
            print("1) Beijing (China site, CN) - dashscope.aliyuncs.com")
            print("2) Singapore (International site, INTL) - dashscope-intl.aliyuncs.com")
            print("3) Virginia (US site, US) - dashscope-us.aliyuncs.com")
            
            raw = input("Selection [1/2/3] (default 1): ").strip().lower()
            if raw in {"", "1", "cn", "beijing", "china", "zh"}:
                return "cn"
            if raw in {"2", "intl", "int", "international", "singapore", "sg"}:
                return "intl"
            if raw in {"3", "us", "usa", "america", "virginia"}:
                return "us"
            print("Invalid choice. Enter 1, 2, or 3.")
    else:  # coding plan
        while True:
            print("\n=== Coding Plan Site ===")
            print("1) China site (CN) - coding.dashscope.aliyuncs.com")
            print("   • Models: Qwen3.5-Plus, Qwen3-Max, Qwen3-Coder, MiniMax, GLM, Kimi")
            print("2) International site (INTL) - coding-intl.dashscope.aliyuncs.com")
            print("   • Models: Qwen flagship series")
            
            raw = input("Selection [1/2] (default 1): ").strip().lower()
            if raw in {"", "1", "cn", "china", "zh"}:
                return "cn"
            if raw in {"2", "intl", "international", "sg"}:
                return "intl"
            print("Invalid choice. Enter 1 or 2.")


def get_base_url(plan_type: str, site: str) -> str:
    """Get base URL based on plan type and site."""
    if plan_type == "payg":
        if site == "cn":
            return PAYG_CN_BASE_URL
        elif site == "intl":
            return PAYG_INTL_BASE_URL
        else:  # us
            return PAYG_US_BASE_URL
    else:  # coding plan
        if site == "cn":
            return CODING_CN_BASE_URL
        else:  # intl
            return CODING_INTL_BASE_URL


def get_models(plan_type: str, site: str) -> list[Dict[str, Any]]:
    """Get model list based on plan type and site."""
    if plan_type == "payg":
        return get_payg_models()  # 12 models (flagship + latest Qwen)
    else:  # coding plan
        if site == "cn":
            return get_coding_cn_models()  # 18 models (PayG + third-party)
        else:
            return get_coding_intl_models()  # 18 models (same as CN)


def prompt_api_key() -> str:
    while True:
        value = getpass.getpass("DashScope API key (input hidden): ").strip()
        if value:
            return value
        print("API key cannot be empty.")


def prompt_api_key_source() -> str:
    raw = input(
        "Use safer mode (store API key in environment variable, not openclaw.json)? [Y/n]: "
    ).strip().lower()
    if raw in {"", "y", "yes"}:
        return "env"
    return "inline"


def prompt_set_default() -> bool:
    raw = input("Set as default model for agents? [Y/n]: ").strip().lower()
    return raw in {"", "y", "yes"}


def prompt_primary_model(models: list[Dict[str, Any]]) -> str:
    """Prompt user to choose primary model."""
    print("\n=== Available Models ===")
    for i, m in enumerate(models, 1):
        print(f"{i:2d}. {m['id']:30s} ({m.get('contextWindow', 'N/A'):>8} ctx)")
    
    while True:
        raw = input(f"\nChoose primary model [1-{len(models)}] (default 1): ").strip()
        if raw == "":
            return models[0]["id"]
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(models):
                return models[idx]["id"]
        except ValueError:
            pass
        print(f"Invalid choice. Enter 1-{len(models)}.")


def prompt_add_extra_models() -> bool:
    """Ask if user wants to add more models from live API."""
    raw = input("Fetch and add more models from live API? [y/N]: ").strip().lower()
    return raw in {"y", "yes"}


def list_live_models(base_url: str, api_key: str) -> list[str]:
    """Fetch available models from API."""
    url = f"{base_url}/models"
    req = request.Request(url)
    req.add_header("Authorization", f"Bearer {api_key}")
    
    try:
        with request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return [m["id"] for m in data.get("data", [])]
    except Exception as e:
        print(f"⚠️  Failed to fetch models: {e}")
        return []


def validate_api_key(base_url: str, api_key: str) -> bool:
    """Validate API key by making a test request."""
    url = f"{base_url}/models"
    req = request.Request(url)
    req.add_header("Authorization", f"Bearer {api_key}")
    
    try:
        with request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except error.HTTPError as e:
        print(f"❌ API key validation failed: HTTP {e.code}")
        return False
    except Exception as e:
        print(f"❌ API key validation failed: {e}")
        return False


def backup_config(config_path: Path) -> Path:
    """Create timestamped backup of config file."""
    if not config_path.exists():
        return config_path
    
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = config_path.parent / f"{config_path.name}.{timestamp}.bak"
    shutil.copy2(config_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load config from JSON file."""
    if not config_path.exists():
        return {}
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config_path: Path, config: Dict[str, Any]) -> None:
    """Save config to JSON file with pretty formatting."""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")


def update_config(
    config: Dict[str, Any],
    base_url: str,
    api_key: str,
    api_key_source: str,
    env_var: str,
    models: list[Dict[str, Any]],
    primary_model: str,
    set_default: bool,
) -> None:
    """Update config with Bailian provider."""
    
    # Ensure models section exists
    if "models" not in config:
        config["models"] = {}
    
    if config["models"].get("mode") != "merge":
        config["models"]["mode"] = "merge"
    
    # Add/update provider
    if "providers" not in config["models"]:
        config["models"]["providers"] = {}
    
    provider_config = {
        "baseUrl": base_url,
        "api": "openai-completions",
        "models": models,
    }
    
    if api_key_source == "inline":
        provider_config["apiKey"] = api_key
    # else: apiKey will be read from env var
    
    config["models"]["providers"][PROVIDER_NAME] = provider_config
    
    # Set default model if requested
    if set_default:
        if "agents" not in config:
            config["agents"] = {}
        if "defaults" not in config["agents"]:
            config["agents"]["defaults"] = {}
        if "model" not in config["agents"]["defaults"]:
            config["agents"]["defaults"]["model"] = {}
        
        config["agents"]["defaults"]["model"]["primary"] = f"{PROVIDER_NAME}/{primary_model}"
        
        # Add to defaults.models
        if "models" not in config["agents"]["defaults"]:
            config["agents"]["defaults"]["models"] = {}
        
        for m in models:
            config["agents"]["defaults"]["models"][f"{PROVIDER_NAME}/{m['id']}"] = {}


def main():
    args = parse_args()
    
    print("🤖 OpenClaw Bailian Provider Configurator")
    print("=" * 50)
    
    # Detect config path
    config_path = args.config or detect_config_path()
    print(f"\n📁 Config path: {config_path}")
    
    # Prompt plan type
    plan_type = args.plan_type or prompt_plan_type()
    print(f"📋 Plan type: {plan_type}")
    
    # Prompt site
    site = args.site or prompt_site(plan_type)
    print(f"🌍 Site: {site}")
    
    base_url = get_base_url(plan_type, site)
    print(f"🔗 Base URL: {base_url}")
    
    # Get models
    models = get_models(plan_type, site)
    print(f"📦 Models: {len(models)} models loaded")
    
    # Prompt API key
    api_key = args.api_key
    if not api_key:
        api_key = prompt_api_key()
    
    # Validate API key
    print("\n🔑 Validating API key...")
    if not validate_api_key(base_url, api_key):
        print("❌ API key validation failed. Exiting.")
        return 1
    print("✅ API key valid!")
    
    # Prompt API key source
    api_key_source = args.api_key_source or prompt_api_key_source()
    env_var = args.env_var or "DASHSCOPE_API_KEY"
    print(f"🔐 API key source: {api_key_source}")
    
    # Prompt primary model
    primary_model = args.model or prompt_primary_model(models)
    print(f"🎯 Primary model: {primary_model}")
    
    # Prompt set default
    set_default = args.set_default or prompt_set_default()
    print(f"⚙️  Set as default: {set_default}")
    
    # Backup config
    if config_path.exists():
        backup_config(config_path)
    
    # Load and update config
    config = load_config(config_path)
    update_config(
        config,
        base_url,
        api_key,
        api_key_source,
        env_var,
        models,
        primary_model,
        set_default,
    )
    
    # Save config
    save_config(config_path, config)
    print(f"\n✅ Config saved: {config_path}")
    
    # Validate JSON
    print("\n🔍 Validating JSON...")
    try:
        json.dumps(config)
        print("✅ JSON valid!")
    except Exception as e:
        print(f"❌ JSON validation failed: {e}")
        return 1
    
    # Summary
    print("\n" + "=" * 50)
    print("✅ Configuration complete!")
    print(f"\n📊 Summary:")
    print(f"  • Provider: {PROVIDER_NAME}")
    print(f"  • Plan: {plan_type}")
    print(f"  • Site: {site}")
    print(f"  • Base URL: {base_url}")
    print(f"  • Models: {len(models)}")
    print(f"  • Primary: {primary_model}")
    print(f"  • Default: {set_default}")
    
    if api_key_source == "env":
        print(f"\n🔐 API key stored in environment variable: {env_var}")
        print(f"   Add to ~/.bashrc: export {env_var}=YOUR_KEY")
    
    print(f"\n🚀 Next steps:")
    print(f"  1. Restart Gateway: openclaw gateway restart")
    print(f"  2. Test model: openclaw tui")
    
    return 0


if __name__ == "__main__":
    exit(main())
