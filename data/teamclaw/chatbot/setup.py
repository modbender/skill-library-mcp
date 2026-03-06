#!/usr/bin/env python3
"""
Chatbot 设置与启动器
- 交互式配置 .env 中的 Telegram Bot / QQ Bot 信息
- 启动聊天机器人进程
"""

import os
import subprocess
import sys

# chatbot 目录
CHATBOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 项目根目录
PROJECT_ROOT = os.path.dirname(CHATBOT_DIR)

# 配置文件路径（统一使用 config/.env）
ENV_FILE = os.path.join(PROJECT_ROOT, "config", ".env")

# 项目 uv 环境
if sys.platform == "win32":
    VENV_PYTHON = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
else:
    VENV_PYTHON = os.path.join(PROJECT_ROOT, ".venv", "bin", "python")

# 需要管理的 .env 配置项
ENV_KEYS_TG = {
    "TELEGRAM_BOT_TOKEN": ("Telegram Bot Token（从 @BotFather 获取）", ""),
    "AI_MODEL_TG": ("Telegram Bot 使用的 AI 模型", "gemini-2.0-flash"),
}

ENV_KEYS_QQ = {
    "QQ_APP_ID": ("QQ Bot AppID（QQ 开放平台获取）", ""),
    "QQ_BOT_SECRET": ("QQ Bot Secret", ""),
    "QQ_BOT_USERNAME": ("QQ Bot 以哪个系统用户身份调用 Agent", "qquser"),
    "AI_MODEL_QQ": ("QQ Bot 使用的 AI 模型", "gemini-3-flash-preview"),
}

ENV_KEYS_COMMON = {
    "AI_API_URL": ("Agent OpenAI 兼容接口地址", "http://127.0.0.1:51200/v1/chat/completions"),
}


def _read_env() -> dict[str, str]:
    """读取 .env 文件为 dict，保留注释行的顺序信息。"""
    env = {}
    if not os.path.exists(ENV_FILE):
        return env
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, val = line.partition("=")
                env[key.strip()] = val.strip()
    return env


def _read_env_lines() -> list[str]:
    """读取 .env 文件的所有原始行。"""
    if not os.path.exists(ENV_FILE):
        return []
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        return f.readlines()


def _write_env_key(key: str, value: str):
    """更新 .env 中的某个 key，若不存在则追加。"""
    lines = _read_env_lines()
    found = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            k, _, _ = stripped.partition("=")
            if k.strip() == key:
                new_lines.append(f"{key}={value}\n")
                found = True
                continue
        new_lines.append(line)
    if not found:
        new_lines.append(f"{key}={value}\n")
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def _mask_value(val: str, show_chars: int = 6) -> str:
    """遮掩敏感值，只显示前几个字符。"""
    if not val or len(val) <= show_chars:
        return val or "(空)"
    return val[:show_chars] + "****"


def configure_env_group(title: str, keys: dict[str, tuple[str, str]]):
    """交互式配置一组 .env 变量。"""
    env = _read_env()
    print(f"\n{'=' * 40}")
    print(f"  {title}")
    print(f"{'=' * 40}")

    for key, (desc, default) in keys.items():
        current = env.get(key, "")
        # 判断是否是有效值（非 placeholder）
        is_placeholder = current.startswith("your_") or not current
        display = _mask_value(current) if current and not is_placeholder else "(未设置)"

        print(f"\n  {desc}")
        print(f"  环境变量: {key}")
        print(f"  当前值:   {display}")

        if default:
            prompt = f"  输入新值（回车保留当前, 'd' 使用默认 {default}）: "
        else:
            prompt = "  输入新值（回车保留当前）: "

        new_val = input(prompt).strip()

        if new_val == "d" and default:
            new_val = default
        elif not new_val:
            if is_placeholder and not current:
                print(f"  ⚠️ 跳过（仍未设置）")
            else:
                print(f"  ↩ 保留当前值")
            continue

        _write_env_key(key, new_val)
        print(f"  ✅ 已更新 {key}")


