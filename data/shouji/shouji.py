#!/usr/bin/env python3
"""
Mobile number attribution skill for OpenClaw.
基于极速数据手机号码归属地 API：
https://www.jisuapi.com/api/shouji/
"""

import sys
import json
import os
import requests


SHOUJI_QUERY_URL = "https://api.jisuapi.com/shouji/query"


def query_shouji(appkey: str, req: dict):
    """
    调用 /shouji/query 接口，根据手机号查询归属地和运营商信息。

    请求 JSON 示例：
    {
        "shouji": "13456755448"
    }
    """
    params = {"appkey": appkey}

    number = req.get("shouji")
    if not number:
        return {
            "error": "missing_param",
            "message": "shouji is required",
        }
    params["shouji"] = number

    try:
        resp = requests.get(SHOUJI_QUERY_URL, params=params, timeout=10)
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
            "  shouji.py '{\"shouji\":\"13456755448\"}'  # 查询手机号码归属地",
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

    if "shouji" not in req or not req["shouji"]:
        print("Error: 'shouji' is required in request JSON.", file=sys.stderr)
        sys.exit(1)

    result = query_shouji(appkey, req)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

