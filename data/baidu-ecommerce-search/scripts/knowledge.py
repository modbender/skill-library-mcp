#!/usr/bin/env python3
"""
商品百科知识
提供品类选购指南、品牌科普知识、全维度参数库的服务
"""
import sys
from common import request_api, output_json, output_error


def brand_info(query):
    """
    查询品牌知识

    Args:
        query: 品牌名称，如 "华为"、"ysl"

    Returns:
        包含品牌简介、定位、明星产品、荣誉、大事记的 JSON
    """
    return request_api("brand_info", {"query": query})


def entity_info(query):
    """
    查询品类知识

    Args:
        query: 品类选购查询，格式为 "xxx怎么选" 或 "怎么选xxx"
               例如: "无人机怎么选"

    Returns:
        包含选购要点、选购建议、避坑指南的 JSON
    """
    return request_api("entity_info", {"query": query})


def param_info(query):
    """
    查询商品参数

    Args:
        query: SPU 名称，如 "iphone16"、"小米14"

    Returns:
        包含 SPU 名称、图片、价格、参数列表、AI 解读的 JSON
    """
    return request_api("param_info", {"query": query})


def main():
    if len(sys.argv) < 3:
        output_error(
            "用法: python knowledge.py <子命令> <查询>",
            commands={
                "brand": "品牌知识 - python knowledge.py brand '华为'",
                "entity": "品类知识 - python knowledge.py entity '无人机怎么选'",
                "param": "商品参数 - python knowledge.py param 'iphone16'"
            }
        )

    command = sys.argv[1]
    query = sys.argv[2]

    if command == "brand":
        result = brand_info(query)
    elif command == "entity":
        result = entity_info(query)
    elif command == "param":
        result = param_info(query)
    else:
        output_error(
            "用法: python knowledge.py <子命令> <查询>",
            commands={
                "brand": "品牌知识 - python knowledge.py brand '华为'",
                "entity": "品类知识 - python knowledge.py entity '无人机怎么选'",
                "param": "商品参数 - python knowledge.py param 'iphone16'"
            }
        )

    output_json(result)


if __name__ == "__main__":
    main()
