"""JSON-RPC 2.0 客户端辅助函数。

[INPUT]: httpx.AsyncClient, 端点路径, 方法名, 参数, DIDWbaAuthHeader
[OUTPUT]: rpc_call() 辅助函数, authenticated_rpc_call() 带 401 重试, JsonRpcError 异常类
[POS]: 为 auth.py 和外部调用者提供统一的 JSON-RPC 调用封装

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""

from __future__ import annotations

from typing import Any

import httpx


class JsonRpcError(Exception):
    """JSON-RPC 错误响应异常。"""

    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"JSON-RPC error {code}: {message}")


async def rpc_call(
    client: httpx.AsyncClient,
    endpoint: str,
    method: str,
    params: dict | None = None,
    request_id: int | str = 1,
) -> Any:
    """发送 JSON-RPC 2.0 请求并返回 result。

    Args:
        client: httpx 异步客户端。
        endpoint: RPC 端点路径（如 "/did-auth/rpc"）。
        method: RPC 方法名（如 "register"）。
        params: 方法参数。
        request_id: 请求 ID。

    Returns:
        JSON-RPC result 字段的值。

    Raises:
        JsonRpcError: 服务端返回 JSON-RPC error 时。
        httpx.HTTPStatusError: HTTP 层错误时。
    """
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": request_id,
    }
    resp = await client.post(endpoint, json=payload)
    resp.raise_for_status()
    body = resp.json()
    if body.get("error") is not None:
        error = body["error"]
        raise JsonRpcError(
            error["code"],
            error["message"],
            error.get("data"),
        )
    return body["result"]


__all__ = [
    "JsonRpcError",
    "rpc_call",
    "authenticated_rpc_call",
]


async def authenticated_rpc_call(
    client: httpx.AsyncClient,
    endpoint: str,
    method: str,
    params: dict | None = None,
    request_id: int | str = 1,
    *,
    auth: Any = None,
    credential_name: str = "default",
) -> Any:
    """带 401 自动重试的 JSON-RPC 2.0 请求。

    使用 DIDWbaAuthHeader 管理认证头和 token 缓存。
    401 时自动清除过期 token 并重新生成 DIDWba 认证头重试。

    Args:
        client: httpx 异步客户端（已设置 base_url）。
        endpoint: RPC 端点路径。
        method: RPC 方法名。
        params: 方法参数。
        request_id: 请求 ID。
        auth: DIDWbaAuthHeader 实例。
        credential_name: 凭证名称（用于持久化新 JWT）。

    Returns:
        JSON-RPC result 字段的值。

    Raises:
        JsonRpcError: 服务端返回 JSON-RPC error 时。
        httpx.HTTPStatusError: HTTP 层错误时（非 401）。
    """
    server_url = str(client.base_url)
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": request_id,
    }

    # 获取认证头
    auth_headers = auth.get_auth_header(server_url)
    resp = await client.post(endpoint, json=payload, headers=auth_headers)

    # 401 → 清除过期 token → 重新认证 → 重试
    if resp.status_code == 401:
        auth.clear_token(server_url)
        auth_headers = auth.get_auth_header(server_url, force_new=True)
        resp = await client.post(endpoint, json=payload, headers=auth_headers)

    resp.raise_for_status()

    # 成功：从响应头缓存新 token
    # 注意：httpx 响应头 key 为小写，DIDWbaAuthHeader.update_token() 期望 "Authorization"
    auth_header_value = resp.headers.get("authorization", "")
    new_token = auth.update_token(server_url, {"Authorization": auth_header_value})
    if new_token:
        from credential_store import update_jwt
        update_jwt(credential_name, new_token)

    body = resp.json()
    if body.get("error") is not None:
        error = body["error"]
        raise JsonRpcError(
            error["code"],
            error["message"],
            error.get("data"),
        )
    return body["result"]
