#!/usr/bin/env python3
"""
通用URL内容读取器
支持多种平台和读取策略
"""

import re
import json
import sys
from urllib.parse import urlparse, unquote


def identify_platform(url: str) -> dict:
    """识别URL所属平台"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    platforms = {
        'wechat': {
            'name': '微信公众号',
            'domains': ['mp.weixin.qq.com'],
            'strategy': 'browser',
            'script': 'wechat_reader.py'
        },
        'xiaohongshu': {
            'name': '小红书',
            'domains': ['xiaohongshu.com', 'xhslink.com', 'www.xiaohongshu.com'],
            'strategy': 'browser',
            'script': 'xiaohongshu_reader.py'
        },
        'toutiao': {
            'name': '今日头条',
            'domains': ['toutiao.com', 'www.toutiao.com'],
            'strategy': 'jina',
        },
        'douyin': {
            'name': '抖音',
            'domains': ['douyin.com', 'www.douyin.com', 'v.douyin.com'],
            'strategy': 'browser',
        },
        'taobao': {
            'name': '淘宝',
            'domains': ['taobao.com', 'item.taobao.com', 'world.taobao.com'],
            'strategy': 'browser',
        },
        'tmall': {
            'name': '天猫',
            'domains': ['tmall.com', 'detail.tmall.com'],
            'strategy': 'browser',
        },
        'jd': {
            'name': '京东',
            'domains': ['jd.com', 'item.jd.com'],
            'strategy': 'jina',
        },
        'baidu': {
            'name': '百度',
            'domains': ['baidu.com', 'www.baidu.com', 'baijiahao.baidu.com'],
            'strategy': 'jina',
        },
        'zhihu': {
            'name': '知乎',
            'domains': ['zhihu.com', 'www.zhihu.com', 'zhuanlan.zhihu.com'],
            'strategy': 'jina',
        },
        'weibo': {
            'name': '微博',
            'domains': ['weibo.com', 'www.weibo.com', 'm.weibo.cn'],
            'strategy': 'browser',
        },
        'bilibili': {
            'name': 'B站',
            'domains': ['bilibili.com', 'www.bilibili.com', 'b23.tv'],
            'strategy': 'jina',
        },
    }

    for platform_id, info in platforms.items():
        for d in info['domains']:
            if d in domain:
                return {
                    'id': platform_id,
                    **info
                }

    # 通用网站
    return {
        'id': 'generic',
        'name': '通用网站',
        'domains': [],
        'strategy': 'jina'
    }


def get_jina_url(url: str) -> str:
    """获取 Jina Reader URL"""
    return f"https://r.jina.ai/{url}"


def main():
    if len(sys.argv) < 2:
        print("用法: python url_identifier.py <url>")
        return

    url = sys.argv[1]
    platform = identify_platform(url)

    print(json.dumps(platform, ensure_ascii=False, indent=2))

    print(f"\n平台: {platform['name']}")
    print(f"推荐策略: {platform['strategy']}")

    if platform['strategy'] == 'jina':
        print(f"Jina URL: {get_jina_url(url)}")
    elif platform['strategy'] == 'browser':
        script = platform.get('script', '需要浏览器自动化')
        print(f"脚本: {script}")


if __name__ == "__main__":
    main()
