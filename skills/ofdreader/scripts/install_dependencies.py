#!/usr/bin/env python3
"""
安装 OfdReader skill 所需的依赖
"""
import subprocess
import sys


def install_dependencies():
    """安装所需的 Python 包"""
    dependencies = [
        # OFD 处理可能需要的库
        # ofdrw 是一个 OFD 读写库
        "ofdrw>=0.3.0",
    ]

    print("正在安装 OfdReader skill 的依赖...")

    for package in dependencies:
        print(f"安装 {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"  {package} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"  警告: {package} 安装失败: {e}")
            print("  注意: 核心功能使用标准库，仍可正常使用")

    print("\n依赖安装完成！")


if __name__ == '__main__':
    install_dependencies()
