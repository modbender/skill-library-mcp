#!/usr/bin/env python3
"""
Calendar skill for OpenClaw.
基于极速数据万年历 API：
https://www.jisuapi.com/api/calendar/
"""

import sys
import json
import os
import requests


CALENDAR_QUERY_URL = "https://api.jisuapi.com/calendar/query"
CALENDAR_HOLIDAY_URL = "https://api.jisuapi.com/calendar/holiday"


def query_calendar(appkey: str, req: dict):
    """
    万年历查询 /calendar/query

    请求 JSON 示例：
    {
        "date": "2015-10-22",
        "islunar": 0,
        "islunarmonth": 0
    }
    """
    params = {"appkey": appkey}

    date = req.get("date")
    if not date:
        return {"error": "missing_param", "message": "date is required"}
    params["date"] = date

    islunar = req.get("islunar")
    if islunar is not None:
        params["islunar"] = islunar
    islunarmonth = req.get("islunarmonth")
    if islunarmonth is not None:
        params["islunarmonth"] = islunarmonth

    try:
        resp = requests.get(CALENDAR_QUERY_URL, params=params, timeout=10)
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


def query_holiday(appkey: str):
    """
    节假日查询 /calendar/holiday
    返回 result map，key 为日期（YYYY-MM-DD），value 为节假日说明或对象。
    """
    params = {"appkey": appkey}

    try:
        resp = requests.get(CALENDAR_HOLIDAY_URL, params=params, timeout=10)
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
            "  calendar.py '{\"date\":\"2015-10-22\"}'              # 万年历查询\n"
            "  calendar.py holiday                                   # 节假日查询",
            file=sys.stderr,
        )
        sys.exit(1)

    appkey = os.getenv("JISU_API_KEY")

    if not appkey:
        print("Error: JISU_API_KEY must be set in environment.", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "holiday":
        result = query_holiday(appkey)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 默认：万年历查询，参数为 JSON
    raw = sys.argv[1]
    try:
        req = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    if "date" not in req or not req["date"]:
        print("Error: 'date' is required in request JSON.", file=sys.stderr)
        sys.exit(1)

    result = query_calendar(appkey, req)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

