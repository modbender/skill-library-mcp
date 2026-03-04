"""
Configuration management for Composio Composer X Skill.
"""

import os
from typing import Optional, Dict
from dataclasses import dataclass, field


@dataclass
class ComposioConfig:
    """Configuration for Composio Composer X Skill."""
    
    # Composio API configuration
    client_id: str = ""
    api_key: str = ""
    session_token: str = ""
    bearer_token: str = ""
    user_id: str = ""
    api_base: str = "https://backend.composio.dev/api/v1"
    
    # Twitter API configuration
    twitter_api_base: str = "https://api.twitter.com/2"
    
    # Client configuration
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Rate limiting
    min_request_interval: float = 1.0
    
    @classmethod
    def from_env(cls) -> "ComposioConfig":
        """Create configuration from environment variables."""
        return cls(
            client_id=os.getenv("COMPOSIO_CLIENT_ID", ""),
            api_key=os.getenv("COMPOSIO_API_KEY", ""),
            session_token=os.getenv("COMPOSIO_SESSION_TOKEN", ""),
            bearer_token=os.getenv("COMPOSIO_BEARER_TOKEN", ""),
            user_id=os.getenv("COMPOSIO_USER_ID", ""),
            api_base=os.getenv("COMPOSIO_API_BASE", "https://backend.composio.dev/api/v1"),
            twitter_api_base=os.getenv("TWITTER_API_BASE", "https://api.twitter.com/2"),
            timeout=int(os.getenv("COMPOSIO_TIMEOUT", "30")),
            max_retries=int(os.getenv("COMPOSIO_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("COMPOSIO_RETRY_DELAY", "1.0")),
            min_request_interval=float(os.getenv("COMPOSIO_RATE_LIMIT", "1.0")),
        )
    
    @classmethod
    def from_file(cls, filepath: str) -> "ComposioConfig":
        """Load configuration from a JSON file."""
        import json
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls(**data)
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary (without secrets)."""
        return {
            "client_id": self.client_id,
            "api_base": self.api_base,
            "twitter_api_base": self.twitter_api_base,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "min_request_interval": self.min_request_interval,
        }
    
    def is_valid(self) -> bool:
        """Check if configuration has required credentials."""
        return bool(self.bearer_token or self.session_token)
    
    def get_auth_token(self) -> str:
        """Get the authentication token (prefers bearer token)."""
        return self.bearer_token or self.session_token


# Default configuration instance
default_config = ComposioConfig.from_env()


def get_config() -> ComposioConfig:
    """Get the current configuration."""
    return default_config


def update_config(**kwargs):
    """Update configuration values."""
    global default_config
    for key, value in kwargs.items():
        if hasattr(default_config, key):
            setattr(default_config, key, value)
