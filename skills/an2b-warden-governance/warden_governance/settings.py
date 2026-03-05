"""War/Den Settings -- configuration from environment variables or skill config dict."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    """All configuration for the governance skill.

    Built from OpenClaw skill config dict or environment variables.
    Community mode requires zero configuration.
    """

    # Governance
    sentinel_api_key: str = ""
    sentinel_base_url: str = "https://getsentinelos.com"
    warden_fail_open: bool = False
    warden_mode: str = "community"

    # Memory
    engramport_api_key: str = ""
    engramport_base_url: str = "https://mandeldb.com/api/v1/portal"
    engramport_fallback: bool = True
    warden_memory_db: str = "~/.warden/memory.db"

    # Community governance
    warden_policy_file: str = ""
    warden_policy_packs: str = ""
    warden_audit_db: str = "~/.warden/audit.db"

    # Cache
    warden_cache_ttl: int = 300

    # Agent
    warden_agent_id: str = "openclaw-agent"

    def __post_init__(self) -> None:
        if self.sentinel_api_key:
            self.warden_mode = "enterprise"
        else:
            self.warden_mode = "community"

    @classmethod
    def from_config(cls, config: dict) -> Settings:
        """Build Settings from an OpenClaw skill config dict."""
        return cls(
            sentinel_api_key=config.get("SENTINEL_API_KEY", ""),
            engramport_api_key=config.get("ENGRAMPORT_API_KEY", ""),
            warden_fail_open=str(config.get("WARDEN_FAIL_OPEN", "false")).lower() == "true",
            warden_agent_id=config.get("WARDEN_AGENT_ID", "openclaw-agent"),
            warden_policy_file=config.get("WARDEN_POLICY_FILE", ""),
            warden_policy_packs=config.get("WARDEN_POLICY_PACKS", ""),
            warden_memory_db=config.get("WARDEN_MEMORY_DB", "~/.warden/memory.db"),
            warden_audit_db=config.get("WARDEN_AUDIT_DB", "~/.warden/audit.db"),
            warden_cache_ttl=int(config.get("WARDEN_CACHE_TTL", "300")),
        )

    @classmethod
    def from_env(cls) -> Settings:
        """Build Settings from environment variables."""
        return cls(
            sentinel_api_key=os.environ.get("SENTINEL_API_KEY", ""),
            sentinel_base_url=os.environ.get("SENTINEL_BASE_URL", "https://getsentinelos.com"),
            engramport_api_key=os.environ.get("ENGRAMPORT_API_KEY", ""),
            engramport_base_url=os.environ.get("ENGRAMPORT_BASE_URL", "https://mandeldb.com/api/v1/portal"),
            engramport_fallback=os.environ.get("ENGRAMPORT_FALLBACK", "true").lower() == "true",
            warden_fail_open=os.environ.get("WARDEN_FAIL_OPEN", "false").lower() == "true",
            warden_agent_id=os.environ.get("WARDEN_AGENT_ID", "openclaw-agent"),
            warden_policy_file=os.environ.get("WARDEN_POLICY_FILE", ""),
            warden_policy_packs=os.environ.get("WARDEN_POLICY_PACKS", ""),
            warden_memory_db=os.environ.get("WARDEN_MEMORY_DB", "~/.warden/memory.db"),
            warden_audit_db=os.environ.get("WARDEN_AUDIT_DB", "~/.warden/audit.db"),
            warden_cache_ttl=int(os.environ.get("WARDEN_CACHE_TTL", "300")),
        )
