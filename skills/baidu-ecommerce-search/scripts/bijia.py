#!/usr/bin/env python3
"""
全网比价
通过商品关键词，获取全网相关 SPU 与优质低价商品链接
支持多级查询：SPU → SKU → 商品
"""
import sys
from common import request_api, output_json, output_error


def spu_search(query):
    """
    SPU比价：基于query的spu比价，返回SPU列表及SPUID

    Args:
        query: 商品搜索关键词，如 "iphone16价格"、"手机价格"

    Returns:
        包含 SPU ID、名称、图片、价格区间、SKU 信息的 JSON
    """
    return request_api("bijia_spu_search", {"query": query})


def spu_goods_search(query):
    """
    默认SKU商品比价：基于query的默认spu的默认sku的商品比价

    Args:
        query: 商品搜索关键词，如 "苹果手机价格"

    Returns:
        包含多平台比价商品信息的 JSON
    """
    return request_api("bijia_spu_goods_search", {"query": query})


def sku_list_search(spu_id):
    """
    SKU比价：基于SPUID的SKU比价，返回SKU列表及SKUID

    Args:
        spu_id: SPU ID，从 SPU比价结果中获取

    Returns:
        包含 SKU ID、名称、规格参数、价格的 JSON
    """
    return request_api("bijia_sku_list_search", {"spu_id": spu_id})


def sku_goods_search(sku_id):
    """
    SKU商品比价：基于SKUID的不同平台不同渠道的商品比价

    Args:
        sku_id: SKU ID，从 SKU比价结果中获取

    Returns:
        包含多平台比价商品详情的 JSON
    """
    return request_api("bijia_sku_goods_search", {"sku_id": sku_id})


def main():
    if len(sys.argv) < 3:
        output_error(
            "用法: python bijia.py <子命令> <参数>",
            commands={
                "spu": "SPU比价 - python bijia.py spu 'iphone16价格'",
                "goods": "默认SKU商品比价 - python bijia.py goods '苹果手机价格'",
                "sku_list": "SKU比价 - python bijia.py sku_list '<spu_id>'",
                "sku_goods": "SKU商品比价 - python bijia.py sku_goods '<sku_id>'"
            }
        )

    command = sys.argv[1]
    param = sys.argv[2]

    if command == "spu":
        result = spu_search(param)
    elif command == "goods":
        result = spu_goods_search(param)
    elif command == "sku_list":
        result = sku_list_search(param)
    elif command == "sku_goods":
        result = sku_goods_search(param)
    else:
        output_error(
            "用法: python bijia.py <子命令> <参数>",
            commands={
                "spu": "SPU比价 - python bijia.py spu 'iphone16价格'",
                "goods": "默认SKU商品比价 - python bijia.py goods '苹果手机价格'",
                "sku_list": "SKU比价 - python bijia.py sku_list '<spu_id>'",
                "sku_goods": "SKU商品比价 - python bijia.py sku_goods '<sku_id>'"
            }
        )

    output_json(result)


if __name__ == "__main__":
    main()
