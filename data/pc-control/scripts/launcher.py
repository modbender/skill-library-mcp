#!/usr/bin/env python3
"""从 WSL 启动/关闭 PC Control 服务"""

import json
import subprocess
import time
import urllib.request
from pathlib import Path

CONFIG = json.loads((Path(__file__).parent.parent / "config.json").read_text())
POWERSHELL = CONFIG["powershell"]
PY = CONFIG["server"]["python_path"]
HOST = CONFIG["server"]["host"]
PORT = CONFIG["server"]["port"]
SERVER_SCRIPT = str(Path(__file__).parent / "server.py").replace("/mnt/c/", "C:\\\\").replace("/mnt/d/", "D:\\\\").replace("/", "\\\\")
# server.py 在 WSL 路径下，需要用 wslpath 转换
LAST_USED = Path(__file__).parent.parent / ".last_used"


def is_running() -> bool:
    try:
        resp = urllib.request.urlopen(f"http://{HOST}:{PORT}/status", timeout=3)
        return resp.status == 200
    except Exception:
        return False


def start(timeout=30) -> bool:
    if is_running():
        _touch()
        return True

    # 从WSL获取Windows路径
    wsl_server = str(Path(__file__).parent / "server.py")
    result = subprocess.run(["wslpath", "-w", wsl_server], capture_output=True, text=True)
    win_server = result.stdout.strip()

    cmd = (
        f"Start-Process -FilePath '{PY}' "
        f"-ArgumentList '{win_server}' "
        f"-WindowStyle Hidden"
    )
    subprocess.run([POWERSHELL, "-Command", cmd], capture_output=True, timeout=15)

    for _ in range(timeout // 2):
        time.sleep(2)
        if is_running():
            _touch()
            return True
    return False


def stop() -> bool:
    if not is_running():
        return True
    try:
        token = (Path(__file__).parent.parent / ".auth_token").read_text().strip()
        data = b"{}"
        req = urllib.request.Request(
            f"http://{HOST}:{PORT}/shutdown",
            data=data,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass
    time.sleep(2)
    if not is_running():
        return True
    # 强制关闭
    subprocess.run(
        [POWERSHELL, "-Command",
         "Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like '*server.py*'} | Stop-Process -Force"],
        capture_output=True, timeout=10
    )
    return not is_running()


def _touch():
    LAST_USED.write_text(str(time.time()))


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "start":
        ok = start()
        print(f"{'✅ PC Control 服务已启动' if ok else '❌ 启动失败'}")
    elif cmd == "stop":
        ok = stop()
        print(f"{'✅ 已关闭' if ok else '❌ 关闭失败'}")
    elif cmd == "status":
        print(f"{'🟢 运行中' if is_running() else '🔴 未运行'}")
