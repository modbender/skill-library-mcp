"""
Twitter API Client Library

A well-structured library for interacting with Twitter's API.
This library provides a clean interface for common Twitter operations.
"""

__version__ = '1.0.0'

from .twitter import Twitter
from .core.client import TwitterAPIClient
from .api.user import UserAPI
from .config.settings import load_config, save_config, get_config_value, update_config_value

__all__ = ['Twitter', 'TwitterAPIClient', 'UserAPI'] 