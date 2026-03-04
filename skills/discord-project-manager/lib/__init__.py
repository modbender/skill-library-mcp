"""
Discord Project Manager - Python Library

Core modules for Discord thread and permission management.
"""

__version__ = "2.0.0"

from .registry import AgentRegistry
from .discord_api import DiscordAPI
from .config import OpenClawConfig
from .permissions import PermissionsManager
from .thread import ThreadManager

__all__ = [
    'AgentRegistry',
    'DiscordAPI',
    'OpenClawConfig',
    'PermissionsManager',
    'ThreadManager',
]
