#!/usr/bin/env python3
"""测试 xAI Responses API 原生数据返回"""

import os
import httpx
import json

api_key = os.environ.get("GROK_API_KEY")
proxy = "socks5://127.0.0.1:40000"
url = "https://api.x.ai/v1/responses"

payload = {
    "model": "grok-4-1-fast",  # 切换至低成本模型
    "input": [
        {"role": "system", "content": "仅调用工具，不要回复任何解释性文本。"},
        {"role": "user", "content": "搜索 Yi He HTX 的最新推文"}
    ],
    "tools": [{"type": "x_search"}]
}

# 建议在实际项目中将此替换为全局维护的 Client
with httpx.Client(proxy=proxy, timeout=60.0) as client:
    try:
        response = client.post(url, headers={"Authorization": f"Bearer {api_key}"}, json=payload)
        response.raise_for_status()
        print("Status:", response.status_code)
        print("\nRaw Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except httpx.HTTPStatusError as e:
        print(f"API 请求失败: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"网络异常: {e}")