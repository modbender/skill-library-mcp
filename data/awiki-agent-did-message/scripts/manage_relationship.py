"""关注/取关/查看关系状态/列表。

用法：
    # 关注
    uv run python scripts/manage_relationship.py --follow "did:wba:localhost:user:abc123"

    # 取消关注
    uv run python scripts/manage_relationship.py --unfollow "did:wba:localhost:user:abc123"

    # 查看与指定 DID 的关系状态
    uv run python scripts/manage_relationship.py --status "did:wba:localhost:user:abc123"

    # 查看关注列表
    uv run python scripts/manage_relationship.py --following

    # 查看粉丝列表
    uv run python scripts/manage_relationship.py --followers

[INPUT]: SDK（RPC 调用）、credential_store（加载身份凭证）
[OUTPUT]: 关系操作结果
[POS]: 社交关系管理脚本

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from utils import SDKConfig, create_user_service_client, authenticated_rpc_call
from credential_store import create_authenticator


RPC_ENDPOINT = "/user-service/did/relationships/rpc"


async def follow(target_did: str, credential_name: str = "default") -> None:
    """关注指定 DID。"""
    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"凭证 '{credential_name}' 不可用，请先创建身份")
        sys.exit(1)

    auth, _ = auth_result
    async with create_user_service_client(config) as client:
        result = await authenticated_rpc_call(
            client, RPC_ENDPOINT, "follow", {"target_did": target_did},
            auth=auth, credential_name=credential_name,
        )
        print("关注成功:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def unfollow(target_did: str, credential_name: str = "default") -> None:
    """取消关注指定 DID。"""
    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"凭证 '{credential_name}' 不可用，请先创建身份")
        sys.exit(1)

    auth, _ = auth_result
    async with create_user_service_client(config) as client:
        result = await authenticated_rpc_call(
            client, RPC_ENDPOINT, "unfollow", {"target_did": target_did},
            auth=auth, credential_name=credential_name,
        )
        print("取关成功:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def get_status(target_did: str, credential_name: str = "default") -> None:
    """查看与指定 DID 的关系状态。"""
    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"凭证 '{credential_name}' 不可用，请先创建身份")
        sys.exit(1)

    auth, _ = auth_result
    async with create_user_service_client(config) as client:
        result = await authenticated_rpc_call(
            client, RPC_ENDPOINT, "get_status", {"target_did": target_did},
            auth=auth, credential_name=credential_name,
        )
        print("关系状态:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def get_following(
    credential_name: str = "default",
    limit: int = 50,
    offset: int = 0,
) -> None:
    """查看关注列表。"""
    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"凭证 '{credential_name}' 不可用，请先创建身份")
        sys.exit(1)

    auth, _ = auth_result
    async with create_user_service_client(config) as client:
        result = await authenticated_rpc_call(
            client, RPC_ENDPOINT, "get_following",
            {"limit": limit, "offset": offset},
            auth=auth, credential_name=credential_name,
        )
        print("关注列表:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def get_followers(
    credential_name: str = "default",
    limit: int = 50,
    offset: int = 0,
) -> None:
    """查看粉丝列表。"""
    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"凭证 '{credential_name}' 不可用，请先创建身份")
        sys.exit(1)

    auth, _ = auth_result
    async with create_user_service_client(config) as client:
        result = await authenticated_rpc_call(
            client, RPC_ENDPOINT, "get_followers",
            {"limit": limit, "offset": offset},
            auth=auth, credential_name=credential_name,
        )
        print("粉丝列表:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="社交关系管理")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--follow", type=str, help="关注指定 DID")
    group.add_argument("--unfollow", type=str, help="取消关注指定 DID")
    group.add_argument("--status", type=str, help="查看与指定 DID 的关系状态")
    group.add_argument("--following", action="store_true", help="查看关注列表")
    group.add_argument("--followers", action="store_true", help="查看粉丝列表")

    parser.add_argument("--credential", type=str, default="default",
                        help="凭证名称（默认: default）")
    parser.add_argument("--limit", type=int, default=50,
                        help="列表返回数量（默认: 50）")
    parser.add_argument("--offset", type=int, default=0,
                        help="列表偏移量（默认: 0）")

    args = parser.parse_args()

    if args.follow:
        asyncio.run(follow(args.follow, args.credential))
    elif args.unfollow:
        asyncio.run(unfollow(args.unfollow, args.credential))
    elif args.status:
        asyncio.run(get_status(args.status, args.credential))
    elif args.following:
        asyncio.run(get_following(args.credential, args.limit, args.offset))
    elif args.followers:
        asyncio.run(get_followers(args.credential, args.limit, args.offset))


if __name__ == "__main__":
    main()
