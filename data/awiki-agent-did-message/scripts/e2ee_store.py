"""E2EE 状态持久化：保存/加载 E2eeClient 状态到本地文件。

[INPUT]: E2eeClient.export_state() 生成的 dict（HPKE 方案，含 version="hpke_v1"）
[OUTPUT]: save_e2ee_state(), load_e2ee_state(), delete_e2ee_state()
[POS]: E2EE 会话状态持久化模块，支持跨进程 HPKE E2EE 加密通信

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from typing import Any

# 凭证存储目录（与 credential_store 共用同一父目录）
_CREDENTIALS_DIR = Path(__file__).resolve().parent.parent / ".credentials"


def _ensure_credentials_dir() -> Path:
    """确保凭证目录存在并设置权限。"""
    _CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(_CREDENTIALS_DIR, stat.S_IRWXU)
    return _CREDENTIALS_DIR


def _e2ee_state_path(credential_name: str) -> Path:
    """获取 E2EE 状态文件路径。"""
    return _ensure_credentials_dir() / f"e2ee_{credential_name}.json"


def save_e2ee_state(state: dict[str, Any], credential_name: str = "default") -> Path:
    """保存 E2EE 客户端状态到本地文件。

    Args:
        state: 由 ``E2eeClient.export_state()`` 生成的 dict。
        credential_name: 凭证名称（默认 ``"default"``）。

    Returns:
        状态文件路径。
    """
    path = _e2ee_state_path(credential_name)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    return path


def load_e2ee_state(credential_name: str = "default") -> dict[str, Any] | None:
    """从本地文件加载 E2EE 客户端状态。

    Args:
        credential_name: 凭证名称（默认 ``"default"``）。

    Returns:
        状态 dict，不存在时返回 None。
    """
    path = _e2ee_state_path(credential_name)
    if not path.exists():
        return None
    return json.loads(path.read_text())


def delete_e2ee_state(credential_name: str = "default") -> bool:
    """删除已保存的 E2EE 状态文件。

    Args:
        credential_name: 凭证名称（默认 ``"default"``）。

    Returns:
        是否成功删除。
    """
    path = _e2ee_state_path(credential_name)
    if path.exists():
        path.unlink()
        return True
    return False
