"""
千帆知识库搜索 Skill

该 Skill 用于从用户在千帆平台的知识库中进行知识检索。
"""
import sys
import json
import requests
import os


def knowledgebase_search(api_key: str, request_body: dict):
    """执行知识库搜索

    Args:
        api_key: 千帆平台的 API Key
        request_body: 请求体字典

    Returns:
        API 响应的 JSON 数据
    """
    url = "https://qianfan.baidubce.com/v2/knowledgebases/search"

    headers = {
        "Authorization": "Bearer %s" % api_key,
        "X-Appbuilder-From": "openclaw",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=request_body, headers=headers)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search.py <json_request_body>")
        sys.exit(1)

    query_input = sys.argv[1]
    parse_data = {}
    try:
        parse_data = json.loads(query_input)
        print(f"success parse request body: {parse_data}")
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        sys.exit(1)

    # 验证必要参数
    if "query" not in parse_data:
        print("Error: query must be present in request body.")
        sys.exit(1)

    # 从环境变量获取 API Key
    api_key = os.getenv("BAIDU_API_KEY")
    if not api_key:
        print("Error: BAIDU_API_KEY must be set in environment.")
        sys.exit(1)

    # 获取知识库 ID：优先使用请求参数，否则使用环境变量
    knowledgebase_ids = parse_data.get("knowledgebase_ids")
    if not knowledgebase_ids:
        env_kb_ids = os.getenv("QIANFAN_KNOWLEDGEBASE_IDS")
        if env_kb_ids:
            # 支持逗号分隔的多个ID
            knowledgebase_ids = [kb_id.strip() for kb_id in env_kb_ids.split(",") if kb_id.strip()]

    if not knowledgebase_ids:
        print("Error: knowledgebase_ids must be present in request body or QIANFAN_KNOWLEDGEBASE_IDS environment variable.")
        sys.exit(1)

    # 构建请求体
    request_body = {
        "query": [{"type": "text", "text": parse_data["query"]}],
        "knowledgebase_ids": knowledgebase_ids,
        "recall": {
            "type": parse_data.get("recall_type", "hybrid"),
            "top_k": parse_data.get("recall_top_k", 100)
        },
        "rerank": {
            "enable": parse_data.get("rerank_enable", True),
            "top_n": parse_data.get("rerank_top_n", 20)
        },
        "top_k": parse_data.get("top_k", 6),
        "score_threshold": parse_data.get("score_threshold", 0.4)
    }

    # 仅在 hybrid 模式下添加 vec_weight
    if request_body["recall"]["type"] == "hybrid":
        request_body["recall"]["vec_weight"] = parse_data.get("vec_weight", 0.75)

    if "enable_graph" in parse_data:
        request_body["enable_graph"] = parse_data["enable_graph"]

    if "enable_expansion" in parse_data:
        request_body["enable_expansion"] = parse_data["enable_expansion"]

    try:
        results = knowledgebase_search(api_key, request_body)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)