#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 user_cache.json 中根据用户名获取 mid"""

import json
import os
import sys

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_cache.json")


def get_mid(username: str) -> int | None:
    """根据用户名从 user_cache.json 获取 mid，不区分大小写"""
    if not os.path.exists(CACHE_FILE):
        return None

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)

    key = username.lower()
    for k, v in cache.items():
        if k.lower() == key:
            return v.get("mid")
    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"用法: python3 {sys.argv[0]} <用户名>", file=sys.stderr)
        sys.exit(1)

    username = sys.argv[1]
    mid = get_mid(username)

    if mid is not None:
        print(mid)
    else:
        print("NOT_FOUND")
        sys.exit(1)
