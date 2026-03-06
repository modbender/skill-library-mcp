#!/usr/bin/env python3
"""
Git 同步模块

⚠️  安全说明
-----------
本模块使用 subprocess.run 调用系统 git 命令，会对本地仓库进行
git add / git commit / git push 操作。

安全措施：
  1. 所有 subprocess.run 调用均使用参数列表（list），禁止 shell=True，
     杜绝 shell 注入漏洞。
  2. commit message 经过 _sanitize_message() 净化，移除控制字符。
  3. 所有 git 功能默认关闭（settings.yaml → git.enabled: false），
     需用户显式开启。
  4. auto_push 单独设置，默认同样关闭，防止意外向远程推送。

启用方式：
  编辑 config/settings.yaml：
    git:
      enabled: true
      auto_push: true   # 如需自动推送到远程，再单独开启
"""

import re
import logging
import subprocess
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("heartbeat.git")


# ──────────────────────────────────────────────────────────────────────────────
# 内部工具
# ──────────────────────────────────────────────────────────────────────────────

def _load_config() -> dict:
    import yaml
    p = Path(__file__).parent.parent / "config" / "settings.yaml"
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _git_cfg() -> dict:
    return _load_config().get("git", {})


def _is_enabled() -> bool:
    """检查 git.enabled 开关（默认 false）"""
    return _git_cfg().get("enabled", False)


def _get_repo_root() -> Path:
    """返回当前 git 仓库根目录"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, cwd=Path(__file__).parent.parent,
            # shell=False 是默认值，此处显式注释说明安全意图
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except FileNotFoundError:
        pass
    return Path(__file__).parent.parent


def _sanitize_message(msg: str) -> str:
    """
    净化 commit message：
    - 移除控制字符（防止终端转义注入）
    - 截断到 200 字符
    - 若为空则使用默认值
    """
    # 移除所有控制字符（除换行、制表符）
    clean = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", msg)
    clean = clean.strip()[:200]
    return clean or f"[heartbeat] auto @ {datetime.now().strftime('%Y-%m-%d %H:%M')}"


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """
    执行 git 子命令。

    安全约束：
    - args 必须是 list（已在调用处保证）
    - 禁止使用 shell=True
    - 超时 30 秒，防止挂起
    """
    return subprocess.run(
        ["git"] + args,
        capture_output=True, text=True,
        cwd=cwd,
        timeout=30,
        # shell=False（Python 默认值，此处不传 shell= 参数）
    )


# ──────────────────────────────────────────────────────────────────────────────
# 公开接口
# ──────────────────────────────────────────────────────────────────────────────

def git_add_workspace() -> bool:
    """
    git add workspace/
    仅添加 workspace/ 目录，不影响其他文件。
    """
    if not _is_enabled():
        logger.debug("Git 功能已禁用（settings.yaml git.enabled=false）")
        return False

    repo = _get_repo_root()
    workspace = Path(__file__).parent.parent / "workspace"
    rel = workspace.relative_to(repo)

    result = _run_git(["add", str(rel)], cwd=repo)
    if result.returncode == 0:
        logger.info("git add workspace 成功")
        return True
    else:
        logger.error("git add 失败: %s", result.stderr.strip())
        return False


def git_commit(message: str = "") -> bool:
    """
    git commit，commit message 经过净化处理。
    若工作区无变更则跳过（不报错）。
    """
    if not _is_enabled():
        return False
    if not _git_cfg().get("auto_commit", True):
        return False

    repo = _get_repo_root()
    prefix = _sanitize_message(_git_cfg().get("commit_prefix", "[heartbeat]"))
    raw_msg = message or f"beat @ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    full_msg = _sanitize_message(f"{prefix} {raw_msg}")

    # 检查是否有变更（避免空 commit）
    status = _run_git(["status", "--porcelain"], cwd=repo)
    if not status.stdout.strip():
        logger.debug("git 工作区无变更，跳过 commit")
        return True  # 视为成功（无需操作）

    result = _run_git(["commit", "-m", full_msg], cwd=repo)
    if result.returncode == 0:
        logger.info("git commit 成功: %s", full_msg)
        return True
    else:
        logger.error("git commit 失败: %s", result.stderr.strip())
        return False


def git_push() -> bool:
    """
    git push 至远程仓库。

    ⚠️ 此操作会向远程仓库推送内容，需在 settings.yaml 中
       同时开启 git.enabled=true 和 git.auto_push=true。
    """
    if not _is_enabled():
        logger.debug("Git 功能已禁用，跳过 push")
        return False
    if not _git_cfg().get("auto_push", False):
        logger.debug("git.auto_push=false，跳过 push")
        return False

    repo = _get_repo_root()
    result = _run_git(["push"], cwd=repo)
    if result.returncode == 0:
        logger.info("git push 成功")
        return True
    else:
        logger.error("git push 失败: %s", result.stderr.strip())
        return False


def git_sync(message: str = "") -> dict:
    """
    一次性执行 add → commit → push（按配置决定是否执行每步）。
    返回各步骤结果字典。
    """
    if not _is_enabled():
        return {"enabled": False, "add": False, "commit": False, "push": False}

    added    = git_add_workspace()
    committed = git_commit(message)
    pushed   = git_push()
    return {"enabled": True, "add": added, "commit": committed, "push": pushed}
