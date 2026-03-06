#!/usr/bin/env python3
"""一键安装 PC Control 服务端依赖到 Windows Python"""

import json
import subprocess
from pathlib import Path

CONFIG = json.loads((Path(__file__).parent.parent / "config.json").read_text())
POWERSHELL = CONFIG["powershell"]
PY = CONFIG["server"]["python_path"]

DEPS = ["fastapi", "uvicorn", "mss", "pyautogui", "pillow"]

def install():
    cmd = f"& '{PY}' -m pip install {' '.join(DEPS)}"
    result = subprocess.run([POWERSHELL, "-Command", cmd], capture_output=True, text=True, timeout=120)
    print(result.stdout)
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
    else:
        print("✅ 依赖安装完成")

if __name__ == "__main__":
    install()
