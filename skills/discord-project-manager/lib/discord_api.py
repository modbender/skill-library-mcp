#!/usr/bin/env python3
"""
Discord API Wrapper

Simplified Discord operations using OpenClaw CLI and Discord REST API.
"""

import json
import os
import subprocess
from typing import Dict, Optional


class DiscordAPI:
    """Discord API wrapper using OpenClaw CLI and REST API."""
    
    DISCORD_API_BASE = "https://discord.com/api/v10"
    
    def __init__(self, channel: str = 'discord', bot_token: Optional[str] = None):
        """Initialize Discord API.
        
        Args:
            channel: Channel name (default: discord)
            bot_token: Discord bot token. If not provided, reads from OpenClaw config.
        """
        self.channel = channel
        self._bot_token = bot_token
    
    def _get_bot_token(self) -> str:
        """Get bot token from OpenClaw config (default account).
        
        Returns:
            Bot token string
        """
        if self._bot_token:
            return self._bot_token
        
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        with open(config_path) as f:
            config = json.load(f)
        
        # Try default account first, then top-level discord token
        accounts = config.get('channels', {}).get('discord', {}).get('accounts', {})
        if 'default' in accounts and 'token' in accounts['default']:
            self._bot_token = accounts['default']['token']
        else:
            self._bot_token = config.get('channels', {}).get('discord', {}).get('token', '')
        
        return self._bot_token
    
    def create_channel(self, guild_id: str, name: str, 
                       channel_type: int = 0,
                       topic: Optional[str] = None,
                       parent_id: Optional[str] = None) -> Dict:
        """Create a Discord channel via REST API.
        
        Args:
            guild_id: Guild ID
            name: Channel name
            channel_type: Channel type (0=text, 15=forum)
            topic: Channel topic/description
            parent_id: Parent category ID
            
        Returns:
            Created channel data from Discord API
        """
        token = self._get_bot_token()
        url = f"{self.DISCORD_API_BASE}/guilds/{guild_id}/channels"
        
        payload = {
            "name": name,
            "type": channel_type
        }
        if topic:
            payload["topic"] = topic
        if parent_id:
            payload["parent_id"] = parent_id
        
        import urllib.request
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Authorization': f'Bot {token}',
                'Content-Type': 'application/json',
                'User-Agent': 'DiscordBot (https://github.com/openclaw/openclaw, 1.0)'
            },
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            raise Exception(f"Channel creation failed ({e.code}): {body}")
        except urllib.error.URLError as e:
            raise Exception(f"Network error: {e.reason}")
        
        if 'id' not in data:
            raise Exception(f"Channel creation failed: {json.dumps(data)}")
        
        return data
    
    def create_thread(self, channel_id: str, name: str,
                     message: Optional[str] = None) -> Dict:
        """Create a forum thread.
        
        Args:
            channel_id: Forum channel ID
            name: Thread name
            message: Initial message (optional)
            
        Returns:
            Result dict with thread info
        """
        cmd = [
            'openclaw', 'message', 'thread', 'create',
            '--channel', self.channel,
            '--target', channel_id,
            '--thread-name', name,
            '--json'
        ]
        
        if message:
            cmd.extend(['-m', message])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            
            # Parse JSON output
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Thread creation failed: {e.stderr}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse response: {e}")
        except subprocess.TimeoutExpired:
            raise Exception("Thread creation timed out")
    
    def send_message(self, channel_id: str, message: str) -> Dict:
        """Send a message to a channel.
        
        Args:
            channel_id: Channel ID
            message: Message text
            
        Returns:
            Result dict
        """
        cmd = [
            'openclaw', 'message', 'send',
            '--channel', self.channel,
            '--target', channel_id,
            '--message', message,
            '--json'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=15
            )
            
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Message send failed: {e.stderr}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse response: {e}")
        except subprocess.TimeoutExpired:
            raise Exception("Message send timed out")


def main():
    """CLI entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: discord_api.py <command> [args]")
        print("Commands:")
        print("  create-thread <channel_id> <name> [message]")
        print("  send <channel_id> <message>")
        sys.exit(1)
    
    api = DiscordAPI()
    command = sys.argv[1]
    
    if command == 'create-thread':
        if len(sys.argv) < 4:
            print("Error: create-thread requires channel_id and name")
            sys.exit(1)
        channel_id = sys.argv[2]
        name = sys.argv[3]
        message = sys.argv[4] if len(sys.argv) > 4 else None
        
        result = api.create_thread(channel_id, name, message)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == 'send':
        if len(sys.argv) < 4:
            print("Error: send requires channel_id and message")
            sys.exit(1)
        result = api.send_message(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
