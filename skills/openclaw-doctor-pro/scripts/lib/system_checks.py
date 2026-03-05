"""System and environment checks for OpenClaw diagnostics."""
from __future__ import annotations

import shutil
import socket
from pathlib import Path

from .utils import run_command, which_binary


def check_port_available(port: int) -> tuple[bool, str]:
    """Check if port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', port))
            if result == 0:
                return True, "In use (OpenClaw running)"
            else:
                return False, "Available"
    except Exception as e:
        return False, f"Error: {e}"


def check_network_connectivity(host: str, port: int = 443) -> bool:
    """Check network connectivity to host."""
    try:
        socket.create_connection((host, port), timeout=5)
        return True
    except Exception:
        return False


def check_docker() -> tuple[bool, str]:
    """Check Docker availability."""
    if which_binary("docker"):
        code, stdout, stderr = run_command(["docker", "ps"], timeout=5)
        return code == 0, stdout if code == 0 else "Docker not running"
    return False, "Docker not installed"


def check_node_version() -> tuple[bool, str]:
    """Check Node.js version."""
    if not which_binary("node"):
        return False, "Not installed"

    code, stdout, stderr = run_command(["node", "--version"])
    if code != 0:
        return False, "Error checking version"

    version = stdout.strip().lstrip('v')
    try:
        major = int(version.split('.')[0])
        if major >= 22:
            return True, version
        else:
            return False, f"{version} (need >=22)"
    except Exception:
        return False, version


def check_disk_space(path: Path) -> tuple[int, int, int]:
    """
    Check disk space for path.

    Returns:
        Tuple of (total_gb, used_gb, free_gb)
    """
    try:
        stat = shutil.disk_usage(path)
        total_gb = stat.total // (1024 ** 3)
        used_gb = stat.used // (1024 ** 3)
        free_gb = stat.free // (1024 ** 3)
        return total_gb, used_gb, free_gb
    except Exception:
        return 0, 0, 0


def check_binary(name: str) -> bool:
    """Check if binary exists in PATH."""
    return which_binary(name) is not None
