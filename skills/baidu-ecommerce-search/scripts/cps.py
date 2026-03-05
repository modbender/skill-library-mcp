#!/usr/bin/env python3
"""
全网 CPS 商品
通过商品关键词，获取全网 CPS 商品链接及热卖商品信息
"""
import sys
from common import request_api, output_json, output_error


def goods_search(query):
    """
    搜索 CPS 商品

    Args:
        query: 商品搜索关键词，如 "iphone16"、"机械键盘"

    Returns:
        包含商品名称、图片、价格、购买链接、销量、优惠信息的 JSON
    """
    return request_api("goods_search", {"query": query})


def main():
    if len(sys.argv) < 2:
        output_error(
            "用法: python cps.py <商品关键词>",
            example="python cps.py 'iphone16'"
        )

    query = sys.argv[1]
    result = goods_search(query)
    output_json(result)


if __name__ == "__main__":
    main()
