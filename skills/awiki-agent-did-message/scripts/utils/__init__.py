"""awiki-sdk：DID 身份创建、WBA 认证、JWT 获取的通用 SDK。

[INPUT]: ANP 库
[OUTPUT]: 公共 API（DIDIdentity, create_identity, register_did, ...）
[POS]: 包入口，集中导出所有公共接口

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""

# 核心类型
from utils.config import SDKConfig
from utils.identity import DIDIdentity, create_identity, load_private_key
from utils.auth import (
    generate_wba_auth_header,
    register_did,
    get_jwt_via_wba,
    create_authenticated_identity,
)
from utils.client import create_user_service_client, create_molt_message_client
from utils.e2ee import E2eeClient
from utils.rpc import JsonRpcError, rpc_call, authenticated_rpc_call

__all__ = [
    # config
    "SDKConfig",
    # identity
    "DIDIdentity",
    "create_identity",
    "load_private_key",
    # auth
    "generate_wba_auth_header",
    "register_did",
    "get_jwt_via_wba",
    "create_authenticated_identity",
    # client
    "create_user_service_client",
    "create_molt_message_client",
    # e2ee
    "E2eeClient",
    # rpc
    "JsonRpcError",
    "rpc_call",
    "authenticated_rpc_call",
]
