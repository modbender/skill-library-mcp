#!/usr/bin/env python3
"""
ISBN skill for OpenClaw.
基于极速数据 ISBN 图书书号查询 API：
https://www.jisuapi.com/api/isbn/
"""

import sys
import json
import os
import requests


ISBN_QUERY_URL = "https://api.jisuapi.com/isbn/query"
ISBN_SEARCH_URL = "https://api.jisuapi.com/isbn/search"


def query_isbn(appkey: str, req: dict):
    """
    调用 /isbn/query 接口，按 ISBN 查询图书信息。

    请求 JSON 示例：
    {
        "isbn": "9787212058937"
    }
    """
    params = {"appkey": appkey}

    isbn = req.get("isbn")
    if not isbn:
        return {
            "error": "missing_param",
            "message": "isbn is required",
        }
    params["isbn"] = isbn

    try:
        resp = requests.get(ISBN_QUERY_URL, params=params, timeout=10)
    except Exception as e:
        return {
            "error": "request_failed",
            "message": str(e),
        }

    if resp.status_code != 200:
        return {
            "error": "http_error",
            "status_code": resp.status_code,
            "body": resp.text,
        }

    try:
        data = resp.json()
    except Exception:
        return {
            "error": "invalid_json",
            "body": resp.text,
        }

    if data.get("status") != 0:
        return {
            "error": "api_error",
            "code": data.get("status"),
            "message": data.get("msg"),
        }

    return data.get("result", {})


def search_isbn(appkey: str, req: dict):
    """
    调用 /isbn/search 接口，根据关键字搜索图书列表。

    请求 JSON 示例：
    {
        "keyword": "老人与海",
        "pagenum": 1
    }
    """
    params = {"appkey": appkey}

    keyword = req.get("keyword")
    if not keyword:
        return {
            "error": "missing_param",
            "message": "keyword is required",
        }
    params["keyword"] = keyword

    pagenum = req.get("pagenum")
    if pagenum is not None:
        params["pagenum"] = pagenum

    try:
        resp = requests.get(ISBN_SEARCH_URL, params=params, timeout=10)
    except Exception as e:
        return {
            "error": "request_failed",
            "message": str(e),
        }

    if resp.status_code != 200:
        return {
            "error": "http_error",
            "status_code": resp.status_code,
            "body": resp.text,
        }

    try:
        data = resp.json()
    except Exception:
        return {
            "error": "invalid_json",
            "body": resp.text,
        }

    if data.get("status") != 0:
        return {
            "error": "api_error",
            "code": data.get("status"),
            "message": data.get("msg"),
        }

    return data.get("result", {})


def main():
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  isbn.py '{\"isbn\":\"9787212058937\"}'              # 按 ISBN 查询图书\n"
            "  isbn.py search '{\"keyword\":\"老人与海\",\"pagenum\":1}'  # 按关键字搜索图书",
            file=sys.stderr,
        )
        sys.exit(1)

    appkey = os.getenv("JISU_API_KEY")

    if not appkey:
        print("Error: JISU_API_KEY must be set in environment.", file=sys.stderr)
        sys.exit(1)

    # 子命令: 搜索
    if sys.argv[1].lower() in ("search", "s"):
        if len(sys.argv) < 3:
            print("Error: JSON body is required for search subcommand.", file=sys.stderr)
            sys.exit(1)
        raw = sys.argv[2]
        try:
            req = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}", file=sys.stderr)
            sys.exit(1)

        result = search_isbn(appkey, req)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 默认：ISBN 精确查询
    raw = sys.argv[1]
    try:
        req = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    if "isbn" not in req or not req["isbn"]:
        print("Error: 'isbn' is required in request JSON.", file=sys.stderr)
        sys.exit(1)

    result = query_isbn(appkey, req)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

