#!/usr/bin/env python3
"""OpenClaw 集成脚本 - 支持通过消息触发 SSH 批量管理命令。

用法:
  openclaw run --task "ssh-batch-enable-all"
  openclaw run --task "ssh-batch-disable-all"
"""

import sys
import subprocess
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent / "ssh-batch-manager.py"

def run_command(args):
    """运行 ssh-batch-manager 命令。"""
    cmd = [sys.executable, str(SCRIPT_PATH)] + args
    result = subprocess.run(cmd, capture_output=False, text=True)
    return result.returncode

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  openclaw-integration.py enable-all")
        print("  openclaw-integration.py disable-all")
        print("  openclaw-integration.py enable <target>")
        print("  openclaw-integration.py disable <target>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "enable-all":
        sys.exit(run_command(["enable-all"]))
    elif command == "disable-all":
        sys.exit(run_command(["disable-all"]))
    elif command == "enable" and len(sys.argv) >= 3:
        sys.exit(run_command(["enable", sys.argv[2]]))
    elif command == "disable" and len(sys.argv) >= 3:
        sys.exit(run_command(["disable", sys.argv[2]]))
    else:
        print(f"未知命令：{command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
