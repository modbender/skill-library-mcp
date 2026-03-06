import json
import os
from typing import Dict, Any, Optional

# Default configuration values
DEFAULT_CONFIG = {
    "proxy": "beeaVXlWtDSdzRin:beeVvI6kd02MB@hive.beeproxies.com:1337",
    "ct0_fix": False,
    "threads": 10,
    "update_console": True,
    "save_followers_count": False
}

# Path to the configuration file
CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")

def load_config() -> Dict[str, Any]:
    """
    Load configuration from the config.json file.
    If the file doesn't exist, return default configuration.
    
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    try:
        with open(CONFIG_FILE_PATH, "r") as f:
            config = json.load(f)
        
        # Merge with default config to ensure all required keys exist
        merged_config = DEFAULT_CONFIG.copy()
        merged_config.update(config)
        return merged_config
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load config file: {e}")
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]) -> bool:
    """
    Save configuration to the config.json file.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(CONFIG_FILE_PATH, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get a specific configuration value.
    
    Args:
        key (str): Configuration key
        default (Any, optional): Default value if key doesn't exist
        
    Returns:
        Any: Configuration value
    """
    config = load_config()
    return config.get(key, default)

def update_config_value(key: str, value: Any) -> bool:
    """
    Update a specific configuration value.
    
    Args:
        key (str): Configuration key
        value (Any): New value
        
    Returns:
        bool: True if successful, False otherwise
    """
    config = load_config()
    config[key] = value
    return save_config(config) 