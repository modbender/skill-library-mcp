import sys
import json
import requests
import os


def baidu_search(api_key, requestBody: dict):
    url = "https://qianfan.baidubce.com/v2/ai_search/web_search"

    headers = {
        "Authorization": "Bearer %s" % api_key,
        "X-Appbuilder-From": "openclaw",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=requestBody, headers=headers)
    response.raise_for_status()
    results = response.json()
    if "code" in results:
        raise Exception(results["message"])
    datas = results["references"]
    # 移除 snippet 字段以减少输出
    keys_to_remove = {"snippet"}
    for item in datas:
        for key in keys_to_remove:
            if key in item:
                del item[key]
    return datas


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search.py '<JSON>'")
        sys.exit(1)

    query = sys.argv[1]
    parse_data = {}
    try:
        parse_data = json.loads(query)
        print(f"success parse request body: {parse_data}")
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        sys.exit(1)

    if "query" not in parse_data:
        print("Error: query must be present in request body.")
        sys.exit(1)

    # 从环境变量获取 API Key
    api_key = os.getenv("BAIDU_API_KEY")

    if not api_key:
        print("Error: BAIDU_API_KEY must be set in environment.")
        sys.exit(1)

    request_body = {
        "messages": [
            {
                "content": parse_data["query"],
                "role": "user"
            }
        ],
        "edition": parse_data.get("edition", "standard"),
        "search_source": "baidu_search_v2",
        "resource_type_filter": parse_data.get("resource_type_filter", [{"type": "web", "top_k": 20}]),
        "search_filter": parse_data.get("search_filter", {}),
        "block_websites": parse_data.get("block_websites"),
        "search_recency_filter": parse_data.get("search_recency_filter", "year"),
        "safe_search": parse_data.get("safe_search", False),
    }
    
    try:
        results = baidu_search(api_key, request_body)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
