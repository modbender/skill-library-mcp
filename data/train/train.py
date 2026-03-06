#!/usr/bin/env python3
"""
Train query skill for OpenClaw.
基于极速数据火车查询 API：
https://www.jisuapi.com/api/train/
"""

import sys
import json
import os
import requests


TRAIN_STATION2S_URL = "https://api.jisuapi.com/train/station2s"
TRAIN_LINE_URL = "https://api.jisuapi.com/train/line"
TRAIN_TICKET_URL = "https://api.jisuapi.com/train/ticket"


def station2s(appkey: str, req: dict):
    """
    站站查询 /train/station2s

    请求 JSON 示例：
    {
        "start": "杭州",
        "end": "北京",
        "ishigh": 0,
        "date": "2025-04-03"
    }
    """
    start = req.get("start")
    end = req.get("end")
    if not start:
        return {"error": "missing_param", "message": "start is required"}
    if not end:
        return {"error": "missing_param", "message": "end is required"}

    params = {
        "appkey": appkey,
        "start": start,
        "end": end,
    }
    if "ishigh" in req and req["ishigh"] != "" and req["ishigh"] is not None:
        params["ishigh"] = req["ishigh"]
    if req.get("date"):
        params["date"] = req["date"]

    try:
        resp = requests.get(TRAIN_STATION2S_URL, params=params, timeout=10)
    except Exception as e:
        return {"error": "request_failed", "message": str(e)}

    if resp.status_code != 200:
        return {"error": "http_error", "status_code": resp.status_code, "body": resp.text}

    try:
        data = resp.json()
    except Exception:
        return {"error": "invalid_json", "body": resp.text}

    if data.get("status") != 0:
        return {"error": "api_error", "code": data.get("status"), "message": data.get("msg")}

    return data.get("result", [])


def line(appkey: str, req: dict):
    """
    车次查询 /train/line

    请求 JSON 示例：
    {
        "trainno": "G34",
        "date": "2025-04-04"
    }
    """
    trainno = req.get("trainno")
    if not trainno:
        return {"error": "missing_param", "message": "trainno is required"}

    params = {"appkey": appkey, "trainno": trainno}
    if req.get("date"):
        params["date"] = req["date"]

    try:
        resp = requests.get(TRAIN_LINE_URL, params=params, timeout=10)
    except Exception as e:
        return {"error": "request_failed", "message": str(e)}

    if resp.status_code != 200:
        return {"error": "http_error", "status_code": resp.status_code, "body": resp.text}

    try:
        data = resp.json()
    except Exception:
        return {"error": "invalid_json", "body": resp.text}

    if data.get("status") != 0:
        return {"error": "api_error", "code": data.get("status"), "message": data.get("msg")}

    return data.get("result", {})


def ticket(appkey: str, req: dict):
    """
    余票查询 /train/ticket

    请求 JSON 示例：
    {
        "start": "杭州",
        "end": "北京",
        "date": "2015-10-20"
    }
    """
    start = req.get("start")
    end = req.get("end")
    date = req.get("date")
    if not start:
        return {"error": "missing_param", "message": "start is required"}
    if not end:
        return {"error": "missing_param", "message": "end is required"}
    if not date:
        return {"error": "missing_param", "message": "date is required"}

    params = {"appkey": appkey, "start": start, "end": end, "date": date}

    try:
        resp = requests.get(TRAIN_TICKET_URL, params=params, timeout=10)
    except Exception as e:
        return {"error": "request_failed", "message": str(e)}

    if resp.status_code != 200:
        return {"error": "http_error", "status_code": resp.status_code, "body": resp.text}

    try:
        data = resp.json()
    except Exception:
        return {"error": "invalid_json", "body": resp.text}

    if data.get("status") != 0:
        return {"error": "api_error", "code": data.get("status"), "message": data.get("msg")}

    return data.get("result", [])


def main():
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  train.py station2s '{\"start\":\"杭州\",\"end\":\"北京\",\"ishigh\":0}'   # 站站查询\n"
            "  train.py line '{\"trainno\":\"G34\"}'                                 # 车次查询\n"
            "  train.py ticket '{\"start\":\"杭州\",\"end\":\"北京\",\"date\":\"2015-10-20\"}'  # 余票查询",
            file=sys.stderr,
        )
        sys.exit(1)

    appkey = os.getenv("JISU_API_KEY")

    if not appkey:
        print("Error: JISU_API_KEY must be set in environment.", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd not in ("station2s", "line", "ticket"):
        print(f"Error: unknown command '{cmd}'", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) < 3:
        print(f"Error: JSON body is required for '{cmd}'.", file=sys.stderr)
        sys.exit(1)

    raw = sys.argv[2]
    try:
        req = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    if cmd == "station2s":
        result = station2s(appkey, req)
    elif cmd == "line":
        result = line(appkey, req)
    else:
        result = ticket(appkey, req)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

