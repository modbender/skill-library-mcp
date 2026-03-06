#!/usr/bin/env python3
"""
AI新闻获取脚本 - 使用Tavily API或Brave API搜索最新AI资讯
支持仅RSS模式（无需API Key）
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta


def get_api_key(service="tavily"):
    """
    获取API Key - 可选，不是必须的
    
    Args:
        service: "tavily" 或 "brave"
    
    Returns:
        str or None: API Key或None
    """
    if service == "tavily":
        return os.environ.get('TAVILY_API_KEY')
    elif service == "brave":
        return os.environ.get('BRAVE_API_KEY')
    return None


def search_ai_news_tavily(api_key, days=3, limit=10, query="AI artificial intelligence"):
    """
    使用Tavily搜索AI新闻
    
    Args:
        api_key: Tavily API Key
        days: 搜索最近N天的新闻
        limit: 返回新闻数量
        query: 搜索关键词
    
    Returns:
        list: 新闻列表
    """
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
    except ImportError:
        print("错误: 请安装tavily-python: pip install tavily-python", file=sys.stderr)
        return []
    
    # 计算日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 搜索查询
    search_query = f"{query} {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    
    # 执行搜索
    try:
        response = client.search(
            query=search_query,
            search_depth="advanced",
            include_answer=False,
            max_results=limit * 2,
            topic="news"
        )
    except Exception as e:
        print(f"Tavily搜索失败: {e}", file=sys.stderr)
        return []
    
    # 处理结果
    news_list = []
    for result in response.get('results', []):
        news_item = {
            'title': result.get('title', ''),
            'url': result.get('url', ''),
            'content': result.get('content', ''),
            'published_date': result.get('published_date', ''),
            'source': result.get('source', 'Tavily'),
            'source_type': 'tavily'
        }
        news_list.append(news_item)
        
        if len(news_list) >= limit:
            break
    
    return news_list


def search_ai_news_brave(api_key, days=3, limit=10, query="AI artificial intelligence"):
    """
    使用Brave Search API搜索AI新闻
    
    Args:
        api_key: Brave API Key
        days: 搜索最近N天的新闻
        limit: 返回新闻数量
        query: 搜索关键词
    
    Returns:
        list: 新闻列表
    """
    import requests
    
    # 计算日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 添加时间范围到查询
    search_query = f"{query} after:{start_date.strftime('%Y-%m-%d')} before:{end_date.strftime('%Y-%m-%d')}"
    
    headers = {
        "X-Subscription-Token": api_key,
        "Accept": "application/json"
    }
    
    params = {
        "q": search_query,
        "count": min(limit * 2, 20),  # Brave限制
        "search_lang": "en",
        "freshness": f"{days}d"  # 最近N天
    }
    
    try:
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers=headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        news_list = []
        for result in data.get("web", {}).get("results", []):
            news_item = {
                'title': result.get('title', ''),
                'url': result.get('url', ''),
                'content': result.get('description', ''),
                'published_date': result.get('age', ''),  # Brave返回的是相对时间
                'source': result.get('meta', {}).get('domain', 'Brave'),
                'source_type': 'brave'
            }
            news_list.append(news_item)
            
            if len(news_list) >= limit:
                break
        
        return news_list
        
    except Exception as e:
        print(f"Brave搜索失败: {e}", file=sys.stderr)
        return []


def format_news_output(news_list, output_format='json'):
    """
    格式化新闻输出
    
    Args:
        news_list: 新闻列表
        output_format: 输出格式 (json, text, markdown)
    """
    if output_format == 'json':
        print(json.dumps(news_list, ensure_ascii=False, indent=2))
    elif output_format == 'text':
        for i, news in enumerate(news_list, 1):
            print(f"\n[{i}] {news['title']}")
            print(f"    来源: {news['source']}")
            print(f"    链接: {news['url']}")
            if news.get('published_date'):
                print(f"    日期: {news['published_date']}")
            print(f"    摘要: {news['content'][:200]}...")
    elif output_format == 'markdown':
        print("# AI新闻资讯\n")
        for i, news in enumerate(news_list, 1):
            print(f"## {i}. {news['title']}\n")
            print(f"- **来源**: {news['source']}")
            print(f"- **链接**: [{news['url']}]({news['url']})")
            if news.get('published_date'):
                print(f"- **日期**: {news['published_date']}")
            print(f"\n{news['content']}\n")
            print("---\n")


def main():
    parser = argparse.ArgumentParser(
        description='AI新闻获取工具 - 支持Tavily、Brave、RSS多源',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  # 使用Tavily API（需要TAVILY_API_KEY）
  python3 fetch_ai_news.py --source tavily --limit 10
  
  # 使用Brave API（需要BRAVE_API_KEY）
  python3 fetch_ai_news.py --source brave --limit 10
  
  # 仅使用RSS源（无需API Key）
  python3 fetch_ai_news.py --source rss --limit 10
  
  # 多源聚合（Tavily + Brave + RSS）
  python3 fetch_ai_news.py --source all --limit 10
        '''
    )
    
    parser.add_argument('--limit', type=int, default=10, help='返回新闻数量 (默认10)')
    parser.add_argument('--days', type=int, default=3, help='搜索最近N天的新闻 (默认3)')
    parser.add_argument('--source', choices=['tavily', 'brave', 'rss', 'all'], default='all',
                        help='新闻源选择 (默认all，聚合所有可用源)')
    parser.add_argument('--format', choices=['json', 'text', 'markdown'], default='json',
                        help='输出格式 (默认json)')
    parser.add_argument('--output', type=str, help='输出到文件')
    parser.add_argument('--query', type=str, default='AI artificial intelligence',
                        help='搜索关键词 (默认: AI artificial intelligence)')
    
    args = parser.parse_args()
    
    news_list = []
    
    # 根据source参数选择新闻源
    if args.source in ['tavily', 'all']:
        api_key = get_api_key('tavily')
        if api_key:
            print("正在从 Tavily 获取新闻...")
            tavily_news = search_ai_news_tavily(api_key, days=args.days, limit=args.limit, query=args.query)
            news_list.extend(tavily_news)
            print(f"  Tavily: 获取了 {len(tavily_news)} 条新闻")
        else:
            if args.source == 'tavily':
                print("错误: 未设置 TAVILY_API_KEY 环境变量", file=sys.stderr)
                sys.exit(1)
            else:
                print("  Tavily: 跳过 (未设置 TAVILY_API_KEY)")
    
    if args.source in ['brave', 'all']:
        api_key = get_api_key('brave')
        if api_key:
            print("正在从 Brave 获取新闻...")
            brave_news = search_ai_news_brave(api_key, days=args.days, limit=args.limit, query=args.query)
            news_list.extend(brave_news)
            print(f"  Brave: 获取了 {len(brave_news)} 条新闻")
        else:
            if args.source == 'brave':
                print("错误: 未设置 BRAVE_API_KEY 环境变量", file=sys.stderr)
                sys.exit(1)
            else:
                print("  Brave: 跳过 (未设置 BRAVE_API_KEY)")
    
    if args.source in ['rss', 'all']:
        print("正在从 RSS 源获取新闻...")
        try:
            from news_sources import RSSSource
            rss_source = RSSSource()
            rss_news = rss_source.fetch(query=args.query, limit=args.limit, days=args.days)
            news_list.extend(rss_news)
            print(f"  RSS: 获取了 {len(rss_news)} 条新闻")
        except Exception as e:
            print(f"  RSS: 获取失败 - {e}", file=sys.stderr)
    
    if not news_list:
        print("错误: 未能从任何源获取新闻", file=sys.stderr)
        sys.exit(1)
    
    # 去重
    seen_urls = set()
    unique_news = []
    for news in news_list:
        url = news.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_news.append(news)
    
    # 按日期排序
    def parse_date(news):
        date_str = news.get('published_date', '')
        if date_str:
            try:
                from datetime import datetime
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                pass
        from datetime import datetime
        return datetime.min
    
    unique_news.sort(key=parse_date, reverse=True)
    
    print(f"\n总共获取 {len(unique_news)} 条不重复新闻")
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            if args.format == 'json':
                json.dump(unique_news, f, ensure_ascii=False, indent=2)
            else:
                import io
                from contextlib import redirect_stdout
                
                output_buffer = io.StringIO()
                with redirect_stdout(output_buffer):
                    format_news_output(unique_news, args.format)
                f.write(output_buffer.getvalue())
        print(f"结果已保存到: {args.output}")
    else:
        format_news_output(unique_news, args.format)


if __name__ == '__main__':
    main()
