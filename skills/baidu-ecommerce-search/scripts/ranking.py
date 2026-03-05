#!/usr/bin/env python3
"""
实时品牌天梯榜单
基于综合搜索热度、全网声量及销量，提供客观权威的品牌排行推荐服务
"""
import sys
from common import request_api, output_json, output_error


def brand_ranking(query):
    """
    查询品牌榜单

    Args:
        query: 榜单查询，格式为 "xxx品牌榜"
               例如: "手机品牌榜"、"冰箱品牌榜"

    Returns:
        包含品牌排名、名称、推荐理由、热门商品的 JSON
    """
    return request_api("brand_rank", {"query": query})


def product_ranking(query):
    """
    查询单品榜

    Args:
        query: 单品榜查询，格式为 "品牌+品类+排行榜"
               例如: "苹果手机排行榜"

    Returns:
        包含商品排名、名称、价格、推荐理由的 JSON
    """
    return request_api("product_rank", {"query": query})


def main():
    if len(sys.argv) < 3:
        output_error(
            "用法: python ranking.py <子命令> <查询>",
            commands={
                "brand": "品牌榜单 - python ranking.py brand '手机品牌榜'",
                "product": "单品榜 - python ranking.py product '苹果手机排行榜'"
            }
        )

    command = sys.argv[1]
    query = sys.argv[2]

    if command == "brand":
        result = brand_ranking(query)
    elif command == "product":
        result = product_ranking(query)
    else:
        output_error(
            "用法: python ranking.py <子命令> <查询>",
            commands={
                "brand": "品牌榜单 - python ranking.py brand '手机品牌榜'",
                "product": "单品榜 - python ranking.py product '苹果手机排行榜'"
            }
        )

    output_json(result)


if __name__ == "__main__":
    main()
