"""
Shared ANSI color codes and colorize helper for Token Optimizer.
"""

import os
import sys

# Global flag - set to True to disable all color output
NO_COLOR = os.environ.get("NO_COLOR", "") != ""


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


def colorize(text: str, color: str) -> str:
    """Apply color to text if terminal supports it and NO_COLOR is not set."""
    if NO_COLOR:
        return text
    if sys.stdout.isatty():
        return f"{color}{text}{Colors.END}"
    return text
