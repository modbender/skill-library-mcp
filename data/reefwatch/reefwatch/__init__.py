"""
ReefWatch
~~~~~~~~~
Continuous local security monitoring for OpenClaw hosts.
"""

__version__ = "1.0.0"
__all__ = [
    "AlertManager",
    "ReefWatchDaemon",
    "load_config",
    "expand",
    "SYSTEM",
    "get_os_key",
    "logger",
]

from reefwatch._common import SYSTEM, expand, get_os_key, logger
from reefwatch.alert_manager import AlertManager
from reefwatch.config import load_config
from reefwatch.daemon import ReefWatchDaemon
