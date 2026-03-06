#!/usr/bin/env python3
"""
Forum Channel Management

Manage Discord Forum Channels for large projects.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

import discord_api
import registry as registry_module
import skill_config


class ForumChannelManager:
    """Forum Channel manager."""
    
    def __init__(self, registry_path: Optional[str] = None):
        """Initialize Forum Channel manager.
        
        Args:
            registry_path: Path to registry file (default: data/agents.json)
        """
        if registry_path is None:
            skill_dir = Path(__file__).parent.parent
            registry_path = skill_dir / 'data' / 'agents.json'
        
        self.registry = registry_module.AgentRegistry(registry_path)
        self.config = skill_config.SkillConfig()
        self.discord = discord_api.DiscordAPI()
    
    def create_forum_channel(self, name: str, emoji: Optional[str] = None,
                             description: Optional[str] = None) -> Dict:
        """Create a Forum Channel directly via Discord API.
        
        Args:
            name: Channel name
            emoji: Channel emoji (optional)
            description: Channel description (optional)
            
        Returns:
            Dict with created channel info
        """
        guild_id = self.config.get_guild()
        
        if not guild_id:
            raise ValueError(
                "Guild ID not configured. Run: discord-pm.py registry init"
            )
        
        # Format channel name
        if emoji:
            channel_name = f"{emoji}-{name}"
        else:
            channel_name = name
        
        # Create via Discord REST API
        print(f"Creating forum channel: {channel_name}...")
        data = self.discord.create_channel(
            guild_id=guild_id,
            name=channel_name,
            channel_type=15,  # Forum
            topic=description
        )
        
        channel_id = data['id']
        
        # Auto-register to registry
        registry_data = self.registry.load()
        if 'forumChannels' not in registry_data:
            registry_data['forumChannels'] = {}
        registry_data['forumChannels'][name] = channel_id
        self.registry.save(registry_data)
        
        print(f"✅ Forum channel created: {channel_name} ({channel_id})")
        print(f"   Registered as: {name}")
        
        return {
            'channelId': channel_id,
            'name': channel_name,
            'registryName': name,
            'guildId': guild_id,
            'type': 'forum'
        }
    
    def create_forum_channel_guide(self, name: str, emoji: Optional[str] = None,
                                   description: Optional[str] = None) -> Dict:
        """Generate guide for creating a Forum Channel (legacy fallback).
        
        Args:
            name: Channel name
            emoji: Channel emoji (optional)
            description: Channel description (optional)
            
        Returns:
            Guide dict with instructions
        """
        guild_id = self.config.get_guild()
        
        if not guild_id:
            raise ValueError(
                "Guild ID not configured. Run: discord-pm.py registry init"
            )
        
        if emoji:
            channel_name = f"{emoji}-{name}"
        else:
            channel_name = name
        
        guide = {
            'action': 'channel-create',
            'channel': 'discord',
            'guildId': guild_id,
            'name': channel_name,
            'type': 15
        }
        
        if description:
            guide['topic'] = description
        
        return guide
    
    def set_default_forum(self, channel_id: str) -> Dict:
        """Set default Forum Channel.
        
        Args:
            channel_id: Discord channel ID
            
        Returns:
            Updated registry
        """
        # Update both config.json and agents.json
        self.config.set_default_forum(channel_id)
        
        registry_data = self.registry.load()
        registry_data['defaultForum'] = channel_id
        self.registry.save(registry_data)
        
        print(f"✅ Set default forum: {channel_id}")
        print(f"   Updated: config.json + agents.json")
        return registry_data
    
    def add_forum_channel(self, channel_id: str, name: str) -> Dict:
        """Add a Forum Channel to registry.
        
        Args:
            channel_id: Discord channel ID
            name: Project name
            
        Returns:
            Updated registry
        """
        registry_data = self.registry.load()
        
        if 'forumChannels' not in registry_data:
            registry_data['forumChannels'] = {}
        
        registry_data['forumChannels'][name] = channel_id
        self.registry.save(registry_data)
        
        print(f"Added forum channel: {name} -> {channel_id}")
        return registry_data
    
    def remove_forum_channel(self, name: str) -> Dict:
        """Remove a Forum Channel from registry.
        
        Args:
            name: Project name
            
        Returns:
            Updated registry
        """
        registry_data = self.registry.load()
        
        if 'forumChannels' not in registry_data:
            raise ValueError("No forum channels in registry")
        
        if name not in registry_data['forumChannels']:
            raise ValueError(f"Forum channel '{name}' not found")
        
        del registry_data['forumChannels'][name]
        self.registry.save(registry_data)
        
        print(f"Removed forum channel: {name}")
        return registry_data
    
    def list_forum_channels(self) -> Dict:
        """List all Forum Channels.
        
        Returns:
            Dict of forum channels
        """
        registry_data = self.registry.load()
        
        result = {
            'defaultForum': registry_data.get('defaultForum'),
            'forumChannels': registry_data.get('forumChannels', {})
        }
        
        return result
    
    def get_or_create_default_forum(self) -> str:
        """Get default Forum Channel, create if not exists.
        
        Returns:
            Default forum channel ID
        """
        registry_data = self.registry.load()
        default_forum = registry_data.get('defaultForum')
        
        if default_forum:
            return default_forum
        
        # No default forum, need to create
        print("No default forum channel found.")
        print("Please create a forum channel in Discord (e.g., 🎯-projects),")
        print("then run: ./scripts/cli.sh forum-channel set-default <channel_id>")
        
        raise ValueError("No default forum channel configured")


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: forum.py <command> [args]")
        print("Commands:")
        print("  guide <name> [--emoji <emoji>] [--description <text>]")
        print("  set-default <channel_id>           - Set default forum channel")
        print("  add <channel_id> <name>            - Add forum channel to registry")
        print("  remove <name>                      - Remove forum channel from registry")
        print("  list                               - List all forum channels")
        sys.exit(1)
    
    manager = ForumChannelManager()
    command = sys.argv[1]
    
    if command == 'create':
        if len(sys.argv) < 3:
            print("Error: create requires name")
            sys.exit(1)
        
        name = sys.argv[2]
        emoji = None
        description = None
        
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == '--emoji' and i + 1 < len(sys.argv):
                emoji = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--description' and i + 1 < len(sys.argv):
                description = sys.argv[i + 1]
                i += 2
            else:
                print(f"Error: unknown argument '{sys.argv[i]}'")
                sys.exit(1)
        
        result = manager.create_forum_channel(name, emoji, description)
        print(json.dumps(result, indent=2))
    
    elif command == 'guide':
        if len(sys.argv) < 3:
            print("Error: guide requires name")
            sys.exit(1)
        
        name = sys.argv[2]
        emoji = None
        description = None
        
        # Parse optional arguments
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == '--emoji' and i + 1 < len(sys.argv):
                emoji = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--description' and i + 1 < len(sys.argv):
                description = sys.argv[i + 1]
                i += 2
            else:
                print(f"Error: unknown argument '{sys.argv[i]}'")
                sys.exit(1)
        
        result = manager.create_forum_channel_guide(name, emoji, description)
        print(json.dumps(result, indent=2))
    
    elif command == 'set-default':
        if len(sys.argv) < 3:
            print("Error: set-default requires channel_id")
            sys.exit(1)
        
        channel_id = sys.argv[2]
        result = manager.set_default_forum(channel_id)
        print(json.dumps(result, indent=2))
    
    elif command == 'add':
        if len(sys.argv) < 4:
            print("Error: add requires channel_id and name")
            sys.exit(1)
        
        channel_id = sys.argv[2]
        name = sys.argv[3]
        result = manager.add_forum_channel(channel_id, name)
        print(json.dumps(result, indent=2))
    
    elif command == 'remove':
        if len(sys.argv) < 3:
            print("Error: remove requires name")
            sys.exit(1)
        
        name = sys.argv[2]
        result = manager.remove_forum_channel(name)
        print(json.dumps(result, indent=2))
    
    elif command == 'list':
        result = manager.list_forum_channels()
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Error: unknown command '{command}'")
        sys.exit(1)


if __name__ == '__main__':
    main()
