import os
from uuid import uuid4
import sys
from loguru import logger

# 配置基础日志记录器
logger.remove()
logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")

def get_file_size(file_path: str) -> int:
    """获取文件大小 (比特)"""
    if os.path.exists(file_path):
        return os.path.getsize(file_path)
    return 0

def generate_output_path(input_path: str) -> str:
    """在输入文同级目录生成带有 uuid 或 timestamp 的压缩后新路径"""
    directory, filename = os.path.split(input_path)
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_compressed_{uuid4().hex[:6]}{ext}"
    return os.path.join(directory, new_filename)
