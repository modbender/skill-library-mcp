"""查看 DID Profile（自己或公开）。

用法：
    # 查看自己的 Profile
    uv run python scripts/get_profile.py

    # 查看指定 DID 的公开 Profile
    uv run python scripts/get_profile.py --did "did:wba:localhost:user:abc123"

    # 解析 DID 文档
    uv run python scripts/get_profile.py --resolve "did:wba:localhost:user:abc123"

[INPUT]: SDK（RPC 调用）、credential_store（加载身份凭证）
[OUTPUT]: Profile 信息的 JSON 输出
[POS]: Profile 查询脚本

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from utils import SDKConfig, create_user_service_client, rpc_call, authenticated_rpc_call
from credential_store import create_authenticator


PROFILE_RPC = "/user-service/did/profile/rpc"


async def get_my_profile(credential_name: str = "default") -> None:
    """查看自己的 Profile。"""
    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"凭证 '{credential_name}' 不可用，请先创建身份")
        sys.exit(1)

    auth, _ = auth_result
    async with create_user_service_client(config) as client:
        me = await authenticated_rpc_call(
            client, PROFILE_RPC, "get_me",
            auth=auth, credential_name=credential_name,
        )
        print(json.dumps(me, indent=2, ensure_ascii=False))


async def get_public_profile(did: str) -> None:
    """查看指定 DID 的公开 Profile。"""
    config = SDKConfig()
    async with create_user_service_client(config) as client:
        profile = await rpc_call(
            client, PROFILE_RPC, "get_public_profile", {"did": did}
        )
        print(json.dumps(profile, indent=2, ensure_ascii=False))


async def resolve_did(did: str) -> None:
    """解析 DID 文档。"""
    config = SDKConfig()
    async with create_user_service_client(config) as client:
        resolved = await rpc_call(
            client, PROFILE_RPC, "resolve", {"did": did}
        )
        print(json.dumps(resolved, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="查看 DID Profile")
    parser.add_argument("--did", type=str, help="查看指定 DID 的公开 Profile")
    parser.add_argument("--resolve", type=str, help="解析指定 DID 文档")
    parser.add_argument("--credential", type=str, default="default",
                        help="凭证名称（默认: default）")

    args = parser.parse_args()

    if args.resolve:
        asyncio.run(resolve_did(args.resolve))
    elif args.did:
        asyncio.run(get_public_profile(args.did))
    else:
        asyncio.run(get_my_profile(args.credential))


if __name__ == "__main__":
    main()
