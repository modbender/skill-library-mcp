"""
Tunnel integration for remote dashboard access.

Provides a simple way to expose the local dashboard to the internet
using Cloudflare Tunnel (cloudflared), ngrok, or localtunnel.

No external Python dependencies — these tools are invoked as subprocesses.
"""

import logging
import re
import shutil
import subprocess
import threading
import time
from typing import Optional

logger = logging.getLogger("nlplanner.tunnel")

_process: Optional[subprocess.Popen] = None
_tunnel_url: str = ""
_monitor_thread: Optional[threading.Thread] = None


# ── Tunnel tool detection ──────────────────────────────────────────

def detect_tunnel_tool() -> Optional[str]:
    """
    Detect which tunnel tool is available on the system.

    Checks in order of preference: cloudflared, ngrok, localtunnel (lt).

    Returns:
        The name of the available tool, or None if none found.

    Example:
        >>> tool = detect_tunnel_tool()
        >>> print(tool)
        'cloudflared'
    """
    for tool in ["cloudflared", "ngrok", "lt"]:
        if shutil.which(tool):
            logger.info("Tunnel tool found: %s", tool)
            return tool

    logger.info("No tunnel tool found on PATH.")
    return None


def get_install_instructions() -> str:
    """
    Return installation instructions for tunnel tools.

    Returns:
        A human-readable string with install commands for each platform.
    """
    return (
        "To expose your dashboard remotely, install one of these tools:\n"
        "\n"
        "  Cloudflare Tunnel (recommended, free, no account needed for quick tunnels):\n"
        "    Windows:  winget install cloudflare.cloudflared\n"
        "    macOS:    brew install cloudflared\n"
        "    Linux:    https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/\n"
        "\n"
        "  ngrok (free tier available, requires account):\n"
        "    All:      https://ngrok.com/download\n"
        "\n"
        "  localtunnel (npm, no account needed):\n"
        "    All:      npm install -g localtunnel\n"
    )


# ── Start / Stop ──────────────────────────────────────────────────

def start_tunnel(port: int, tool: Optional[str] = None) -> str:
    """
    Start a tunnel to expose a local port to the internet.

    Args:
        port: The local port to tunnel (e.g., 8080).
        tool: Which tool to use. If None, auto-detects.

    Returns:
        The public tunnel URL, or empty string on failure.

    Example:
        >>> url = start_tunnel(8080)
        >>> print(url)
        'https://random-name.trycloudflare.com'
    """
    global _process, _tunnel_url

    if _process is not None:
        logger.info("Tunnel is already running at %s", _tunnel_url)
        return _tunnel_url

    if tool is None:
        tool = detect_tunnel_tool()

    if tool is None:
        logger.error("No tunnel tool available.")
        print(get_install_instructions())
        return ""

    try:
        if tool == "cloudflared":
            return _start_cloudflared(port)
        elif tool == "ngrok":
            return _start_ngrok(port)
        elif tool == "lt":
            return _start_localtunnel(port)
        else:
            logger.error("Unknown tunnel tool: %s", tool)
            return ""
    except Exception as e:
        logger.error("Failed to start tunnel with %s: %s", tool, e)
        return ""


def stop_tunnel() -> None:
    """Stop the running tunnel process."""
    global _process, _tunnel_url, _monitor_thread

    if _process is None:
        logger.info("No tunnel is running.")
        return

    try:
        _process.terminate()
        _process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        _process.kill()
    except Exception as e:
        logger.warning("Error stopping tunnel: %s", e)

    _process = None
    _tunnel_url = ""
    _monitor_thread = None
    logger.info("Tunnel stopped.")


def get_tunnel_url() -> str:
    """
    Get the public URL of the running tunnel.

    Returns:
        The tunnel URL, or empty string if not running.
    """
    return _tunnel_url


def is_tunnel_running() -> bool:
    """Check if a tunnel is currently active."""
    if _process is None:
        return False
    return _process.poll() is None


# ── Tool-specific launchers ────────────────────────────────────────

def _start_cloudflared(port: int) -> str:
    """Start a Cloudflare quick tunnel."""
    global _process, _tunnel_url

    cmd = ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"]
    logger.info("Starting cloudflared: %s", " ".join(cmd))

    _process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Cloudflared prints the URL to stderr/stdout — watch for it
    url = _capture_url_from_output(
        _process,
        pattern=r"(https://[a-zA-Z0-9-]+\.trycloudflare\.com)",
        timeout=15,
    )

    if url:
        _tunnel_url = url
        logger.info("Cloudflare tunnel active: %s", url)
        return url

    logger.error("Could not capture cloudflared URL within timeout.")
    stop_tunnel()
    return ""


def _start_ngrok(port: int) -> str:
    """Start an ngrok tunnel."""
    global _process, _tunnel_url

    cmd = ["ngrok", "http", str(port), "--log", "stdout"]
    logger.info("Starting ngrok: %s", " ".join(cmd))

    _process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    url = _capture_url_from_output(
        _process,
        pattern=r"(https://[a-zA-Z0-9-]+\.ngrok[a-zA-Z0-9.-]*\.[a-z]+)",
        timeout=10,
    )

    if url:
        _tunnel_url = url
        logger.info("ngrok tunnel active: %s", url)
        return url

    logger.error("Could not capture ngrok URL within timeout.")
    stop_tunnel()
    return ""


def _start_localtunnel(port: int) -> str:
    """Start a localtunnel (lt) tunnel."""
    global _process, _tunnel_url

    cmd = ["lt", "--port", str(port)]
    logger.info("Starting localtunnel: %s", " ".join(cmd))

    _process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    url = _capture_url_from_output(
        _process,
        pattern=r"(https://[a-zA-Z0-9-]+\.loca\.lt)",
        timeout=10,
    )

    if url:
        _tunnel_url = url
        logger.info("localtunnel active: %s", url)
        return url

    logger.error("Could not capture localtunnel URL within timeout.")
    stop_tunnel()
    return ""


def _capture_url_from_output(
    proc: subprocess.Popen,
    pattern: str,
    timeout: int = 15,
) -> str:
    """
    Read process output line by line and capture the first URL matching pattern.

    Runs in the current thread, blocking up to `timeout` seconds.
    After capturing, spawns a background thread to drain remaining output.
    """
    url = ""
    deadline = time.time() + timeout

    while time.time() < deadline:
        if proc.stdout is None:
            break
        # Use a short readline with the deadline in mind
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            time.sleep(0.1)
            continue

        match = re.search(pattern, line)
        if match:
            url = match.group(1)
            break

    # Drain remaining output in background to prevent pipe blocking
    if proc.stdout:
        def _drain():
            try:
                for _ in proc.stdout:
                    pass
            except Exception:
                pass

        global _monitor_thread
        _monitor_thread = threading.Thread(target=_drain, daemon=True)
        _monitor_thread.start()

    return url
