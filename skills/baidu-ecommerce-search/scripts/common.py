#!/usr/bin/env python3
"""
公共模块
提供 API 请求、Token 管理等通用功能
"""
import os
import sys
import json
import time
import socket
import urllib.request
import urllib.parse
import urllib.error

# QPS控制从 lock.py 模块导入
try:
    from .lock import wait_for_rate_limit, set_qps  # 作为包导入时
except ImportError:
    from lock import wait_for_rate_limit, set_qps   # 直接运行脚本时

BASE_URL = "https://mcp-youxuan.baidu.com/skill"


def get_token():
    """获取 API Token"""
    token = os.environ.get("BAIDU_EC_SEARCH_TOKEN")
    if not token:
        print(json.dumps({"errno": -1, "errmsg": "BAIDU_EC_SEARCH_TOKEN 环境变量未设置"}))
        sys.exit(1)
    return token


def request_api(endpoint, params, timeout=30):
    """
    发送 API 请求

    Args:
        endpoint: API 端点
        params: 请求参数字典
        timeout: 超时时间（秒），默认 30 秒

    Returns:
        API 响应的 JSON 数据
    """
    # 等待以满足QPS限制（跨进程同步）
    wait_for_rate_limit()

    params["key"] = get_token()
    params["_t"] = int(time.time() * 1000)

    url = f"{BASE_URL}/{endpoint}?" + urllib.parse.urlencode(params)

    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "BaiduEcommerceSkill/1.0")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"errno": e.code, "errmsg": f"HTTP Error: {e.reason}"}
    except urllib.error.URLError as e:
        return {"errno": -1, "errmsg": f"URL Error: {e.reason}"}
    except socket.timeout:
        return {"errno": -1, "errmsg": f"请求超时（{timeout}秒）"}
    except json.JSONDecodeError:
        return {"errno": -1, "errmsg": "Invalid JSON response"}


def output_json(data):
    """输出格式化的 JSON"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def output_error(message, **extra):
    """输出错误信息"""
    error = {"errno": -1, "errmsg": message}
    error.update(extra)
    output_json(error)
    sys.exit(1)
