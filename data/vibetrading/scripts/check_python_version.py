#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Version Checker - Ensure Python 3.6+ is being used

This script checks the Python version and exits with an error
if the version is below 3.6, since f-strings and other modern
features require Python 3.6+.
"""

import sys

def check_python_version(min_version=(3, 6)):
    """
    Check if Python version meets minimum requirements.
    
    Args:
        min_version: Minimum version as tuple (major, minor)
    
    Returns:
        bool: True if version meets requirements, False otherwise
    """
    current_version = sys.version_info
    
    if current_version < min_version:
        print(f"❌ Python版本错误: 需要Python {min_version[0]}.{min_version[1]}+")
        print(f"   当前版本: {sys.version}")
        print(f"\n💡 解决方案:")
        print(f"   1. 升级Python到3.6或更高版本")
        print(f"   2. 使用pyenv管理多个Python版本")
        print(f"   3. 使用conda创建Python 3.6+环境")
        return False
    
    print(f"✅ Python版本检查通过: {sys.version}")
    print(f"   f-string和其他Python 3.6+功能可用")
    return True

def main():
    """Main function"""
    if not check_python_version():
        sys.exit(1)
    
    # Additional checks
    print(f"\n📊 系统信息:")
    print(f"  平台: {sys.platform}")
    print(f"  可执行文件: {sys.executable}")
    print(f"  路径: {sys.path[:3]}...")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())