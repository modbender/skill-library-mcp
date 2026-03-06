#!/usr/bin/env python3
"""
IssueFinder Tool Wrapper
包装脚本，自动管理日志输出到 ISSUEFINDER_LOGS_PATH 环境变量指定的路径
默认路径：~/issuefinder_mcp_log
目录结构：年/月/日/VIN_xxx 或 年/月/日/文件名/
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path


def get_base_log_dir():
    """获取基础日志目录"""
    base_dir = os.environ.get('ISSUEFINDER_LOGS_PATH', os.path.expanduser('~/issuefinder_mcp_log'))
    return base_dir


def get_dated_output_dir():
    """
    获取带日期结构的输出目录: base_dir/YYYY/MM/DD/
    """
    base_dir = get_base_log_dir()
    now = datetime.now()
    dated_path = os.path.join(base_dir, now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"))
    os.makedirs(dated_path, exist_ok=True)
    return dated_path


def extract_output_subdir_from_args(args):
    """
    从命令行参数中提取输出子目录名称
    
    Args:
        args: 命令行参数列表
        
    Returns:
        str: 子目录名称，如 "VIN_xxx" 或本地文件名
    """
    # 检查是否是云端下载模式（有 --vin 参数）
    if '--vin' in args:
        vin_index = args.index('--vin')
        if vin_index + 1 < len(args):
            vin = args[vin_index + 1]
            return f"VIN_{vin}"
    
    # 检查是否是本地处理模式（有 -u 或 --upload 参数）
    if '-u' in args:
        upload_index = args.index('-u')
        if upload_index + 1 < len(args):
            file_path = args[upload_index + 1]
            return os.path.basename(file_path)
    
    if '--upload' in args:
        upload_index = args.index('--upload')
        if upload_index + 1 < len(args):
            file_path = args[upload_index + 1]
            return os.path.basename(file_path)
    
    # 默认使用时间戳
    return datetime.now().strftime("log_%Y%m%d_%H%M%S")


def main():
    """主函数"""
    # 获取原始 issuefinder-tool.py 的路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    original_tool = os.path.join(script_dir, 'issuefinder-tool.py')
    
    if not os.path.exists(original_tool):
        print(f"错误: 找不到原始工具脚本: {original_tool}")
        sys.exit(1)
    
    # 获取命令行参数（排除脚本名本身）
    args = sys.argv[1:]
    
    # 检查是否已经指定了 --output 参数
    has_output = '--output' in args or any(arg.startswith('--output=') for arg in args)
    
    # 如果没有指定 --output，则使用带日期结构的默认路径
    if not has_output:
        dated_dir = get_dated_output_dir()
        # 不在这里添加子目录，让原始脚本自己处理
        # 因为原始脚本会根据 VIN 或文件名创建子目录
        args = ['--output', dated_dir] + args
        print(f"[INFO] 使用默认输出目录: {dated_dir}")
    
    # 构建完整的命令
    cmd = [sys.executable, original_tool] + args
    
    # 执行原始工具
    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
