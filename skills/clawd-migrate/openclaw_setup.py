"""
Post-migration: install openclaw globally and run openclaw onboard in the target directory.
Ensures the migrated directory is set up as an openclaw workspace with existing files in place.
Works on Windows, macOS, and Linux; uses shell so PATH matches the user's terminal.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

_WIN = sys.platform == "win32"


def install_openclaw_global() -> Tuple[bool, str]:
    """
    Run npm i -g openclaw. Returns (success, message).
    Uses shell=True so npm is found via the same PATH as the user's terminal (macOS/Linux).
    """
    try:
        r = subprocess.run(
            "npm install -g openclaw",
            capture_output=True,
            text=True,
            timeout=120,
            shell=True,
        )
        if r.returncode != 0:
            return False, r.stderr or r.stdout or f"npm exit code {r.returncode}"
        return True, "openclaw installed globally"
    except FileNotFoundError:
        return False, "npm not found; ensure Node.js is installed"
    except subprocess.TimeoutExpired:
        return False, "npm install timed out"
    except Exception as e:
        return False, str(e)


def run_openclaw_onboard(target_dir: Path) -> Tuple[bool, str]:
    """
    Run openclaw onboard with cwd=target_dir. Returns (success, message).
    Uses shell=True so openclaw is found via PATH (e.g. /usr/local/bin on macOS).
    """
    try:
        r = subprocess.run(
            "openclaw onboard",
            cwd=str(target_dir),
            capture_output=True,
            text=True,
            timeout=60,
            shell=True,
        )
        if r.returncode != 0:
            err = r.stderr or r.stdout or f"openclaw onboard exit code {r.returncode}"
            return False, err.strip() or str(r.returncode)
        return True, "openclaw onboard completed"
    except FileNotFoundError:
        return False, "openclaw not found; run npm i -g openclaw first"
    except subprocess.TimeoutExpired:
        return False, "openclaw onboard timed out"
    except Exception as e:
        return False, str(e)


def install_openclaw_and_onboard(target_dir: Optional[Path] = None) -> dict:
    """
    Install openclaw globally (npm i -g openclaw), then run openclaw onboard
    in target_dir (default: cwd). Target dir should be the migration output
    directory so openclaw sets it up with your migrated files in place.

    Returns dict: install_ok, onboard_ok, install_message, onboard_message, errors.
    """
    target_dir = Path(target_dir or ".").resolve()
    result = {
        "install_ok": False,
        "onboard_ok": False,
        "install_message": "",
        "onboard_message": "",
        "errors": [],
    }
    ok, msg = install_openclaw_global()
    result["install_ok"] = ok
    result["install_message"] = msg
    if not ok:
        result["errors"].append(f"install: {msg}")
        return result
    ok2, msg2 = run_openclaw_onboard(target_dir)
    result["onboard_ok"] = ok2
    result["onboard_message"] = msg2
    if not ok2:
        result["errors"].append(f"onboard: {msg2}")
    return result
