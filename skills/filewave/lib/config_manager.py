#!/usr/bin/env python3
"""
Configuration manager for FileWave profiles.

Handles reading/writing ~/.filewave/config with multiple server profiles.
Supports environment variable overrides for CI/CD.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, List
import configparser


class FileWaveConfig:
    """Manage FileWave server profiles."""
    
    CONFIG_DIR = Path.home() / ".filewave"
    CONFIG_FILE = CONFIG_DIR / "config"
    DEFAULT_SECTION = "default"
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.loaded = False
        self._load_config()
    
    def _load_config(self):
        """Load config file if it exists."""
        if self.CONFIG_FILE.exists():
            try:
                self.config.read(self.CONFIG_FILE)
                self.loaded = True
            except Exception as e:
                print(f"Error reading config file: {e}", file=sys.stderr)
                self.loaded = False
    
    def get_profile(self, profile_name: Optional[str] = None) -> Optional[Dict[str, str]]:
        """Get profile by name, or default if not specified.
        
        Priority:
        1. profile_name parameter
        2. FILEWAVE_PROFILE env var
        3. [default] profile = ... in config
        4. First profile found
        """
        # Use provided profile name
        if profile_name:
            return self._get_profile_by_name(profile_name)
        
        # Check env var override
        if os.getenv("FILEWAVE_PROFILE"):
            return self._get_profile_by_name(os.getenv("FILEWAVE_PROFILE"))
        
        # Check config file default
        if self.config.has_section(self.DEFAULT_SECTION):
            default_name = self.config.get(self.DEFAULT_SECTION, "profile", fallback=None)
            if default_name:
                return self._get_profile_by_name(default_name)
        
        # Fall back to first profile
        profiles = self.list_profiles()
        if profiles:
            return self._get_profile_by_name(profiles[0])
        
        return None
    
    def _get_profile_by_name(self, profile_name: str) -> Optional[Dict[str, str]]:
        """Get specific profile from config."""
        # Check env var override first (FILEWAVE_SERVER + FILEWAVE_TOKEN)
        if os.getenv("FILEWAVE_SERVER") and os.getenv("FILEWAVE_TOKEN"):
            return {
                "server": os.getenv("FILEWAVE_SERVER"),
                "token": os.getenv("FILEWAVE_TOKEN"),
                "profile": "(env override)",
                "from_env": True,
            }
        
        # Check config file
        if not self.config.has_section(profile_name):
            print(f"ERROR: Profile '{profile_name}' not found in {self.CONFIG_FILE}", file=sys.stderr)
            return None
        
        server = self.config.get(profile_name, "server", fallback=None)
        token = self.config.get(profile_name, "token", fallback=None)
        
        if not server or not token:
            print(f"ERROR: Profile '{profile_name}' missing server or token", file=sys.stderr)
            return None
        
        return {
            "profile": profile_name,
            "server": server,
            "token": token,
            "description": self.config.get(profile_name, "description", fallback=""),
            "from_env": False,
        }
    
    def list_profiles(self) -> List[str]:
        """List all available profiles (exclude [default] section)."""
        profiles = []
        for section in self.config.sections():
            if section != self.DEFAULT_SECTION:
                profiles.append(section)
        return sorted(profiles)
    
    def get_default_profile(self) -> Optional[str]:
        """Get default profile name."""
        if self.config.has_section(self.DEFAULT_SECTION):
            return self.config.get(self.DEFAULT_SECTION, "profile", fallback=None)
        return None
    
    def add_profile(self, name: str, server: str, token: str, description: str = ""):
        """Add or update a profile."""
        if not self.config.has_section(name):
            self.config.add_section(name)
        
        self.config.set(name, "server", server)
        self.config.set(name, "token", token)
        if description:
            self.config.set(name, "description", description)
        
        self._save_config()
    
    def set_default_profile(self, name: str):
        """Set default profile."""
        if not self.config.has_section(self.DEFAULT_SECTION):
            self.config.add_section(self.DEFAULT_SECTION)
        
        self.config.set(self.DEFAULT_SECTION, "profile", name)
        self._save_config()
    
    def delete_profile(self, name: str):
        """Remove a profile."""
        if self.config.has_section(name):
            self.config.remove_section(name)
            self._save_config()
    
    def _save_config(self):
        """Save config to file with proper permissions."""
        self.CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
        
        with open(self.CONFIG_FILE, "w") as f:
            self.config.write(f)
        
        # Set permissions to 600 (user read/write only)
        os.chmod(self.CONFIG_FILE, 0o600)
    
    def print_profiles(self):
        """Print all profiles in readable format."""
        default = self.get_default_profile()
        profiles = self.list_profiles()
        
        if not profiles:
            print("No profiles configured.")
            print(f"\nCreate one at: {self.CONFIG_FILE}")
            print("""
Example:
[lab]
server = filewave.company.com
token = your_token_here

[production]
server = filewave.company.com
token = production_token_here
""")
            return
        
        print(f"Configured profiles:\n")
        for profile in profiles:
            profile_data = self._get_profile_by_name(profile)
            is_default = " (default)" if profile == default else ""
            description = f" — {profile_data['description']}" if profile_data.get('description') else ""
            print(f"  {profile}{is_default}{description}")
            print(f"    Server: {profile_data['server']}")
            print(f"    Token:  {profile_data['token'][:10]}..." if len(profile_data['token']) > 10 else f"    Token:  {profile_data['token']}")
            print()


def setup_wizard():
    """Interactive setup for creating a profile."""
    config = FileWaveConfig()
    
    print("FileWave Profile Setup\n")
    print(f"Config file: {config.CONFIG_FILE}\n")
    
    profile_name = input("Profile name (e.g., 'lab', 'production'): ").strip()
    if not profile_name:
        print("Profile name required.")
        return
    
    server = input("Server URL (e.g., 'filewave.company.com'): ").strip()
    if not server:
        print("Server URL required.")
        return
    
    # Normalize server URL
    if not server.startswith("http"):
        server = f"https://{server}"
    
    token = input("API Token (from FileWave Admin Console): ").strip()
    if not token:
        print("API Token required.")
        return
    
    description = input("Description (optional): ").strip()
    
    # Add profile
    config.add_profile(profile_name, server, token, description)
    
    # Set as default if first profile
    if not config.get_default_profile():
        config.set_default_profile(profile_name)
        print(f"\nProfile '{profile_name}' created and set as default.")
    else:
        print(f"\nProfile '{profile_name}' created.")
    
    print(f"Config saved to: {config.CONFIG_FILE}")
    print(f"Permissions: 600 (user read/write only)")


# Example usage
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_wizard()
    else:
        config = FileWaveConfig()
        config.print_profiles()
