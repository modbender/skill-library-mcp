#!/usr/bin/env python3
"""
阿里云OSS文件处理器
负责文件验证、重命名、分片上传等核心功能
"""

import os
import uuid
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

class FileProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_file_size = config.get('max_file_size_mb', 2048) * 1024 * 1024  # 转换为字节
        self.chunk_size = config.get('chunk_size_mb', 10) * 1024 * 1024  # 分片大小
        self.rename_strategy = config.get('rename_strategy', 'uuid')  # uuid, timestamp
        
    def validate_file(self, file_path: str) -> bool:
        """
        验证文件是否符合上传要求
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否通过验证
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            max_mb = self.max_file_size // (1024 * 1024)
            raise ValueError(f"文件大小超过限制 ({max_mb}MB): {file_path}")
            
        return True
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """
        生成唯一文件名，保留原始扩展名
        
        Args:
            original_filename: 原始文件名
            
        Returns:
            str: 唯一文件名
        """
        name, ext = os.path.splitext(original_filename)
        
        if self.rename_strategy == 'uuid':
            unique_name = str(uuid.uuid4())
        elif self.rename_strategy == 'timestamp':
            timestamp = int(time.time() * 1000)
            random_suffix = str(uuid.uuid4())[:8]
            unique_name = f"{timestamp}_{random_suffix}"
        else:
            # 默认使用UUID
            unique_name = str(uuid.uuid4())
            
        return f"{unique_name}{ext}"
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            dict: 文件信息
        """
        stat = os.stat(file_path)
        return {
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'extension': os.path.splitext(file_path)[1].lower()
        }
    
    def should_use_multipart(self, file_path: str) -> bool:
        """
        判断是否应该使用分片上传
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否使用分片上传
        """
        file_size = os.path.getsize(file_path)
        multipart_threshold = self.config.get('multipart_threshold_mb', 100) * 1024 * 1024
        return file_size > multipart_threshold
    
    def split_file_for_upload(self, file_path: str) -> List[bytes]:
        """
        将文件分割为分片（用于分片上传）
        
        Args:
            file_path: 文件路径
            
        Returns:
            list: 分片数据列表
        """
        chunks = []
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                chunks.append(chunk)
        return chunks

def main():
    """测试文件处理器"""
    config = {
        'max_file_size_mb': 2048,
        'chunk_size_mb': 10,
        'multipart_threshold_mb': 100,
        'rename_strategy': 'uuid'
    }
    
    processor = FileProcessor(config)
    
    # 测试文件验证
    try:
        test_file = "/etc/hosts"  # 使用系统小文件测试
        processor.validate_file(test_file)
        print(f"✅ 文件验证通过: {test_file}")
        
        # 测试文件名生成
        original_name = "test.txt"
        new_name = processor.generate_unique_filename(original_name)
        print(f"✅ 原始文件名: {original_name}")
        print(f"✅ 新文件名: {new_name}")
        
        # 测试文件信息
        info = processor.get_file_info(test_file)
        print(f"✅ 文件信息: {info}")
        
    except Exception as e:
        print(f"❌ 文件处理错误: {e}")

if __name__ == "__main__":
    main()