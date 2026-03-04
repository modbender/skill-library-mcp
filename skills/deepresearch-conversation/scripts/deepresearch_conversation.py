"""Deep Research conversation client for Baidu Qianfan API."""

import os
import sys
import requests
import json


def deepresearch_conversation(api_key: str, parse_data: dict):
    """Stream SSE responses from the Deep Research conversation API."""
    url = "https://qianfan.baidubce.com/v2/agent/deepresearch/run"
    headers = {
        "Authorization": "Bearer %s" % api_key,
        "X-Appbuilder-From": "openclaw",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    }

    with requests.post(url, headers=headers, json=parse_data, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            line = line.decode('utf-8')
            if line and line.startswith("data:"):
                data_str = line[5:].strip()
                if data_str == "[DONE]":
                    break
                yield json.loads(data_str)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deepresearch_conversation.py <requestBody>")
        sys.exit(1)

    try:
        parse_data = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        sys.exit(1)

    if "query" not in parse_data:
        print("Error: query must be present in request body.")
        sys.exit(1)

    # 多源获取 API Key：环境变量 -> OpenClaw 配置文件
    api_key = os.getenv("BAIDU_API_KEY")

    if not api_key:
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    skill = config.get("skills", {})
                    entry = skill.get("entries", {})
                    dr = entry.get("deepresearch-conversation", {})
                    api_key = dr.get("env", {}).get("BAIDU_API_KEY")
                    if api_key:
                        print("Info: Using BAIDU_API_KEY from OpenClaw config file.")
        except Exception as e:
            print(f"Warning: Failed to read config file: {e}")

    if not api_key:
        print("Error: BAIDU_API_KEY must be set in environment or OpenClaw config.")
        sys.exit(1)

    try:
        results = deepresearch_conversation(api_key, parse_data)
        for result in results:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
