"""httpx AsyncClient 工厂。

[INPUT]: SDKConfig
[OUTPUT]: create_user_service_client(), create_molt_message_client()
[POS]: 提供预配置的 HTTP 客户端

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""

from __future__ import annotations

import httpx

from utils.config import SDKConfig


def create_user_service_client(config: SDKConfig) -> httpx.AsyncClient:
    """创建指向 user-service 的异步 HTTP 客户端。"""
    return httpx.AsyncClient(
        base_url=config.user_service_url,
        timeout=30.0,
        trust_env=False,
    )


def create_molt_message_client(config: SDKConfig) -> httpx.AsyncClient:
    """创建指向 molt-message 的异步 HTTP 客户端。"""
    return httpx.AsyncClient(
        base_url=config.molt_message_url,
        timeout=30.0,
        trust_env=False,
    )


__all__ = ["create_molt_message_client", "create_user_service_client"]
