#!/usr/bin/env python3
"""
非交互式 .env 配置工具。供外部 agent 调用。

用法:
    python selfskill/scripts/configure.py <KEY> <VALUE>          # 设置单个配置项
    python selfskill/scripts/configure.py --show                 # 显示当前配置（隐藏敏感值）
    python selfskill/scripts/configure.py --show-raw             # 显示当前配置（含原始值）
    python selfskill/scripts/configure.py --init                 # 从 .env.example 初始化 .env（不覆盖已有）
    python selfskill/scripts/configure.py --batch K1=V1 K2=V2    # 批量设置

示例:
    python skill/scripts/configure.py LLM_API_KEY sk-xxxx
    python skill/scripts/configure.py LLM_BASE_URL https://api.deepseek.com
    python skill/scripts/configure.py LLM_MODEL deepseek-chat
    python skill/scripts/configure.py --batch LLM_API_KEY=sk-xxx LLM_BASE_URL=https://api.deepseek.com LLM_MODEL=deepseek-chat
"""
import os
import re
import sys
import shutil

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(PROJECT_ROOT, "config", ".env")
ENV_EXAMPLE = os.path.join(PROJECT_ROOT, "config", ".env.example")

SENSITIVE_KEYS = {"LLM_API_KEY", "INTERNAL_TOKEN", "TELEGRAM_BOT_TOKEN", "QQ_BOT_SECRET"}


def read_env():
    """读取 .env 为 (行列表, {key: value} 字典)"""
    if not os.path.exists(ENV_PATH):
        return [], {}
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    kvs = {}
    for line in lines:
        s = line.strip()
        if s and not s.startswith("#") and "=" in s:
            k, v = s.split("=", 1)
            kvs[k.strip()] = v.strip()
    return lines, kvs


def set_env(key, value):
    """设置单个 key=value，如果 key 已存在则更新，否则追加"""
    lines, _ = read_env()
    key_found = False
    new_lines = []
    for line in lines:
        s = line.strip()
        if s.startswith(f"{key}=") or s.startswith(f"# {key}="):
            new_lines.append(f"{key}={value}\n")
            key_found = True
        else:
            new_lines.append(line)
    if not key_found:
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines.append("\n")
        new_lines.append(f"{key}={value}\n")
    os.makedirs(os.path.dirname(ENV_PATH), exist_ok=True)
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"✅ {key} 已设置")


def show_env(raw=False):
    """显示当前配置"""
    _, kvs = read_env()
    if not kvs:
        print("⚠️  config/.env 不存在或为空")
        return
    for k, v in kvs.items():
        if not raw and k in SENSITIVE_KEYS and v:
            display = v[:4] + "****" + v[-4:] if len(v) > 8 else "****"
        else:
            display = v
        print(f"  {k}={display}")


def init_env():
    """从 .env.example 初始化 .env（不覆盖已有）"""
    if os.path.exists(ENV_PATH):
        print(f"✅ config/.env 已存在，跳过初始化")
        return
    if not os.path.exists(ENV_EXAMPLE):
        print(f"❌ config/.env.example 不存在", file=sys.stderr)
        sys.exit(1)
    os.makedirs(os.path.dirname(ENV_PATH), exist_ok=True)
    shutil.copy2(ENV_EXAMPLE, ENV_PATH)
    print(f"✅ 已从 .env.example 初始化 config/.env")


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "--show":
        show_env(raw=False)
    elif cmd == "--show-raw":
        show_env(raw=True)
    elif cmd == "--init":
        init_env()
    elif cmd == "--batch":
        if len(sys.argv) < 3:
            print("用法: configure.py --batch KEY1=VAL1 KEY2=VAL2 ...", file=sys.stderr)
            sys.exit(1)
        for arg in sys.argv[2:]:
            if "=" not in arg:
                print(f"⚠️  跳过无效参数: {arg}", file=sys.stderr)
                continue
            k, v = arg.split("=", 1)
            set_env(k.strip(), v.strip())
    else:
        # 单个 KEY VALUE
        if len(sys.argv) != 3:
            print("用法: configure.py <KEY> <VALUE>", file=sys.stderr)
            sys.exit(1)
        set_env(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
