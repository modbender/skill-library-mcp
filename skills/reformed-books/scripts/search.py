#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改革宗书籍乐园搜索脚本 (Reformed Books Search)
搜索 http://www.https.ng:1234 上的基督教神学书籍
"""

import argparse
import io
import json
import re
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import List, Dict, Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SEARCH_URL = "http://www.https.ng:1234"
BROWSE_URL = "http://www.https.ng"

class SearchResultParser(HTMLParser):
    """解析搜索结果页面"""
    def __init__(self):
        super().__init__()
        self.results: List[Dict] = []
        self.in_result_row = False
        self.in_link = False
        self.current_result: Dict = {}
        self.current_data = ""
        self.cell_index = 0
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'tr' and 'class' in attrs_dict:
            self.in_result_row = True
            self.current_result = {}
            self.cell_index = 0
        elif tag == 'a' and self.in_result_row:
            self.in_link = True
            href = attrs_dict.get('href', '')
            if href and not href.startswith('#'):
                self.current_result['url'] = href
                
    def handle_endtag(self, tag):
        if tag == 'tr' and self.in_result_row:
            if self.current_result.get('name'):
                self.results.append(self.current_result)
            self.in_result_row = False
        elif tag == 'td' and self.in_result_row:
            data = self.current_data.strip()
            if self.cell_index == 0 and data:
                self.current_result['name'] = data
            elif self.cell_index == 1:
                self.current_result['path'] = data
            elif self.cell_index == 2:
                self.current_result['size'] = data
            elif self.cell_index == 3:
                self.current_result['date'] = data
            self.cell_index += 1
            self.current_data = ""
        elif tag == 'a':
            self.in_link = False
            
    def handle_data(self, data):
        if self.in_result_row:
            self.current_data += data


def search_books(keywords: str, format_filter: Optional[str] = None, limit: int = 20) -> List[Dict]:
    """
    搜索书籍
    
    Args:
        keywords: 搜索关键词，空格分隔
        format_filter: 文件格式过滤 (pdf, epub, mobi, doc, txt)
        limit: 返回结果数量限制
    
    Returns:
        搜索结果列表
    """
    # 添加格式到关键词
    search_query = keywords
    if format_filter and format_filter.lower() not in keywords.lower():
        search_query = f"{keywords} {format_filter}"
    
    # 构建搜索信息
    results = []
    
    # 由于该网站使用 JavaScript 前端搜索，无法直接通过 HTTP 请求获取结果
    # 返回搜索指导信息
    print(f"\n📚 改革宗书籍乐园搜索")
    print(f"{'='*50}")
    print(f"\n🔍 搜索关键词: {search_query}")
    print(f"\n📌 请在浏览器中打开以下链接进行搜索:")
    print(f"\n   {SEARCH_URL}")
    print(f"\n💡 搜索步骤:")
    print(f"   1. 在搜索框输入: {search_query}")
    print(f"   2. 点击 '🔍 搜索' 按钮")
    print(f"   3. 点击文件名即可下载")
    
    if format_filter:
        print(f"\n📁 已添加格式过滤: {format_filter}")
        print(f"   或使用下拉菜单选择 '{format_filter}' 格式")
    
    print(f"\n🔗 其他有用链接:")
    print(f"   • 高级搜索: http://www.https.ng:5757")
    print(f"   • 资源导航: http://www.https.ng:1234/0.html")
    print(f"   • 在线浏览: {BROWSE_URL}")
    
    # 尝试通过简单请求获取一些信息
    try:
        # 尝试访问主站获取基本信息
        req = urllib.request.Request(
            BROWSE_URL,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                print(f"\n✅ 网站可访问")
    except Exception as e:
        print(f"\n⚠️  网站可能暂时无法访问，请稍后重试")
        print(f"   错误: {e}")
    
    print(f"\n{'='*50}")
    
    return results


def format_results(results: List[Dict], prefer_pdf: bool = True) -> str:
    """
    格式化搜索结果
    
    Args:
        results: 搜索结果列表
        prefer_pdf: 是否优先显示 PDF
    
    Returns:
        格式化的结果字符串
    """
    if not results:
        return "未找到结果"
    
    # PDF 优先排序
    if prefer_pdf:
        results.sort(key=lambda x: (
            0 if x.get('name', '').lower().endswith('.pdf') else 1,
            x.get('name', '')
        ))
    
    output = []
    for i, r in enumerate(results, 1):
        name = r.get('name', '未知')
        url = r.get('url', '')
        size = r.get('size', '')
        date = r.get('date', '')
        
        output.append(f"{i}. {name}")
        if size:
            output.append(f"   大小: {size}")
        if date:
            output.append(f"   日期: {date}")
        if url:
            output.append(f"   下载: {url}")
        output.append("")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description='搜索改革宗书籍乐园 (https.ng)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s "系统神学"
  %(prog)s "加尔文 要义" --format pdf
  %(prog)s "威斯敏斯特 信条"
  %(prog)s "清教徒" --format epub
        """
    )
    parser.add_argument('keywords', help='搜索关键词，用空格分隔')
    parser.add_argument('--format', '-f', dest='format_filter',
                        choices=['pdf', 'epub', 'mobi', 'doc', 'txt', 'azw3', 'ppt'],
                        help='文件格式过滤')
    parser.add_argument('--limit', '-l', type=int, default=20,
                        help='结果数量限制 (默认: 20)')
    parser.add_argument('--json', '-j', action='store_true',
                        help='以 JSON 格式输出')
    
    args = parser.parse_args()
    
    # 执行搜索
    results = search_books(
        args.keywords,
        format_filter=args.format_filter,
        limit=args.limit
    )
    
    if args.json:
        print(json.dumps({
            'keywords': args.keywords,
            'format': args.format_filter,
            'search_url': SEARCH_URL,
            'results': results
        }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
