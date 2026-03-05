#!/usr/bin/env python3
"""
Permissions Management

Manage Discord channel permissions for agents.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path

import registry
import config as config_module
import projects


class PermissionsManager:
    """Manage Discord channel permissions."""
    
    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize permissions manager.
        
        Args:
            registry_path: Path to agents.json
        """
        self.registry = registry.AgentRegistry(registry_path)
        self.config = config_module.OpenClawConfig()
    
    def set_thread_permissions(self, thread_id: str, owner: str,
                              participants: List[str],
                              mention_mode: bool = True) -> Dict:
        """Set permissions for a thread.
        
        Args:
            thread_id: Discord thread ID
            owner: Owner agent ID (free discussion)
            participants: List of participant agent IDs (mention-only)
            mention_mode: Enable mention-only mode for participants
            
        Returns:
            Result from config patch
        """
        registry = self.registry.load()
        guild_id = registry.get('guild')
        
        if not guild_id:
            raise ValueError("Guild ID not set in registry")
        
        # Build config patch
        patch = {
            'channels': {
                'discord': {
                    'accounts': {}
                }
            }
        }
        
        accounts = patch['channels']['discord']['accounts']
        
        # Owner: allow + no mention required
        owner_info = registry['agents'].get(owner)
        if not owner_info:
            raise ValueError(f"Agent {owner} not found in registry")
        
        owner_account = owner_info['accountId']
        accounts[owner_account] = {
            'guilds': {
                guild_id: {
                    'channels': {
                        thread_id: {
                            'allow': True,
                            'requireMention': False
                        }
                    }
                }
            }
        }
        
        # Participants: allow + mention required (if mention_mode)
        for participant in participants:
            if participant == owner:
                continue  # Skip owner
            
            participant_info = registry['agents'].get(participant)
            if not participant_info:
                print(f"Warning: Agent {participant} not found in registry, skipping")
                continue
            
            participant_account = participant_info['accountId']
            
            if participant_account not in accounts:
                accounts[participant_account] = {
                    'guilds': {
                        guild_id: {
                            'channels': {}
                        }
                    }
                }
            
            if guild_id not in accounts[participant_account]['guilds']:
                accounts[participant_account]['guilds'][guild_id] = {
                    'channels': {}
                }
            
            accounts[participant_account]['guilds'][guild_id]['channels'][thread_id] = {
                'allow': True,
                'requireMention': mention_mode
            }
        
        # Apply patch
        note = f"Set permissions for thread {thread_id}: owner={owner}, participants={','.join(participants)}"
        return self.config.patch(patch, note)
    
    def add_participant(self, thread_id: str, agent_id: str,
                       require_mention: bool = True) -> Dict:
        """Add a participant to a thread.
        
        Args:
            thread_id: Discord thread ID
            agent_id: Agent ID to add
            require_mention: Whether to require mention
            
        Returns:
            Result from config patch
        """
        registry = self.registry.load()
        guild_id = registry.get('guild')
        
        if not guild_id:
            raise ValueError("Guild ID not set in registry")
        
        agent_info = registry['agents'].get(agent_id)
        if not agent_info:
            raise ValueError(f"Agent {agent_id} not found in registry")
        
        account_id = agent_info['accountId']
        
        result = self.config.set_channel_permission(
            account_id, guild_id, thread_id, True, require_mention
        )
        
        # Sync to projects.json
        projects.add_participant(thread_id, agent_id)
        
        return result
    
    def add_participants(self, thread_id: str, agent_ids: List[str],
                        require_mention: bool = True) -> Dict:
        """Add multiple participants to a thread in a single config patch.
        
        Args:
            thread_id: Discord thread ID
            agent_ids: List of agent IDs to add
            require_mention: Whether to require mention
            
        Returns:
            Result from config patch
        """
        registry = self.registry.load()
        guild_id = registry.get('guild')
        
        if not guild_id:
            raise ValueError("Guild ID not set in registry")
        
        patch = {
            'channels': {
                'discord': {
                    'accounts': {}
                }
            }
        }
        accounts = patch['channels']['discord']['accounts']
        added = []
        skipped = []
        
        for agent_id in agent_ids:
            agent_info = registry['agents'].get(agent_id)
            if not agent_info:
                skipped.append(agent_id)
                print(f"Warning: Agent {agent_id} not found in registry, skipping")
                continue
            
            account_id = agent_info['accountId']
            if not account_id:
                skipped.append(agent_id)
                print(f"Warning: Agent {agent_id} has no accountId, skipping")
                continue
            
            accounts[account_id] = {
                'guilds': {
                    guild_id: {
                        'channels': {
                            thread_id: {
                                'allow': True,
                                'requireMention': require_mention
                            }
                        }
                    }
                }
            }
            added.append(agent_id)
            
            # Sync to projects.json
            projects.add_participant(thread_id, agent_id)
        
        if not added:
            return {'ok': False, 'error': 'No valid agents to add', 'skipped': skipped}
        
        note = f"Add {','.join(added)} to thread {thread_id} (mention={require_mention})"
        result = self.config.patch(patch, note)
        result['added'] = added
        result['skipped'] = skipped
        return result
    
    def remove_participant(self, thread_id: str, agent_id: str) -> Dict:
        """Remove a participant from a thread.
        
        Args:
            thread_id: Discord thread ID
            agent_id: Agent ID to remove
            
        Returns:
            Result from config patch
        """
        registry = self.registry.load()
        guild_id = registry.get('guild')
        
        if not guild_id:
            raise ValueError("Guild ID not set in registry")
        
        agent_info = registry['agents'].get(agent_id)
        if not agent_info:
            raise ValueError(f"Agent {agent_id} not found in registry")
        
        account_id = agent_info['accountId']
        
        result = self.config.remove_channel_permission(
            account_id, guild_id, thread_id
        )
        
        # Sync to projects.json
        projects.remove_participant(thread_id, agent_id)
        
        return result
    
    def remove_participants(self, thread_id: str, agent_ids: List[str]) -> Dict:
        """Remove multiple participants from a thread.
        
        Args:
            thread_id: Discord thread ID
            agent_ids: List of agent IDs to remove
            
        Returns:
            Result dict
        """
        registry = self.registry.load()
        guild_id = registry.get('guild')
        
        if not guild_id:
            raise ValueError("Guild ID not set in registry")
        
        removed = []
        skipped = []
        
        for agent_id in agent_ids:
            agent_info = registry['agents'].get(agent_id)
            if not agent_info:
                skipped.append(agent_id)
                print(f"Warning: Agent {agent_id} not found in registry, skipping")
                continue
            
            account_id = agent_info['accountId']
            if not account_id:
                skipped.append(agent_id)
                print(f"Warning: Agent {agent_id} has no accountId, skipping")
                continue
            
            try:
                self.config.remove_channel_permission(account_id, guild_id, thread_id)
                removed.append(agent_id)
                projects.remove_participant(thread_id, agent_id)
            except Exception as e:
                skipped.append(agent_id)
                print(f"Warning: Failed to remove {agent_id}: {e}")
        
        return {
            'ok': len(removed) > 0,
            'threadId': thread_id,
            'removed': removed,
            'skipped': skipped
        }
    
    def set_mention_mode(self, thread_id: str, agents: List[str],
                        mode: bool) -> Dict:
        """Set mention mode for agents in a thread.
        
        Args:
            thread_id: Discord thread ID
            agents: List of agent IDs
            mode: True = mention-only, False = free discussion
            
        Returns:
            Result from config patch
        """
        registry = self.registry.load()
        guild_id = registry.get('guild')
        
        if not guild_id:
            raise ValueError("Guild ID not set in registry")
        
        # Build config patch
        patch = {
            'channels': {
                'discord': {
                    'accounts': {}
                }
            }
        }
        
        accounts = patch['channels']['discord']['accounts']
        applied = []
        
        for agent_id in agents:
            agent_info = registry['agents'].get(agent_id)
            if not agent_info:
                print(f"Warning: Agent {agent_id} not found in registry, skipping")
                continue
            
            account_id = agent_info['accountId']
            if not account_id:
                print(f"Warning: Agent {agent_id} has no accountId, skipping")
                continue
            
            accounts[account_id] = {
                'guilds': {
                    guild_id: {
                        'channels': {
                            thread_id: {
                                'allow': True,  # Keep access permission
                                'requireMention': mode
                            }
                        }
                    }
                }
            }
            applied.append(agent_id)
        
        if not applied:
            return {'ok': False, 'error': 'No valid agents to update'}
        
        # Apply patch
        mode_str = "mention-only" if mode else "free discussion"
        note = f"Set {mode_str} for thread {thread_id}: agents={','.join(applied)}"
        result = self.config.patch(patch, note)
        result['applied'] = applied
        return result
    
    def set_mention_mode_all(self, thread_id: str, mode: bool) -> Dict:
        """Set mention mode for ALL agents that currently have access to a thread.
        
        Scans the live OpenClaw config to find every account with a channel entry
        for this thread, then sets requireMention for all of them.
        
        Args:
            thread_id: Discord thread ID
            mode: True = mention-only, False = free discussion
            
        Returns:
            Result from config patch
        """
        registry = self.registry.load()
        guild_id = registry.get('guild')
        
        if not guild_id:
            raise ValueError("Guild ID not set in registry")
        
        # Read live config to find ALL accounts with access
        full_config = self.config.get()
        discord_accounts = full_config.get('channels', {}).get('discord', {}).get('accounts', {})
        
        patch = {
            'channels': {
                'discord': {
                    'accounts': {}
                }
            }
        }
        accounts = patch['channels']['discord']['accounts']
        applied = []
        
        for account_id, acc_config in discord_accounts.items():
            guilds = acc_config.get('guilds', {})
            guild_config = guilds.get(guild_id, {})
            channels = guild_config.get('channels', {})
            
            if thread_id in channels and channels[thread_id].get('allow'):
                accounts[account_id] = {
                    'guilds': {
                        guild_id: {
                            'channels': {
                                thread_id: {
                                    'allow': True,
                                    'requireMention': mode
                                }
                            }
                        }
                    }
                }
                # Resolve account_id to agent name for display
                agent_name = self._account_to_agent(registry, account_id)
                applied.append(agent_name or account_id)
        
        if not applied:
            return {'ok': False, 'error': f'No agents found with access to thread {thread_id}'}
        
        mode_str = "mention-only" if mode else "free discussion"
        note = f"Set {mode_str} for ALL in thread {thread_id}: {','.join(applied)}"
        result = self.config.patch(patch, note)
        result['applied'] = applied
        return result
    
    def _account_to_agent(self, registry: Dict, account_id: str) -> Optional[str]:
        """Resolve an account ID back to an agent name.
        
        Args:
            registry: Loaded registry dict
            account_id: Discord account ID
            
        Returns:
            Agent name or None
        """
        for agent_id, info in registry.get('agents', {}).items():
            if info.get('accountId') == account_id:
                return agent_id
        return None


