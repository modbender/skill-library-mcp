"""
平台适配器注册
"""

from .base import (
    PlatformBase,
    PlatformError,
    CredentialsExpiredError,
    CredentialsNotFoundError,
    RateLimitError,
    ContentBlockedError,
)
from .zhihu import ZhihuPlatform
from .douban import DoubanPlatform

# 注册所有平台
PLATFORMS = {
    "zhihu": ZhihuPlatform,
    "douban": DoubanPlatform,
    # "weibo": WeiboPlatform,  # 待实现
}


def get_platform(name: str) -> PlatformBase:
    """获取平台实例"""
    if name not in PLATFORMS:
        raise PlatformError(f"不支持的平台: {name}，支持的平台: {', '.join(PLATFORMS.keys())}")
    return PLATFORMS[name]()


def list_platforms() -> list:
    """列出所有支持的平台"""
    return list(PLATFORMS.keys())
