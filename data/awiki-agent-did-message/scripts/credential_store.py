"""凭证持久化：保存/加载私钥、DID、JWT 到本地文件。

[INPUT]: DIDIdentity 对象, DIDWbaAuthHeader (ANP SDK)
[OUTPUT]: save_identity(), load_identity(), list_identities(), delete_identity(),
         extract_auth_files(), create_authenticator()
[POS]: 凭证管理核心模块，支持跨会话身份复用，提供 DIDWbaAuthHeader 工厂

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""

from __future__ import annotations

import json
import os
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# 凭证存储目录（相对于 SKILL_DIR）
_CREDENTIALS_DIR = Path(__file__).resolve().parent.parent / ".credentials"


def _ensure_credentials_dir() -> Path:
    """确保凭证目录存在并设置权限。"""
    _CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    # 目录权限设为 700（仅当前用户可访问）
    os.chmod(_CREDENTIALS_DIR, stat.S_IRWXU)
    return _CREDENTIALS_DIR


def _credential_path(name: str) -> Path:
    """获取凭证文件路径。"""
    return _ensure_credentials_dir() / f"{name}.json"


def save_identity(
    did: str,
    unique_id: str,
    user_id: str | None,
    private_key_pem: bytes,
    public_key_pem: bytes,
    jwt_token: str | None = None,
    display_name: str | None = None,
    name: str = "default",
    did_document: dict[str, Any] | None = None,
    e2ee_signing_private_pem: bytes | None = None,
    e2ee_agreement_private_pem: bytes | None = None,
) -> Path:
    """保存 DID 身份到本地文件。

    Args:
        did: DID 标识符
        unique_id: 从 DID 提取的唯一 ID
        user_id: 注册后的用户 ID
        private_key_pem: PEM 编码的私钥
        public_key_pem: PEM 编码的公钥
        jwt_token: JWT token
        display_name: 显示名称
        name: 凭证名称（默认 "default"）
        did_document: DID 文档（供 DIDWbaAuthHeader 使用）
        e2ee_signing_private_pem: key-2 secp256r1 签名私钥 PEM
        e2ee_agreement_private_pem: key-3 X25519 协商私钥 PEM

    Returns:
        凭证文件路径
    """
    credential_data: dict[str, Any] = {
        "did": did,
        "unique_id": unique_id,
        "user_id": user_id,
        "private_key_pem": private_key_pem.decode("utf-8")
            if isinstance(private_key_pem, bytes) else private_key_pem,
        "public_key_pem": public_key_pem.decode("utf-8")
            if isinstance(public_key_pem, bytes) else public_key_pem,
        "jwt_token": jwt_token,
        "name": display_name,
        "did_document": did_document,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    if e2ee_signing_private_pem is not None:
        credential_data["e2ee_signing_private_pem"] = (
            e2ee_signing_private_pem.decode("utf-8")
            if isinstance(e2ee_signing_private_pem, bytes)
            else e2ee_signing_private_pem
        )
    if e2ee_agreement_private_pem is not None:
        credential_data["e2ee_agreement_private_pem"] = (
            e2ee_agreement_private_pem.decode("utf-8")
            if isinstance(e2ee_agreement_private_pem, bytes)
            else e2ee_agreement_private_pem
        )

    path = _credential_path(name)
    path.write_text(json.dumps(credential_data, indent=2, ensure_ascii=False))
    # 私钥文件权限设为 600（仅当前用户可读写）
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    return path


def load_identity(name: str = "default") -> dict[str, Any] | None:
    """从本地文件加载 DID 身份。

    Args:
        name: 凭证名称（默认 "default"）

    Returns:
        凭证数据字典，不存在时返回 None
    """
    path = _credential_path(name)
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return data


def list_identities() -> list[dict[str, Any]]:
    """列出所有已保存的身份。

    Returns:
        身份列表，每项含 name、did、created_at 等信息
    """
    cred_dir = _ensure_credentials_dir()
    identities = []
    for path in sorted(cred_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text())
            identities.append({
                "credential_name": path.stem,
                "did": data.get("did", ""),
                "unique_id": data.get("unique_id", ""),
                "name": data.get("name", ""),
                "user_id": data.get("user_id", ""),
                "created_at": data.get("created_at", ""),
                "has_jwt": bool(data.get("jwt_token")),
            })
        except (json.JSONDecodeError, OSError):
            continue
    return identities


def delete_identity(name: str) -> bool:
    """删除已保存的身份。

    Args:
        name: 凭证名称

    Returns:
        是否成功删除
    """
    path = _credential_path(name)
    if path.exists():
        path.unlink()
        return True
    return False


def update_jwt(name: str, jwt_token: str) -> bool:
    """更新已保存身份的 JWT token。

    Args:
        name: 凭证名称
        jwt_token: 新的 JWT token

    Returns:
        是否成功更新
    """
    data = load_identity(name)
    if data is None:
        return False
    data["jwt_token"] = jwt_token
    path = _credential_path(name)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    return True


def extract_auth_files(name: str = "default") -> tuple[Path, Path] | None:
    """从凭证中提取 DID 文档和私钥文件供 DIDWbaAuthHeader 使用。

    Args:
        name: 凭证名称

    Returns:
        (did_doc_path, key_path) 元组，凭证不存在或缺少 DID 文档时返回 None
    """
    data = load_identity(name)
    if data is None or not data.get("did_document"):
        return None

    cred_dir = _ensure_credentials_dir()

    # 写入 DID 文档 JSON
    did_doc_path = cred_dir / f"{name}_did_document.json"
    did_doc_path.write_text(json.dumps(data["did_document"], indent=2, ensure_ascii=False))

    # 写入私钥 PEM
    key_path = cred_dir / f"{name}_private_key.pem"
    private_key_pem = data["private_key_pem"]
    if isinstance(private_key_pem, str):
        private_key_pem = private_key_pem.encode("utf-8")
    key_path.write_bytes(private_key_pem)
    os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)

    return (did_doc_path, key_path)


def create_authenticator(
    name: str = "default",
    config: Any = None,
) -> tuple[Any, dict[str, Any]] | None:
    """创建 DIDWbaAuthHeader 实例。

    Args:
        name: 凭证名称
        config: SDKConfig 实例（用于预填充 token 缓存）

    Returns:
        (authenticator, identity_data) 元组，不可用时返回 None
    """
    from anp.authentication import DIDWbaAuthHeader

    data = load_identity(name)
    if data is None:
        return None

    auth_files = extract_auth_files(name)
    if auth_files is None:
        return None

    did_doc_path, key_path = auth_files
    auth = DIDWbaAuthHeader(str(did_doc_path), str(key_path))

    # 若有已保存的 JWT，预填充到 token 缓存（避免首次请求重新 DIDWba 认证）
    if data.get("jwt_token") and config is not None:
        server_url = config.user_service_url
        auth.update_token(server_url, {"Authorization": f"Bearer {data['jwt_token']}"})
        # molt-message 也预填充
        if hasattr(config, "molt_message_url"):
            auth.update_token(
                config.molt_message_url,
                {"Authorization": f"Bearer {data['jwt_token']}"},
            )

    return (auth, data)
