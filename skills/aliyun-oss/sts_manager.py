#!/usr/bin/env python3
"""
阿里云OSS认证管理器（简化版）
仅支持AK/SK直接认证
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

class AuthManager:
    def __init__(self, config_path: str = "/root/.openclaw/aliyun-oss-config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """加载OSS配置"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件未找到: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_credentials(self) -> Dict[str, str]:
        """获取AK/SK凭证"""
        auth_config = self.config.get('auth', {})
        
        if 'access_key_id' not in auth_config or 'access_key_secret' not in auth_config:
            raise ValueError("配置文件中缺少 access_key_id 或 access_key_secret")
        
        return {
            'access_key_id': auth_config['access_key_id'],
            'access_key_secret': auth_config['access_key_secret']
        }