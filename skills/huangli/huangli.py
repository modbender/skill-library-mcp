#!/usr/bin/env python3
"""
Huangli (Almanac) skill for OpenClaw.
基于极速数据黄历查询 API：
https://www.jisuapi.com/api/huangli
"""

import sys
import json
import os
import requests


HUANGLI_DATE_URL = "https://api.jisuapi.com/huangli/date"


def query_huangli(appkey: str, req: dict):
    """
    黄历查询 /huangli/date

    请求 JSON 示例：
    {
        "year": 2015,
        "month": 10,
        "day": 27
    }
    """
    year = req.get("year")
    month = req.get("month")
    day = req.get("day")

    if year is None:
        return {"error": "missing_param", "message": "year is required"}
    if month is None:
        return {"error": "missing_param", "message": "month is required"}
    if day is None:
        return {"error": "missing_param", "message": "day is required"}

    params = {
        "appkey": appkey,
        "year": year,
        "month": month,
        "day": day,
    }

    try:
        resp = requests.get(HUANGLI_DATE_URL, params=params, timeout=10)
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
            "  huangli.py '{\"year\":2015,\"month\":10,\"day\":27}'  # 黄历查询",
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

    for field in ("year", "month", "day"):
        if field not in req or req[field] is None or req[field] == "":
            print(f"Error: '{field}' is required in request JSON.", file=sys.stderr)
            sys.exit(1)

    result = query_huangli(appkey, req)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

