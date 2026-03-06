#!/usr/bin/env python3
"""
Recipe skill for OpenClaw.
基于极速数据菜谱大全 API：
https://www.jisuapi.com/api/recipe/
"""

import sys
import json
import os
import requests


RECIPE_SEARCH_URL = "https://api.jisuapi.com/recipe/search"
RECIPE_CLASS_URL = "https://api.jisuapi.com/recipe/class"
RECIPE_BYCLASS_URL = "https://api.jisuapi.com/recipe/byclass"
RECIPE_DETAIL_URL = "https://api.jisuapi.com/recipe/detail"


def _call_recipe_api(url: str, appkey: str, params: dict | None = None):
    query = {"appkey": appkey}
    if params:
        for k, v in params.items():
            if v not in (None, ""):
                query[k] = v

    try:
        resp = requests.get(url, params=query, timeout=10)
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


def recipe_search(appkey: str, req: dict):
    """
    菜谱搜索 /recipe/search

    请求 JSON 示例：
    {
        "keyword": "白菜",
        "num": 10,
        "start": 0
    }
    """
    keyword = req.get("keyword")
    if not keyword:
        return {"error": "missing_param", "message": "keyword is required"}

    if "num" not in req or req.get("num") is None:
        return {"error": "missing_param", "message": "num is required"}
    if "start" not in req or req.get("start") is None:
        return {"error": "missing_param", "message": "start is required"}

    params = {
        "keyword": keyword,
        "num": req.get("num"),
        "start": req.get("start"),
    }
    return _call_recipe_api(RECIPE_SEARCH_URL, appkey, params)


def recipe_class(appkey: str):
    """
    菜谱分类 /recipe/class
    无额外参数。
    """
    return _call_recipe_api(RECIPE_CLASS_URL, appkey, {})


def recipe_byclass(appkey: str, req: dict):
    """
    按分类检索 /recipe/byclass

    请求 JSON 示例：
    {
        "classid": 2,
        "start": 0,
        "num": 10
    }
    """
    if "classid" not in req or req.get("classid") is None:
        return {"error": "missing_param", "message": "classid is required"}
    if "start" not in req or req.get("start") is None:
        return {"error": "missing_param", "message": "start is required"}
    if "num" not in req or req.get("num") is None:
        return {"error": "missing_param", "message": "num is required"}

    params = {
        "classid": req.get("classid"),
        "start": req.get("start"),
        "num": req.get("num"),
    }
    return _call_recipe_api(RECIPE_BYCLASS_URL, appkey, params)


def recipe_detail(appkey: str, req: dict):
    """
    根据 ID 查询详情 /recipe/detail

    请求 JSON 示例：
    {
        "id": 5
    }
    """
    if "id" not in req or req.get("id") is None:
        return {"error": "missing_param", "message": "id is required"}

    params = {"id": req.get("id")}
    return _call_recipe_api(RECIPE_DETAIL_URL, appkey, params)


def main():
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  recipe.py search '{\"keyword\":\"白菜\",\"num\":10,\"start\":0}'     # 菜谱搜索\n"
            "  recipe.py class                                                   # 获取菜谱分类\n"
            "  recipe.py byclass '{\"classid\":2,\"start\":0,\"num\":10}'         # 按分类检索\n"
            "  recipe.py detail '{\"id\":5}'                                      # 根据 ID 查询详情",
            file=sys.stderr,
        )
        sys.exit(1)

    appkey = os.getenv("JISU_API_KEY")

    if not appkey:
        print("Error: JISU_API_KEY must be set in environment.", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd not in ("search", "class", "byclass", "detail"):
        print(f"Error: unknown command '{cmd}'", file=sys.stderr)
        sys.exit(1)

    # class 不需要 JSON 参数
    if cmd == "class":
        result = recipe_class(appkey)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if len(sys.argv) < 3:
        print("Error: JSON body is required.", file=sys.stderr)
        sys.exit(1)

    raw = sys.argv[2]
    try:
        req = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    if cmd == "search":
        result = recipe_search(appkey, req)
    elif cmd == "byclass":
        result = recipe_byclass(appkey, req)
    elif cmd == "detail":
        result = recipe_detail(appkey, req)
    else:
        print(f"Error: unhandled command '{cmd}'", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

