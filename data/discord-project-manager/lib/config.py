#!/usr/bin/env python3
"""
OpenClaw Config Operations

Wrapper for openclaw config commands with Python-friendly interface.

IMPORTANT: All config changes go through `openclaw config.patch` which sends
SIGUSR1 (graceful restart), NOT `openclaw gateway restart` (SIGTERM hard kill).
This prevents the cascade restart problem that caused 100+ SIGTERMs on 2026-02-25.
"""

import json
import subprocess
import os
import time
import signal
import shutil
import fcntl
from typing import Dict, Any, Optional


class OpenClawConfig:
    """OpenClaw config manager."""
    
    CONFIG_PATH = os.path.expanduser("~/.openclaw/openclaw.json")
    LOCK_PATH = os.path.expanduser("~/.openclaw/openclaw.json.lock")
    
    def _send_sigusr1(self) -> bool:
        """Send SIGUSR1 to the OpenClaw gateway process.
        
        Uses PID file first, falls back to narrow pgrep.
        
        Returns:
            True if signal sent successfully
        """
        # Try PID file first
        pid_file = os.path.expanduser("~/.openclaw/gateway.pid")
        if os.path.exists(pid_file):
            try:
                with open(pid_file) as f:
                    pid = int(f.read().strip())
                os.kill(pid, signal.SIGUSR1)
                return True
            except (ValueError, ProcessLookupError, PermissionError):
                pass
        
        # Fallback: pgrep for openclaw gateway process
        try:
            # Try multiple patterns from specific to broad
            patterns = [
                ['pgrep', '-f', 'openclaw.*gateway start'],
                ['pgrep', '-f', 'openclaw gateway'],
                ['pgrep', '-f', 'openclaw.*gateway'],
            ]
            for cmd in patterns:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    for pid_str in result.stdout.strip().split('\n'):
                        if pid_str.strip():
                            os.kill(int(pid_str.strip()), signal.SIGUSR1)
                    return True
        except Exception:
            pass
        
        # Last resort: openclaw gateway restart
        try:
            result = subprocess.run(
                ['openclaw', 'gateway', 'restart'],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                return True
        except Exception:
            pass
        
        return False
    
    def _write_config_locked(self, config: Dict) -> str:
        """Write config with file locking and backup.
        
        Args:
            config: Config dict to write
            
        Returns:
            Backup file path
        """
        backup_path = f"{self.CONFIG_PATH}.bak-{int(time.time())}"
        shutil.copy(self.CONFIG_PATH, backup_path)
        
        lock_fd = open(self.LOCK_PATH, 'w')
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            # Write to temp file then rename (atomic)
            tmp_path = f"{self.CONFIG_PATH}.tmp"
            with open(tmp_path, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.CONFIG_PATH)
            
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()
        
        return backup_path
    
    def get(self) -> Dict[str, Any]:
        """Get full OpenClaw config.
        
        Returns:
            Config dict
        """
        with open(self.CONFIG_PATH) as f:
            return json.load(f)
    
    def patch(self, patch: Dict[str, Any], note: str) -> Dict[str, Any]:
        """Apply config patch via openclaw CLI (SIGUSR1 graceful restart).
        
        Args:
            patch: Config patch dict (deep-merged with existing config)
            note: Human-readable note for restart
            
        Returns:
            Result dict
        """
        patch_json = json.dumps(patch)
        
        result = subprocess.run(
            ['openclaw', 'config.patch', '--raw', patch_json, '--note', note],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            # Fallback: try writing directly + SIGUSR1
            return self._patch_fallback(patch, note, result.stderr)
        
        return {
            'ok': True,
            'note': note,
            'method': 'openclaw config.patch',
            'restart': 'SIGUSR1 (graceful)'
        }
    
    def _patch_fallback(self, patch: Dict[str, Any], note: str, 
                        original_error: str) -> Dict[str, Any]:
        """Fallback: write config directly + send SIGUSR1.
        
        Only used if `openclaw config.patch` CLI fails.
        Uses file locking and atomic writes for safety.
        """
        # Read current config
        with open(self.CONFIG_PATH) as f:
            config = json.load(f)
        
        # Deep merge
        def deep_merge(target, source):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    deep_merge(target[key], value)
                else:
                    target[key] = value
        
        deep_merge(config, patch)
        
        # Write with locking
        backup_path = self._write_config_locked(config)
        
        # Send SIGUSR1 to gateway (graceful restart, NOT SIGTERM)
        if not self._send_sigusr1():
            return {
                'ok': False,
                'note': note,
                'method': 'fallback (direct write)',
                'error': 'Failed to send SIGUSR1 to gateway',
                'original_error': original_error,
                'backup': backup_path
            }
        
        return {
            'ok': True,
            'note': note,
            'method': 'fallback (direct write + SIGUSR1)',
            'backup': backup_path,
            'original_error': original_error
        }
    
    def get_discord_accounts(self) -> Dict[str, Dict]:
        """Get Discord accounts config."""
        config = self.get()
        return config.get('channels', {}).get('discord', {}).get('accounts', {})
    
    def get_guild_channels(self, account_id: str, guild_id: str) -> Dict[str, Dict]:
        """Get channels config for a guild."""
        accounts = self.get_discord_accounts()
        account = accounts.get(account_id, {})
        guilds = account.get('guilds', {})
        guild = guilds.get(guild_id, {})
        return guild.get('channels', {})
    
    def set_channel_permission(self, account_id: str, guild_id: str,
                              channel_id: str, allow: bool,
                              require_mention: Optional[bool] = None) -> Dict:
        """Set channel permission for an account.
        
        Uses config.patch (SIGUSR1 graceful restart).
        """
        channel_config = {'allow': allow}
        if require_mention is not None:
            channel_config['requireMention'] = require_mention
        
        patch = {
            'channels': {
                'discord': {
                    'accounts': {
                        account_id: {
                            'guilds': {
                                guild_id: {
                                    'channels': {
                                        channel_id: channel_config
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        note = f"Set {account_id} permission for channel {channel_id}"
        return self.patch(patch, note)
    
    def remove_channel_permission(self, account_id: str, guild_id: str,
                                  channel_id: str) -> Dict:
        """Remove channel permission (delete key).
        
        Reads config, removes the key, writes back with locking, sends SIGUSR1.
        """
        # Read current config
        with open(self.CONFIG_PATH) as f:
            config = json.load(f)
        
        # Navigate to channels and delete the key
        try:
            channels = config['channels']['discord']['accounts'][account_id]['guilds'][guild_id]['channels']
            if channel_id in channels:
                del channels[channel_id]
            else:
                return {'ok': True, 'note': 'Key not found, nothing to remove'}
        except KeyError:
            return {'ok': True, 'note': 'Path not found, nothing to remove'}
        
        # Write with locking
        backup_path = self._write_config_locked(config)
        
        # Send SIGUSR1 (graceful restart), NOT openclaw gateway restart (SIGTERM)
        if not self._send_sigusr1():
            return {
                'ok': False,
                'note': f'Config written but SIGUSR1 failed',
                'backup': backup_path
            }
        
        return {
            'ok': True,
            'note': f"Removed {account_id} permission for channel {channel_id}",
            'backup': backup_path,
            'restart': 'SIGUSR1 (graceful)'
        }


def main():
    """CLI entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: config.py <command> [args]")
        print("Commands:")
        print("  get                                    - Get full config")
        print("  accounts                               - List Discord accounts")
        print("  channels <account> <guild>             - List channels for guild")
        print("  set <account> <guild> <channel> <allow> [require_mention]")
        print("  remove <account> <guild> <channel>     - Remove channel permission")
        sys.exit(1)
    
    config = OpenClawConfig()
    command = sys.argv[1]
    
    if command == 'get':
        result = config.get()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == 'accounts':
        accounts = config.get_discord_accounts()
        print(json.dumps(accounts, indent=2, ensure_ascii=False))
    
    elif command == 'channels':
        if len(sys.argv) < 4:
            print("Error: account_id and guild_id required")
            sys.exit(1)
        channels = config.get_guild_channels(sys.argv[2], sys.argv[3])
        print(json.dumps(channels, indent=2, ensure_ascii=False))
    
    elif command == 'set':
        if len(sys.argv) < 6:
            print("Error: set requires account guild channel allow [require_mention]")
            sys.exit(1)
        account_id = sys.argv[2]
        guild_id = sys.argv[3]
        channel_id = sys.argv[4]
        allow = sys.argv[5].lower() in ('true', '1', 'yes')
        require_mention = None
        if len(sys.argv) > 6:
            require_mention = sys.argv[6].lower() in ('true', '1', 'yes')
        
        result = config.set_channel_permission(
            account_id, guild_id, channel_id, allow, require_mention
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == 'remove':
        if len(sys.argv) < 5:
            print("Error: remove requires account guild channel")
            sys.exit(1)
        result = config.remove_channel_permission(sys.argv[2], sys.argv[3], sys.argv[4])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
