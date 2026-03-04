#!/usr/bin/env python3
"""setup.py — Install dependencies for the mlb-daily-scores skill.

Cross-platform (macOS, Linux, Windows). Run once after installing the skill.
Creates a virtual environment in .venv/ inside the skill directory and installs
packages there, avoiding PEP 668 "externally managed environment" issues.

Usage:
    python3 setup.py        (macOS/Linux)
    python setup.py         (Windows)
"""

import subprocess
import shutil
import sys
import os
from pathlib import Path

PACKAGES = ["MLB-StatsAPI", "requests"]


def main():
    print("=== mlb-daily-scores: Installing dependencies ===")

    base_dir = Path(__file__).resolve().parent
    venv_dir = base_dir / ".venv"

    # Create virtual environment if it doesn't exist
    if not venv_dir.exists():
        print(f"Creating virtual environment in {venv_dir} ...")
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])

    # Determine the venv's Python and pip paths
    if sys.platform == "win32":
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:
        venv_python = venv_dir / "bin" / "python3"
        if not venv_python.exists():
            venv_python = venv_dir / "bin" / "python"

    if not venv_python.exists():
        print(f"ERROR: Could not find Python in venv at {venv_python}")
        sys.exit(1)

    # Install packages into the venv
    uv = shutil.which("uv")
    if uv:
        print("Using uv...")
        subprocess.check_call(
            [uv, "pip", "install", "--python", str(venv_python)] + PACKAGES
        )
    else:
        print(f"Using pip ({venv_python})...")
        subprocess.check_call(
            [str(venv_python), "-m", "pip", "install"] + PACKAGES
        )

    print()
    print("=== mlb-daily-scores: Dependencies installed successfully ===")
    print(f"    Virtual environment: {venv_dir}")
    print()
    print("Next steps:")
    print('  1. Add config to ~/.openclaw/openclaw.json (see SKILL.md)')
    print("  2. Set up the daily cron job (see SKILL.md)")


if __name__ == "__main__":
    main()
