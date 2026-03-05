#!/usr/bin/env python3
"""
Express tracking skill for OpenClaw.
Uses Jisu API: https://www.jisuapi.com/api/express
"""

import sys
import json
import os
import requests


API_URL = "https://api.jisuapi.com/express/query"
TYPE_URL = "https://api.jisuapi.com/express/type"


def query_express(appkey: str, req: dict):
    """
    调用极速数据快递查询接口。

    请求体示例（来自命令行 JSON 入参）:
    {
        "number": "70303808964270",
        "type": "auto",          # 可选，默认 auto，支持具体快递代号
        "mobile": "1234"         # 可选，顺丰 / 中通 / 跨越 需要
    }
    """
    params = {
        "appkey": appkey,
        "number": req.get("number", ""),
        "type": req.get("type", "auto"),
    }

    mobile = req.get("mobile")
    if mobile:
        params["mobile"] = mobile

    try:
        resp = requests.get(API_URL, params=params, timeout=10)
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

    # Jisu 业务状态码
    if data.get("status") != 0:
        return {
            "error": "api_error",
            "code": data.get("status"),
            "message": data.get("msg"),
        }

    # 直接返回 result 字段，包含 number/type/typename/logo/list/deliverystatus/issign
    return data.get("result", {})


def query_express_type(appkey: str):
    """
    查询所有支持的快递公司列表，对应 /express/type 接口。
    返回值为官方的 result 数组，每一项包含:
    { "name": "德邦", "type": "DEPPON", "letter": "D", "tel": "95353", "number": "330060412" }
    """
    params = {"appkey": appkey}

    try:
        resp = requests.get(TYPE_URL, params=params, timeout=10)
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

    return data.get("result", [])


def main():
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  express.py '{\"number\":\"快递单号\",\"type\":\"auto\"}'  # 查询快递轨迹\n"
            "  express.py type                                         # 查询支持的快递公司列表",
            file=sys.stderr,
        )
        sys.exit(1)

    # 优先使用 JISU_API_KEY，可选备用变量
    appkey = (
        os.getenv("JISU_API_KEY")
    )

    if not appkey:
        print(
            "Error: JISU_API_KEY"
            "must be set in environment.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 子命令: 查询快递公司列表
    if sys.argv[1].lower() in ("type", "types", "company", "companies"):
        result = query_express_type(appkey)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    raw = sys.argv[1]
    try:
        req = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    if "number" not in req or not req["number"]:
        print("Error: 'number' is required in request JSON.", file=sys.stderr)
        sys.exit(1)

    result = query_express(appkey, req)
    # 统一 JSON 输出，方便 OpenClaw 消费
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

