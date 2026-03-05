"""Configuration management for Linear Todos."""

import json
import os
import re
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo


def _find_openclaw_user_timezone() -> Optional[str]:
    """Try to extract timezone from OpenClaw's USER.md if present.

    Searches up the directory tree from the skill location for a workspace
    containing USER.md, then parses the timezone field.
    """
    # Start from the skill directory and search upward for workspace
    skill_dir = Path(__file__).resolve().parent
    current = skill_dir

    # Search up a few levels for workspace root
    for _ in range(5):
        user_md = current / "USER.md"
        if user_md.exists():
            try:
                content = user_md.read_text()
                # Look for timezone: America/New_York or similar
                match = re.search(r'(?:timezone|time.?zone)\s*[:=]\s*["\']?([^\n"\']+)["\']?', content, re.IGNORECASE)
                if match:
                    tz = match.group(1).strip()
                    # Clean up common markdown/formatting artifacts
                    tz = tz.split('(')[0].strip()  # Remove " (EST/EDT)" suffix
                    tz = tz.replace('*', '').strip()  # Remove markdown asterisks
                    # Validate it looks like a timezone (has a slash for region/city)
                    if '/' in tz and not tz.startswith('http'):
                        return tz
            except (IOError, OSError):
                pass
            break

        # Also check if we're in skills/ subdirectory of workspace
        if current.name == "skills":
            user_md = current.parent / "USER.md"
            if user_md.exists():
                try:
                    content = user_md.read_text()
                    match = re.search(r'(?:timezone|time.?zone)\s*[:=]\s*["\']?([^\n"\']+)["\']?', content, re.IGNORECASE)
                    if match:
                        tz = match.group(1).strip()
                        # Clean up common markdown/formatting artifacts
                        tz = tz.split('(')[0].strip()  # Remove " (EST/EDT)" suffix
                        tz = tz.replace('*', '').strip()  # Remove markdown asterisks
                        if '/' in tz and not tz.startswith('http'):
                            return tz
                except (IOError, OSError):
                    pass
                break

        parent = current.parent
        if parent == current:
            break
        current = parent

    return None


class Config:
    """Manages configuration for Linear Todos.
    
    Configuration is loaded in this order (later overrides earlier):
    1. Default values (none)
    2. Config file: ~/.config/linear-todos/config.json
    3. Environment variables: LINEAR_*
    """
    
    CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "linear-todos"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    
    def __init__(self):
        self._config = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Start with config file if it exists
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, "r") as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._config = {}
        
        # Environment variables override config file
        env_mappings = {
            "LINEAR_API_KEY": "apiKey",
            "LINEAR_TEAM_ID": "teamId",
            "LINEAR_STATE_ID": "stateId",
            "LINEAR_DONE_STATE_ID": "doneStateId",
            "LINEAR_TIMEZONE": "timezone",
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.environ.get(env_var)
            if value:
                self._config[config_key] = value
    
    @property
    def api_key(self) -> Optional[str]:
        """Get the Linear API key."""
        return self._config.get("apiKey")
    
    @property
    def team_id(self) -> Optional[str]:
        """Get the team ID."""
        return self._config.get("teamId")
    
    @property
    def state_id(self) -> Optional[str]:
        """Get the initial state ID for new todos."""
        return self._config.get("stateId")
    
    @property
    def done_state_id(self) -> Optional[str]:
        """Get the done state ID."""
        return self._config.get("doneStateId")

    @property
    def timezone(self) -> Optional[str]:
        """Get the timezone string (e.g., 'America/New_York')."""
        return self._config.get("timezone")

    def get_timezone(self) -> Optional[ZoneInfo]:
        """Get the timezone as a ZoneInfo object.

        Checks configuration in this order:
        1. LINEAR_TIMEZONE environment variable
        2. timezone key in config.json
        3. OpenClaw USER.md (if running inside OpenClaw workspace)
        4. Returns None (defaults to UTC behavior)

        Returns:
            ZoneInfo object if timezone is found, None otherwise.
        """
        tz_str = self.timezone

        # Fallback: Check OpenClaw USER.md if no config timezone set
        # Disable with LINEAR_TODOS_NO_USERMD_FALLBACK=1 (for testing)
        if not tz_str and not os.environ.get("LINEAR_TODOS_NO_USERMD_FALLBACK"):
            tz_str = _find_openclaw_user_timezone()

        if tz_str:
            try:
                return ZoneInfo(tz_str)
            except Exception:
                return None
        return None

    def save(self, api_key: str, team_id: str, state_id: str,
             done_state_id: Optional[str] = None) -> None:
        """Save configuration to file.

        Args:
            api_key: Linear API key
            team_id: Team ID for todos
            state_id: Initial state ID for new todos
            done_state_id: State ID for completed todos
        """
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        config = {
            "apiKey": api_key,
            "teamId": team_id,
            "stateId": state_id,
        }

        if done_state_id:
            config["doneStateId"] = done_state_id

        # Write with restrictive permissions (user read/write only)
        import stat
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        self.CONFIG_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)

        self._config = config
    
    def is_configured(self) -> bool:
        """Check if the minimum required configuration is present.
        
        Returns:
            True if api_key and team_id are set
        """
        return bool(self.api_key and self.team_id)
    
    def __repr__(self) -> str:
        return f"Config(team_id={self.team_id}, configured={self.is_configured()})"
