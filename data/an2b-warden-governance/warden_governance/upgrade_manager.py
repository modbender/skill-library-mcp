"""War/Den Upgrade Manager -- detects mode and initializes components."""

from __future__ import annotations

from warden_governance.memory_client import MemoryClient
from warden_governance.sentinel_client import SentinelClient
from warden_governance.settings import Settings

MODE_FULL_COMMUNITY = "full_community"
MODE_GOVERNED_COMMUNITY = "governed_community"
MODE_MEMORY_ENTERPRISE = "memory_enterprise"
MODE_FULL_ENTERPRISE = "full_enterprise"


class UpgradeManager:
    """Detects operational mode and initializes matching components.

    Mode matrix (zero code changes, just env vars):

    SENTINEL_API_KEY | ENGRAMPORT_API_KEY | Mode
    -----------------|--------------------|-------------------
    --               | --                 | Full Community
    Set              | --                 | Governed Community
    --               | Set                | Memory Enterprise
    Set              | Set                | Full Enterprise
    """

    def __init__(self, config: Settings):
        self.config = config

    def detect_mode(self) -> dict:
        """Detect operational mode based on available API keys."""
        has_sentinel = bool(self.config.sentinel_api_key)
        has_engramport = bool(self.config.engramport_api_key)

        if has_sentinel and has_engramport:
            return {
                "mode": MODE_FULL_ENTERPRISE,
                "governance": "enterprise",
                "memory": "enterprise",
            }
        elif has_sentinel:
            return {
                "mode": MODE_GOVERNED_COMMUNITY,
                "governance": "enterprise",
                "memory": "community",
            }
        elif has_engramport:
            return {
                "mode": MODE_MEMORY_ENTERPRISE,
                "governance": "community",
                "memory": "enterprise",
            }
        else:
            return {
                "mode": MODE_FULL_COMMUNITY,
                "governance": "community",
                "memory": "community",
            }

    def initialize(self) -> dict:
        """Initialize components based on detected mode."""
        mode_info = self.detect_mode()
        sentinel = SentinelClient(self.config)
        memory = MemoryClient(self.config, sentinel)

        return {
            "mode": mode_info,
            "sentinel": sentinel,
            "memory": memory,
        }

    def print_mode_banner(self) -> str:
        """Print the mode banner and return the banner string."""
        mode_info = self.detect_mode()
        mode = mode_info["mode"]

        if mode == MODE_FULL_ENTERPRISE:
            governance_label = "Sentinel_OS"
            memory_label = "EngramPort"
            synthesis_label = "Eidetic AI"
        elif mode == MODE_GOVERNED_COMMUNITY:
            governance_label = "Sentinel_OS"
            memory_label = "SQLite"
            synthesis_label = "Basic"
        elif mode == MODE_MEMORY_ENTERPRISE:
            governance_label = "Local"
            memory_label = "EngramPort"
            synthesis_label = "Eidetic AI"
        else:
            governance_label = "Local"
            memory_label = "SQLite"
            synthesis_label = "Basic"

        mode_display = mode.replace("_", " ").title()

        lines = [
            "",
            "\033[91m\033[1m\U0001f99e War/Den governance active.\033[0m",
            "   Your OpenClaw bot is now governed.",
            "",
            f"   Governance: {governance_label}",
            f"   Memory:     {memory_label}",
            f"   Synthesis:  {synthesis_label}",
            f"   Mode:       {mode_display}",
        ]

        if mode != MODE_FULL_ENTERPRISE:
            lines.append("   Upgrade:    getsentinelos.com")

        lines.append("")

        banner = "\n".join(lines)
        print(banner)
        return banner
