#!/usr/bin/env python3
"""
Agent Registry Management

Manages the agent registry (data/agents.json) with Discord information.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

import skill_config


class AgentRegistry:
    """Agent registry manager."""
    
    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize registry manager.
        
        Args:
            registry_path: Path to agents.json. Defaults to data/agents.json
        """
        if registry_path is None:
            skill_dir = Path(__file__).parent.parent
            registry_path = skill_dir / "data" / "agents.json"
        
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = skill_config.SkillConfig()
    
    def load(self) -> Dict:
        """Load registry from file.
        
        Returns:
            Registry dict with agents, guild, defaultForum, forumChannels
        """
        if not self.registry_path.exists():
            return {
                "agents": {},
                "guild": None,
                "defaultForum": None,
                "forumChannels": {}
            }
        
        with open(self.registry_path) as f:
            data = json.load(f)
            
        # Ensure new fields exist
        if "defaultForum" not in data:
            data["defaultForum"] = None
        if "forumChannels" not in data:
            data["forumChannels"] = {}
            
        return data
    
    def save(self, registry: Dict):
        """Save registry to file.
        
        Args:
            registry: Registry dict to save
        """
        with open(self.registry_path, 'w') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
    
    def init_from_config(self) -> Dict:
        """Initialize registry from OpenClaw config.
        
        Returns:
            Initialized registry dict
        """
        # Initialize skill config first
        config = self.config.init_from_openclaw()
        guild_id = config['guild']
        
        # Read OpenClaw config directly
        import os
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        
        try:
            with open(config_path) as f:
                openclaw_config = json.load(f)
        except Exception as e:
            raise Exception(f"Failed to read OpenClaw config: {e}")
        
        # Extract agent info
        agents = {}
        
        # Get Discord accounts
        discord_config = openclaw_config.get('channels', {}).get('discord', {})
        accounts = discord_config.get('accounts', {})
        
        # Get agent list
        agent_list = openclaw_config.get('agents', {}).get('list', [])
        
        for agent_config in agent_list:
            agent_id = agent_config.get('id')
            if not agent_id:
                continue
            
            # Find Discord account for this agent
            account_id = None
            user_id = None
            channel_id = None
            
            # Check if agent has a named account
            for acc_id, acc_config in accounts.items():
                if acc_id == agent_id or acc_config.get('name', '').lower() == agent_id:
                    account_id = acc_id
                    break
            
            # If no named account, might be using default
            if not account_id and agent_config.get('default'):
                account_id = 'default'
            
            # Get mention patterns
            mention_patterns = agent_config.get('groupChat', {}).get('mentionPatterns', [])
            
            # Get channel ID from heartbeat config
            heartbeat = agent_config.get('heartbeat', {})
            if heartbeat.get('target') == 'discord':
                channel_id = heartbeat.get('to')
            
            agents[agent_id] = {
                'accountId': account_id,
                'userId': user_id,  # Will be filled manually or via Discord API
                'channelId': channel_id,
                'mentionPatterns': mention_patterns
            }
        
        registry = {
            'agents': agents,
            'guild': guild_id,
            'defaultForum': None,  # Will be set manually
            'forumChannels': {}
        }
        
        self.save(registry)
        
        print(f"✅ Registry initialized")
        print(f"   Guild ID: {guild_id}")
        print(f"   Agents: {len(agents)}")
        print(f"   Default Forum: Not set (use 'forum-channel set-default <id>')")
        
        return registry
    
    def list_agents(self) -> List[Dict]:
        """List all agents in registry.
        
        Returns:
            List of agent dicts with id and info
        """
        registry = self.load()
        agents = []
        
        for agent_id, info in registry.get('agents', {}).items():
            agents.append({
                'id': agent_id,
                **info
            })
        
        return agents
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent info by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent info dict or None
        """
        registry = self.load()
        return registry.get('agents', {}).get(agent_id)
    
    def add_agent(self, agent_id: str, account_id: str, user_id: str,
                  channel_id: str, mention_patterns: List[str]):
        """Add or update agent in registry.
        
        Args:
            agent_id: Agent ID
            account_id: Discord account ID
            user_id: Discord user ID
            channel_id: Discord channel ID
            mention_patterns: Mention regex patterns
        """
        registry = self.load()
        
        if 'agents' not in registry:
            registry['agents'] = {}
        
        registry['agents'][agent_id] = {
            'accountId': account_id,
            'userId': user_id,
            'channelId': channel_id,
            'mentionPatterns': mention_patterns
        }
        
        self.save(registry)
    
    def remove_agent(self, agent_id: str):
        """Remove agent from registry.
        
        Args:
            agent_id: Agent ID
        """
        registry = self.load()
        
        if agent_id in registry.get('agents', {}):
            del registry['agents'][agent_id]
            self.save(registry)
    
    def set_guild(self, guild_id: str):
        """Set guild ID.
        
        Args:
            guild_id: Discord guild ID
        """
        self.config.set_guild(guild_id)
    
    def set_forum(self, forum_id: str):
        """Set forum channel ID.
        
        Args:
            forum_id: Discord forum channel ID
        """
        self.config.set_default_forum(forum_id)


def main():
    """CLI entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: registry.py <command> [args]")
        print("Commands:")
        print("  init              - Initialize from OpenClaw config")
        print("  list              - List all agents")
        print("  get <agent_id>    - Get agent info")
        print("  add <agent_id> <account_id> <user_id> <channel_id> <patterns...>")
        print("  remove <agent_id> - Remove agent")
        print("  set-guild <id>    - Set guild ID")
        print("  set-forum <id>    - Set forum channel ID")
        sys.exit(1)
    
    registry = AgentRegistry()
    command = sys.argv[1]
    
    if command == 'init':
        result = registry.init_from_config()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == 'list':
        agents = registry.list_agents()
        print(json.dumps(agents, indent=2, ensure_ascii=False))
    
    elif command == 'get':
        if len(sys.argv) < 3:
            print("Error: agent_id required")
            sys.exit(1)
        agent = registry.get_agent(sys.argv[2])
        if agent:
            print(json.dumps(agent, indent=2, ensure_ascii=False))
        else:
            print(f"Agent {sys.argv[2]} not found")
            sys.exit(1)
    
    elif command == 'add':
        if len(sys.argv) < 7:
            print("Error: add requires agent_id account_id user_id channel_id patterns...")
            sys.exit(1)
        agent_id = sys.argv[2]
        account_id = sys.argv[3]
        user_id = sys.argv[4]
        channel_id = sys.argv[5]
        patterns = sys.argv[6:]
        registry.add_agent(agent_id, account_id, user_id, channel_id, patterns)
        print(f"Added/updated agent: {agent_id}")
    
    elif command == 'remove':
        if len(sys.argv) < 3:
            print("Error: agent_id required")
            sys.exit(1)
        registry.remove_agent(sys.argv[2])
        print(f"Removed agent: {sys.argv[2]}")
    
    elif command == 'set-guild':
        if len(sys.argv) < 3:
            print("Error: guild_id required")
            sys.exit(1)
        registry.set_guild(sys.argv[2])
        print(f"Set guild: {sys.argv[2]}")
    
    elif command == 'set-forum':
        if len(sys.argv) < 3:
            print("Error: forum_id required")
            sys.exit(1)
        registry.set_forum(sys.argv[2])
        print(f"Set forum: {sys.argv[2]}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
