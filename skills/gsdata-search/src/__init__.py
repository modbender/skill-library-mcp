"""
GS Data Search API Client
访问 projects-databus.gsdata.cn 搜索接口
"""

import json
import requests

API_URL = "http://projects-databus.gsdata.cn:7777/api-project/service"
ROUTER = "/standard/search/get-data"


def search(project_id: str, sign: str, keywords: str, posttime_start: str, posttime_end: str, limit: int = 10) -> dict:
    """
    调用 GS Data 搜索接口

    Args:
        project_id:     项目 ID
        sign:           签名
        keywords:       搜索关键词
        posttime_start: 开始时间 (格式: 2026-03-01 00:00:00)
        posttime_end:   结束时间 (格式: 2026-03-01 23:59:59)
        limit:          返回条数，默认 10

    Returns:
        API 返回的 JSON 数据（dict）
    """
    params_json = json.dumps({"keywords_include": keywords, "limit": limit, "posttime_start": posttime_start, "posttime_end": posttime_end}, ensure_ascii=False)

    payload = {
        "project_id": project_id,
        "sign": sign,
        "router": ROUTER,
        "params": params_json,
    }

    resp = requests.post(API_URL, data=payload, timeout=30)
    resp.raise_for_status()
    api_response = resp.json()

    # 只返回指定字段
    target_fields = ["news_title", "news_uuid", "media_name", "news_posttime", "news_emotion", "news_url", "news_digest"]

    # 处理返回结果为列表格式
    result_list = []
    if "data" in api_response:
        for item in api_response["data"]:
            filtered_item = {}
            for field in target_fields:
                if field in item:
                    filtered_item[field] = item[field]
            result_list.append(filtered_item)

    return result_list


# --------------- 命令行直接运行 ---------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GS Data 搜索工具")
    parser.add_argument("--project_id", required=True, help="项目 ID")
    parser.add_argument("--sign", required=True, help="签名")
    parser.add_argument("--keywords", required=True, help="搜索关键词")
    parser.add_argument("--posttime_start", required=True, help="开始时间")
    parser.add_argument("--posttime_end", required=True, help="结束时间")
    parser.add_argument("--limit", type=int, default=10, help="返回条数 (默认 10)")
    args = parser.parse_args()

    result = search(args.project_id, args.sign, args.keywords, args.posttime_start, args.posttime_end, args.limit)
    # 按照列表格式输出
    for i, item in enumerate(result, 1):
        print(f"----- 结果 {i} -----")
        for key, value in item.items():
            print(f"{key}: {value}")
        print()
