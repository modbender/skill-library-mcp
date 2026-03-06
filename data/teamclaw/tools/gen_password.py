#!/usr/bin/env python3
"""
用户密码哈希生成工具。
用法：python tools/gen_password.py
会交互式输入用户名和密码，输出追加到 config/users.json。
"""
import hashlib
import json
import os
import getpass

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "users.json")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def main():
    # 加载已有用户
    users = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            users = json.load(f)
        print(f"已加载 {len(users)} 个用户: {', '.join(users.keys())}")
    else:
        print("未检测到 users.json，将创建新文件。")

    print("-" * 40)
    username = input("请输入用户名: ").strip()
    if not username:
        print("用户名不能为空！")
        return

    password = getpass.getpass("请输入密码: ")
    if not password:
        print("密码不能为空！")
        return

    confirm = getpass.getpass("请再次输入密码: ")
    if password != confirm:
        print("两次密码不一致！")
        return

    pw_hash = hash_password(password)
    users[username] = pw_hash

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

    print(f"\n✅ 用户 '{username}' 已保存到 {CONFIG_PATH}")
    print(f"   哈希: {pw_hash}")


if __name__ == "__main__":
    main()
