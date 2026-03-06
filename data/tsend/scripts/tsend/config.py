"""Configuration management for tsend with profile support"""

import json
import os
from pathlib import Path
from typing import Any


class Config:
    """Manages tsend configuration from ~/.tsend/config.json with profile support"""

    CONFIG_PATH = Path.home() / ".tsend" / "config.json"

    def __init__(self, profile: str | None = None):
        self._data: dict[str, Any] = {}
        self._active_profile: str | None = profile or os.getenv("TSEND_PROFILE")
        self._load()

    def _load(self) -> None:
        """Load configuration from file"""
        if self.CONFIG_PATH.exists():
            with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                self._data = json.load(f)

    def save(self) -> None:
        """Save configuration to file"""
        self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value from current profile"""
        profile_name = self._active_profile or self._data.get("default", "default")
        profiles = self._data.get("profiles", {})
        profile_data = profiles.get(profile_name, {})
        return profile_data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value in current profile"""
        profile_name = self._active_profile or self._data.get("default", "default")
        if "profiles" not in self._data:
            self._data["profiles"] = {}
        if profile_name not in self._data["profiles"]:
            self._data["profiles"][profile_name] = {}
        self._data["profiles"][profile_name][key] = value

    @property
    def token(self) -> str | None:
        # Priority: env var > profile config
        return os.getenv("TSEND_TOKEN") or self.get("token")

    @property
    def chat_id(self) -> str | None:
        # Priority: env var > profile config
        return os.getenv("TSEND_CHAT_ID") or self.get("chat_id")

    @property
    def profiles(self) -> list[str]:
        """List available profiles"""
        if "profiles" not in self._data:
            return []
        return list(self._data["profiles"].keys())

    @property
    def default_profile(self) -> str | None:
        """Get the default profile name"""
        return self._data.get("default")

    def set_default_profile(self, profile: str) -> None:
        """Set the default profile"""
        if profile and profile in self.profiles:
            self._data["default"] = profile
        else:
            raise ValueError(f"Profile '{profile}' does not exist")

    @property
    def active_profile_name(self) -> str | None:
        """Get the name of the currently active profile"""
        return self._active_profile or self.default_profile

    def validate(self) -> tuple[bool, str]:
        """Validate required configuration"""
        if not self.token:
            return False, "Token not configured. Run: tsend config --token YOUR_TOKEN [--profile PROFILE_NAME]"
        if not self.chat_id:
            return False, "Chat ID not configured. Run: tsend config --chat-id YOUR_CHAT_ID [--profile PROFILE_NAME]"
        return True, ""
