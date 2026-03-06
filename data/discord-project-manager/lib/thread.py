#!/usr/bin/env python3
"""
Thread Management

Create and manage Discord forum threads with permissions.
"""

import json
import sys
from pathlib import Path
from typing import List, Optional

import registry
import discord_api
import permissions
import skill_config
import validators
import projects


class ThreadManager:
    """Manage Discord forum threads."""
    
    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize thread manager.
        
        Args:
            registry_path: Path to agents.json
        """
        self.registry = registry.AgentRegistry(registry_path)
        self.config = skill_config.SkillConfig()
        self.discord = discord_api.DiscordAPI()
        self.permissions = permissions.PermissionsManager(registry_path)
    
    def create_thread(self, name: str, owner: str,
                     participants: List[str],
                     mention_mode: bool = True,
                     message: Optional[str] = None,
                     forum_channel: Optional[str] = None,
                     description: str = "") -> dict:
        """Create a forum thread with permissions.
        
        Args:
            name: Thread name
            owner: Owner agent ID (free discussion)
            participants: List of participant agent IDs
            mention_mode: Enable mention-only mode for participants
            message: Initial message (optional)
            forum_channel: Forum channel ID (optional, uses default if not specified)
            description: Short description of the project
            
        Returns:
            Result dict with thread info and config result
        """
        # Validate inputs
        validators.validate_agent_id(owner)
        for p in participants:
            validators.validate_agent_id(p)
        if forum_channel:
            validators.validate_snowflake(forum_channel, "forum channel ID")
        
        # Determine forum channel
        if forum_channel:
            forum_id = forum_channel
            print(f"Using specified forum channel: {forum_id}")
        else:
            # Use default forum channel from config
            forum_id = self.config.get_default_forum()
            if not forum_id:
                raise ValueError(
                    "No default forum channel configured. "
                    "Run: ./scripts/cli.sh registry init"
                )
            print(f"Using default forum channel: {forum_id}")
        
        # Create thread
        print(f"Creating thread '{name}' in forum {forum_id}...")
        thread_result = self.discord.create_thread(
            forum_id, name, message
        )
        
        # Extract thread ID from response
        thread_id = thread_result.get('payload', {}).get('thread', {}).get('id')
        if not thread_id:
            raise ValueError(f"Failed to create thread: no thread id in response. Got: {thread_result}")
        
        print(f"✅ Thread created: {thread_id} (in forum {forum_id})")
        
        # Set permissions
        print(f"Setting permissions: owner={owner}, participants={','.join(participants)}")
        perm_result = self.permissions.set_thread_permissions(
            thread_id, owner, participants, mention_mode
        )
        
        print("✅ Permissions configured")
        print("⏳ Gateway restarting (2-5 seconds)...")
        
        # Register in projects.json
        projects.register_thread(
            thread_id, name, owner, participants, forum_id, description
        )
        print(f"📋 Project registered in projects.json")
        
        return {
            'thread': thread_result,
            'permissions': perm_result,
            'threadId': thread_id,
            'forumId': forum_id,
            'owner': owner,
            'participants': participants,
            'mentionMode': mention_mode
        }
    
    def archive_thread(self, thread_id: str) -> dict:
        """Archive a thread by removing all permissions.
        
        Args:
            thread_id: Discord thread ID
            
        Returns:
            Result dict with removed permissions
        """
        registry_data = self.registry.load()
        guild_id = registry_data.get('guild')
        
        if not guild_id:
            raise ValueError("Guild ID not set in registry")
        
        print(f"Archiving thread {thread_id}...")
        validators.validate_snowflake(thread_id, "thread ID")
        
        # Get all agents from registry
        agents = registry_data.get('agents', {})
        
        # Remove permissions for all agents
        import config as config_module
        config = config_module.OpenClawConfig()
        
        removed_accounts = []
        
        for agent_id, agent_info in agents.items():
            account_id = agent_info.get('accountId')
            if not account_id:
                continue
            
            # Use remove_channel_permission to delete the key (not set to null)
            try:
                config.remove_channel_permission(account_id, guild_id, thread_id)
                removed_accounts.append(account_id)
                print(f"  Removed {account_id}")
            except Exception as e:
                print(f"  Warning: Failed to remove {account_id}: {e}")
        
        print(f"✅ Thread archived: {thread_id}")
        print(f"   Removed {len(removed_accounts)} accounts")
        print("⏳ Gateway restarting (2-5 seconds)...")
        
        # Update projects.json
        projects.archive_thread(thread_id)
        print(f"📋 Project marked as archived in projects.json")
        
        return {
            'threadId': thread_id,
            'archived': True,
            'removedAccounts': removed_accounts
        }
    
    def get_thread_status(self, thread_id: str) -> dict:
        """Get thread permission status.
        
        Args:
            thread_id: Discord thread ID
            
        Returns:
            Dict with thread permissions and participants
        """
        registry_data = self.registry.load()
        guild_id = registry_data.get('guild')
        
        if not guild_id:
            raise ValueError("Guild ID not set in registry")
        
        import config as config_module
        config = config_module.OpenClawConfig()
        
        # Get all agents from registry
        agents = registry_data.get('agents', {})
        
        # Check permissions for each agent
        participants = []
        owner = None
        
        for agent_id, agent_info in agents.items():
            account_id = agent_info.get('accountId')
            if not account_id:
                continue
            
            channels = config.get_guild_channels(account_id, guild_id)
            channel_config = channels.get(thread_id)
            
            if channel_config and channel_config.get('allow'):
                require_mention = channel_config.get('requireMention', True)
                
                participant_info = {
                    'agent': agent_id,
                    'account': account_id,
                    'requireMention': require_mention
                }
                
                if not require_mention:
                    owner = agent_id
                
                participants.append(participant_info)
        
        return {
            'threadId': thread_id,
            'owner': owner,
            'participants': participants,
            'totalParticipants': len(participants)
        }
    
    def list_threads(self, active_only: bool = False,
                    archived_only: bool = False,
                    owner: Optional[str] = None) -> List[dict]:
        """List threads in the forum channel.
        
        Args:
            active_only: Only show active threads
            archived_only: Only show archived threads
            owner: Filter by owner agent ID
            
        Returns:
            List of thread info dicts
        """
        # Note: This requires Discord API integration
        # For now, return a placeholder
        # TODO: Implement Discord API call to list threads
        
        print("⚠️ Thread listing requires Discord API integration")
        print("   This feature will be implemented in Phase 2.2")
        
        return []


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: thread.py <command> [args]")
        print("Commands:")
        print("  create --name <name> --owner <agent> --participants <agents...> [--no-mention] [--message <text>]")
        print("  archive <thread_id>")
        print("  status <thread_id>")
        print("  list [--active] [--archived] [--owner <agent>]")
        sys.exit(1)
    
    manager = ThreadManager()
    command = sys.argv[1]
    
    if command == 'create':
        # Parse arguments
        args = sys.argv[2:]
        name = None
        owner = None
        participants = []
        mention_mode = True
        message = None
        forum_channel = None
        description = ""
        
        i = 0
        while i < len(args):
            if args[i] == '--name' and i + 1 < len(args):
                name = args[i + 1]
                i += 2
            elif args[i] == '--owner' and i + 1 < len(args):
                owner = args[i + 1]
                i += 2
            elif args[i] == '--participants' and i + 1 < len(args):
                participants = args[i + 1].split(',')
                i += 2
            elif args[i] == '--message' and i + 1 < len(args):
                message = args[i + 1]
                i += 2
            elif args[i] == '--forum-channel' and i + 1 < len(args):
                forum_channel = args[i + 1]
                i += 2
            elif args[i] == '--description' and i + 1 < len(args):
                description = args[i + 1]
                i += 2
            elif args[i] == '--no-mention':
                mention_mode = False
                i += 1
            else:
                i += 1
        
        if not name or not owner or not participants:
            print("Error: --name, --owner, and --participants are required")
            sys.exit(1)
        
        result = manager.create_thread(
            name, owner, participants, mention_mode, message, forum_channel, description
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == 'archive':
        if len(sys.argv) < 3:
            print("Error: thread_id required")
            sys.exit(1)
        
        result = manager.archive_thread(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == 'status':
        if len(sys.argv) < 3:
            print("Error: thread_id required")
            sys.exit(1)
        
        result = manager.get_thread_status(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == 'list':
        # Parse flags
        active_only = '--active' in sys.argv
        archived_only = '--archived' in sys.argv
        owner = None
        
        if '--owner' in sys.argv:
            idx = sys.argv.index('--owner')
            if idx + 1 < len(sys.argv):
                owner = sys.argv[idx + 1]
        
        result = manager.list_threads(active_only, archived_only, owner)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
