#!/usr/bin/env python3
"""
Enterprise info skill for OpenClaw.
基于极速数据企业工商信息 API：
https://www.jisuapi.com/api/enterprise/
"""

import sys
import json
import os
import requests


BASE_URL = "https://api.jisuapi.com/enterprise"


def _call_enterprise_api(path: str, appkey: str, params: dict):
    all_params = {"appkey": appkey}
    all_params.update(params)
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


def query_enterprise(appkey: str, req: dict):
    """
    调用 /enterprise/query 接口，按公司名称/统一信用代码/注册号/组织机构代码查询企业工商信息。

    请求 JSON 示例：
    {
        "company": "杭州极速互联科技有限公司",
        "creditno": "",
        "regno": "",
        "orgno": ""
    }

    四个参数只需提供一个即可，其余可留空。
    """
    params: dict = {}
    for key in ("company", "creditno", "regno", "orgno"):
        value = req.get(key)
        if value:
            params[key] = value

    if not params:
        return {
            "error": "missing_param",
            "message": "one of company/creditno/regno/orgno is required",
        }

    return _call_enterprise_api("query", appkey, params)


def search_enterprise(appkey: str, req: dict):
    """
    调用 /enterprise/search 接口，根据关键词搜索企业列表。

    请求 JSON 示例：
    {
        "keyword": "极速互联",
        "page": 1,
        "pagesize": 10
    }
    """
    keyword = req.get("keyword")
    if not keyword:
        return {"error": "missing_param", "message": "keyword is required"}

    params: dict = {"keyword": keyword}
    if "page" in req and req["page"]:
        params["page"] = req["page"]
    if "pagesize" in req and req["pagesize"]:
        params["pagesize"] = req["pagesize"]

    return _call_enterprise_api("search", appkey, params)


def changerecord(appkey: str, req: dict):
    """
    调用 /enterprise/changerecord 接口，查询企业变更记录。
    company / creditno / regno / orgno 四者提供其一即可。
    """
    params: dict = {}
    for key in ("company", "creditno", "regno", "orgno"):
        value = req.get(key)
        if value:
            params[key] = value

    if not params:
        return {
            "error": "missing_param",
            "message": "one of company/creditno/regno/orgno is required",
        }

    return _call_enterprise_api("changerecord", appkey, params)


def shareholder(appkey: str, req: dict):
    """
    调用 /enterprise/shareholder 接口，查询企业股东及高管信息。
    company / creditno / regno / orgno 四者提供其一即可。
    """
    params: dict = {}
    for key in ("company", "creditno", "regno", "orgno"):
        value = req.get(key)
        if value:
            params[key] = value

    if not params:
        return {
            "error": "missing_param",
            "message": "one of company/creditno/regno/orgno is required",
        }

    return _call_enterprise_api("shareholder", appkey, params)


def main():
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  enterprise.py '{\"company\":\"杭州极速互联科技有限公司\"}'          # 企业基本信息查询\n"
            "  enterprise.py search '{\"keyword\":\"极速互联\",\"page\":1}'     # 企业名称搜索\n"
            "  enterprise.py changerecord '{\"company\":\"杭州极速互联科技有限公司\"}'  # 企业变更记录\n"
            "  enterprise.py shareholder '{\"company\":\"杭州极速互联科技有限公司\"}'   # 股东/高管信息",
            file=sys.stderr,
        )
        sys.exit(1)

    appkey = os.getenv("JISU_API_KEY")

    if not appkey:
        print("Error: JISU_API_KEY must be set in environment.", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    # search/changerecord/shareholder 需要第二个参数 JSON
    if cmd in ("search", "changerecord", "shareholder"):
        if len(sys.argv) < 3:
            print(f"Error: JSON body is required for '{cmd}' subcommand.", file=sys.stderr)
            sys.exit(1)
        raw = sys.argv[2]
        try:
            req = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}", file=sys.stderr)
            sys.exit(1)

        if cmd == "search":
            result = search_enterprise(appkey, req)
        elif cmd == "changerecord":
            result = changerecord(appkey, req)
        else:
            result = shareholder(appkey, req)

        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 默认：企业基本信息查询（/enterprise/query）
    raw = sys.argv[1]
    try:
        req = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    result = query_enterprise(appkey, req)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

