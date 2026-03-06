#!/usr/bin/env python3
"""
依赖检测模块
检查 pyte 等依赖是否安装
"""

import sys
from pathlib import Path
from typing import List, Tuple


class DependencyChecker:
    """依赖项检查器"""
    
    REQUIRED_PACKAGES = [
        ("pyte", "pyte"),
    ]
    
    OPTIONAL_PACKAGES = [
        ("select", "select"),  # 标准库，应该都有
    ]
    
    @staticmethod
    def check_pyte() -> bool:
        """检查 pyte 是否安装"""
        try:
            import pyte
            return True
        except ImportError:
            return False
    
    @staticmethod
    def check_all() -> Tuple[List[str], List[str]]:
        """
        检查所有依赖
        
        Returns:
            (missing_packages, installed_packages)
        """
        missing = []
        installed = []
        
        for package_name, import_name in DependencyChecker.REQUIRED_PACKAGES:
            try:
                __import__(import_name)
                installed.append(package_name)
            except ImportError:
                missing.append(package_name)
        
        return missing, installed
    
    @staticmethod
    def print_install_instructions(missing: List[str]) -> None:
        """打印安装指引"""
        if not missing:
            return
        
        print("=" * 60)
        print("[ERROR] Missing required dependencies:")
        print()
        for pkg in missing:
            print(f"  - {pkg}")
        print()
        print("Please install using one of these methods:")
        print()
        print("  Method 1: pip (user)")
        print(f"    pip3 install {' '.join(missing)}")
        print()
        print("  Method 2: pip (system)")
        print(f"    sudo pip3 install {' '.join(missing)}")
        print()
        print("  Method 3: apt (Debian/Ubuntu)")
        print(f"    sudo apt-get install python3-pyte")
        print()
        print("=" * 60)
    
    @staticmethod
    def ensure_dependencies() -> bool:
        """
        确保依赖已安装
        
        Returns:
            如果所有依赖都已安装返回 True
        """
        missing, installed = DependencyChecker.check_all()
        
        if missing:
            DependencyChecker.print_install_instructions(missing)
            return False
        
        print(f"[INFO] All dependencies satisfied: {', '.join(installed)}")
        return True


def main():
    """独立运行检查"""
    if DependencyChecker.ensure_dependencies():
        print("✅ All dependencies ready!")
        return 0
    else:
        print("❌ Missing dependencies. Please install and retry.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
