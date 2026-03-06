#!/usr/bin/env python3
"""
阿里云OSS文件上传工具 - 核心功能模块
支持单文件、批量、大文件分片上传，生成预签名URL
"""

import os
import sys
import json
import uuid
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

# 阿里云OSS SDK
try:
    import oss2
    from oss2 import SizedFileAdapter, determine_part_size
    from oss2.models import PartInfo
except ImportError:
    print("❌ 需要安装阿里云OSS SDK: pip install oss2")
    sys.exit(1)

class AliyunOSSUploader:
    def __init__(self, config_path: str = "/root/.openclaw/aliyun-oss-config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.auth = None
        self.bucket = None
        self.init_oss_client()
    
    def load_config(self) -> dict:
        """加载OSS配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件未找到: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def init_oss_client(self):
        """初始化OSS客户端 - 使用AK/SK认证"""
        # 从配置文件获取AK/SK
        auth_config = self.config.get('auth', {})
        
        if 'access_key_id' not in auth_config or 'access_key_secret' not in auth_config:
            raise ValueError("配置文件中缺少必要的认证信息: access_key_id 和 access_key_secret")
        
        # AK/SK认证
        self.auth = oss2.Auth(
            auth_config['access_key_id'],
            auth_config['access_key_secret']
        )
        
        # 初始化Bucket
        endpoint = self.config['endpoint']
        bucket_name = self.config['bucket_name']
        self.bucket = oss2.Bucket(self.auth, endpoint, bucket_name)
    
    def validate_file_size(self, file_path: str) -> bool:
        """验证文件大小是否符合限制"""
        max_size = self.config.get('max_file_size_mb', 2048) * 1024 * 1024
        file_size = os.path.getsize(file_path)
        return file_size <= max_size
    
    def generate_unique_filename(self, original_filename: str, strategy: str = "uuid") -> str:
        """
        生成唯一文件名
        strategy: "uuid" | "timestamp"
        """
        name, ext = os.path.splitext(original_filename)
        
        if strategy == "uuid":
            unique_name = str(uuid.uuid4())
        elif strategy == "timestamp":
            timestamp = int(time.time() * 1000)
            random_suffix = str(uuid.uuid4())[:8]
            unique_name = f"{timestamp}_{random_suffix}"
        else:
            unique_name = str(uuid.uuid4())
        
        return f"{unique_name}{ext}"
    
    def upload_single_file(
        self, 
        local_file: str, 
        oss_key: Optional[str] = None,
        rename_strategy: str = "uuid",
        public_read: bool = False
    ) -> Dict[str, str]:
        """
        上传单个文件
        
        Args:
            local_file: 本地文件路径
            oss_key: OSS中的文件路径（可选）
            rename_strategy: 重命名策略
            public_read: 是否设置为公共读（慎用）
            
        Returns:
            包含上传结果和预签名URL的字典
        """
        # 验证文件存在
        if not os.path.exists(local_file):
            raise FileNotFoundError(f"文件不存在: {local_file}")
            
        # 验证文件大小
        if not self.validate_file_size(local_file):
            raise ValueError(f"文件大小超过限制: {local_file}")
        
        # 生成OSS key
        if oss_key is None:
            filename = os.path.basename(local_file)
            unique_filename = self.generate_unique_filename(filename, rename_strategy)
            oss_key = unique_filename
        elif '/' not in oss_key and not oss_key.startswith('/'):
            # 如果只提供了文件名，使用默认前缀
            prefix = self.config.get('default_prefix', '')
            if prefix:
                oss_key = f"{prefix.rstrip('/')}/{oss_key}"
        
        # 获取文件大小
        file_size = os.path.getsize(local_file)
        large_file_threshold = self.config.get('large_file_threshold_mb', 100) * 1024 * 1024
        
        try:
            if file_size > large_file_threshold:
                # 大文件分片上传
                result = self._upload_large_file(local_file, oss_key)
            else:
                # 小文件直接上传
                with open(local_file, 'rb') as f:
                    self.bucket.put_object(oss_key, f)
                result = {"key": oss_key, "etag": "small_file"}
            
            # 设置公共读权限（如果需要）
            if public_read:
                self.bucket.put_object_acl(oss_key, oss2.OBJECT_ACL_PUBLIC_READ)
            
            # 生成预签名URL
            presigned_url = self.generate_presigned_url(
                oss_key, 
                expire_hours=self.config.get('default_expire_hours', 0.5)
            )
            
            return {
                "status": "success",
                "oss_key": oss_key,
                "file_size": file_size,
                "presigned_url": presigned_url,
                "public_url": f"https://{self.config['bucket_name']}.{self.config['endpoint'].replace('https://', '').replace('http://', '')}/{oss_key}" if public_read else None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "oss_key": oss_key
            }
    
    def _upload_large_file(self, local_file: str, oss_key: str) -> Dict[str, str]:
        """大文件分片上传"""
        total_size = os.path.getsize(local_file)
        part_size = determine_part_size(total_size, preferred_size=100 * 1024)
        
        upload_id = self.bucket.init_multipart_upload(oss_key).upload_id
        parts = []
        
        with open(local_file, 'rb') as fileobj:
            part_number = 1
            offset = 0
            
            while offset < total_size:
                size_to_upload = min(part_size, total_size - offset)
                result = self.bucket.upload_part(
                    oss_key, upload_id, part_number,
                    SizedFileAdapter(fileobj, size_to_upload)
                )
                parts.append(PartInfo(part_number, result.etag))
                offset += size_to_upload
                part_number += 1
        
        self.bucket.complete_multipart_upload(oss_key, upload_id, parts)
        return {"key": oss_key, "etag": "multipart"}
    
    def upload_multiple_files(
        self, 
        local_files: List[str], 
        oss_prefix: Optional[str] = None,
        rename_strategy: str = "uuid",
        public_read: bool = False
    ) -> List[Dict[str, str]]:
        """批量上传文件"""
        results = []
        for local_file in local_files:
            if not os.path.exists(local_file):
                results.append({
                    "status": "error",
                    "error": f"文件不存在: {local_file}",
                    "oss_key": None
                })
                continue
                
            if oss_prefix:
                filename = os.path.basename(local_file)
                oss_key = f"{oss_prefix.rstrip('/')}/{filename}"
            else:
                oss_key = None
            
            result = self.upload_single_file(
                local_file, 
                oss_key, 
                rename_strategy, 
                public_read
            )
            results.append(result)
        
        return results
    
    def generate_presigned_url(self, oss_key: str, expire_hours: float = 0.5) -> str:
        """生成预签名URL（强制使用HTTPS）"""
        expire_seconds = int(expire_hours * 3600)
        url = self.bucket.sign_url('GET', oss_key, expire_seconds)
        # 强制转换为HTTPS
        if url.startswith('http://'):
            url = 'https://' + url[7:]
        return url
    
    def search_file_by_name(self, filename: str, prefix: str = "") -> List[Dict[str, str]]:
        """根据文件名搜索OSS中的文件"""
        results = []
        try:
            for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
                if filename in obj.key:
                    presigned_url = self.generate_presigned_url(
                        obj.key,
                        expire_hours=self.config.get('default_expire_hours', 0.5)
                    )
                    results.append({
                        "oss_key": obj.key,
                        "size": obj.size,
                        "last_modified": obj.last_modified,
                        "presigned_url": presigned_url
                    })
        except Exception as e:
            print(f"搜索文件时出错: {e}")
        
        return results

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python3 aliyun_oss_uploader.py <action> [args...]")
        print("支持的操作:")
        print("  upload <file_path> [oss_key] [rename_strategy] [public_read]")
        print("  batch_upload <file1> <file2> ... [oss_prefix]")
        print("  search <filename> [prefix]")
        sys.exit(1)
    
    action = sys.argv[1]
    uploader = AliyunOSSUploader()
    
    if action == "upload":
        if len(sys.argv) < 3:
            print("用法: upload <file_path> [oss_key] [rename_strategy] [public_read]")
            sys.exit(1)
        
        file_path = sys.argv[2]
        oss_key = sys.argv[3] if len(sys.argv) > 3 else None
        rename_strategy = sys.argv[4] if len(sys.argv) > 4 else "uuid"
        public_read = sys.argv[5].lower() == "true" if len(sys.argv) > 5 else False
        
        result = uploader.upload_single_file(file_path, oss_key, rename_strategy, public_read)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif action == "batch_upload":
        if len(sys.argv) < 3:
            print("用法: batch_upload <file1> <file2> ... [oss_prefix]")
            sys.exit(1)
        
        files = sys.argv[2:-1] if len(sys.argv) > 3 else [sys.argv[2]]
        oss_prefix = sys.argv[-1] if len(sys.argv) > 3 else None
        
        results = uploader.upload_multiple_files(files, oss_prefix)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    elif action == "search":
        if len(sys.argv) < 3:
            print("用法: search <filename> [prefix]")
            sys.exit(1)
        
        filename = sys.argv[2]
        prefix = sys.argv[3] if len(sys.argv) > 3 else ""
        
        results = uploader.search_file_by_name(filename, prefix)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    else:
        print(f"不支持的操作: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()