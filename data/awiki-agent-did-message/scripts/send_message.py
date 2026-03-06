"""发送消息给指定 DID。

用法：
    # 发送文本消息
    uv run python scripts/send_message.py --to "did:wba:localhost:user:abc123" --content "你好！"

    # 指定消息类型
    uv run python scripts/send_message.py --to "did:wba:localhost:user:abc123" --content "hello" --type text

[INPUT]: SDK（RPC 调用）、credential_store（加载身份凭证）
[OUTPUT]: 发送结果
[POS]: 消息发送脚本

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from utils import SDKConfig, create_molt_message_client, authenticated_rpc_call
from credential_store import create_authenticator


MESSAGE_RPC = "/message/rpc"


async def send_message(
    receiver_did: str,
    content: str,
    msg_type: str = "text",
    credential_name: str = "default",
) -> None:
    """发送消息给指定 DID。"""
    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"凭证 '{credential_name}' 不可用，请先创建身份")
        sys.exit(1)

    auth, data = auth_result
    async with create_molt_message_client(config) as client:
        result = await authenticated_rpc_call(
            client,
            MESSAGE_RPC,
            "send",
            params={
                "sender_did": data["did"],
                "receiver_did": receiver_did,
                "content": content,
                "type": msg_type,
            },
            auth=auth,
            credential_name=credential_name,
        )
        print("消息发送成功:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="发送 DID 消息")
    parser.add_argument("--to", required=True, type=str, help="接收方 DID")
    parser.add_argument("--content", required=True, type=str, help="消息内容")
    parser.add_argument("--type", type=str, default="text",
                        help="消息类型（默认: text）")
    parser.add_argument("--credential", type=str, default="default",
                        help="凭证名称（默认: default）")

    args = parser.parse_args()
    asyncio.run(send_message(args.to, args.content, args.type, args.credential))


if __name__ == "__main__":
    main()
