"""
小红书MCP工具包

一个集成MCP协议的小红书自动化发布工具，支持Cookie管理、图文发布、视频发布等功能。
"""

import os
from pathlib import Path

def _get_version():
    """从version.txt文件读取版本号"""
    try:
        # 获取项目根目录（相对于src目录的上级目录）
        current_dir = Path(__file__).parent
        version_file = current_dir.parent / "version.txt"
        
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                version = f.read().strip()
                if version:
                    return version
        
        # 如果文件不存在或为空，返回默认版本
        return "1.0.0"
        
    except Exception:
        # 任何读取错误都返回默认版本
        return "1.0.0"

__version__ = _get_version()
__author__ = "XHS-Toolkit Team"
__description__ = "小红书MCP自动化工具包 - 支持图文和视频发布"

# 导出主要类
from .core.config import XHSConfig
from .core.browser import ChromeDriverManager
from .xiaohongshu.client import XHSClient
from .xiaohongshu.models import XHSNote, XHSPublishResult
from .auth.cookie_manager import CookieManager
from .server.mcp_server import MCPServer

__all__ = [
    "XHSConfig",
    "ChromeDriverManager", 
    "XHSClient",
    "XHSNote",
    "XHSPublishResult",
    "CookieManager",
    "MCPServer",
    "__version__",
    "__author__",
    "__description__"
] 