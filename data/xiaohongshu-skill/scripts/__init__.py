"""
xiaohongshu-skill

基于 xiaohongshu-mcp Go 源码翻译的 Python Playwright 实现
"""

from .client import XiaohongshuClient, create_client, DEFAULT_COOKIE_PATH
from . import login
from . import search
from . import feed
from . import user
from . import comment
from . import interact
from . import explore
from . import publish

__version__ = "1.1.0"
__all__ = [
    "XiaohongshuClient",
    "create_client",
    "DEFAULT_COOKIE_PATH",
    "login",
    "search",
    "feed",
    "user",
    "comment",
    "interact",
    "explore",
    "publish",
]
