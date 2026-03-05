#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration management module for the STT processor.

This module handles:
1. Loading configuration from JSON files
2. Managing environment variables
3. Validating provider configuration
4. Providing access to settings
"""

import json
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv

# Load .env only from the skill root directory (parent of scripts/),
# not from an arbitrary working directory.
_skill_root = Path(__file__).resolve().parent.parent
_dotenv_path = _skill_root / ".env"
if _dotenv_path.is_file():
    load_dotenv(_dotenv_path)

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Manages configuration for the STT system.

    Supports loading configuration from multiple sources:
    - JSON files
    - Environment variables
    - Deep-merge with environment variables taking priority
    """

    def __init__(self) -> None:
        """Initialize the configuration manager."""
        self.default_config_path = self.get_default_config_path()

    def get_default_config_path(self) -> str:
        """
        Get the default path to config.json (relative to skill root).

        Returns:
            str: Path to the configuration file
        """
        return str(_skill_root / "config.json")

    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        Load configuration from a JSON file and environment variables.

        Args:
            config_path: Path to the configuration file (optional)

        Returns:
            Dict[str, Any]: Merged configuration

        Raises:
            FileNotFoundError: If the configuration file is not found
            json.JSONDecodeError: If the configuration file is invalid JSON
        """
        json_config = {}
        if config_path is None:
            config_path = self.default_config_path

        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    json_config = json.load(f)
                logger.info(f"Configuration loaded from file: {config_path}")
            else:
                json_config = self._try_create_from_template(config_path)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON file {config_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")
            raise

        env_config = self.load_from_env()
        merged_config = self.merge_configs(json_config, env_config)

        errors = self.validate_config(merged_config)
        if errors:
            msg = "Configuration is invalid:\n" + "\n".join(f"  - {e}" for e in errors)
            logger.error(msg)
            raise ValueError(msg)

        return merged_config

    def _try_create_from_template(self, config_path: str) -> Dict[str, Any]:
        """
        If config.json is missing, try to create it from assets/config.example.json.

        Returns:
            Dict[str, Any]: Loaded config from the template, or empty dict.
        """
        template_path = _skill_root / "assets" / "config.example.json"
        if template_path.is_file():
            shutil.copy2(str(template_path), config_path)
            logger.warning(
                f"config.json not found — created from template {template_path}. "
                "Edit it and fill in your API keys."
            )
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"Configuration file not found: {config_path}")
            return {}

    def load_from_env(self) -> Dict[str, Any]:
        """
        Load configuration from environment variables.

        Returns:
            Dict[str, Any]: Configuration from environment variables
        """
        env_config = {
            "default_provider": os.getenv("STT_DEFAULT_PROVIDER"),
            "providers": {
                "yandex": {
                    "api_key": os.getenv("YANDEX_API_KEY"),
                    "folder_id": os.getenv("YANDEX_FOLDER_ID")
                }
            },
            "audio": {
                "temp_dir": os.getenv("STT_TEMP_DIR")
            }
        }

        env_config = self._remove_none_values(env_config)

        if env_config:
            logger.info("Configuration loaded from environment variables")

        return env_config

    def merge_configs(self, json_config: Dict[str, Any], env_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge configurations, with environment variables taking priority.

        Args:
            json_config: Configuration from JSON file
            env_config: Configuration from environment variables

        Returns:
            Dict[str, Any]: Merged configuration
        """
        merged = json_config.copy()

        def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                elif value is not None:
                    result[key] = value
            return result

        merged = deep_merge(merged, env_config)

        logger.debug("Configurations merged (environment variables take priority)")
        return merged

    def validate_config(self, config: Dict[str, Any]) -> list:
        """
        Validate required fields in the configuration.

        Args:
            config: Configuration to validate

        Returns:
            list: Empty list if valid, otherwise list of error strings.
        """
        errors = []

        if not isinstance(config, dict):
            return ["Configuration must be a dictionary"]

        if "default_provider" not in config or not config["default_provider"]:
            errors.append(
                "default_provider not set. "
                "Check config.json or set STT_DEFAULT_PROVIDER in .env"
            )
            return errors

        default_provider = config["default_provider"]

        if "providers" not in config or not isinstance(config["providers"], dict):
            errors.append("'providers' section is missing in configuration")
            return errors

        if default_provider not in config["providers"]:
            errors.append(f"No configuration found for provider: {default_provider}")
            return errors

        provider_config = config["providers"][default_provider]

        if default_provider == "yandex":
            errors.extend(self._validate_yandex_config(provider_config))

        if not errors:
            logger.info(f"Configuration valid for provider: {default_provider}")

        return errors

    def _validate_yandex_config(self, config: Dict[str, Any]) -> list:
        """
        Validate Yandex provider configuration.

        Args:
            config: Yandex provider configuration

        Returns:
            list: Empty list if valid, otherwise list of error strings.
        """
        errors = []
        env_to_field = {
            "api_key": "YANDEX_API_KEY",
            "folder_id": "YANDEX_FOLDER_ID",
        }

        for field, env_var in env_to_field.items():
            value = config.get(field, "")
            if not value or value in ("YOUR_YANDEX_API_KEY", "YOUR_FOLDER_ID"):
                errors.append(
                    f"{env_var} not set. Provide it in one of these ways:\n"
                    "    1. In ~/.openclaw/openclaw.json (recommended)\n"
                    "    2. In .env file in the skill folder\n"
                    "    3. In config.json under providers.yandex"
                )

        return errors

    def get_provider_config(self, config: Dict[str, Any], provider_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific provider.

        Args:
            config: Full configuration dictionary
            provider_name: Provider name

        Returns:
            Dict[str, Any]: Provider configuration

        Raises:
            KeyError: If the provider is not found in the configuration
        """
        if "providers" not in config:
            raise KeyError("Configuration has no providers section")

        if provider_name not in config["providers"]:
            raise KeyError(f"Provider '{provider_name}' not found in configuration")

        return config["providers"][provider_name]

    def create_temp_dir(self, config: Dict[str, Any]) -> str:
        """
        Create a temporary directory for audio files.

        Args:
            config: System configuration

        Returns:
            str: Path to the created temporary directory

        Raises:
            OSError: If the directory cannot be created
        """
        temp_dir = "./temp"  # default value

        if "audio" in config and "temp_dir" in config["audio"]:
            temp_dir = config["audio"]["temp_dir"]

        Path(temp_dir).mkdir(parents=True, exist_ok=True)

        logger.debug(f"Temporary directory created/verified: {temp_dir}")
        return temp_dir

    def _remove_none_values(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively remove None values from a dictionary.

        Args:
            d: Dictionary to clean

        Returns:
            Dict[str, Any]: Cleaned dictionary
        """
        if not isinstance(d, dict):
            return d

        result = {}
        for key, value in d.items():
            if value is None:
                continue
            elif isinstance(value, dict):
                cleaned = self._remove_none_values(value)
                if cleaned:
                    result[key] = cleaned
            else:
                result[key] = value

        return result
