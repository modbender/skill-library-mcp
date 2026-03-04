#!/usr/bin/env python3
"""
Unregister personality-switcher Telegram commands from gateway config.
Usage: python3 unregister_telegram_commands.py

Removes /personality, /create_personality, /rename_personality, /delete_personality
from channels.telegram.customCommands in the gateway config.
"""

import json
import sys
from pathlib import Path

def unregister_commands():
    """Unregister personality commands from gateway config."""
    
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
        
        # Check if channels.telegram.customCommands exists
        if ("channels" not in config or 
            "telegram" not in config["channels"] or
            "customCommands" not in config["channels"]["telegram"]):
            return {
                "status": "success",
                "message": "No custom commands to remove.",
                "removed_count": 0
            }
        
        # Commands to remove
        commands_to_remove = {
            "personality",
            "create_personality",
            "rename_personality",
            "delete_personality"
        }
        
        # Filter out personality commands
        current_commands = config["channels"]["telegram"]["customCommands"]
        if not isinstance(current_commands, list):
            current_commands = []
        
        original_count = len(current_commands)
        filtered_commands = [
            c for c in current_commands 
            if c.get("command") not in commands_to_remove
        ]
        removed_count = original_count - len(filtered_commands)
        
        # Update config
        config["channels"]["telegram"]["customCommands"] = filtered_commands
        
        # Write back config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {
            "status": "success",
            "message": f"Removed {removed_count} personality command(s) from Telegram config.",
            "removed_count": removed_count,
            "remaining_commands": len(filtered_commands)
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to unregister commands: {str(e)}",
            "code": "unregistration_failed"
        }

def main():
    result = unregister_commands()
    print(json.dumps(result))
    
    # Exit with error code if failed
    if result["status"] == "error":
        sys.exit(1)

if __name__ == "__main__":
    main()
