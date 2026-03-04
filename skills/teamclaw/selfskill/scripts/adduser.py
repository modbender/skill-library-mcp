#!/usr/bin/env python3
"""
非交互式用户创建工具。供外部 agent 调用。

用法:
    python selfskill/scripts/adduser.py <username> <password>

如果用户已存在则更新密码，否则新增。
"""
import hashlib
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "users.json")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def main():
    if len(sys.argv) != 3:
        print("用法: python skill/scripts/adduser.py <username> <password>", file=sys.stderr)
        sys.exit(1)

    username, password = sys.argv[1], sys.argv[2]
    if not username or not password:
        print("用户名和密码不能为空", file=sys.stderr)
        sys.exit(1)

    users = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            users = json.load(f)

    action = "updated" if username in users else "created"
    users[username] = hash_password(password)

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

    print(f"✅ User '{username}' {action}")


if __name__ == "__main__":
    main()
