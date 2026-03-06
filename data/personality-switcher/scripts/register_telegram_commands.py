#!/usr/bin/env python3
"""
Register personality-switcher Telegram commands in gateway config.
Usage: python3 register_telegram_commands.py

Adds /personality, /create_personality, /rename_personality, /delete_personality
to channels.telegram.customCommands in the gateway config.
"""

import json
import sys
import os
from pathlib import Path

def register_commands():
    """Register personality commands in gateway config."""
    
    try:
        # Read the gateway config
        config_path = Path.home() / ".openclaw" / "openclaw.json"
        
        if not config_path.exists():
            return {
                "status": "error",
                "message": "Gateway config not found.",
                "code": "config_not_found"
            }
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Ensure channels.telegram.customCommands exists
        if "channels" not in config:
            config["channels"] = {}
        if "telegram" not in config["channels"]:
            config["channels"]["telegram"] = {}
        if "customCommands" not in config["channels"]["telegram"]:
            config["channels"]["telegram"]["customCommands"] = []
        
        # Define personality commands
        commands = [
            {
                "command": "personality",
                "description": "List or switch AI personalities"
            },
            {
                "command": "create_personality",
                "description": "Create a new personality"
            },
            {
                "command": "rename_personality",
                "description": "Rename a personality"
            },
            {
                "command": "delete_personality",
                "description": "Delete a personality"
            }
        ]
        
        # Get current commands
        current_commands = config["channels"]["telegram"]["customCommands"]
        if not isinstance(current_commands, list):
            current_commands = []
        
        # Add personality commands if not already present
        added_count = 0
        for cmd in commands:
            # Check if command already exists
            exists = any(c.get("command") == cmd["command"] for c in current_commands)
            if not exists:
                current_commands.append(cmd)
                added_count += 1
        
        # Write back config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {
            "status": "success",
            "message": f"Registered {added_count} personality command(s) in Telegram config.",
            "added_count": added_count,
            "total_commands": len(current_commands)
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to register commands: {str(e)}",
            "code": "registration_failed"
        }

def main():
    result = register_commands()
    print(json.dumps(result))
    
    # Exit with error code if failed
    if result["status"] == "error":
        sys.exit(1)

if __name__ == "__main__":
    main()
