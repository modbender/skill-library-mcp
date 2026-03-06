"""E2EE 端到端加密消息收发（HPKE 方案，支持跨进程状态持久化）。

用法：
    # 发起 E2EE 会话（一步初始化，会话立即 ACTIVE）
    uv run python scripts/e2ee_messaging.py --handshake "did:wba:awiki.ai:user:abc123"

    # 发送加密消息（需要先完成初始化）
    uv run python scripts/e2ee_messaging.py --send "did:wba:awiki.ai:user:abc123" --content "secret message"

    # 处理收件箱中的 E2EE 消息（自动处理 init + 解密）
    uv run python scripts/e2ee_messaging.py --process --peer "did:wba:awiki.ai:user:abc123"

支持的工作流：
1. Alice: --handshake <Bob's DID>       → 发起会话（一步初始化，立即 ACTIVE）
2. Bob:   --process --peer <Alice's DID> → 处理收件箱（收到 e2ee_init，会话直接 ACTIVE）
3. Alice: --send <Bob's DID> --content "secret" → 发送加密消息
4. Bob:   --process --peer <Alice's DID> → 从磁盘恢复会话，解密消息

[INPUT]: SDK（E2eeClient、RPC 调用）、credential_store（加载身份凭证）、e2ee_store（E2EE 状态持久化）
[OUTPUT]: E2EE 操作结果
[POS]: 端到端加密消息脚本，集成状态持久化支持跨进程 E2EE 通信（HPKE 方案）

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from utils import SDKConfig, E2eeClient, create_molt_message_client, authenticated_rpc_call
from credential_store import create_authenticator, load_identity
from e2ee_store import save_e2ee_state, load_e2ee_state


MESSAGE_RPC = "/message/rpc"

# E2EE 相关消息类型
_E2EE_MSG_TYPES = {"e2ee_init", "e2ee_msg", "e2ee_rekey", "e2ee_error"}

# E2EE 消息类型的协议顺序
_E2EE_TYPE_ORDER = {"e2ee_init": 0, "e2ee_rekey": 1, "e2ee_msg": 2, "e2ee_error": 3}


def _load_or_create_e2ee_client(
    local_did: str, credential_name: str
) -> E2eeClient:
    """从磁盘加载已有 E2EE 客户端状态，不存在时创建新客户端。

    从凭证中加载 E2EE 密钥（signing_pem + x25519_pem）。
    """
    # 从凭证加载 E2EE 密钥
    cred = load_identity(credential_name)
    signing_pem: str | None = None
    x25519_pem: str | None = None
    if cred is not None:
        signing_pem = cred.get("e2ee_signing_private_pem")
        x25519_pem = cred.get("e2ee_agreement_private_pem")

    if signing_pem is None or x25519_pem is None:
        print("警告: 凭证缺少 E2EE 密钥（key-2/key-3），请重新创建身份以启用 HPKE E2EE")

    state = load_e2ee_state(credential_name)
    if state is not None and state.get("local_did") == local_did:
        # 用凭证中的密钥覆盖状态中的（确保使用最新密钥）
        if signing_pem is not None:
            state["signing_pem"] = signing_pem
        if x25519_pem is not None:
            state["x25519_pem"] = x25519_pem
        client = E2eeClient.from_state(state)
        return client

    return E2eeClient(local_did, signing_pem=signing_pem, x25519_pem=x25519_pem)


def _save_e2ee_client(client: E2eeClient, credential_name: str) -> None:
    """将 E2EE 客户端状态保存到磁盘。"""
    state = client.export_state()
    save_e2ee_state(state, credential_name)


async def _send_msg(client, sender_did, receiver_did, msg_type, content, *, auth, credential_name="default"):
    """发送消息（E2EE 或普通消息）。"""
    if isinstance(content, dict):
        content = json.dumps(content)
    return await authenticated_rpc_call(
        client, MESSAGE_RPC, "send",
        params={
            "sender_did": sender_did,
            "receiver_did": receiver_did,
            "content": content,
            "type": msg_type,
        },
        auth=auth,
        credential_name=credential_name,
    )


async def initiate_handshake(
    peer_did: str,
    credential_name: str = "default",
) -> None:
    """发起 E2EE 会话（一步初始化）。"""
    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"凭证 '{credential_name}' 不可用，请先创建身份")
        sys.exit(1)

    auth, data = auth_result
    e2ee_client = _load_or_create_e2ee_client(data["did"], credential_name)
    msg_type, content = await e2ee_client.initiate_handshake(peer_did)

    async with create_molt_message_client(config) as client:
        await _send_msg(client, data["did"], peer_did, msg_type, content,
                        auth=auth, credential_name=credential_name)

    _save_e2ee_client(e2ee_client, credential_name)

    print(f"E2EE 会话已建立（一步初始化）")
    print(f"  session_id: {content.get('session_id')}")
    print(f"  peer_did  : {peer_did}")
    print("会话已 ACTIVE，可以直接发送加密消息")


async def send_encrypted(
    peer_did: str,
    plaintext: str,
    credential_name: str = "default",
) -> None:
    """发送加密消息。"""
    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"凭证 '{credential_name}' 不可用，请先创建身份")
        sys.exit(1)

    auth, data = auth_result
    e2ee_client = _load_or_create_e2ee_client(data["did"], credential_name)

    if not e2ee_client.has_active_session(peer_did):
        print(f"没有与 {peer_did} 的活跃 E2EE 会话")
        print("请先发起 E2EE 会话: --handshake <DID>")
        sys.exit(1)

    enc_type, enc_content = e2ee_client.encrypt_message(peer_did, plaintext)

    async with create_molt_message_client(config) as client:
        await _send_msg(client, data["did"], peer_did, enc_type, enc_content,
                        auth=auth, credential_name=credential_name)

    # 保存状态（send_seq 已递增）
    _save_e2ee_client(e2ee_client, credential_name)

    print("加密消息已发送")
    print(f"  原文: {plaintext}")
    print(f"  接收方: {peer_did}")


async def process_inbox(
    peer_did: str,
    credential_name: str = "default",
) -> None:
    """处理收件箱中的 E2EE 消息。"""
    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"凭证 '{credential_name}' 不可用，请先创建身份")
        sys.exit(1)

    auth, data = auth_result
    async with create_molt_message_client(config) as client:
        # 获取收件箱
        inbox = await authenticated_rpc_call(
            client, MESSAGE_RPC, "get_inbox",
            params={"user_did": data["did"], "limit": 50},
            auth=auth, credential_name=credential_name,
        )
        messages = inbox.get("messages", [])
        if not messages:
            print("收件箱为空")
            return

        # 按时间和协议顺序排序
        messages.sort(key=lambda m: (
            m.get("created_at", ""),
            _E2EE_TYPE_ORDER.get(m.get("type"), 99),
        ))

        e2ee_client: E2eeClient | None = None

        # 尝试从磁盘恢复已有 E2EE 客户端
        e2ee_client = _load_or_create_e2ee_client(data["did"], credential_name)
        processed_ids = []

        for msg in messages:
            msg_type = msg["type"]
            sender_did = msg.get("sender_did", "?")

            if msg_type in _E2EE_MSG_TYPES:
                content = json.loads(msg["content"])

                if msg_type == "e2ee_msg":
                    try:
                        original_type, plaintext = e2ee_client.decrypt_message(content)
                        print(f"  [{msg_type}] 解密消息: [{original_type}] {plaintext}")
                    except RuntimeError as e:
                        print(f"  [{msg_type}] 解密失败: {e}")
                else:
                    responses = await e2ee_client.process_e2ee_message(msg_type, content)
                    print(f"  [{msg_type}] 处理协议消息，生成 {len(responses)} 条响应")
                    for resp_type, resp_content in responses:
                        await _send_msg(
                            client, data["did"], peer_did, resp_type, resp_content,
                            auth=auth, credential_name=credential_name,
                        )
                        print(f"    -> 发送 {resp_type}")
            else:
                print(f"  [{msg_type}] 来自 {sender_did[:40]}...: {msg['content']}")

            processed_ids.append(msg["id"])

        # 标记已读
        if processed_ids:
            await authenticated_rpc_call(
                client, MESSAGE_RPC, "mark_read",
                params={"user_did": data["did"], "message_ids": processed_ids},
                auth=auth, credential_name=credential_name,
            )
            print(f"\n已标记 {len(processed_ids)} 条消息为已读")

        if e2ee_client and e2ee_client.has_active_session(peer_did):
            print(f"\nE2EE 会话状态: ACTIVE (与 {peer_did})")

        # 保存 E2EE 客户端状态到磁盘
        if e2ee_client is not None:
            _save_e2ee_client(e2ee_client, credential_name)


def main() -> None:
    parser = argparse.ArgumentParser(description="E2EE 端到端加密消息（HPKE 方案）")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--handshake", type=str, help="向指定 DID 发起 E2EE 会话")
    group.add_argument("--send", type=str, help="向指定 DID 发送加密消息")
    group.add_argument("--process", action="store_true",
                       help="处理收件箱中的 E2EE 消息")

    parser.add_argument("--content", type=str, help="消息内容（--send 时必需）")
    parser.add_argument("--peer", type=str,
                        help="对端 DID（--process 时必需）")
    parser.add_argument("--credential", type=str, default="default",
                        help="凭证名称（默认: default）")

    args = parser.parse_args()

    if args.handshake:
        asyncio.run(initiate_handshake(args.handshake, args.credential))
    elif args.send:
        if not args.content:
            parser.error("发送加密消息需要 --content")
        asyncio.run(send_encrypted(args.send, args.content, args.credential))
    elif args.process:
        if not args.peer:
            parser.error("处理收件箱需要 --peer")
        asyncio.run(process_inbox(args.peer, args.credential))


if __name__ == "__main__":
    main()
