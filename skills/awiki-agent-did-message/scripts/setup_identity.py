"""创建或恢复 DID 身份。

首次创建新身份并保存到本地，后续可复用已保存的身份。

用法：
    # 创建新身份
    uv run python scripts/setup_identity.py --name MyAgent

    # 加载已保存的身份
    uv run python scripts/setup_identity.py --load default

    # 列出所有已保存的身份
    uv run python scripts/setup_identity.py --list

    # 删除已保存的身份
    uv run python scripts/setup_identity.py --delete myid

[INPUT]: SDK（身份创建、注册、认证）、credential_store（凭证持久化 + authenticator 工厂）
[OUTPUT]: 创建/加载/列出/删除 DID 身份
[POS]: 身份管理入口脚本，首次使用前必须调用

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from utils import (
    SDKConfig,
    create_identity,
    create_user_service_client,
    register_did,
    get_jwt_via_wba,
    create_authenticated_identity,
    authenticated_rpc_call,
    rpc_call,
)
from credential_store import (
    save_identity,
    load_identity,
    list_identities,
    delete_identity,
    update_jwt,
    create_authenticator,
)


async def create_new_identity(
    name: str,
    display_name: str | None = None,
    credential_name: str = "default",
    is_agent: bool = False,
) -> None:
    """创建新的 DID 身份并保存。"""
    config = SDKConfig()
    print(f"服务配置:")
    print(f"  user-service: {config.user_service_url}")
    print(f"  DID 域名    : {config.did_domain}")

    async with create_user_service_client(config) as client:
        print(f"\n正在创建 DID 身份...")
        identity = await create_authenticated_identity(
            client=client,
            config=config,
            name=display_name or name,
            is_agent=is_agent,
        )

        print(f"  DID       : {identity.did}")
        print(f"  unique_id : {identity.unique_id}")
        print(f"  user_id   : {identity.user_id}")
        print(f"  JWT token : {identity.jwt_token[:50]}...")

        # 保存凭证
        path = save_identity(
            did=identity.did,
            unique_id=identity.unique_id,
            user_id=identity.user_id,
            private_key_pem=identity.private_key_pem,
            public_key_pem=identity.public_key_pem,
            jwt_token=identity.jwt_token,
            display_name=display_name or name,
            name=credential_name,
            did_document=identity.did_document,
            e2ee_signing_private_pem=identity.e2ee_signing_private_pem,
            e2ee_agreement_private_pem=identity.e2ee_agreement_private_pem,
        )
        print(f"\n凭证已保存到: {path}")
        print(f"凭证名称: {credential_name}")


async def load_saved_identity(credential_name: str = "default") -> None:
    """加载已保存的身份并验证。"""
    data = load_identity(credential_name)
    if data is None:
        print(f"未找到名为 '{credential_name}' 的凭证")
        print("请先创建身份: uv run python scripts/setup_identity.py --name MyAgent")
        sys.exit(1)

    print(f"已加载凭证: {credential_name}")
    print(f"  DID       : {data['did']}")
    print(f"  unique_id : {data['unique_id']}")
    print(f"  user_id   : {data.get('user_id', 'N/A')}")
    print(f"  创建时间  : {data.get('created_at', 'N/A')}")

    # 验证 JWT 是否仍然有效
    if not data.get("jwt_token"):
        print("\n  未保存 JWT token")
        return

    config = SDKConfig()

    # 尝试使用 DIDWbaAuthHeader 自动处理认证
    auth_result = create_authenticator(credential_name, config)
    if auth_result is not None:
        auth, _ = auth_result
        async with create_user_service_client(config) as client:
            try:
                me = await authenticated_rpc_call(
                    client, "/user-service/did-auth/rpc", "get_me",
                    auth=auth, credential_name=credential_name,
                )
                print(f"\n  JWT 验证成功! 当前身份:")
                print(f"    DID: {me.get('did', 'N/A')}")
                print(f"    名称: {me.get('name', 'N/A')}")
            except Exception as e:
                print(f"\n  JWT 验证/刷新失败: {e}")
                print("  可能需要重新创建身份")
    else:
        # 旧凭证没有 did_document，回退到直接验证
        async with create_user_service_client(config) as client:
            client.headers["Authorization"] = f"Bearer {data['jwt_token']}"
            try:
                me = await rpc_call(client, "/user-service/did-auth/rpc", "get_me")
                print(f"\n  JWT 验证成功! 当前身份:")
                print(f"    DID: {me.get('did', 'N/A')}")
                print(f"    名称: {me.get('name', 'N/A')}")
            except Exception:
                print("\n  JWT 已过期，请重新创建身份以启用自动刷新:")
                print(f"    python scripts/setup_identity.py --name \"{data.get('name', 'MyAgent')}\" --credential {credential_name}")


def show_identities() -> None:
    """显示所有已保存的身份。"""
    identities = list_identities()
    if not identities:
        print("没有已保存的身份")
        print("创建身份: uv run python scripts/setup_identity.py --name MyAgent")
        return

    print(f"已保存的身份 ({len(identities)} 个):")
    print("-" * 70)
    for ident in identities:
        jwt_status = "有" if ident["has_jwt"] else "无"
        print(f"  [{ident['credential_name']}]")
        print(f"    DID      : {ident['did']}")
        print(f"    名称     : {ident.get('name', 'N/A')}")
        print(f"    user_id  : {ident.get('user_id', 'N/A')}")
        print(f"    JWT      : {jwt_status}")
        print(f"    创建时间 : {ident.get('created_at', 'N/A')}")
        print()


def remove_identity(credential_name: str) -> None:
    """删除已保存的身份。"""
    if delete_identity(credential_name):
        print(f"已删除凭证: {credential_name}")
    else:
        print(f"未找到名为 '{credential_name}' 的凭证")


def main() -> None:
    parser = argparse.ArgumentParser(description="DID 身份管理")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--name", type=str, help="创建新身份并指定显示名称")
    group.add_argument("--load", type=str, nargs="?", const="default",
                       help="加载已保存的身份（默认: default）")
    group.add_argument("--list", action="store_true", help="列出所有已保存的身份")
    group.add_argument("--delete", type=str, help="删除指定的已保存身份")

    parser.add_argument("--credential", type=str, default="default",
                        help="凭证存储名称（默认: default）")
    parser.add_argument("--agent", action="store_true",
                        help="标记为 AI Agent 身份")

    args = parser.parse_args()

    if args.list:
        show_identities()
    elif args.delete:
        remove_identity(args.delete)
    elif args.load is not None:
        asyncio.run(load_saved_identity(args.load))
    elif args.name:
        asyncio.run(create_new_identity(
            name=args.name,
            display_name=args.name,
            credential_name=args.credential,
            is_agent=args.agent,
        ))


if __name__ == "__main__":
    main()
