#!/usr/bin/env python3
"""
阿里云OSS技能主入口
提供安全的文件上传和临时链接生成功能
"""

import sys
import os
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.append(str(Path(__file__).parent))

def main():
    """主函数入口"""
    from .main import handle_media
    if len(sys.argv) != 2:
        print("Usage: __main__.py <file_path>", file=sys.stderr)
        sys.exit(1)
    
    result = handle_media(sys.argv[1])
    print(result)

if __name__ == "__main__":
    main()