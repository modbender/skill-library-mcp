"""
reefwatch._common
~~~~~~~~~~~~~~~~~
Shared constants and utilities used across all submodules.
"""

import logging
import os
import platform
from pathlib import Path

SYSTEM = platform.system()  # "Linux" or "Darwin"
logger = logging.getLogger("reefwatch")


def get_os_key() -> str:
    return "linux" if SYSTEM == "Linux" else "darwin"


def expand(path_str: str) -> Path:
    return Path(os.path.expanduser(path_str))
