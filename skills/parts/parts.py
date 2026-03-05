#!/usr/bin/env python3
"""
Auto parts OE query skill for OpenClaw.
基于极速数据汽车配件OE信息查询 API：
https://www.jisuapi.com/api/parts/
"""

import sys
import json
import os
import requests


BASE_URL = "https://api.jisuapi.com/parts"


def _call_parts_api(path: str, appkey: str, params: dict | None = None):
    if params is None:
        params = {}
    all_params = {"appkey": appkey}
    all_params.update({k: v for k, v in params.items() if v not in (None, "")})
    url = f"{BASE_URL}/{path}"

    try:
        resp = requests.get(url, params=all_params, timeout=10)
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


def brand(appkey: str):
    """
    配件品牌 /parts/brand
    """
    return _call_parts_api("brand", appkey, {})


def search(appkey: str, req: dict):
    """
    原厂零件号模糊搜索 /parts/search
    请求 JSON：{ "number": "L8WD807065KGRU" }
    """
    number = req.get("number")
    if not number:
        return {"error": "missing_param", "message": "number is required"}
    return _call_parts_api("search", appkey, {"number": number})


def salecar(appkey: str, req: dict):
    """
    零件号查销售车型 /parts/salecar
    请求 JSON：number、brandid、partsid 任选其一或组合，如 {"number":"L8WD807065KGRU","brandid":219}
    """
    number = req.get("number")
    brandid = req.get("brandid")
    partsid = req.get("partsid")
    has_any = (number not in (None, "")) or (brandid not in (None, "")) or (partsid not in (None, ""))
    if not has_any:
        return {"error": "missing_param", "message": "number or brandid or partsid is required"}
    params = {}
    if number not in (None, ""):
        params["number"] = number
    if brandid not in (None, ""):
        params["brandid"] = brandid
    if partsid not in (None, ""):
        params["partsid"] = partsid
    return _call_parts_api("salecar", appkey, params)


def replace(appkey: str, req: dict):
    """
    查询替换件 /parts/replace
    请求 JSON：number+brandid 或 partsid 任选一组，如 {"number":"01402917258","brandid":10} 或 {"partsid":12656367}
    """
    number = req.get("number")
    brandid = req.get("brandid")
    partsid = req.get("partsid")
    has_partsid = partsid not in (None, "")
    has_number_brand = (number is not None and number != "") or (brandid is not None)
    if not has_partsid and not has_number_brand:
        return {"error": "missing_param", "message": "partsid or (number and/or brandid) is required"}
    params = {}
    if number is not None and number != "":
        params["number"] = number
    if brandid is not None:
        params["brandid"] = brandid
    if has_partsid:
        params["partsid"] = partsid
    return _call_parts_api("replace", appkey, params)


def main():
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  parts.py brand\n"
            "  parts.py search '{\"number\":\"L8WD807065KGRU\"}'\n"
            "  parts.py salecar '{\"number\":\"L8WD807065KGRU\",\"brandid\":219}'\n"
            "  parts.py replace '{\"number\":\"01402917258\",\"brandid\":10}'",
            file=sys.stderr,
        )
        sys.exit(1)

    appkey = os.getenv("JISU_API_KEY")
    if not appkey:
        print("Error: JISU_API_KEY must be set in environment.", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "brand":
        result = brand(appkey)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if cmd not in ("search", "salecar", "replace"):
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

    if cmd == "search":
        result = search(appkey, req)
    elif cmd == "salecar":
        result = salecar(appkey, req)
    elif cmd == "replace":
        result = replace(appkey, req)
    else:
        print(f"Error: unhandled command '{cmd}'", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
