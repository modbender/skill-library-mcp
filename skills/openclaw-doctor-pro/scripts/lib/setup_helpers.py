"""Helper functions for OpenClaw setup wizard."""
from __future__ import annotations

from pathlib import Path

from .utils import CONFIG_FILE, run_command, save_json, which_binary

AVAILABLE_CHANNELS = [
    "whatsapp", "telegram", "discord", "slack", "signal",
    "imessage", "teams", "matrix", "google-chat", "zalo", "bluebubbles"
]

AI_PROVIDERS = ["anthropic", "openai", "gemini"]


def install_pnpm() -> bool:
    """Install pnpm via npm."""
    code, _, _ = run_command(["npm", "install", "-g", "pnpm"], timeout=60)
    return code == 0


def install_openclaw() -> bool:
    """Install openclaw CLI via npm."""
    code, _, _ = run_command(["npm", "install", "-g", "openclaw"], timeout=120)
    return code == 0


def generate_config(channels: list[str], ai_config: dict) -> dict:
    """Generate openclaw.json configuration."""
    config = {
        "gateway": {
            "port": 18789,
            "bind": "0.0.0.0",
            "authMode": "token",
            "authToken": f"changeme-{hash(ai_config['api_key']) % 100000000:08d}"
        },
        "agent": {
            "model": ai_config["model"],
            "provider": ai_config["provider"],
            "workspace": str(Path.home() / "openclaw-workspace"),
            "sandboxMode": "relaxed"
        },
        "channels": {},
        "skills": {},
        "plugins": []
    }

    config["agent"][f"{ai_config['provider']}_api_key"] = ai_config["api_key"]

    for channel in channels:
        config["channels"][channel] = {
            "enabled": True,
            "dmPolicy": "whitelist",
            "allowFrom": []
        }

    return config


def save_config_with_backup(config: dict) -> bool:
    """Save config with backup of existing."""
    if CONFIG_FILE.exists():
        backup_file = CONFIG_FILE.with_suffix(".json.backup")
        try:
            import shutil
            shutil.copy2(CONFIG_FILE, backup_file)
        except Exception:
            pass

    return save_json(CONFIG_FILE, config)


def get_model_suggestion(provider: str) -> str:
    """Get default model for provider."""
    suggestions = {
        "anthropic": "claude-3-5-sonnet-20241022",
        "openai": "gpt-4o",
        "gemini": "gemini-2.0-flash-exp"
    }
    return suggestions.get(provider, "")
