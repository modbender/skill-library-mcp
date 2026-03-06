# 扩展新平台

本指南说明如何为 content-distributor 添加新平台支持。

## 架构概览

```
scripts/
├── post.py          # 主发布脚本
├── configure.py     # 凭据配置
├── distribute.py    # 批量分发
└── platforms/       # 平台适配器
    ├── __init__.py
    ├── base.py      # 基类
    ├── zhihu.py     # 知乎适配器
    ├── douban.py    # 豆瓣适配器
    └── weibo.py     # 微博适配器
```

## 添加新平台步骤

### 1. 创建平台适配器

在 `scripts/platforms/` 下创建新文件，例如 `xiaohongshu.py`：

```python
from .base import PlatformBase

class XiaohongshuPlatform(PlatformBase):
    """小红书平台适配器"""
    
    PLATFORM_NAME = "xiaohongshu"
    REQUIRED_COOKIES = ["customer-sesc", "xsec_token"]
    
    def post_note(self, title: str, content: str, images: list = None) -> dict:
        """发布笔记"""
        # 实现发布逻辑
        pass
    
    def validate_credentials(self) -> bool:
        """验证凭据有效性"""
        # 实现验证逻辑
        pass
```

### 2. 实现基类接口

所有平台适配器必须继承 `PlatformBase` 并实现以下方法：

```python
class PlatformBase:
    def load_credentials(self) -> dict:
        """从 secrets 文件加载凭据"""
        
    def save_credentials(self, creds: dict) -> None:
        """保存凭据到 secrets 文件"""
        
    def validate_credentials(self) -> bool:
        """验证凭据是否有效"""
        
    def get_headers(self) -> dict:
        """构建请求头"""
```

### 3. 注册平台

在 `scripts/platforms/__init__.py` 中注册：

```python
from .xiaohongshu import XiaohongshuPlatform

PLATFORMS = {
    "zhihu": ZhihuPlatform,
    "douban": DoubanPlatform,
    "weibo": WeiboPlatform,
    "xiaohongshu": XiaohongshuPlatform,  # 新增
}
```

### 4. 更新凭据配置

在 `references/credentials.md` 中添加新平台的 Cookie 获取说明。

### 5. 更新 SKILL.md

在支持平台列表中添加新平台。

## 平台特性标记

不同平台支持不同的发布类型，使用 `SUPPORTED_TYPES` 标记：

```python
class XiaohongshuPlatform(PlatformBase):
    SUPPORTED_TYPES = ["note", "video"]
```

## 错误处理

平台适配器应抛出统一的异常：

```python
from .exceptions import (
    CredentialsExpiredError,
    RateLimitError,
    ContentBlockedError,
    PlatformError,
)
```

## 测试

为新平台添加测试用例，确保：
1. 凭据验证正常
2. 发布功能正常
3. 错误处理正确
