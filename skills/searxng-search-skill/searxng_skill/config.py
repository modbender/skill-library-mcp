"""
Configuration management for SearXNG skill
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import json


@dataclass
class SearXNGConfig:
    """Configuration for SearXNG skill"""
    instance_url: str = "http://localhost:8080"
    default_timeout: int = 10
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_factor: float = 2.0
    verify_ssl: bool = True
    default_language: str = "en"
    default_safe_search: int = 1
    user_agent: str = "SearXNG-Skill/1.0"
    custom_headers: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls) -> 'SearXNGConfig':
        """Load configuration from environment variables"""
        return cls(
            instance_url=os.getenv("SEARXNG_URL", "http://localhost:8080"),
            default_timeout=int(os.getenv("SEARXNG_TIMEOUT", "10")),
            max_retries=int(os.getenv("SEARXNG_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("SEARXNG_RETRY_DELAY", "1.0")),
            backoff_factor=float(os.getenv("SEARXNG_BACKOFF_FACTOR", "2.0")),
            verify_ssl=os.getenv("SEARXNG_VERIFY_SSL", "true").lower() == "true",
            default_language=os.getenv("SEARXNG_LANGUAGE", "en"),
            user_agent=os.getenv("SEARXNG_USER_AGENT", "SearXNG-Skill/1.0"),
        )
    
    @classmethod
    def from_file(cls, filepath: str) -> 'SearXNGConfig':
        """Load configuration from JSON file"""
        with open(filepath, 'r') as f:
            config_dict = json.load(f)
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "instance_url": self.instance_url,
            "default_timeout": self.default_timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "backoff_factor": self.backoff_factor,
            "verify_ssl": self.verify_ssl,
            "default_language": self.default_language,
            "default_safe_search": self.default_safe_search,
            "user_agent": self.user_agent,
            "custom_headers": self.custom_headers,
        }
    
    def save(self, filepath: str) -> None:
        """Save configuration to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)