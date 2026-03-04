#!/usr/bin/env python3
"""
Configuration Management

Manages skill configuration (guild ID, default forum, etc.)
"""

import json
from pathlib import Path
from typing import Dict, Optional


class SkillConfig:
    """Skill configuration manager."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config manager.
        
        Args:
            config_path: Path to config.json. Defaults to data/config.json
        """
        if config_path is None:
            skill_dir = Path(__file__).parent.parent
            config_path = skill_dir / "data" / "config.json"
        
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> Dict:
        """Load configuration from file.
        
        Returns:
            Config dict with guild, defaultForum, registryPath
        """
        if not self.config_path.exists():
            return self._get_default_config()
        
        with open(self.config_path) as f:
            return json.load(f)
    
    def save(self, config: Dict):
        """Save configuration to file.
        
        Args:
            config: Config dict to save
        """
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def _get_default_config(self) -> Dict:
        """Get default configuration.
        
        Returns:
            Default config dict
        """
        return {
            "guild": None,
            "defaultForum": None,
            "registryPath": "./data/agents.json"
        }
    
    def init_from_openclaw(self) -> Dict:
        """Initialize configuration from OpenClaw config.
        
        Returns:
            Initialized config dict
        """
        import os
        
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        
        try:
            with open(config_path) as f:
                openclaw_config = json.load(f)
        except Exception as e:
            raise Exception(f"Failed to read OpenClaw config: {e}")
        
        # Extract guild ID from Discord config
        guild_id = None
        discord_config = openclaw_config.get('channels', {}).get('discord', {})
        accounts = discord_config.get('accounts', {})
        
        for account_config in accounts.values():
            guilds = account_config.get('guilds', {})
            if guilds:
                guild_id = list(guilds.keys())[0]
                break
        
        if not guild_id:
            raise Exception("No Discord guild found in OpenClaw config")
        
        config = {
            "guild": guild_id,
            "defaultForum": None,  # User must set manually
            "registryPath": "./data/agents.json"
        }
        
        self.save(config)
        
        print(f"✅ Configuration initialized")
        print(f"   Guild ID: {guild_id}")
        print(f"   Default Forum: Not set (use 'forum-channel set-default <id>')")
        
        return config
    
    def get_guild(self) -> Optional[str]:
        """Get guild ID from config.
        
        Returns:
            Guild ID or None
        """
        config = self.load()
        return config.get('guild')
    
    def get_default_forum(self) -> Optional[str]:
        """Get default forum channel ID from config.
        
        Returns:
            Default forum ID or None
        """
        config = self.load()
        return config.get('defaultForum')
    
    def set_guild(self, guild_id: str):
        """Set guild ID.
        
        Args:
            guild_id: Discord guild ID
        """
        config = self.load()
        config['guild'] = guild_id
        self.save(config)
    
    def set_default_forum(self, forum_id: str):
        """Set default forum channel ID.
        
        Args:
            forum_id: Discord forum channel ID
        """
        config = self.load()
        config['defaultForum'] = forum_id
        self.save(config)


def main():
    """CLI entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: skill_config.py <command> [args]")
        print("Commands:")
        print("  init              - Initialize from OpenClaw config")
        print("  get               - Show current configuration")
        print("  set-guild <id>    - Set guild ID")
        print("  set-forum <id>    - Set default forum ID")
        sys.exit(1)
    
    config_mgr = SkillConfig()
    command = sys.argv[1]
    
    if command == 'init':
        config = config_mgr.init_from_openclaw()
        print(json.dumps(config, indent=2))
    
    elif command == 'get':
        config = config_mgr.load()
        print(json.dumps(config, indent=2))
    
    elif command == 'set-guild':
        if len(sys.argv) < 3:
            print("Error: set-guild requires guild_id")
            sys.exit(1)
        config_mgr.set_guild(sys.argv[2])
        print(f"✅ Guild ID set: {sys.argv[2]}")
    
    elif command == 'set-forum':
        if len(sys.argv) < 3:
            print("Error: set-forum requires forum_id")
            sys.exit(1)
        config_mgr.set_default_forum(sys.argv[2])
        print(f"✅ Default forum set: {sys.argv[2]}")
    
    else:
        print(f"Error: unknown command '{command}'")
        sys.exit(1)


if __name__ == '__main__':
    main()
