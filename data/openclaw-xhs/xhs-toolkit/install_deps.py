#!/usr/bin/env python3
"""
智能依赖安装脚本
支持 uv 和 pip 两种方式
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, check=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_command_exists(cmd):
    """检查命令是否存在"""
    # Windows 下某些命令可能需要不同的参数
    test_args = ["--version", "-version", "/?", "-h"]
    for arg in test_args:
        try:
            if os.name == 'nt':  # Windows
                # 使用 where 命令检查
                result = subprocess.run(f"where {cmd}", shell=True, capture_output=True)
                if result.returncode == 0:
                    return True
            else:
                # Unix 系统使用 which
                result = subprocess.run(f"which {cmd}", shell=True, capture_output=True)
                if result.returncode == 0:
                    return True
        except:
            pass
    return False


def install_with_uv():
    """使用 uv 安装依赖"""
    print("🚀 使用 uv 安装依赖...")
    
    if not check_command_exists("uv"):
        print("❌ 未找到 uv 命令")
        print("\n安装 uv 的方法：")
        if os.name == 'nt':  # Windows
            print("  PowerShell: irm https://astral.sh/uv/install.ps1 | iex")
        else:
            print("  curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False
    
    success, stdout, stderr = run_command("uv sync")
    if success:
        print("✅ 依赖安装成功！")
        return True
    else:
        print(f"❌ uv sync 失败: {stderr}")
        return False


def install_with_pip():
    """使用 pip 安装依赖"""
    print("📦 使用 pip 安装依赖...")
    
    # 检查是否在虚拟环境中
    in_venv = sys.prefix != sys.base_prefix
    
    if not in_venv:
        print("⚠️  建议在虚拟环境中安装依赖")
        print("\n创建虚拟环境：")
        print("  python -m venv .venv")
        print("\n激活虚拟环境：")
        print("  Mac/Linux: source .venv/bin/activate")
        print("  Windows: .venv\\Scripts\\activate")
        
        # Windows 下可能需要额外提示
        if os.name == 'nt':
            print("\nWindows 提示：")
            print("  如果遇到脚本执行策略错误，请在 PowerShell 中运行：")
            print("  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser")
        print("\n" + "="*50)
        
        response = input("\n是否继续在全局环境安装？(y/N): ")
        if response.lower() != 'y':
            return False
    
    # 安装依赖
    req_file = "requirements.txt"
    success, stdout, stderr = run_command(f"{sys.executable} -m pip install -r {req_file}")
    if success:
        print("✅ 依赖安装成功！")
        return True
    else:
        print(f"❌ pip install 失败: {stderr}")
        
        # 尝试使用国内镜像
        print("\n🔄 尝试使用清华镜像...")
        success, stdout, stderr = run_command(
            f"{sys.executable} -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple"
        )
        if success:
            print("✅ 使用镜像安装成功！")
            return True
        else:
            print(f"❌ 镜像安装也失败了: {stderr}")
            return False


def main():
    """主函数"""
    print("🔧 小红书工具包 - 依赖安装向导")
    print("="*50)
    
    # 切换到脚本目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 检查依赖文件
    if not Path("requirements.txt").exists():
        print("❌ 未找到 requirements.txt 文件")
        return 1
    
    print("\n选择安装方式：")
    print("1. 使用 uv（推荐，速度快）")
    print("2. 使用 pip（传统方式）")
    print("3. 自动选择")
    
    choice = input("\n请选择 (1/2/3，默认3): ").strip() or "3"
    
    if choice == "1":
        success = install_with_uv()
    elif choice == "2":
        success = install_with_pip()
    else:
        # 自动选择
        if check_command_exists("uv"):
            print("\n✅ 检测到 uv，优先使用")
            success = install_with_uv()
        else:
            print("\n📦 使用 pip 安装")
            success = install_with_pip()
    
    if success:
        print("\n🎉 安装完成！")
        print("\n运行程序：")
        if os.name == 'nt':  # Windows
            print("  xhs.bat")
            print("  或: python xhs_toolkit_interactive.py")
        else:
            print("  ./xhs")
            print("  或: python3 xhs_toolkit_interactive.py")
        return 0
    else:
        print("\n❌ 安装失败，请检查错误信息")
        return 1


if __name__ == "__main__":
    sys.exit(main())