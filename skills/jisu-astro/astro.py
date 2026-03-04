#!/usr/bin/env python3
"""
Astro fortune skill for OpenClaw.
基于极速数据星座运势 API：
https://www.jisuapi.com/api/astro/
"""

import sys
import json
import os
import requests


ASTRO_ALL_URL = "https://api.jisuapi.com/astro/all"
ASTRO_FORTUNE_URL = "https://api.jisuapi.com/astro/fortune"


def list_astros(appkey: str):
    """
    星座列表 /astro/all
    返回 12 星座的基本信息：
    { "astroid": 1, "astroname": "白羊座", "date": "3-21~4-19", "pic": "..." }
    """
    params = {"appkey": appkey}

    try:
        resp = requests.get(ASTRO_ALL_URL, params=params, timeout=10)
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

    return data.get("result", [])


def astro_fortune(appkey: str, req: dict):
    """
    星座运势查询 /astro/fortune

    请求 JSON 示例：
    {
        "astroid": 1,
        "date": "2016-01-19"
    }

    astroid 为必填，date 可选（默认今天）。
    """
    astroid = req.get("astroid")
    if astroid in (None, ""):
        return {"error": "missing_param", "message": "astroid is required"}

    params = {
        "appkey": appkey,
        "astroid": astroid,
    }
    if req.get("date"):
        params["date"] = req["date"]

    try:
        resp = requests.get(ASTRO_FORTUNE_URL, params=params, timeout=10)
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
            "  astro.py all                                           # 星座列表\n"
            "  astro.py fortune '{\"astroid\":1,\"date\":\"2016-01-19\"}'  # 星座运势查询",
            file=sys.stderr,
        )
        sys.exit(1)

    appkey = os.getenv("JISU_API_KEY")

    if not appkey:
        print("Error: JISU_API_KEY must be set in environment.", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "all":
        result = list_astros(appkey)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if cmd == "fortune":
        if len(sys.argv) < 3:
            print("Error: JSON body is required for 'fortune'.", file=sys.stderr)
            sys.exit(1)
        raw = sys.argv[2]
        try:
            req = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}", file=sys.stderr)
            sys.exit(1)

        if "astroid" not in req or req["astroid"] in (None, ""):
            print("Error: 'astroid' is required in request JSON.", file=sys.stderr)
            sys.exit(1)

        result = astro_fortune(appkey, req)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"Error: unknown command '{cmd}'", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()

