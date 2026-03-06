"""注册 + WBA 认证 + JWT 获取。

[INPUT]: httpx.AsyncClient, DIDIdentity, ANP auth 函数, rpc_call(), services
[OUTPUT]: register_did(), get_jwt_via_wba(), generate_wba_auth_header(), create_authenticated_identity()
[POS]: 封装完整的 DID 认证流程，全部基于 ANP，通过 JSON-RPC 2.0 与 user-service 通信
      RPC 路径使用 /user-service 前缀（兼容 nginx 反向代理和 localhost 直连）

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""

from __future__ import annotations

from typing import Any

import httpx
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

from anp.authentication import generate_auth_header

from utils.config import SDKConfig
from utils.identity import DIDIdentity, create_identity
from utils.rpc import rpc_call


def _secp256k1_sign_callback(
    private_key: ec.EllipticCurvePrivateKey,
) -> callable:
    """创建 secp256k1 签名回调（适配 ANP generate_auth_header 接口）。

    ANP generate_auth_header 要求 sign_callback(content: bytes, vm_fragment: str) -> bytes，
    返回 DER 格式签名。
    """

    def _callback(content: bytes, verification_method_fragment: str) -> bytes:
        return private_key.sign(content, ec.ECDSA(hashes.SHA256()))

    return _callback


def generate_wba_auth_header(
    identity: DIDIdentity,
    service_domain: str,
) -> str:
    """生成 DID WBA Authorization 头。

    Args:
        identity: DID 身份
        service_domain: 目标服务域名

    Returns:
        Authorization 头的值（DIDWba 格式）
    """
    private_key = identity.get_private_key()
    return generate_auth_header(
        did_document=identity.did_document,
        service_domain=service_domain,
        sign_callback=_secp256k1_sign_callback(private_key),
    )


async def register_did(
    client: httpx.AsyncClient,
    identity: DIDIdentity,
    name: str | None = None,
    is_public: bool = False,
    is_agent: bool = False,
    role: str | None = None,
    endpoint_url: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """注册 DID 身份。

    直接发送 identity.did_document（已含 ANP 生成的 authentication proof），
    通过 JSON-RPC 调用 user-service 的 did-auth.register 方法。

    Args:
        client: 指向 user-service 的 HTTP 客户端
        identity: DID 身份（did_document 已含 authentication proof）
        name: 显示名称
        is_public: 是否公开
        is_agent: 是否为 AI Agent
        role: 角色
        endpoint_url: 连接端点
        description: 描述

    Returns:
        注册响应 dict（含 did, user_id, message）

    Raises:
        JsonRpcError: 注册失败时抛出
        httpx.HTTPStatusError: HTTP 层错误时抛出
    """
    payload: dict[str, Any] = {"did_document": identity.did_document}
    if name is not None:
        payload["name"] = name
    if is_public:
        payload["is_public"] = True
    if is_agent:
        payload["is_agent"] = True
    if role is not None:
        payload["role"] = role
    if endpoint_url is not None:
        payload["endpoint_url"] = endpoint_url
    if description is not None:
        payload["description"] = description

    return await rpc_call(client, "/user-service/did-auth/rpc", "register", payload)


async def get_jwt_via_wba(
    client: httpx.AsyncClient,
    identity: DIDIdentity,
    domain: str,
) -> str:
    """通过 DID WBA 签名获取 JWT token。

    Args:
        client: 指向 user-service 的 HTTP 客户端
        identity: DID 身份
        domain: 服务域名

    Returns:
        JWT access token 字符串
    """
    auth_header = generate_wba_auth_header(identity, domain)
    result = await rpc_call(
        client,
        "/user-service/did-auth/rpc",
        "verify",
        {"authorization": auth_header, "domain": domain},
    )
    return result["access_token"]


async def create_authenticated_identity(
    client: httpx.AsyncClient,
    config: SDKConfig,
    name: str | None = None,
    is_public: bool = False,
    is_agent: bool = False,
    role: str | None = None,
    endpoint_url: str | None = None,
    services: list[dict[str, Any]] | None = None,
) -> DIDIdentity:
    """一站式创建完整 DID 身份（生成密钥 → 注册 → 获取 JWT）。

    使用 key-bound DID：公钥 fingerprint 自动成为 DID 路径末段（k1_{fp}），
    无需手动指定 unique_id。path_prefix 固定为 ["user"]（服务端要求）。

    Args:
        client: 指向 user-service 的 HTTP 客户端
        config: SDK 配置
        name: 显示名称
        is_public: 是否公开
        is_agent: 是否为 AI Agent
        role: 角色
        endpoint_url: 连接端点
        services: 自定义 service 条目列表，写入 DID 文档并被 proof 签名覆盖

    Returns:
        填充了 user_id 和 jwt_token 的 DIDIdentity
    """
    # 1. 创建 key-bound DID 身份（含 authentication proof，绑定到服务域名）
    #    path_prefix 固定 ["user"]：服务端要求 DID 格式为 did:wba:{domain}:user:{id}
    identity = create_identity(
        hostname=config.did_domain,
        path_prefix=["user"],
        proof_purpose="authentication",
        domain=config.did_domain,
        services=services,
    )

    # 2. 注册（直接发送 ANP 生成的文档）
    reg_result = await register_did(
        client,
        identity,
        name=name,
        is_public=is_public,
        is_agent=is_agent,
        role=role,
        endpoint_url=endpoint_url,
    )
    identity.user_id = reg_result["user_id"]

    # 3. 获取 JWT
    identity.jwt_token = await get_jwt_via_wba(client, identity, config.did_domain)

    return identity


__all__ = [
    "generate_wba_auth_header",
    "register_did",
    "get_jwt_via_wba",
    "create_authenticated_identity",
]
