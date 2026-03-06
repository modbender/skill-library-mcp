#!/usr/bin/env python3
"""
GeoConvert skill for OpenClaw.
基于极速数据经纬度地址转换 API：
https://www.jisuapi.com/api/geoconvert/
"""

import sys
import json
import os
import requests


COORD2ADDR_URL = "https://api.jisuapi.com/geoconvert/coord2addr"
ADDR2COORD_URL = "https://api.jisuapi.com/geoconvert/addr2coord"


def coord2addr(appkey: str, req: dict):
    """
    经纬度转地址 /geoconvert/coord2addr

    请求 JSON 示例：
    {
        "lat": "30.2812129803",
        "lng": "120.11523398",
        "type": "baidu"  # 可选 baidu / google，默认 baidu
    }
    """
    lat = req.get("lat")
    lng = req.get("lng")
    if not lat:
        return {"error": "missing_param", "message": "lat is required"}
    if not lng:
        return {"error": "missing_param", "message": "lng is required"}

    params = {
        "appkey": appkey,
        "lat": lat,
        "lng": lng,
    }
    if req.get("type"):
        params["type"] = req["type"]

    try:
        resp = requests.get(COORD2ADDR_URL, params=params, timeout=10)
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


def addr2coord(appkey: str, req: dict):
    """
    地址转经纬度 /geoconvert/addr2coord

    请求 JSON 示例：
    {
        "address": "益乐路39号",
        "type": "baidu"  # 可选 baidu / google，默认 baidu
    }
    """
    address = req.get("address")
    if not address:
        return {"error": "missing_param", "message": "address is required"}

    params = {
        "appkey": appkey,
        "address": address,
    }
    if req.get("type"):
        params["type"] = req["type"]

    try:
        resp = requests.get(ADDR2COORD_URL, params=params, timeout=10)
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
            "  geoconvert.py coord2addr '{\"lat\":\"30.2812129803\",\"lng\":\"120.11523398\",\"type\":\"baidu\"}'  # 经纬度转地址\n"
            "  geoconvert.py addr2coord '{\"address\":\"益乐路39号\",\"type\":\"baidu\"}'                       # 地址转经纬度",
            file=sys.stderr,
        )
        sys.exit(1)

    appkey = os.getenv("JISU_API_KEY")

    if not appkey:
        print("Error: JISU_API_KEY must be set in environment.", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd not in ("coord2addr", "addr2coord"):
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

    if cmd == "coord2addr":
        result = coord2addr(appkey, req)
    else:
        result = addr2coord(appkey, req)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

