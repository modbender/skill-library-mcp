#!/usr/bin/env python3
"""Install Windows rr command without PowerShell scripts.
Creates %USERPROFILE%\bin\rr.cmd and copies rr_win.py there.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

script_dir = Path(__file__).resolve().parent
src = script_dir / "rr_win.py"
if not src.exists():
    raise SystemExit(f"rr_win.py not found: {src}")

home = Path.home()
target_dir = home / "bin"
target_dir.mkdir(parents=True, exist_ok=True)

target_py = target_dir / "rr_win.py"
shutil.copy2(src, target_py)

rr_cmd = target_dir / "rr.cmd"
rr_cmd.write_text('@echo off\r\npy -3 "%~dp0rr_win.py" %*\r\n', encoding="ascii")

user_path = os.environ.get("Path", "")
if str(target_dir).lower() not in user_path.lower():
    print(f"Add to your User PATH: {target_dir}")

print(f"OK: installed {target_py}")
print(f"OK: installed {rr_cmd}")
print("Reopen terminal, then run: rr show")
