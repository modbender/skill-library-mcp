#!/usr/bin/env python3
"""
Kaspa Wallet Installer

Installs the Kaspa Python SDK with maximum compatibility.
Works on macOS, Linux, Windows - even minimal Docker images.

Usage:
    python3 install.py

Fallback cascade:
    1. Use existing .venv if present
    2. Standard venv creation
    3. venv --without-pip + get-pip.py bootstrap
    4. pip install --user (no venv)
    5. virtualenv (if available)
"""
from __future__ import annotations

import os
import platform
import shutil
import signal
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"
REQ_FILE = ROOT / "requirements.txt"
LOG_FILE = ROOT / "install.log"
MIN_PYTHON = (3, 8)

# Installation mode flags
USE_VENV = True  # Will be set False if all venv methods fail


def log(msg: str) -> None:
    """Log to both console and file."""
    line = f"[kaspa-wallet] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{datetime.now().isoformat()} {line}\n")
    except:
        pass


def error(msg: str) -> None:
    """Log error to stderr and file."""
    line = f"[kaspa-wallet] ERROR: {msg}"
    print(line, file=sys.stderr)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{datetime.now().isoformat()} {line}\n")
    except:
        pass


def init_log() -> None:
    """Initialize log file with system info."""
    try:
        with open(LOG_FILE, "w") as f:
            f.write(f"=== Kaspa Wallet Install Log ===\n")
            f.write(f"Time: {datetime.now().isoformat()}\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"Platform: {platform.system()} {platform.machine()}\n")
            f.write(f"Executable: {sys.executable}\n")
            f.write(f"================================\n\n")
    except:
        pass


def get_python_info() -> dict:
    """Get detailed Python environment info for diagnostics."""
    return {
        "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "executable": sys.executable,
        "platform": platform.system(),
        "arch": platform.machine(),
        "implementation": platform.python_implementation(),
    }


def check_python_version() -> bool:
    """Ensure Python version meets minimum requirements."""
    if sys.version_info < MIN_PYTHON:
        error(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        error("Please install a newer Python version:")
        error("  macOS:   brew install python@3.12")
        error("  Ubuntu:  sudo apt install python3.12")
        error("  Windows: Download from python.org")
        return False
    return True


def find_best_python() -> str:
    """Find the best available Python executable."""
    # Allow override via environment
    custom = os.environ.get("KASPA_PYTHON")
    if custom:
        if shutil.which(custom) or os.path.isfile(custom):
            return custom
        error(f"KASPA_PYTHON={custom} not found, falling back to default")

    # Try newer versions first
    for ver in ("3.13", "3.12", "3.11", "3.10", "3.9", "3.8"):
        exe = shutil.which(f"python{ver}")
        if exe:
            return exe

    # Fallback to generic python3/python
    for name in ("python3", "python"):
        exe = shutil.which(name)
        if exe:
            return exe

    return sys.executable


def run_command(
    cmd: list[str],
    capture: bool = False,
    timeout: int | None = 300,
    env: dict | None = None,
) -> subprocess.CompletedProcess:
    """Run a command with proper error handling and signal detection."""
    cmd_str = " ".join(cmd)
    log(f"Running: {cmd_str}")
    
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=capture,
            text=True,
            timeout=timeout,
            env=run_env,
        )
        
        # Check for signal termination (negative return code)
        if result.returncode < 0:
            sig = -result.returncode
            sig_name = signal.Signals(sig).name if sig in signal.Signals._value2member_map_ else f"signal {sig}"
            
            if sig == signal.SIGKILL:
                error(f"Process killed by {sig_name} (likely OOM or watchdog)")
                error("")
                error("This usually means the system ran out of memory.")
                error("Try one of:")
                error("  1. pip install --no-cache-dir kaspa")
                error("  2. Run on a machine with more RAM (>= 1GB)")
                error("  3. Check: dmesg | tail -20  (for OOM killer logs)")
                raise subprocess.CalledProcessError(result.returncode, cmd)
            else:
                error(f"Process killed by {sig_name}")
                raise subprocess.CalledProcessError(result.returncode, cmd)
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
            
        return result
        
    except subprocess.TimeoutExpired:
        error(f"Command timed out after {timeout}s: {cmd_str}")
        raise
    except subprocess.CalledProcessError as e:
        if capture and e.stderr:
            error(f"Command failed: {cmd_str}")
            error(f"Output: {e.stderr[:500]}")
        raise


# =============================================================================
# VENV CREATION STRATEGIES
# =============================================================================

def try_venv_standard(python_exe: str) -> bool:
    """Strategy 1: Standard venv module."""
    log("Trying: python -m venv (standard)")
    try:
        run_command([python_exe, "-m", "venv", str(VENV_DIR)], capture=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        shutil.rmtree(VENV_DIR, ignore_errors=True)
        return False


def try_venv_without_pip(python_exe: str) -> bool:
    """Strategy 2: venv without pip, then bootstrap with get-pip.py."""
    log("Trying: python -m venv --without-pip + get-pip.py")
    try:
        run_command([python_exe, "-m", "venv", "--without-pip", str(VENV_DIR)], capture=True)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        shutil.rmtree(VENV_DIR, ignore_errors=True)
        return False
    
    # Get venv python path
    if os.name == "nt":
        venv_python = VENV_DIR / "Scripts" / "python.exe"
    else:
        venv_python = VENV_DIR / "bin" / "python"
    
    if not venv_python.exists():
        log("Warning: venv created but python not found inside")
        shutil.rmtree(VENV_DIR, ignore_errors=True)
        return False
    
    # Bootstrap pip with get-pip.py
    if not bootstrap_pip(venv_python):
        shutil.rmtree(VENV_DIR, ignore_errors=True)
        return False
    
    return True


def try_virtualenv(python_exe: str) -> bool:
    """Strategy 3: Use virtualenv if available."""
    virtualenv = shutil.which("virtualenv")
    if not virtualenv:
        return False
    
    log("Trying: virtualenv")
    try:
        run_command([virtualenv, "-p", python_exe, str(VENV_DIR)], capture=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        shutil.rmtree(VENV_DIR, ignore_errors=True)
        return False


def bootstrap_pip(venv_python: Path) -> bool:
    """Bootstrap pip using get-pip.py."""
    import tempfile
    import urllib.request
    
    log("Downloading get-pip.py...")
    get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
    
    try:
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False) as f:
            with urllib.request.urlopen(get_pip_url, timeout=60) as response:
                f.write(response.read())
            get_pip_path = f.name
        
        log("Installing pip via get-pip.py...")
        run_command([str(venv_python), get_pip_path], capture=True)
        
        os.unlink(get_pip_path)
        return True
        
    except Exception as e:
        log(f"Warning: get-pip.py failed: {e}")
        try:
            os.unlink(get_pip_path)
        except:
            pass
        return False


def create_venv(python_exe: str) -> bool:
    """Create virtual environment using fallback strategies.
    
    Returns True if venv was created, False if should use --user install.
    """
    global USE_VENV
    
    if VENV_DIR.exists():
        log(f"Using existing venv: {VENV_DIR}")
        return True

    log(f"Creating virtual environment...")
    
    # Strategy 1: Standard venv
    if try_venv_standard(python_exe):
        log("✓ Created venv (standard)")
        return True
    
    # Strategy 2: venv --without-pip + get-pip.py
    if try_venv_without_pip(python_exe):
        log("✓ Created venv (--without-pip + get-pip.py)")
        return True
    
    # Strategy 3: virtualenv
    if try_virtualenv(python_exe):
        log("✓ Created venv (virtualenv)")
        return True
    
    # All venv strategies failed - fall back to --user install
    log("")
    log("All venv methods failed. Falling back to pip install --user")
    log("(This installs to your user site-packages instead of a venv)")
    USE_VENV = False
    return False


def get_pip_command() -> list[str]:
    """Get the pip command to use based on install mode."""
    if USE_VENV:
        if os.name == "nt":
            venv_python = VENV_DIR / "Scripts" / "python.exe"
        else:
            venv_python = VENV_DIR / "bin" / "python"
        return [str(venv_python), "-m", "pip"]
    else:
        # Use system python with --user
        return [sys.executable, "-m", "pip"]


def install_dependencies() -> None:
    """Install dependencies from requirements.txt."""
    if not REQ_FILE.exists():
        error(f"requirements.txt not found at {REQ_FILE}")
        raise FileNotFoundError(str(REQ_FILE))

    pip_cmd = get_pip_command()
    
    # Set pip cache directory (use local to avoid permission issues)
    pip_cache = ROOT / ".pip-cache"
    env = {"PIP_CACHE_DIR": str(pip_cache)}

    # Upgrade pip first (ignore failure)
    log("Upgrading pip...")
    try:
        run_command(pip_cmd + ["install", "--upgrade", "pip"], capture=True, env=env)
    except:
        log("Warning: Could not upgrade pip, continuing...")

    # Install requirements
    log("Installing kaspa SDK...")
    install_cmd = pip_cmd + ["install", "-r", str(REQ_FILE)]
    
    if not USE_VENV:
        install_cmd.append("--user")
    
    # Add --no-cache-dir if low memory environment suspected
    # (can be forced via environment variable)
    if os.environ.get("KASPA_LOW_MEMORY"):
        install_cmd.append("--no-cache-dir")
        log("Using --no-cache-dir for low memory environment")

    try:
        run_command(install_cmd, env=env)
    except subprocess.CalledProcessError as e:
        error("Failed to install dependencies")
        info = get_python_info()
        error(f"Python: {info['version']} ({info['implementation']})")
        error(f"Platform: {info['platform']} {info['arch']}")
        error("")
        error("Common fixes:")
        error("  1. Check internet connection")
        error("  2. Try: KASPA_LOW_MEMORY=1 python3 install.py")
        error("  3. Try: pip install --user kaspa")
        error("  4. Check platform support: https://pypi.org/project/kaspa/")
        raise


def verify_installation() -> bool:
    """Verify kaspa SDK is properly installed."""
    log("Verifying installation...")

    test_script = """
import sys
try:
    import kaspa
    version = getattr(kaspa, '__version__', 'unknown')
    for name in ['PrivateKey', 'Address', 'RpcClient', 'Generator']:
        if not hasattr(kaspa, name):
            print(f"MISSING:{name}", file=sys.stderr)
            sys.exit(1)
    print(f"OK:{version}")
except ImportError as e:
    print(f"IMPORT_ERROR:{e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"ERROR:{e}", file=sys.stderr)
    sys.exit(1)
"""

    # Determine which python to test with
    if USE_VENV:
        if os.name == "nt":
            test_python = str(VENV_DIR / "Scripts" / "python.exe")
        else:
            test_python = str(VENV_DIR / "bin" / "python")
    else:
        test_python = sys.executable

    try:
        result = run_command([test_python, "-c", test_script], capture=True)
        if result.stdout.startswith("OK:"):
            version = result.stdout.split(":")[1].strip()
            log(f"✓ Kaspa SDK version: {version}")
            return True
    except subprocess.CalledProcessError as e:
        stderr = e.stderr or ""
        if "IMPORT_ERROR" in stderr:
            error("Kaspa SDK import failed")
            if not USE_VENV:
                error("Try: python3 -c 'import kaspa' to debug")
        elif "MISSING" in stderr:
            error("Kaspa SDK is incomplete")
            error("Try: rm -rf .venv && python3 install.py")
        else:
            error(f"Verification failed: {stderr}")
        return False

    return False


def print_success() -> None:
    """Print success message with usage instructions."""
    log("")
    log("=" * 50)
    log("✓ Installation complete!")
    log("=" * 50)
    log("")
    log("Quick test:")
    log("  ./kaswallet.sh help")
    log("")
    log("Set wallet credentials:")
    log("  export KASPA_PRIVATE_KEY='your-64-char-hex-key'")
    log("  # or")
    log("  export KASPA_MNEMONIC='your 12-24 word phrase'")
    log("")
    log("Then check balance:")
    log("  ./kaswallet.sh balance")
    
    if not USE_VENV:
        log("")
        log("Note: Installed to user site-packages (no venv)")
        log("      kaspa module available system-wide for this user")


def main() -> int:
    init_log()
    
    log("Kaspa Wallet Installer")
    log("=" * 50)

    # Check Python version
    if not check_python_version():
        return 1

    python_exe = find_best_python()
    info = get_python_info()
    log(f"Python: {info['version']} on {info['platform']} ({info['arch']})")
    log(f"Executable: {python_exe}")

    try:
        # Create venv (or fall back to --user mode)
        create_venv(python_exe)

        # Verify venv python exists (if using venv)
        if USE_VENV:
            if os.name == "nt":
                venv_python = VENV_DIR / "Scripts" / "python.exe"
            else:
                venv_python = VENV_DIR / "bin" / "python"
            
            if not venv_python.exists():
                error(f"Venv Python not found at {venv_python}")
                error("Try: rm -rf .venv && python3 install.py")
                return 1

        # Install dependencies
        install_dependencies()

        # Verify installation
        if not verify_installation():
            return 1

        print_success()
        return 0

    except KeyboardInterrupt:
        error("Installation cancelled by user")
        return 130
    except Exception as e:
        error(f"Installation failed: {e}")
        error("")
        error(f"See {LOG_FILE} for details")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
