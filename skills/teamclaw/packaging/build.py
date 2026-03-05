"""
打包脚本：将 launcher.py 打包为单个 exe（MiniTimeBot.exe）
用法：python packaging/build.py
"""
import subprocess
import shutil
import sys
import os

# 项目根目录
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGING_DIR = os.path.join(ROOT, "packaging")
DIST_DIR = os.path.join(ROOT, "dist")


def check_pyinstaller():
    """检查 PyInstaller 是否已安装"""
    try:
        import PyInstaller  # noqa: F401
        return True
    except ImportError:
        return False


def build_exe():
    """打包 launcher.py 为 MiniTimeBot.exe"""
    if not check_pyinstaller():
        print("[ERROR] 请先安装 PyInstaller：pip install pyinstaller")
        sys.exit(1)

    launcher = os.path.join(PACKAGING_DIR, "launcher.py")
    icon = os.path.join(PACKAGING_DIR, "icon.ico")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "MiniTimeBot",
        "--distpath", DIST_DIR,
        "--workpath", os.path.join(ROOT, "build"),
        "--specpath", os.path.join(ROOT, "build"),
        "--clean",
        "--noconfirm",
    ]

    # 如果有图标文件就用
    if os.path.exists(icon):
        cmd += ["--icon", icon]

    # 保留控制台（run.bat 需要交互：用户输入 y/N）
    cmd.append(launcher)

    print(f"[BUILD] 正在打包 MiniTimeBot.exe ...")
    print(f"  命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT)

    if result.returncode != 0:
        print("[ERROR] 打包失败")
        sys.exit(1)

    exe_path = os.path.join(DIST_DIR, "MiniTimeBot.exe")
    if os.path.exists(exe_path):
        # 复制到项目根目录
        dest = os.path.join(ROOT, "MiniTimeBot.exe")
        shutil.copy2(exe_path, dest)
        print(f"\n[OK] 打包成功！")
        print(f"  exe 位置: {dest}")
        print(f"  大小: {os.path.getsize(dest) / 1024 / 1024:.1f} MB")
    else:
        print("[ERROR] 未找到生成的 exe")
        sys.exit(1)


def main():
    print("=" * 50)
    print("  MiniTimeBot 打包工具")
    print("=" * 50)
    build_exe()
    print("\n[提示] 打包完成后可用 Inno Setup 打开 packaging/installer.iss 制作安装包")


if __name__ == "__main__":
    main()
