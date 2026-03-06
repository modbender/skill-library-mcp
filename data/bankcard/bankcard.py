#!/usr/bin/env python3
"""
Bankcard attribution skill for OpenClaw.
基于极速数据银行卡归属地查询 API：
https://www.jisuapi.com/api/bankcard
"""

import sys
import json
import os
import requests


BANKCARD_QUERY_URL = "https://api.jisuapi.com/bankcard/query"


def query_bankcard(appkey: str, req: dict):
    """
    银行卡归属地查询 /bankcard/query

    请求 JSON 示例：
    {
        "bankcard": "6212261202011584349"
    }
    """
    bankcard = req.get("bankcard")
    if not bankcard:
        return {"error": "missing_param", "message": "bankcard is required"}

    params = {
        "appkey": appkey,
        "bankcard": bankcard,
    }

    try:
        resp = requests.get(BANKCARD_QUERY_URL, params=params, timeout=10)
    except Exception as e:
        return {"error": "request_failed", "message": str(e)}

    if resp.status_code != 200:
        return {
            "error": "http_error",
            "status_code": resp.status_code,
            "body": resp.text,
        }

    try:
        data = resp.json()
    except Exception:
        return {"error": "invalid_json", "body": resp.text}

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
            "  bankcard.py '{\"bankcard\":\"6212261202011584349\"}'  # 银行卡归属地查询",
            file=sys.stderr,
        )
        sys.exit(1)

    appkey = os.getenv("JISU_API_KEY")

    if not appkey:
        print("Error: JISU_API_KEY must be set in environment.", file=sys.stderr)
        sys.exit(1)

    raw = sys.argv[1]
    try:
        req = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    if "bankcard" not in req or not req["bankcard"]:
        print("Error: 'bankcard' is required in request JSON.", file=sys.stderr)
        sys.exit(1)

    result = query_bankcard(appkey, req)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

