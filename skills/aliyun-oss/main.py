#!/usr/bin/env python3
"""
阿里云OSS文件上传工具主入口
支持单文件、批量上传和文件检索功能
"""

import sys
import os
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.append(str(Path(__file__).parent))

def main():
    if len(sys.argv) < 2:
        print("用法: python3 main.py <command> [options]")
        print("命令:")
        print("  upload <file_path> [prefix]     - 上传单个文件")
        print("  batch_upload <file_paths...>    - 批量上传文件")  
        print("  search <filename>               - 检索OSS中的文件")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "upload":
        if len(sys.argv) < 3:
            print("用法: upload <file_path> [prefix]")
            sys.exit(1)
        from aliyun_oss_uploader import AliyunOSSUploader
        uploader = AliyunOSSUploader()
        file_path = sys.argv[2]
        prefix = sys.argv[3] if len(sys.argv) > 3 else ""
        result = uploader.upload_single_file(file_path, oss_key=prefix if prefix else None)
        print(result)
        
    elif command == "batch_upload":
        if len(sys.argv) < 3:
            print("用法: batch_upload <file_paths...> [oss_prefix]")
            sys.exit(1)
        from aliyun_oss_uploader import AliyunOSSUploader
        uploader = AliyunOSSUploader()
        if len(sys.argv) > 3:
            file_paths = sys.argv[2:-1]
            oss_prefix = sys.argv[-1]
        else:
            file_paths = sys.argv[2:]
            oss_prefix = None
        results = uploader.upload_multiple_files(file_paths, oss_prefix)
        for result in results:
            print(result)
            
    elif command == "search":
        if len(sys.argv) < 3:
            print("用法: search <filename>")
            sys.exit(1)
        from aliyun_oss_uploader import AliyunOSSUploader
        uploader = AliyunOSSUploader()
        filename = sys.argv[2]
        result = uploader.search_file_by_name(filename)
        print(result)
        
    else:
        print(f"未知命令: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()