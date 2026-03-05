"""E2EE 端到端加密客户端（封装 ANP e2e_encryption_hpke）。

[INPUT]: ANP E2eeHpkeSession / HpkeKeyManager / detect_message_type, local_did,
         signing_pem (secp256r1 key-2), x25519_pem (key-3)
[OUTPUT]: E2eeClient 类，提供一步初始化、加密、解密、状态导出/恢复的高层 API
[POS]: 封装 ANP 底层 HPKE E2EE 协议（RFC 9180 + 链式 Ratchet），为上层应用提供简洁的加解密接口；
       支持跨进程状态持久化

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""

from __future__ import annotations

import base64
import logging
import time
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    load_pem_private_key,
)

from anp.e2e_encryption_hpke import (
    E2eeHpkeSession,
    SessionState,
    HpkeKeyManager,
    MessageType,
    detect_message_type,
    extract_x25519_public_key_from_did_document,
    extract_signing_public_key_from_did_document,
)
from anp.authentication import resolve_did_wba_document

logger = logging.getLogger(__name__)

# 状态版本标记，用于区分旧格式
_STATE_VERSION = "hpke_v1"


class E2eeClient:
    """E2EE 端到端加密客户端（HPKE 方案）。

    封装 ANP ``E2eeHpkeSession`` 和 ``HpkeKeyManager``，提供：
    - 一步会话初始化（无多步握手）
    - 消息加密与解密（链式 Ratchet 前向安全）
    - 过期会话清理

    关键设计：E2EE 使用两套独立密钥——
    - key-2 secp256r1：proof 签名（证明身份）
    - key-3 X25519：HPKE 密钥协商
    均与 DID 身份密钥（secp256k1 key-1）分离。
    """

    def __init__(
        self,
        local_did: str,
        *,
        signing_pem: str | None = None,
        x25519_pem: str | None = None,
    ) -> None:
        """初始化 E2EE 客户端。

        Args:
            local_did: 本地 DID 标识符。
            signing_pem: secp256r1 签名密钥 PEM 字符串（key-2）。
            x25519_pem: X25519 协商密钥 PEM 字符串（key-3）。
        """
        self.local_did = local_did
        self._signing_pem = signing_pem
        self._x25519_pem = x25519_pem

        # 加载密钥对象
        self._signing_key: ec.EllipticCurvePrivateKey | None = None
        if signing_pem is not None:
            key = load_pem_private_key(signing_pem.encode("utf-8"), password=None)
            if isinstance(key, ec.EllipticCurvePrivateKey):
                self._signing_key = key

        self._x25519_key: X25519PrivateKey | None = None
        if x25519_pem is not None:
            key = load_pem_private_key(x25519_pem.encode("utf-8"), password=None)
            if isinstance(key, X25519PrivateKey):
                self._x25519_key = key

        self._key_manager = HpkeKeyManager()

    async def initiate_handshake(
        self, peer_did: str
    ) -> tuple[str, dict[str, Any]]:
        """发起 E2EE 会话（一步初始化）。

        获取对端 DID 文档中的 X25519 公钥，然后创建会话并发送 e2ee_init。
        发送后会话立即 ACTIVE，无需等待对方响应。

        Args:
            peer_did: 对端 DID 标识符。

        Returns:
            ``(msg_type, content_dict)`` 元组，msg_type 为 ``"e2ee_init"``。

        Raises:
            RuntimeError: 缺少必要的密钥或无法获取对端 DID 文档。
        """
        if self._signing_key is None or self._x25519_key is None:
            raise RuntimeError("缺少 E2EE 密钥（signing_pem 或 x25519_pem），请重新创建身份")

        # 获取对端 DID 文档
        peer_doc = await resolve_did_wba_document(peer_did)
        if peer_doc is None:
            raise RuntimeError(f"无法获取对端 DID 文档: {peer_did}")

        # 提取对端 X25519 公钥
        peer_pk, peer_key_id = extract_x25519_public_key_from_did_document(peer_doc)

        # 确定本地签名验证方法 ID
        signing_vm = f"{self.local_did}#key-2"

        # 确定本地 X25519 key ID
        local_x25519_key_id = f"{self.local_did}#key-3"

        session = E2eeHpkeSession(
            local_did=self.local_did,
            peer_did=peer_did,
            local_x25519_private_key=self._x25519_key,
            local_x25519_key_id=local_x25519_key_id,
            signing_private_key=self._signing_key,
            signing_verification_method=signing_vm,
        )

        msg_type, content = session.initiate_session(peer_pk, peer_key_id)

        # 一步初始化：发送后立即 ACTIVE
        self._key_manager.register_session(session)

        return msg_type, content

    async def process_e2ee_message(
        self, msg_type: str, content: dict[str, Any]
    ) -> list[tuple[str, dict[str, Any]]]:
        """处理收到的 E2EE 协议消息。

        Args:
            msg_type: 消息类型（``e2ee_init`` / ``e2ee_rekey`` / ``e2ee_error``）。
            content: 消息内容 dict。

        Returns:
            需要发送的消息列表（HPKE 方案中通常为空列表，
            因为 init/rekey 无需回复）。
        """
        detected = detect_message_type(msg_type)
        if detected is None:
            logger.warning("无法识别的 E2EE 消息类型: %s", msg_type)
            return []

        if detected == MessageType.E2EE_INIT:
            return await self._handle_init(content)
        elif detected == MessageType.E2EE_REKEY:
            return await self._handle_rekey(content)
        elif detected == MessageType.E2EE_ERROR:
            return self._handle_error(content)
        elif detected == MessageType.E2EE_MSG:
            logger.warning("process_e2ee_message 不处理加密消息，请使用 decrypt_message")
            return []
        else:
            logger.warning("未处理的 E2EE 消息子类型: %s", detected)
            return []

    def has_active_session(self, peer_did: str) -> bool:
        """检查是否存在与指定对端的活跃加密会话。"""
        session = self._key_manager.get_active_session(self.local_did, peer_did)
        return session is not None

    def encrypt_message(
        self, peer_did: str, plaintext: str, original_type: str = "text"
    ) -> tuple[str, dict[str, Any]]:
        """加密消息。

        Args:
            peer_did: 对端 DID 标识符。
            plaintext: 明文内容。
            original_type: 原始消息类型（默认 ``"text"``）。

        Returns:
            ``(msg_type, content_dict)`` 元组，msg_type 为 ``"e2ee_msg"``。

        Raises:
            RuntimeError: 没有与对端的活跃会话。
        """
        session = self._key_manager.get_active_session(self.local_did, peer_did)
        if session is None:
            raise RuntimeError(f"没有与 {peer_did} 的活跃 E2EE 会话")
        return session.encrypt_message(original_type, plaintext)

    def decrypt_message(self, content: dict[str, Any]) -> tuple[str, str]:
        """解密消息。

        根据 ``session_id`` 查找对应的会话并解密。

        Args:
            content: 加密消息的 content dict（含 ``session_id``、``ciphertext`` 等）。

        Returns:
            ``(original_type, plaintext)`` 元组。

        Raises:
            RuntimeError: 找不到对应的会话。
        """
        session_id = content.get("session_id")
        if not session_id:
            raise RuntimeError("消息缺少 session_id")

        session = self._key_manager.get_session_by_id(session_id)
        if session is None:
            raise RuntimeError(f"找不到 session_id={session_id} 对应的会话")
        return session.decrypt_message(content)

    def cleanup_expired(self) -> None:
        """清理过期会话。"""
        self._key_manager.cleanup_expired()

    # ------------------------------------------------------------------
    # 状态导出 / 恢复
    # ------------------------------------------------------------------

    def export_state(self) -> dict[str, Any]:
        """导出客户端状态（密钥 + ACTIVE 会话）。

        Returns:
            可 JSON 序列化的 dict，用于持久化。
        """
        sessions: list[dict[str, Any]] = []
        for session in self._key_manager._sessions_by_did_pair.values():
            if session.state == SessionState.ACTIVE and not session.is_expired():
                exported = self._export_session(session)
                if exported is not None:
                    sessions.append(exported)
        return {
            "version": _STATE_VERSION,
            "local_did": self.local_did,
            "signing_pem": self._signing_pem,
            "x25519_pem": self._x25519_pem,
            "sessions": sessions,
        }

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> E2eeClient:
        """从导出的 dict 恢复完整客户端。

        Args:
            state: 由 ``export_state()`` 生成的 dict。

        Returns:
            恢复后的 ``E2eeClient`` 实例。
        """
        # 检测旧版格式：无 version 标记或版本不匹配
        if state.get("version") != _STATE_VERSION:
            logger.info("检测到旧版 E2EE 状态格式，创建新客户端")
            return cls(
                state["local_did"],
                signing_pem=state.get("signing_pem"),
                x25519_pem=state.get("x25519_pem"),
            )

        client = cls(
            state["local_did"],
            signing_pem=state.get("signing_pem"),
            x25519_pem=state.get("x25519_pem"),
        )
        for session_data in state.get("sessions", []):
            session = cls._restore_session(session_data)
            if session is not None:
                client._key_manager.register_session(session)
        return client

    @staticmethod
    def _export_session(session: E2eeHpkeSession) -> dict[str, Any] | None:
        """序列化单个 ACTIVE 会话。"""
        if session.state != SessionState.ACTIVE:
            return None
        send_chain_key = session._send_chain_key
        recv_chain_key = session._recv_chain_key
        if send_chain_key is None or recv_chain_key is None:
            return None
        return {
            "session_id": session.session_id,
            "local_did": session.local_did,
            "peer_did": session.peer_did,
            "is_initiator": session._is_initiator,
            "send_chain_key": base64.b64encode(send_chain_key).decode("ascii"),
            "recv_chain_key": base64.b64encode(recv_chain_key).decode("ascii"),
            "send_seq": session._seq_manager._send_seq,
            "recv_seq": session._seq_manager._recv_seq,
            "expires_at": session._expires_at,
            "created_at": session._created_at,
            "active_at": session._active_at,
        }

    @staticmethod
    def _restore_session(data: dict[str, Any]) -> E2eeHpkeSession | None:
        """从 dict 恢复单个 ACTIVE 会话。

        使用 ``object.__new__()`` 绕过 ``__init__``，直接设置内部属性。
        """
        expires_at = data.get("expires_at")
        if expires_at is not None and time.time() > expires_at:
            return None

        session = object.__new__(E2eeHpkeSession)
        session.local_did = data["local_did"]
        session.peer_did = data["peer_did"]
        session._session_id = data["session_id"]
        session._state = SessionState.ACTIVE
        session._is_initiator = data.get("is_initiator", True)
        session._send_chain_key = base64.b64decode(data["send_chain_key"])
        session._recv_chain_key = base64.b64decode(data["recv_chain_key"])
        session._expires_at = expires_at
        session._created_at = data.get("created_at", time.time())
        session._active_at = data.get("active_at")

        # 恢复 SeqManager
        from anp.e2e_encryption_hpke.session import SeqManager, SeqMode
        seq_mgr = object.__new__(SeqManager)
        seq_mgr._mode = SeqMode.STRICT
        seq_mgr._send_seq = data.get("send_seq", 0)
        seq_mgr._recv_seq = data.get("recv_seq", 0)
        seq_mgr._max_skip = 256
        seq_mgr._used_seqs = {}
        seq_mgr._skip_key_ttl = 300
        session._seq_manager = seq_mgr

        # ACTIVE 状态不再需要的属性，设置为 None 防止 AttributeError
        session._local_x25519_private_key = None
        session._local_x25519_key_id = ""
        session._signing_private_key = None
        session._signing_verification_method = ""
        session._default_expires = data.get("expires_at", 86400)

        return session

    # ------------------------------------------------------------------
    # 内部处理方法
    # ------------------------------------------------------------------

    async def _handle_init(
        self, content: dict[str, Any]
    ) -> list[tuple[str, dict[str, Any]]]:
        """处理 e2ee_init：获取发送方 DID 文档验证 proof，创建并激活会话。"""
        if self._signing_key is None or self._x25519_key is None:
            logger.error("缺少 E2EE 密钥，无法处理 e2ee_init")
            return []

        sender_did = content.get("sender_did", "")
        if not sender_did:
            logger.warning("e2ee_init 消息缺少 sender_did")
            return []

        # 获取发送方 DID 文档
        sender_doc = await resolve_did_wba_document(sender_did)
        if sender_doc is None:
            logger.warning("无法获取发送方 DID 文档: %s", sender_did)
            return []

        # 提取发送方签名公钥（用于验证 proof）
        proof = content.get("proof", {})
        vm_id = proof.get("verificationMethod", "")
        try:
            sender_signing_pk = extract_signing_public_key_from_did_document(
                sender_doc, vm_id
            )
        except ValueError as e:
            logger.warning("无法提取发送方签名公钥: %s", e)
            return []

        # 确定本地密钥 ID
        signing_vm = f"{self.local_did}#key-2"
        local_x25519_key_id = f"{self.local_did}#key-3"

        session = E2eeHpkeSession(
            local_did=self.local_did,
            peer_did=sender_did,
            local_x25519_private_key=self._x25519_key,
            local_x25519_key_id=local_x25519_key_id,
            signing_private_key=self._signing_key,
            signing_verification_method=signing_vm,
        )

        try:
            session.process_init(content, sender_signing_pk)
        except (ValueError, RuntimeError) as e:
            logger.warning("处理 e2ee_init 失败: %s", e)
            return []

        # 注册会话（立即 ACTIVE）
        self._key_manager.register_session(session)
        logger.info(
            "E2EE 会话激活（接收方）: %s <-> %s (session_id=%s)",
            session.local_did, session.peer_did, session.session_id,
        )

        # HPKE 方案中 init 无需回复
        return []

    async def _handle_rekey(
        self, content: dict[str, Any]
    ) -> list[tuple[str, dict[str, Any]]]:
        """处理 e2ee_rekey：重建会话。"""
        if self._signing_key is None or self._x25519_key is None:
            logger.error("缺少 E2EE 密钥，无法处理 e2ee_rekey")
            return []

        sender_did = content.get("sender_did", "")
        if not sender_did:
            logger.warning("e2ee_rekey 消息缺少 sender_did")
            return []

        # 获取发送方 DID 文档
        sender_doc = await resolve_did_wba_document(sender_did)
        if sender_doc is None:
            logger.warning("无法获取发送方 DID 文档: %s", sender_did)
            return []

        # 提取发送方签名公钥
        proof = content.get("proof", {})
        vm_id = proof.get("verificationMethod", "")
        try:
            sender_signing_pk = extract_signing_public_key_from_did_document(
                sender_doc, vm_id
            )
        except ValueError as e:
            logger.warning("无法提取发送方签名公钥: %s", e)
            return []

        signing_vm = f"{self.local_did}#key-2"
        local_x25519_key_id = f"{self.local_did}#key-3"

        # 尝试获取已有会话进行 rekey
        session = self._key_manager.get_active_session(self.local_did, sender_did)
        if session is not None:
            try:
                session.process_rekey(content, sender_signing_pk)
                self._key_manager.register_session(session)
                logger.info(
                    "E2EE 会话 rekey 成功: %s <-> %s", self.local_did, sender_did
                )
                return []
            except (ValueError, RuntimeError) as e:
                logger.warning("rekey 现有会话失败，尝试创建新会话: %s", e)

        # 没有已有会话或 rekey 失败，创建新会话
        session = E2eeHpkeSession(
            local_did=self.local_did,
            peer_did=sender_did,
            local_x25519_private_key=self._x25519_key,
            local_x25519_key_id=local_x25519_key_id,
            signing_private_key=self._signing_key,
            signing_verification_method=signing_vm,
        )
        try:
            session.process_rekey(content, sender_signing_pk)
        except (ValueError, RuntimeError) as e:
            logger.warning("处理 e2ee_rekey 失败: %s", e)
            return []

        self._key_manager.register_session(session)
        logger.info(
            "E2EE 会话 rekey（新建）: %s <-> %s", self.local_did, sender_did
        )
        return []

    def _handle_error(
        self, content: dict[str, Any]
    ) -> list[tuple[str, dict[str, Any]]]:
        """处理 E2EE Error：记录日志，移除对应会话。"""
        error_code = content.get("error_code", "unknown")
        session_id = content.get("session_id", "")
        logger.warning(
            "收到 E2EE 错误: code=%s, session_id=%s", error_code, session_id
        )
        if session_id:
            session = self._key_manager.get_session_by_id(session_id)
            if session is not None:
                self._key_manager.remove_session(session.local_did, session.peer_did)
        return []


__all__ = ["E2eeClient"]
