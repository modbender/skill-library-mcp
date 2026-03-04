"""更新 DID Profile（昵称、简介、标签等）。

用法：
    # 更新昵称
    uv run python scripts/update_profile.py --nick-name "DID达人"

    # 更新多个字段
    uv run python scripts/update_profile.py \
        --nick-name "DID达人" \
        --bio "去中心化身份爱好者" \
        --tags "developer,did,agent"

    # 更新 Profile Markdown
    uv run python scripts/update_profile.py --profile-md "# About Me\n\nI am an agent."

[INPUT]: SDK（RPC 调用）、credential_store（加载身份凭证）
[OUTPUT]: 更新后的 Profile 信息
[POS]: Profile 更新脚本

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


PROFILE_RPC = "/user-service/did/profile/rpc"


async def update_profile(
    credential_name: str,
    nick_name: str | None = None,
    bio: str | None = None,
    tags: list[str] | None = None,
    profile_md: str | None = None,
) -> None:
    """更新自己的 Profile。"""
    params: dict = {}
    if nick_name is not None:
        params["nick_name"] = nick_name
    if bio is not None:
        params["bio"] = bio
    if tags is not None:
        params["tags"] = tags
    if profile_md is not None:
        params["profile_md"] = profile_md

    if not params:
        print("请至少指定一个要更新的字段")
        print("可用字段: --nick-name, --bio, --tags, --profile-md")
        sys.exit(1)

    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"凭证 '{credential_name}' 不可用，请先创建身份")
        sys.exit(1)

    auth, _ = auth_result
    async with create_user_service_client(config) as client:
        updated = await authenticated_rpc_call(
            client, PROFILE_RPC, "update_me", params,
            auth=auth, credential_name=credential_name,
        )
        print("Profile 更新成功:")
        print(json.dumps(updated, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="更新 DID Profile")
    parser.add_argument("--nick-name", type=str, help="昵称")
    parser.add_argument("--bio", type=str, help="个人简介")
    parser.add_argument("--tags", type=str, help="标签（逗号分隔）")
    parser.add_argument("--profile-md", type=str, help="Profile Markdown 内容")
    parser.add_argument("--credential", type=str, default="default",
                        help="凭证名称（默认: default）")

    args = parser.parse_args()

    tags = args.tags.split(",") if args.tags else None

    asyncio.run(update_profile(
        credential_name=args.credential,
        nick_name=args.nick_name,
        bio=args.bio,
        tags=tags,
        profile_md=args.profile_md,
    ))


if __name__ == "__main__":
    main()
