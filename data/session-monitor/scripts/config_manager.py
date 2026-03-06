#!/usr/bin/env python3
"""
Session Monitor Configuration Manager
Handles user preferences for token display and monitoring features.
"""

import os
import json
from pathlib import Path

class ConfigManager:
    def __init__(self, workspace_path=None):
        self.workspace = Path(workspace_path or os.getenv('OPENCLAW_WORKSPACE', '/home/admin/.openclaw/workspace'))
        self.config_file = self.workspace / 'session_monitor_config.json'
        self.default_config = {
            'token_display': True,
            'display_position': 'bottom',  # 'top', 'bottom', 'none'
            'show_model_info': True,
            'show_context_usage': True,
            'compact_mode': True,
            'auto_save_session': True
        }
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or return defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults to handle new config options
                    merged = self.default_config.copy()
                    merged.update(config)
                    return merged
            except (json.JSONDecodeError, IOError):
                pass
        return self.default_config.copy()
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except IOError:
            return False
    
    def get_setting(self, key, default=None):
        """Get a specific configuration setting."""
        return self.config.get(key, default or self.default_config.get(key))
    
    def set_setting(self, key, value):
        """Set a configuration setting and save to file."""
        self.config[key] = value
        return self.save_config()
    
    def toggle_token_display(self):
        """Toggle token display on/off."""
        current = self.get_setting('token_display')
        self.set_setting('token_display', not current)
        return not current
    
    def set_display_position(self, position):
        """Set where to display the token info."""
        if position in ['top', 'bottom', 'none']:
            return self.set_setting('display_position', position)
        return False
    
    def get_status_string(self):
        """Get current configuration status as string."""
        display = "ON" if self.get_setting('token_display') else "OFF"
        position = self.get_setting('display_position')
        compact = "COMPACT" if self.get_setting('compact_mode') else "DETAILED"
        return f"Token Display: {display} | Position: {position} | Mode: {compact}"