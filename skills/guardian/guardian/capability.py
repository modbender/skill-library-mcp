"""Guardian Capability Restriction Layer — BL-033.

Implements least-privilege enforcement as the primary security boundary.
Even if a malicious instruction passes scanning, this layer prevents execution
of anything dangerous by enforcing per-profile capability constraints.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_SKILL_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_CONFIG_PATH = Path(
    os.environ.get("GUARDIAN_CONFIG") or (_SKILL_ROOT / "config.json")
)
_DEFAULT_WORKSPACE = Path(
    os.environ.get("OPENCLAW_WORKSPACE") or (Path.home() / ".openclaw" / "workspace")
).resolve()


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------


class CapabilityViolation(Exception):
    """Raised when an attempted action violates the active capability profile.

    Attributes:
        violation_type:   Category of the violation (filesystem, email, tool, browsing).
        attempted_action: Human-readable description of what was attempted.
        profile:          Name of the active profile that blocked the action.
    """

    def __init__(self, violation_type: str, attempted_action: str, profile: str) -> None:
        self.violation_type = violation_type
        self.attempted_action = attempted_action
        self.profile = profile
        super().__init__(
            f"[{profile}] Capability violation ({violation_type}): {attempted_action}"
        )


# ---------------------------------------------------------------------------
# Built-in profiles
# ---------------------------------------------------------------------------

_TEMP_DIR = tempfile.gettempdir()

BUILTIN_PROFILES: Dict[str, Dict[str, Any]] = {
    "restricted": {
        "description": "Maximum restriction. Read-only filesystem (workspace only), no email, allowlist-only tools, read-only browsing.",
        "filesystem": {
            "allowed_paths": [str(_DEFAULT_WORKSPACE)],
            "allowed_modes": ["r", "rb", "r+b"],  # read-only
            "allow_write": False,
        },
        "email": {
            "allow_send": False,
            "trusted_addresses": [],
        },
        "tools": {
            "allow_all": False,
            # Minimal safe set: read-only inspection and browsing
            "allowed_tools": [
                "read",
                "web_search",
                "web_fetch",
                "canvas",
                "image",
                "tts",
            ],
        },
        "browsing": {
            "read_only": True,
        },
    },
    "standard": {
        "description": "Balanced. Read/write to workspace + temp dirs, email to trusted addresses only, most tools allowed.",
        "filesystem": {
            "allowed_paths": [str(_DEFAULT_WORKSPACE), _TEMP_DIR],
            "allowed_modes": ["r", "rb", "w", "wb", "a", "ab", "r+", "r+b", "x"],
            "allow_write": True,
        },
        "email": {
            "allow_send": True,
            # Populated at runtime from config.json admin.trusted_sources
            "trusted_addresses": [],
        },
        "tools": {
            "allow_all": False,
            "allowed_tools": [
                "read",
                "write",
                "edit",
                "exec",
                "process",
                "web_search",
                "web_fetch",
                "browser",
                "canvas",
                "image",
                "tts",
                "subagents",
                "nodes",
            ],
        },
        "browsing": {
            "read_only": False,
        },
    },
    "trusted": {
        "description": "Wide access. All tools, full email, full filesystem. For power users only.",
        "filesystem": {
            "allowed_paths": ["/"],
            "allowed_modes": None,  # None = all modes permitted
            "allow_write": True,
        },
        "email": {
            "allow_send": True,
            "trusted_addresses": None,  # None = any address permitted
        },
        "tools": {
            "allow_all": True,
            "allowed_tools": None,  # None = unrestricted
        },
        "browsing": {
            "read_only": False,
        },
    },
}

# Modes that imply a write operation
_WRITE_MODES: Set[str] = {"w", "wb", "a", "ab", "r+", "r+b", "w+", "w+b", "x", "xb"}


# ---------------------------------------------------------------------------
# CapabilityEnforcer
# ---------------------------------------------------------------------------


class CapabilityEnforcer:
    """Primary interface for capability-based access control.

    Usage::

        enforcer = CapabilityEnforcer()           # loads profile from config.json
        enforcer = CapabilityEnforcer("restricted")
        enforcer.check_filesystem_access("/tmp/foo", "w")
        enforcer.check_email_send("user@example.com")
        enforcer.check_tool_invocation("exec")
    """

    def __init__(
        self,
        profile_name: Optional[str] = None,
        config_path: Optional[Union[str, Path]] = None,
    ) -> None:
        self._config_path = Path(config_path) if config_path else _DEFAULT_CONFIG_PATH
        self._config: Dict[str, Any] = self._load_guardian_config()
        self._profile_name: str = ""
        self._profile_config: Dict[str, Any] = {}

        # Determine profile: explicit arg → config.json capability.profile → "standard"
        resolved_name = (
            profile_name
            or self._config.get("capability", {}).get("profile", "standard")
            or "standard"
        )
        self.load_profile(resolved_name)

    # ------------------------------------------------------------------
    # Config helpers
    # ------------------------------------------------------------------

    def _load_guardian_config(self) -> Dict[str, Any]:
        """Load config.json, returning an empty dict on any error."""
        try:
            return json.loads(self._config_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    # ------------------------------------------------------------------
    # Profile management
    # ------------------------------------------------------------------

    def load_profile(self, profile_name: str) -> None:
        """Load a named profile.

        Checks built-in profiles first, then falls back to
        ``config.json → capability.profiles.<name>`` for custom profiles.

        Args:
            profile_name: One of ``restricted``, ``standard``, ``trusted``,
                          or a name defined in the config.

        Raises:
            ValueError: If the profile is not found anywhere.
        """
        if profile_name in BUILTIN_PROFILES:
            import copy
            profile = copy.deepcopy(BUILTIN_PROFILES[profile_name])
            # Merge trusted_sources from config into standard profile email allowlist
            if profile_name == "standard":
                trusted = self._config.get("admin", {}).get("trusted_sources", [])
                if trusted:
                    profile["email"]["trusted_addresses"] = list(trusted)
            self._profile_name = profile_name
            self._profile_config = profile
            return

        # Try custom profile from config
        custom = (
            self._config.get("capability", {})
            .get("profiles", {})
            .get(profile_name)
        )
        if custom is not None and isinstance(custom, dict):
            self._profile_name = profile_name
            self._profile_config = custom
            return

        raise ValueError(
            f"Unknown capability profile '{profile_name}'. "
            f"Built-in profiles: {list(BUILTIN_PROFILES)}. "
            "Custom profiles can be defined under config.json → capability.profiles.<name>."
        )

    def get_active_profile(self) -> Dict[str, Any]:
        """Return the active profile name and its full configuration.

        Returns:
            dict with ``name`` and ``config`` keys.
        """
        return {
            "name": self._profile_name,
            "config": self._profile_config,
        }

    # ------------------------------------------------------------------
    # Filesystem enforcement
    # ------------------------------------------------------------------

    def check_filesystem_access(self, path: Union[str, Path], mode: str = "r") -> None:
        """Assert that ``path`` may be accessed in the given ``mode``.

        Args:
            path: Filesystem path being accessed.
            mode: File open mode string (e.g. ``"r"``, ``"w"``, ``"rb"``).

        Raises:
            CapabilityViolation: If the access is denied by the active profile.
        """
        fs_cfg = self._profile_config.get("filesystem", {})
        resolved = str(Path(path).resolve())
        is_write = mode.strip() in _WRITE_MODES or (
            "w" in mode or "a" in mode or "x" in mode
        )

        # Check write permission at profile level
        if is_write and not fs_cfg.get("allow_write", False):
            raise CapabilityViolation(
                violation_type="filesystem",
                attempted_action=f"write access to '{path}' (mode='{mode}') denied by profile",
                profile=self._profile_name,
            )

        # Check allowed paths
        allowed_paths: Optional[List[str]] = fs_cfg.get("allowed_paths")
        if allowed_paths is not None:
            # "/" means all paths permitted
            if "/" not in allowed_paths:
                if not any(resolved.startswith(str(Path(p).resolve())) for p in allowed_paths):
                    raise CapabilityViolation(
                        violation_type="filesystem",
                        attempted_action=(
                            f"access to '{path}' (mode='{mode}') outside allowed paths "
                            f"{allowed_paths}"
                        ),
                        profile=self._profile_name,
                    )

        # Check allowed modes (if list is defined)
        allowed_modes: Optional[List[str]] = fs_cfg.get("allowed_modes")
        if allowed_modes is not None:
            # Normalise: strip whitespace, compare base mode
            if mode.strip() not in allowed_modes:
                raise CapabilityViolation(
                    violation_type="filesystem",
                    attempted_action=(
                        f"file mode '{mode}' not in allowed modes {allowed_modes} for '{path}'"
                    ),
                    profile=self._profile_name,
                )

    # ------------------------------------------------------------------
    # Email enforcement
    # ------------------------------------------------------------------

    def check_email_send(self, to_address: str) -> None:
        """Assert that an email may be sent to ``to_address``.

        Args:
            to_address: Recipient email address.

        Raises:
            CapabilityViolation: If the profile prohibits sending to this address.
        """
        email_cfg = self._profile_config.get("email", {})

        if not email_cfg.get("allow_send", False):
            raise CapabilityViolation(
                violation_type="email",
                attempted_action=f"email send to '{to_address}' — profile disallows all outgoing email",
                profile=self._profile_name,
            )

        trusted: Optional[List[str]] = email_cfg.get("trusted_addresses")
        if trusted is None:
            # None means unrestricted (trusted profile)
            return

        # Normalise and compare (case-insensitive)
        normalised = to_address.strip().lower()
        if not any(normalised == t.strip().lower() for t in trusted):
            raise CapabilityViolation(
                violation_type="email",
                attempted_action=(
                    f"email send to '{to_address}' not in trusted address list "
                    f"({len(trusted)} entries)"
                ),
                profile=self._profile_name,
            )

    # ------------------------------------------------------------------
    # Tool invocation enforcement
    # ------------------------------------------------------------------

    def check_tool_invocation(self, tool_name: str) -> None:
        """Assert that ``tool_name`` may be invoked under the active profile.

        Args:
            tool_name: Name of the tool (e.g. ``"exec"``, ``"browser"``).

        Raises:
            CapabilityViolation: If the tool is not permitted.
        """
        tools_cfg = self._profile_config.get("tools", {})

        if tools_cfg.get("allow_all", False):
            return  # trusted profile — everything permitted

        allowed: Optional[List[str]] = tools_cfg.get("allowed_tools")
        if allowed is None:
            return  # no restriction list defined

        if tool_name not in allowed:
            raise CapabilityViolation(
                violation_type="tool",
                attempted_action=(
                    f"invocation of tool '{tool_name}' not in allowlist "
                    f"({len(allowed)} tools permitted)"
                ),
                profile=self._profile_name,
            )

    # ------------------------------------------------------------------
    # Browsing enforcement (convenience helper)
    # ------------------------------------------------------------------

    def check_browsing_action(self, action: str) -> None:
        """Assert that a browser action is allowed under the active profile.

        In read-only browsing mode, only non-mutating actions are permitted.

        Args:
            action: Browser action name (e.g. ``"snapshot"``, ``"act"``).

        Raises:
            CapabilityViolation: If the action would mutate state and the profile
                enforces read-only browsing.
        """
        browsing_cfg = self._profile_config.get("browsing", {})
        if not browsing_cfg.get("read_only", False):
            return  # no restriction

        _READ_ONLY_ACTIONS = {"status", "snapshot", "screenshot", "tabs", "profiles", "console"}
        if action not in _READ_ONLY_ACTIONS:
            raise CapabilityViolation(
                violation_type="browsing",
                attempted_action=(
                    f"browser action '{action}' denied — profile enforces read-only browsing"
                ),
                profile=self._profile_name,
            )

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"CapabilityEnforcer(profile={self._profile_name!r})"
