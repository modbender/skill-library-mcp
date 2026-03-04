"""DID 身份创建（封装 ANP）。

[INPUT]: hostname, path_prefix, proof_purpose, domain, services
[OUTPUT]: DIDIdentity, create_identity(), load_private_key()
[POS]: 封装 ANP 的 create_did_wba_document_with_key_binding()，提供 key-bound DID 身份创建能力；
       enable_e2ee=True 时同时生成 key-2 (secp256r1 签名) 和 key-3 (X25519 协商) 密钥

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from anp.authentication import create_did_wba_document_with_key_binding


@dataclass
class DIDIdentity:
    """完整的 DID 身份信息。"""

    did: str
    did_document: dict[str, Any]  # 含 proof（由 ANP 生成）
    private_key_pem: bytes  # PEM 编码的 secp256k1 私钥
    public_key_pem: bytes  # PEM 编码的公钥
    user_id: str | None = field(default=None)  # 注册后填充
    jwt_token: str | None = field(default=None)  # WBA 认证后填充
    e2ee_signing_private_pem: bytes | None = field(default=None)   # key-2 secp256r1
    e2ee_signing_public_pem: bytes | None = field(default=None)
    e2ee_agreement_private_pem: bytes | None = field(default=None) # key-3 X25519
    e2ee_agreement_public_pem: bytes | None = field(default=None)

    @property
    def unique_id(self) -> str:
        """从 DID 中提取 unique_id（最后一个路径段）。

        例如 did:wba:localhost:user:abc123 → abc123
        """
        return self.did.rsplit(":", 1)[-1]

    def get_private_key(self) -> ec.EllipticCurvePrivateKey:
        """从 PEM 加载 secp256k1 私钥对象。"""
        return load_private_key(self.private_key_pem)


def create_identity(
    hostname: str,
    path_prefix: list[str] | None = None,
    proof_purpose: str = "authentication",
    domain: str | None = None,
    challenge: str | None = None,
    services: list[dict[str, Any]] | None = None,
) -> DIDIdentity:
    """创建 key-bound DID 身份（secp256k1 密钥对 + DID 文档 + proof）。

    使用 ANP 的 create_did_wba_document_with_key_binding() 生成完整的 DID 文档。
    自动从公钥计算 fingerprint，构造 k1_{fingerprint} 作为 DID 路径末段。

    Args:
        hostname: DID 所属域名
        path_prefix: DID 路径前缀，如 ["user"]（默认）或 ["agent"]。
            最终 DID 为 did:wba:<hostname>:<prefix>:k1_<fingerprint>
        proof_purpose: proof 用途（默认 "authentication"，用于注册）
        domain: proof 绑定的服务域名（服务端会验证）
        challenge: proof nonce（默认自动生成，用于防重放）
        services: 自定义 service 条目列表。每项为包含 "id", "type",
            "serviceEndpoint" 的 dict。如果 "id" 以 "#" 开头，
            会自动加上 DID 前缀。所有 service 在 proof 签名前写入文档。

    Returns:
        DIDIdentity（did_document 含 ANP 生成的 proof）
    """
    if challenge is None:
        challenge = secrets.token_hex(16)

    did_document, keys = create_did_wba_document_with_key_binding(
        hostname=hostname,
        path_prefix=path_prefix,
        proof_purpose=proof_purpose,
        domain=domain,
        challenge=challenge,
        services=services,
    )

    private_key_pem, public_key_pem = keys["key-1"]

    # E2EE 密钥（enable_e2ee=True 时 ANP 默认生成）
    e2ee_signing_private_pem: bytes | None = None
    e2ee_signing_public_pem: bytes | None = None
    e2ee_agreement_private_pem: bytes | None = None
    e2ee_agreement_public_pem: bytes | None = None
    if "key-2" in keys:
        e2ee_signing_private_pem, e2ee_signing_public_pem = keys["key-2"]
    if "key-3" in keys:
        e2ee_agreement_private_pem, e2ee_agreement_public_pem = keys["key-3"]

    return DIDIdentity(
        did=did_document["id"],
        did_document=did_document,
        private_key_pem=private_key_pem,
        public_key_pem=public_key_pem,
        e2ee_signing_private_pem=e2ee_signing_private_pem,
        e2ee_signing_public_pem=e2ee_signing_public_pem,
        e2ee_agreement_private_pem=e2ee_agreement_private_pem,
        e2ee_agreement_public_pem=e2ee_agreement_public_pem,
    )


def load_private_key(pem_bytes: bytes) -> ec.EllipticCurvePrivateKey:
    """从 PEM 字节加载私钥。"""
    key = load_pem_private_key(pem_bytes, password=None)
    if not isinstance(key, ec.EllipticCurvePrivateKey):
        raise TypeError(f"Expected EllipticCurvePrivateKey, got {type(key).__name__}")
    return key


__all__ = ["DIDIdentity", "create_identity", "load_private_key"]
