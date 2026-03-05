"""
平台适配器基类和异常定义
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


SECRETS_FILE = Path.home() / "clawd" / "secrets" / "content-distributor.json"


class PlatformError(Exception):
    """平台操作错误基类"""
    pass


class CredentialsExpiredError(PlatformError):
    """凭据过期"""
    pass


class CredentialsNotFoundError(PlatformError):
    """凭据未配置"""
    pass


class RateLimitError(PlatformError):
    """频率限制"""
    pass


class ContentBlockedError(PlatformError):
    """内容被屏蔽"""
    pass


class PlatformBase(ABC):
    """平台适配器基类"""
    
    PLATFORM_NAME: str = ""
    REQUIRED_COOKIES: list = []
    SUPPORTED_TYPES: list = []
    
    def __init__(self):
        self.credentials = self.load_credentials()
    
    def load_credentials(self) -> dict:
        """从 secrets 文件加载凭据"""
        if not SECRETS_FILE.exists():
            raise CredentialsNotFoundError(
                f"凭据文件不存在: {SECRETS_FILE}\n"
                f"请运行: python3 scripts/configure.py --platform {self.PLATFORM_NAME}"
            )
        
        with open(SECRETS_FILE, 'r', encoding='utf-8') as f:
            secrets = json.load(f)
        
        if self.PLATFORM_NAME not in secrets:
            raise CredentialsNotFoundError(
                f"未找到 {self.PLATFORM_NAME} 的凭据\n"
                f"请运行: python3 scripts/configure.py --platform {self.PLATFORM_NAME}"
            )
        
        creds = secrets[self.PLATFORM_NAME]
        
        # 验证必需的 Cookie
        cookies = creds.get("cookies", {})
        missing = [c for c in self.REQUIRED_COOKIES if c not in cookies]
        if missing:
            raise CredentialsNotFoundError(
                f"{self.PLATFORM_NAME} 缺少必需的 Cookie: {', '.join(missing)}\n"
                f"请运行: python3 scripts/configure.py --platform {self.PLATFORM_NAME}"
            )
        
        return creds
    
    def get_cookies_string(self) -> str:
        """获取 Cookie 字符串格式"""
        cookies = self.credentials.get("cookies", {})
        return "; ".join(f"{k}={v}" for k, v in cookies.items())
    
    def get_headers(self) -> dict:
        """构建基础请求头"""
        return {
            "User-Agent": self.credentials.get(
                "user_agent",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            ),
            "Cookie": self.get_cookies_string(),
        }
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """验证凭据是否有效"""
        pass
    
    @abstractmethod
    def post(self, post_type: str, **kwargs) -> dict:
        """发布内容"""
        pass
