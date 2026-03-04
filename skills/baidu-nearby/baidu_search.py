#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度搜索工具 - 纯标准库实现
使用百度站内搜索API进行网页搜索
"""

import os
import sys
import json
import urllib.parse
import urllib.request
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def baidu_search(query, num=10, page=1):
    """
    执行百度搜索
    
    Args:
        query: 搜索关键词
        num: 返回结果数量 (1-50)
        page: 页码
    
    Returns:
        dict: 搜索结果
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.baidu.com/',
        'Connection': 'keep-alive'
    }
    
    params = {
        'wd': query,
        'pn': (page - 1) * 10,
        'rn': min(num, 50),
        'tn': 'baidu',
        'ie': 'utf-8'
    }
    
    url = 'https://www.baidu.com/s?' + urllib.parse.urlencode(params)
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        results = []
        
        # 使用正则表达式提取搜索结果
        # 百度结果通常包含在特定class的div中
        
        # 尝试匹配新的百度页面结构
        # 标题: <h3 class="...">...<a ...>(.*?)</a>...</h3>
        # 链接: <a href="(https?://[^"]+)"
        # 摘要: <span class="content-right[^"]*">(.*?)</span>
        
        # 查找所有结果容器
        result_pattern = r'<div[^>]*class="[^"]*result[^"]*"[^>]*>(.*?)</div>\s*</div>'
        result_blocks = re.findall(result_pattern, html, re.DOTALL)
        
        if not result_blocks:
            # 尝试另一种模式
            result_pattern = r'<div[^>]*class="c-container"[^>]*>(.*?)</div>\s*</div>'
            result_blocks = re.findall(result_pattern, html, re.DOTALL)
        
        for block in result_blocks[:num]:
            try:
                # 提取标题
                title_match = re.search(r'<h3[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?</h3>', block, re.DOTALL)
                if not title_match:
                    continue
                
                link = title_match.group(1)
                title = re.sub(r'<[^>]+>', '', title_match.group(2)).strip()
                
                # 提取摘要
                abstract = ""
                # 尝试多种摘要模式
                abstract_patterns = [
                    r'<span class="content-right[^"]*">(.*?)</span>',
                    r'<div class="content-right[^"]*">(.*?)</div>',
                    r'<span class="c-abstract">(.*?)</span>',
                    r'<div class="c-abstract">(.*?)</div>',
                ]
                
                for pattern in abstract_patterns:
                    abs_match = re.search(pattern, block, re.DOTALL)
                    if abs_match:
                        abstract = re.sub(r'<[^>]+>', '', abs_match.group(1)).strip()
                        break
                
                if title:
                    results.append({
                        'title': title,
                        'link': link,
                        'abstract': abstract[:200] + '...' if len(abstract) > 200 else abstract
                    })
            except Exception:
                continue
        
        # 如果没有找到结果，尝试直接匹配所有标题和链接
        if not results:
            # 提取所有h3标签中的链接和标题
            h3_pattern = r'<h3[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?</h3>'
            matches = re.findall(h3_pattern, html, re.DOTALL)
            
            for link, title_html in matches[:num]:
                title = re.sub(r'<[^>]+>', '', title_html).strip()
                if title and link:
                    results.append({
                        'title': title,
                        'link': link,
                        'abstract': ''
                    })
        
        return {
            'query': query,
            'total': len(results),
            'results': results
        }
        
    except Exception as e:
        print(f"搜索出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    if len(sys.argv) < 2:
        print("使用方法: python baidu_search.py <搜索词> [结果数量]")
        print("示例: python baidu_search.py 'Python教程' 10")
        sys.exit(1)
    
    query = sys.argv[1]
    num = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    print(f"🔍 百度搜索: {query}\n")
    
    result = baidu_search(query, num)
    
    if result and result['results']:
        for i, item in enumerate(result['results'], 1):
            print(f"{i}. {item['title']}")
            print(f"   链接: {item['link']}")
            if item['abstract']:
                print(f"   摘要: {item['abstract']}")
            print()
    else:
        print("未找到搜索结果")

if __name__ == '__main__':
    main()