def show_current_config():
    """显示当前 chatbot 相关配置。"""
    env = _read_env()
    print(f"\n{'=' * 40}")
    print("  当前 Chatbot 配置概览")
    print(f"{'=' * 40}")

    sections = [
        ("Telegram Bot", ENV_KEYS_TG),
        ("QQ Bot", ENV_KEYS_QQ),
        ("通用配置", ENV_KEYS_COMMON),
    ]

    for section_name, keys in sections:
        print(f"\n  [{section_name}]")
        for key, (desc, _) in keys.items():
            val = env.get(key, "")
            is_sensitive = "token" in key.lower() or "secret" in key.lower() or "key" in key.lower()
            if is_sensitive:
                display = _mask_value(val)
            else:
                display = val or "(未设置)"
            print(f"    {key} = {display}")

    # 白名单
    whitelist_file = os.path.join(PROJECT_ROOT, "data", "telegram_whitelist.json")
    if os.path.exists(whitelist_file):
        import json
        with open(whitelist_file, "r", encoding="utf-8") as f:
            wl = json.load(f)
        count = len(wl.get("allowed", []))
        print(f"\n  [Telegram 白名单]")
        print(f"    允许用户数: {count}")
        for entry in wl.get("allowed", []):
            print(f"    - {entry.get('username', '?')} → chat_id: {entry.get('chat_id', '?')}")
    else:
        print(f"\n  [Telegram 白名单]")
        print(f"    白名单文件不存在（将在 Agent 设置 chat_id 时自动创建）")


def launch_bots():
    """启动聊天机器人。"""
    # 检查 venv
    if not os.path.exists(VENV_PYTHON):
        print(f"[错误] 未找到虚拟环境: {VENV_PYTHON}")
        return

    print("\n" + "-" * 30)
    print("你想启动哪个机器人？")
    print("1. QQ 机器人 (QQbot.py)")
    print("2. Telegram 机器人 (telegrambot.py)")
    print("3. 全部启动")
    print("4. 跳过")

    choice = input("\n请选择 (1/2/3/4): ").strip()

    # 日志目录
    log_dir = os.path.join(CHATBOT_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)

    if choice == "1":
        print("\n🚀 正在启动 QQ 机器人...")
        log_file = open(os.path.join(log_dir, "qqbot.log"), "a", encoding="utf-8")
        subprocess.Popen(
            [VENV_PYTHON, os.path.join(CHATBOT_DIR, "QQbot.py")],
            stdout=log_file, stderr=log_file,
        )
        print("日志: chatbot/logs/qqbot.log")
    elif choice == "2":
        print("\n🚀 正在启动 Telegram 机器人...")
        log_file = open(os.path.join(log_dir, "telegrambot.log"), "a", encoding="utf-8")
        subprocess.Popen(
            [VENV_PYTHON, os.path.join(CHATBOT_DIR, "telegrambot.py")],
            stdout=log_file, stderr=log_file,
        )
        print("日志: chatbot/logs/telegrambot.log")
    elif choice == "3":
        print("\n🚀 正在启动所有机器人...")
        qq_log = open(os.path.join(log_dir, "qqbot.log"), "a", encoding="utf-8")
        tg_log = open(os.path.join(log_dir, "telegrambot.log"), "a", encoding="utf-8")
        subprocess.Popen(
            [VENV_PYTHON, os.path.join(CHATBOT_DIR, "QQbot.py")],
            stdout=qq_log, stderr=qq_log,
        )
        subprocess.Popen(
            [VENV_PYTHON, os.path.join(CHATBOT_DIR, "telegrambot.py")],
            stdout=tg_log, stderr=tg_log,
        )
        print("日志: chatbot/logs/qqbot.log, chatbot/logs/telegrambot.log")
    else:
        print("\n跳过启动。")
    print("-" * 30)


def main():
    print("=== Chatbot 设置与启动器 ===")

    # 检查 .env 文件
    if not os.path.exists(ENV_FILE):
        print(f"[错误] .env 配置文件不存在: {ENV_FILE}")
        print("请先从 config/.env.example 复制一份 config/.env")
        return

    while True:
        print("\n" + "=" * 40)
        print("  主菜单")
        print("=" * 40)
        print("  1. 配置 Telegram Bot")
        print("  2. 配置 QQ Bot")
        print("  3. 配置通用设置")
        print("  4. 查看当前配置")
        print("  5. 启动机器人")
        print("  0. 退出")

        choice = input("\n请选择 (0-5): ").strip()

        if choice == "1":
            configure_env_group("Telegram Bot 配置", ENV_KEYS_TG)
        elif choice == "2":
            configure_env_group("QQ Bot 配置", ENV_KEYS_QQ)
        elif choice == "3":
            configure_env_group("通用配置", ENV_KEYS_COMMON)
        elif choice == "4":
            show_current_config()
        elif choice == "5":
            launch_bots()
        elif choice == "0":
            print("\n再见！")
            break
        else:
            print("无效选择，请重新输入。")


if __name__ == "__main__":
    main()