def main():
    """CLI entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: permissions.py <command> [args]")
        print("Commands:")
        print("  set-thread <thread_id> <owner> <participants...> [--no-mention]")
        print("  add <thread_id> <agent1> [agent2...] [--no-mention]")
        print("  remove <thread_id> <agent1> [agent2...]")
        print("  mention-mode <thread_id> <on|off> <agents...|--all>")
        sys.exit(1)
    
    manager = PermissionsManager()
    command = sys.argv[1]
    
    if command == 'set-thread':
        if len(sys.argv) < 5:
            print("Error: set-thread requires thread_id owner participants...")
            sys.exit(1)
        
        thread_id = sys.argv[2]
        owner = sys.argv[3]
        
        # Parse participants and flags
        participants = []
        mention_mode = True
        
        for arg in sys.argv[4:]:
            if arg == '--no-mention':
                mention_mode = False
            else:
                participants.append(arg)
        
        result = manager.set_thread_permissions(
            thread_id, owner, participants, mention_mode
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == 'add':
        if len(sys.argv) < 4:
            print("Error: add requires thread_id agent_id [agent_id...]")
            sys.exit(1)
        
        thread_id = sys.argv[2]
        require_mention = '--no-mention' not in sys.argv
        
        # Collect agent IDs (everything after thread_id that isn't a flag)
        agent_ids = [a for a in sys.argv[3:] if not a.startswith('--')]
        
        if len(agent_ids) == 1:
            result = manager.add_participant(thread_id, agent_ids[0], require_mention)
        else:
            result = manager.add_participants(thread_id, agent_ids, require_mention)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == 'remove':
        if len(sys.argv) < 4:
            print("Error: remove requires thread_id agent_id [agent_id...]")
            sys.exit(1)
        
        thread_id = sys.argv[2]
        agent_ids = sys.argv[3:]
        
        if len(agent_ids) == 1:
            result = manager.remove_participant(thread_id, agent_ids[0])
        else:
            result = manager.remove_participants(thread_id, agent_ids)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == 'mention-mode':
        if len(sys.argv) < 4:
            print("Error: mention-mode requires thread_id on|off [agents...|--all]")
            sys.exit(1)
        
        thread_id = sys.argv[2]
        mode = sys.argv[3].lower() in ('on', 'true', '1')
        
        if '--all' in sys.argv[4:]:
            # Apply to ALL agents with access to this thread
            result = manager.set_mention_mode_all(thread_id, mode)
        else:
            agents = [a for a in sys.argv[4:] if not a.startswith('--')]
            if not agents:
                print("Error: specify agent names or use --all")
                sys.exit(1)
            result = manager.set_mention_mode(thread_id, agents, mode)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
