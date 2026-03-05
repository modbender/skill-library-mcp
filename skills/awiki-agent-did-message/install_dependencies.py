#!/usr/bin/env python3
"""依赖安装脚本。

支持 pip 安装。

[INPUT]: 无
[OUTPUT]: 安装 awiki-did 所需依赖
[POS]: 项目根目录，提供 pip 安装

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""

import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], check: bool = True) -> bool:
    """运行命令。"""
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"命令失败: {' '.join(cmd)}")
        if e.stderr:
            print(e.stderr)
        return False
    except FileNotFoundError:
        return False


def find_installer() -> tuple[str, list[str]]:
    """查找可用的包安装器。"""
    script_dir = Path(__file__).parent
    requirements = str(script_dir / "requirements.txt")

    # 优先使用 pip
    if shutil.which("pip"):
        return "pip", ["pip", "install", "-r", requirements]

    # 尝试使用 python -m pip
    return "python-pip", [
        sys.executable, "-m", "pip", "install", "-r", requirements,
    ]


def main() -> int:
    """主函数。"""
    print("=" * 50)
    print("awiki-did Skill 依赖安装")
    print("=" * 50)

    installer_name, cmd = find_installer()
    print(f"\n使用 {installer_name} 安装依赖...")
    print(f"执行: {' '.join(cmd)}\n")

    if run_command(cmd):
        print("\n依赖安装成功!")
        print("\n可以开始使用了:")
        print("  python scripts/setup_identity.py --name MyAgent")
        return 0
    else:
        print("\n依赖安装失败，请手动安装:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
