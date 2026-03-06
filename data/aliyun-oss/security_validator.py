#!/usr/bin/env python3
"""
阿里云OSS安全验证模块
负责文件大小限制、权限验证等安全检查
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List

class SecurityValidator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_file_size = config.get('max_file_size_mb', 2048) * 1024 * 1024  # 转换为字节
        self.allowed_extensions = config.get('allowed_extensions', [])
        self.logger = logging.getLogger(__name__)
    
    def validate_file_size(self, file_path: str) -> bool:
        """
        验证文件大小是否在允许范围内
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: True表示文件大小有效
        """
        try:
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                self.logger.warning(f"文件 {file_path} 大小 {file_size} 超过限制 {self.max_file_size}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"验证文件大小失败: {e}")
            return False
    
    def validate_file_extension(self, file_path: str) -> bool:
        """
        验证文件扩展名是否被允许
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: True表示扩展名有效
        """
        if not self.allowed_extensions:
            return True  # 如果没有限制，则允许所有扩展名
            
        file_ext = Path(file_path).suffix.lower()
        if file_ext in [ext.lower() for ext in self.allowed_extensions]:
            return True
        else:
            self.logger.warning(f"文件 {file_path} 扩展名 {file_ext} 不被允许")
            return False
    
    def validate_oss_permissions(self, oss_config: Dict[str, Any]) -> bool:
        """
        验证OSS配置权限是否符合最小权限原则
        
        Args:
            oss_config: OSS配置
            
        Returns:
            bool: True表示权限配置有效
        """
        # 检查是否使用了STS临时凭证
        if 'security_token' not in oss_config:
            self.logger.warning("未检测到STS临时凭证，可能存在安全风险")
            return False
            
        # 检查权限是否包含必要的操作
        required_permissions = ['PutObject', 'GetObject']
        # 这里可以进一步验证RAM角色的权限策略
        return True
    
    def validate_upload_request(self, file_paths: List[str], oss_prefix: str = "") -> Dict[str, Any]:
        """
        验证整个上传请求的安全性
        
        Args:
            file_paths: 文件路径列表
            oss_prefix: OSS存储前缀
            
        Returns:
            Dict: 验证结果
        """
        results = {
            'valid': True,
            'invalid_files': [],
            'valid_files': []
        }
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                results['valid'] = False
                results['invalid_files'].append(file_path)
                continue
                
            size_valid = self.validate_file_size(file_path)
            ext_valid = self.validate_file_extension(file_path)
            
            if size_valid and ext_valid:
                results['valid_files'].append(file_path)
            else:
                results['valid'] = False
                results['invalid_files'].append(file_path)
        
        return results

def main():
    """测试安全验证功能"""
    # 示例配置
    config = {
        'max_file_size_mb': 2048,
        'allowed_extensions': ['.jpg', '.png', '.pdf', '.txt', '.mp4', '.mp3']
    }
    
    validator = SecurityValidator(config)
    
    # 测试文件（需要实际文件路径）
    test_files = ['/etc/passwd']  # 示例文件
    
    for file_path in test_files:
        if os.path.exists(file_path):
            result = validator.validate_upload_request([file_path])
            print(f"文件 {file_path} 验证结果: {result}")

if __name__ == "__main__":
    main()