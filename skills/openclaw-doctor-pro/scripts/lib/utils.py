"""Shared utility functions for OpenClaw Doctor Pro."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

# Path constants
OPENCLAW_DIR = Path.home() / ".openclaw"
CONFIG_FILE = OPENCLAW_DIR / "openclaw.json"
CREDENTIALS_DIR = OPENCLAW_DIR / "credentials"
DEFAULT_PORT = 18789

# Project paths
SKILL_DIR = Path(__file__).parent.parent.parent
DATA_DIR = SKILL_DIR / "data"
REFERENCES_DIR = SKILL_DIR / "references"

# Rich console instance
console = Console()


def check_mark(ok: bool) -> str:
    """Return green check mark if ok, red X otherwise."""
    return "[green]✓[/green]" if ok else "[red]✗[/red]"


def warn_mark() -> str:
    """Return yellow warning mark."""
    return "[yellow]⚠[/yellow]"


def load_json(path: Path) -> dict | None:
    """
    Safely load JSON file.

    Args:
        path: Path to JSON file

    Returns:
        Parsed JSON dict or None if error
    """
    try:
        if not path.exists():
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        console.print(f"[yellow]Warning: Failed to load {path}: {e}[/yellow]")
        return None


def save_json(path: Path, data: dict) -> bool:
    """
    Safely save JSON file.

    Args:
        path: Path to save JSON file
        data: Dictionary to save

    Returns:
        True if successful, False otherwise
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except (IOError, TypeError) as e:
        console.print(f"[red]Error: Failed to save {path}: {e}[/red]")
        return False


def get_config() -> dict | None:
    """
    Load OpenClaw configuration file.

    Returns:
        Configuration dict or None if not found
    """
    return load_json(CONFIG_FILE)


def run_command(cmd: list[str], timeout: int = 10) -> tuple[int, str, str]:
    """
    Execute command safely with timeout.

    Args:
        cmd: Command and arguments as list
        timeout: Timeout in seconds

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"
    except Exception as e:
        return -1, "", str(e)


def which_binary(name: str) -> str | None:
    """
    Find binary in PATH.

    Args:
        name: Binary name

    Returns:
        Full path to binary or None if not found
    """
    return shutil.which(name)


def format_panel(title: str, content: str, style: str = "blue") -> Panel:
    """
    Create Rich panel with formatted content.

    Args:
        title: Panel title
        content: Panel content
        style: Border style color

    Returns:
        Rich Panel instance
    """
    return Panel(content, title=title, border_style=style)
