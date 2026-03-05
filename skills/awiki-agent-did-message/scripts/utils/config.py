"""SDK 配置。

[INPUT]: 无（纯数据类）
[OUTPUT]: SDKConfig dataclass
[POS]: 集中管理服务地址和域名配置

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class SDKConfig:
    """awiki 系统服务配置。"""

    user_service_url: str = field(
        default_factory=lambda: os.environ.get(
            "E2E_USER_SERVICE_URL", "https://awiki.ai"
        )
    )
    molt_message_url: str = field(
        default_factory=lambda: os.environ.get(
            "E2E_MOLT_MESSAGE_URL", "https://awiki.ai"
        )
    )
    did_domain: str = field(
        default_factory=lambda: os.environ.get("E2E_DID_DOMAIN", "awiki.ai")
    )


__all__ = ["SDKConfig"]
