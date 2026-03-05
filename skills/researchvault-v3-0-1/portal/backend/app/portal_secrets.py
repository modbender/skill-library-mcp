from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import os


@dataclass(frozen=True)
class SecretsStatus:
    brave_api_key_configured: bool
    brave_api_key_source: str  # env|none
    serper_api_key_configured: bool
    serper_api_key_source: str  # env|none
    searxng_base_url_configured: bool
    searxng_base_url_source: str  # env|none
    searxng_base_url: Optional[str] = None


def secrets_status() -> SecretsStatus:
    brave_env = os.getenv("BRAVE_API_KEY")
    serper_env = os.getenv("SERPER_API_KEY")
    searx_env = os.getenv("SEARXNG_BASE_URL")

    brave_conf = bool(brave_env)
    serper_conf = bool(serper_env)
    searx_conf = bool(searx_env and searx_env.strip())

    return SecretsStatus(
        brave_api_key_configured=brave_conf,
        brave_api_key_source=("env" if brave_conf else "none"),
        serper_api_key_configured=serper_conf,
        serper_api_key_source=("env" if serper_conf else "none"),
        searxng_base_url_configured=searx_conf,
        searxng_base_url_source=("env" if searx_conf else "none"),
        searxng_base_url=(searx_env.strip() if searx_conf else None),
    )


def brave_key_status() -> SecretsStatus:
    # Back-compat alias.
    return secrets_status()


def get_brave_api_key() -> Optional[str]:
    env = os.getenv("BRAVE_API_KEY")
    return env if env else None


def get_serper_api_key() -> Optional[str]:
    env = os.getenv("SERPER_API_KEY")
    return env if env else None


def get_searxng_base_url() -> Optional[str]:
    env = os.getenv("SEARXNG_BASE_URL")
    if env and env.strip():
        return env.strip()
    return None


def set_brave_api_key(api_key: str) -> SecretsStatus:
    raise RuntimeError("Portal secret writes are disabled. Set BRAVE_API_KEY in the backend environment.")


def clear_brave_api_key() -> SecretsStatus:
    raise RuntimeError("Portal secret writes are disabled. Unset BRAVE_API_KEY in the backend environment.")


def set_serper_api_key(api_key: str) -> SecretsStatus:
    raise RuntimeError("Portal secret writes are disabled. Set SERPER_API_KEY in the backend environment.")


def clear_serper_api_key() -> SecretsStatus:
    raise RuntimeError("Portal secret writes are disabled. Unset SERPER_API_KEY in the backend environment.")


def set_searxng_base_url(url: str) -> SecretsStatus:
    raise RuntimeError("Portal secret writes are disabled. Set SEARXNG_BASE_URL in the backend environment.")


def clear_searxng_base_url() -> SecretsStatus:
    raise RuntimeError("Portal secret writes are disabled. Unset SEARXNG_BASE_URL in the backend environment.")
