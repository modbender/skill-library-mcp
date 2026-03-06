"""Configuration management for anydocs profiles."""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List


class ConfigManager:
    """Manages anydocs configuration profiles."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize config manager.
        
        Args:
            config_dir: Config directory. Defaults to ~/.anydocs
        """
        if config_dir is None:
            config_dir = os.path.expanduser("~/.anydocs")
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        self._load_configs()
    
    def _load_configs(self) -> None:
        """Load all configurations from disk."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self.configs = json.load(f)
            except Exception:
                self.configs = {}
        else:
            self.configs = {}
    
    def _save_configs(self) -> None:
        """Save configurations to disk."""
        with open(self.config_file, "w") as f:
            json.dump(self.configs, f, indent=2)
    
    def add_profile(self, name: str, base_url: str, sitemap_url: str,
                    search_method: str = "hybrid", cache_ttl_days: int = 7) -> None:
        """
        Add or update a configuration profile.
        
        Args:
            name: Profile name (e.g., "discord", "openclaw")
            base_url: Base documentation URL
            sitemap_url: Sitemap URL
            search_method: "keyword", "semantic", or "hybrid"
            cache_ttl_days: Cache TTL in days
        """
        # Validate inputs
        if not name.strip():
            raise ValueError("Profile name cannot be empty")
        if not base_url.strip():
            raise ValueError("base_url cannot be empty")
        if not sitemap_url.strip():
            raise ValueError("sitemap_url cannot be empty")
        if search_method not in ["keyword", "semantic", "hybrid"]:
            raise ValueError("search_method must be 'keyword', 'semantic', or 'hybrid'")
        
        self.configs[name] = {
            "name": name,
            "base_url": base_url.rstrip("/"),
            "sitemap_url": sitemap_url,
            "search_method": search_method,
            "cache_ttl_days": cache_ttl_days,
        }
        self._save_configs()
    
    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a configuration profile.
        
        Args:
            name: Profile name
        
        Returns:
            Profile dict or None if not found
        """
        return self.configs.get(name)
    
    def list_profiles(self) -> List[str]:
        """Get list of all profile names."""
        return sorted(self.configs.keys())
    
    def delete_profile(self, name: str) -> bool:
        """
        Delete a profile.
        
        Returns:
            True if deleted, False if not found
        """
        if name in self.configs:
            del self.configs[name]
            self._save_configs()
            return True
        return False
    
    def validate_profile(self, name: str) -> tuple[bool, str]:
        """
        Validate that a profile exists and has required fields.
        
        Returns:
            (is_valid, error_message)
        """
        if name not in self.configs:
            return False, f"Profile '{name}' not found"
        
        config = self.configs[name]
        required = ["name", "base_url", "sitemap_url"]
        
        for field in required:
            if field not in config or not config[field]:
                return False, f"Profile missing required field: {field}"
        
        return True, ""
    
    def get_all_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get all profiles."""
        return self.configs.copy()
