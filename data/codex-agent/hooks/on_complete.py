#!/usr/bin/env python3
"""
Codex notify hook — Codex 完成 turn 时：
1. 给用户发 Telegram 通知（看到 Codex 干了什么）
2. 唤醒 OpenClaw agent（去检查输出）

配置：通过环境变量或修改下方默认值
  CODEX_AGENT_CHAT_ID   — Chat ID (Telegram/Discord/WhatsApp etc.)
  CODEX_AGENT_NAME      — OpenClaw agent 名称（默认 main）
"""

import json
import os
import subprocess
import sys
from datetime import datetime

LOG_FILE = "/tmp/codex_notify_log.txt"

# 从环境变量读取，fallback 到默认值（方便部署时不改代码）
CHAT_ID = os.environ.get("CODEX_AGENT_CHAT_ID", "YOUR_CHAT_ID")
CHANNEL = os.environ.get("CODEX_AGENT_CHANNEL", "telegram")
AGENT_NAME = os.environ.get("CODEX_AGENT_NAME", "main")


def log(msg: str):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
    except Exception:
        pass  # 日志写入失败不应影响主流程


def notify_user(msg: str) -> bool:
    """发送 Telegram 通知，返回是否成功启动进程"""
    try:
        proc = subprocess.Popen(
            [
                "openclaw", "message", "send",
                "--channel", CHANNEL,
                "--target", CHAT_ID,
                "--message", msg,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # 等待最多 10 秒，检查是否成功
        try:
            _, stderr = proc.communicate(timeout=10)
            if proc.returncode != 0:
                log(f"channel notify failed (exit {proc.returncode}): {stderr.decode()[:200]}")
                return False
        except subprocess.TimeoutExpired:
            log("channel notify timeout (10s), process still running")
        log("channel notify sent")
        return True
    except Exception as e:
        log(f"channel notify error: {e}")
        return False


def wake_agent(msg: str) -> bool:
    """唤醒 OpenClaw agent，返回是否成功启动进程"""
    try:
        proc = subprocess.Popen(
            [
                "openclaw", "agent",
                "--agent", AGENT_NAME,
                "--message", msg,
                "--deliver",
                "--channel", CHANNEL,
                "--timeout", "120",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        log(f"agent wake fired (pid {proc.pid})")
        return True
    except Exception as e:
        log(f"agent wake error: {e}")
        return False


def main() -> int:
    if len(sys.argv) < 2:
        return 0

    try:
        notification = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        log(f"JSON parse error: {e}")
        return 1

    if notification.get("type") != "agent-turn-complete":
        return 0

    summary = notification.get("last-assistant-message", "Turn Complete!")
    cwd = notification.get("cwd", "unknown")
    thread_id = notification.get("thread-id", "unknown")

    log(f"Codex turn complete: thread={thread_id}, cwd={cwd}")
    log(f"Summary: {summary[:200]}")

    # ⚠️ 注意：summary 可能包含代码片段、路径、密钥等敏感信息
    # 发送到 Telegram 前用户应评估风险（私人仓库/私聊通常可接受）
    msg = (
        f"🔔 Codex 任务回复\n"
        f"📁 {cwd}\n"
        f"💬 {summary}"
    )

    # 1. 给用户发 Telegram 通知
    tg_ok = notify_user(msg)

    # 2. 唤醒 agent（fire-and-forget）
    agent_msg = (
        f"[Codex Hook] 任务完成，请检查输出并汇报。\n"
        f"cwd: {cwd}\n"
        f"thread: {thread_id}\n"
        f"summary: {summary}"
    )
    agent_ok = wake_agent(agent_msg)

    if not tg_ok and not agent_ok:
        log("⚠️ Both channel notify and agent wake failed!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
