#!/usr/bin/env python3
"""
多新闻源聚合模块 - 支持Tavily、Brave、RSS等多种新闻源
"""

import os
import sys
import json
import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class NewsSource:
    """新闻源基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    def fetch(self, query: str = "AI artificial intelligence", limit: int = 10, days: int = 3) -> List[Dict]:
        """获取新闻，子类需实现"""
        raise NotImplementedError


class TavilySource(NewsSource):
    """Tavily API新闻源 - 可选，如果没有API Key则跳过"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Tavily")
        self.api_key = api_key or os.environ.get('TAVILY_API_KEY')
        if not self.api_key:
            print("提示: Tavily API Key未设置，将跳过Tavily源 (RSS源仍可用)", file=sys.stderr)
            raise ValueError("Tavily API Key未设置")
        
        try:
            from tavily import TavilyClient
            self.client = TavilyClient(api_key=self.api_key)
        except ImportError:
            raise ImportError("请安装tavily-python: pip install tavily-python")
    
    def fetch(self, query: str = "AI artificial intelligence", limit: int = 10, days: int = 3) -> List[Dict]:
        """使用Tavily搜索新闻"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        search_query = f"{query} {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        try:
            response = self.client.search(
                query=search_query,
                search_depth="advanced",
                include_answer=False,
                max_results=limit * 2,
                topic="news"
            )
        except Exception as e:
            print(f"Tavily搜索失败: {e}", file=sys.stderr)
            return []
        
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


class BraveSource(NewsSource):
    """Brave Search API新闻源 - 可选"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Brave")
        self.api_key = api_key or os.environ.get('BRAVE_API_KEY')
        if not self.api_key:
            print("提示: Brave API Key未设置，将跳过Brave源 (RSS源仍可用)", file=sys.stderr)
            raise ValueError("Brave API Key未设置")
    
    def fetch(self, query: str = "AI artificial intelligence", limit: int = 10, days: int = 3) -> List[Dict]:
        """使用Brave Search搜索新闻"""
        headers = {
            "X-Subscription-Token": self.api_key,
            "Accept": "application/json"
        }
        
        params = {
            "q": query,
            "count": min(limit * 2, 20),
            "search_lang": "en",
            "freshness": f"{days}d"
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
                    'published_date': result.get('age', ''),
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


class RSSSource(NewsSource):
    """RSS订阅源 - 无需API Key，始终可用"""
    
    # 预定义的AI相关RSS源
    DEFAULT_FEEDS = {
        'techcrunch_ai': 'https://techcrunch.com/category/artificial-intelligence/feed/',
        'mit_tech_review': 'https://www.technologyreview.com/topic/artificial-intelligence/feed/',
        'wired_ai': 'https://www.wired.com/tag/artificial-intelligence/feed/',
    }
    
    def __init__(self, feeds: Optional[Dict[str, str]] = None):
        super().__init__("RSS")
        self.feeds = feeds or self.DEFAULT_FEEDS.copy()
    
    def add_feed(self, name: str, url: str):
        """添加RSS源"""
        self.feeds[name] = url
    
    def fetch(self, query: str = "", limit: int = 10, days: int = 3) -> List[Dict]:
        """获取RSS新闻"""
        news_list = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for feed_name, feed_url in self.feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    # 解析发布日期
                    published = None
                    if hasattr(entry, 'published_parsed'):
                        published = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed'):
                        published = datetime(*entry.updated_parsed[:6])
                    
                    # 过滤日期
                    if published and published < cutoff_date:
                        continue
                    
                    # 如果有查询词，进行过滤
                    if query:
                        query_lower = query.lower()
                        title_match = query_lower in entry.title.lower()
                        summary = entry.get('summary', '')
                        summary_match = query_lower in summary.lower()
                        if not (title_match or summary_match):
                            continue
                    
                    news_item = {
                        'title': entry.title,
                        'url': entry.link,
                        'content': entry.get('summary', '')[:300],
                        'published_date': published.isoformat() if published else '',
                        'source': feed_name,
                        'source_type': 'rss'
                    }
                    news_list.append(news_item)
                    
                    if len(news_list) >= limit:
                        return news_list
                        
            except Exception as e:
                print(f"RSS源 {feed_name} 获取失败: {e}", file=sys.stderr)
                continue
        
        return news_list


class NewsAggregator:
    """新闻聚合器 - 整合多个新闻源"""
    
    def __init__(self):
        self.sources: Dict[str, NewsSource] = {}
    
    def add_source(self, source: NewsSource):
        """添加新闻源"""
        self.sources[source.name] = source
    
    def fetch_all(self, query: str = "AI artificial intelligence", limit: int = 10, days: int = 3) -> List[Dict]:
        """
        从所有源获取新闻并合并
        
        Args:
            query: 搜索关键词
            limit: 每个源获取的数量
            days: 最近N天的新闻
        
        Returns:
            合并后的新闻列表（按时间排序）
        """
        all_news = []
        
        for name, source in self.sources.items():
            try:
                print(f"正在从 {name} 获取新闻...")
                news = source.fetch(query=query, limit=limit, days=days)
                all_news.extend(news)
                print(f"  从 {name} 获取了 {len(news)} 条新闻")
            except Exception as e:
                print(f"从 {name} 获取新闻失败: {e}", file=sys.stderr)
        
        # 去重（基于URL）
        seen_urls = set()
        unique_news = []
        for news in all_news:
            url = news.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_news.append(news)
        
        # 按日期排序（最新的在前）
        def parse_date(news):
            date_str = news.get('published_date', '')
            if date_str:
                try:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    pass
            return datetime.min
        
        unique_news.sort(key=parse_date, reverse=True)
        
        return unique_news


def get_default_aggregator(include_tavily=True, include_brave=True, include_rss=True) -> NewsAggregator:
    """
    获取默认配置的新闻聚合器
    
    Args:
        include_tavily: 是否包含Tavily源（需要TAVILY_API_KEY）
        include_brave: 是否包含Brave源（需要BRAVE_API_KEY）
        include_rss: 是否包含RSS源（无需API Key）
    """
    aggregator = NewsAggregator()
    
    # 添加Tavily源（可选）
    if include_tavily:
        try:
            tavily_source = TavilySource()
            aggregator.add_source(tavily_source)
        except ValueError:
            print("提示: Tavily API Key未设置，跳过Tavily源")
    
    # 添加Brave源（可选）
    if include_brave:
        try:
            brave_source = BraveSource()
            aggregator.add_source(brave_source)
        except ValueError:
            print("提示: Brave API Key未设置，跳过Brave源")
    
    # 添加RSS源（始终添加，无需API Key）
    if include_rss:
        rss_source = RSSSource()
        aggregator.add_source(rss_source)
    
    return aggregator


if __name__ == '__main__':
    # 测试代码
    aggregator = get_default_aggregator()
    news = aggregator.fetch_all(query="AI artificial intelligence", limit=5, days=3)
    print(f"\n总共获取 {len(news)} 条不重复新闻")
    for i, n in enumerate(news[:5], 1):
        print(f"{i}. [{n['source']}] {n['title'][:60]}...")