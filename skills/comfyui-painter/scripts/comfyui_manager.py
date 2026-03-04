#!/usr/bin/env python3
"""ComfyUI 进程管理：启动 / 关闭 / 状态检查"""

import json
import subprocess
import time
import urllib.request
from pathlib import Path

CONFIG = json.loads((Path(__file__).parent.parent / "config.json").read_text())
COMFY = CONFIG["comfyui"]
API_URL = COMFY["api_url"]
LAST_USED = Path(__file__).parent.parent / ".last_used"
POWERSHELL = COMFY["powershell"]


def is_running() -> bool:
    try:
        resp = urllib.request.urlopen(f"{API_URL}/system_stats", timeout=3)
        return resp.status == 200
    except Exception:
        return False


def start(timeout=60) -> bool:
    if is_running():
        _touch()
        return True
    
    cmd = (
        f"Start-Process -FilePath '{COMFY['python_path']}' "
        f"-ArgumentList '{COMFY['main_path']}','--listen','0.0.0.0','--port','{COMFY['port']}' "
        f"-WorkingDirectory '{COMFY['work_dir']}' -WindowStyle Hidden"
    )
    subprocess.run([POWERSHELL, "-Command", cmd], capture_output=True, timeout=15)
    
    # 等待启动
    for _ in range(timeout // 2):
        time.sleep(2)
        if is_running():
            _touch()
            return True
    return False


def stop() -> bool:
    subprocess.run(
        [POWERSHELL, "-Command",
         "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force"],
        capture_output=True, timeout=10
    )
    time.sleep(1)
    return not is_running()


def status() -> dict:
    if not is_running():
        return {"running": False}
    try:
        resp = urllib.request.urlopen(f"{API_URL}/system_stats", timeout=3)
        data = json.loads(resp.read())
        return {"running": True, **data.get("system", {})}
    except Exception:
        return {"running": False}


def _touch():
    LAST_USED.write_text(str(time.time()))


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "start":
        ok = start()
        print(f"{'✅ ComfyUI 已启动' if ok else '❌ 启动失败'}")
    elif cmd == "stop":
        ok = stop()
        print(f"{'✅ ComfyUI 已关闭' if ok else '❌ 关闭失败'}")
    elif cmd == "status":
        s = status()
        print(json.dumps(s, indent=2))
    else:
        print(f"用法: {sys.argv[0]} [start|stop|status]")
