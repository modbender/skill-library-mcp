"""创建群组/邀请/加入/查看成员。

用法：
    # 创建群组
    uv run python scripts/manage_group.py --create --group-name "技术交流群" --description "讨论技术话题"

    # 邀请用户加入群组
    uv run python scripts/manage_group.py --invite --group-id GROUP_ID --target-did "did:wba:..."

    # 加入群组（通过邀请 ID）
    uv run python scripts/manage_group.py --join --group-id GROUP_ID --invite-id INVITE_ID

    # 查看群组成员
    uv run python scripts/manage_group.py --members --group-id GROUP_ID

[INPUT]: SDK（RPC 调用）、credential_store（加载身份凭证）
[OUTPUT]: 群组操作结果
[POS]: 群组管理脚本

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


async def create_group(
    group_name: str,
    description: str | None = None,
    max_members: int = 100,
    is_public: bool = True,
    credential_name: str = "default",
) -> None:
    """创建群组。"""
    params: dict = {
        "name": group_name,
        "max_members": max_members,
        "is_public": is_public,
    }
    if description:
        params["description"] = description

    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"凭证 '{credential_name}' 不可用，请先创建身份")
        sys.exit(1)

    auth, _ = auth_result
    async with create_user_service_client(config) as client:
        result = await authenticated_rpc_call(
            client, RPC_ENDPOINT, "create_group", params,
            auth=auth, credential_name=credential_name,
        )
        print("群组创建成功:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def invite_to_group(
    group_id: str,
    target_did: str,
    credential_name: str = "default",
) -> None:
    """邀请用户加入群组。"""
    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"凭证 '{credential_name}' 不可用，请先创建身份")
        sys.exit(1)

    auth, _ = auth_result
    async with create_user_service_client(config) as client:
        result = await authenticated_rpc_call(
            client, RPC_ENDPOINT, "invite",
            {"group_id": group_id, "target_did": target_did},
            auth=auth, credential_name=credential_name,
        )
        print("邀请发送成功:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def join_group(
    group_id: str,
    invite_id: str,
    credential_name: str = "default",
) -> None:
    """通过邀请加入群组。"""
    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"凭证 '{credential_name}' 不可用，请先创建身份")
        sys.exit(1)

    auth, _ = auth_result
    async with create_user_service_client(config) as client:
        result = await authenticated_rpc_call(
            client, RPC_ENDPOINT, "join",
            {"group_id": group_id, "invite_id": invite_id},
            auth=auth, credential_name=credential_name,
        )
        print("加入群组成功:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def get_group_members(
    group_id: str,
    credential_name: str = "default",
) -> None:
    """查看群组成员。"""
    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"凭证 '{credential_name}' 不可用，请先创建身份")
        sys.exit(1)

    auth, _ = auth_result
    async with create_user_service_client(config) as client:
        result = await authenticated_rpc_call(
            client, RPC_ENDPOINT, "get_group_members",
            {"group_id": group_id},
            auth=auth, credential_name=credential_name,
        )
        print("群组成员:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="群组管理")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--create", action="store_true", help="创建群组")
    group.add_argument("--invite", action="store_true", help="邀请用户加入群组")
    group.add_argument("--join", action="store_true", help="加入群组")
    group.add_argument("--members", action="store_true", help="查看群组成员")

    parser.add_argument("--group-name", type=str, help="群组名称（创建时必需）")
    parser.add_argument("--description", type=str, help="群组描述")
    parser.add_argument("--group-id", type=str, help="群组 ID")
    parser.add_argument("--target-did", type=str, help="目标 DID（邀请时必需）")
    parser.add_argument("--invite-id", type=str, help="邀请 ID（加入时必需）")
    parser.add_argument("--max-members", type=int, default=100,
                        help="最大成员数（默认: 100）")
    parser.add_argument("--public", action="store_true", default=True,
                        help="是否公开群组")
    parser.add_argument("--credential", type=str, default="default",
                        help="凭证名称（默认: default）")

    args = parser.parse_args()

    if args.create:
        if not args.group_name:
            parser.error("创建群组需要 --group-name")
        asyncio.run(create_group(
            args.group_name, args.description, args.max_members,
            args.public, args.credential,
        ))
    elif args.invite:
        if not args.group_id or not args.target_did:
            parser.error("邀请需要 --group-id 和 --target-did")
        asyncio.run(invite_to_group(args.group_id, args.target_did, args.credential))
    elif args.join:
        if not args.group_id or not args.invite_id:
            parser.error("加入群组需要 --group-id 和 --invite-id")
        asyncio.run(join_group(args.group_id, args.invite_id, args.credential))
    elif args.members:
        if not args.group_id:
            parser.error("查看成员需要 --group-id")
        asyncio.run(get_group_members(args.group_id, args.credential))


if __name__ == "__main__":
    main()
