#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多数据源监控
整合 GitHub、抖音、B站、小红书、Twitter
"""

import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional


class MultiSourceMonitor:
    """多数据源监控器"""
    
    def __init__(self):
        self.sources = ['github', 'douyin', 'bilibili', 'xiaohongshu', 'twitter']
    
    def get_all_hot(self) -> Dict[str, List[Dict]]:
        """
        获取所有平台热点
        
        Returns:
            各平台热点数据
        """
        results = {}
        
        # GitHub 热门
        results['github'] = self._get_github_trending()
        
        # 抖音热门
        results['douyin'] = self._get_douyin_hot()
        
        # B站热门
        results['bilibili'] = self._get_bilibili_hot()
        
        # 小红书热门
        results['xiaohongshu'] = self._get_xiaohongshu_hot()
        
        # Twitter AI trending
        results['twitter'] = self._get_twitter_ai()
        
        return results
    
    def _get_github_trending(self) -> List[Dict]:
        """获取 GitHub Trending AI 项目"""
        from github_monitor import GitHubMonitor
        monitor = GitHubMonitor()
        projects = monitor.search_ai_projects(days=7, min_stars=50)
        
        results = []
        for p in projects[:10]:
            results.append({
                'source': 'github',
                'title': p.get('name', ''),
                'description': p.get('description', ''),
                'url': p.get('url', ''),
                'metrics': {
                    'stars': p.get('stars', 0),
                },
                'tags': ['AI', 'GitHub'],
            })
        
        return results
    
    def _get_douyin_hot(self) -> List[Dict]:
        """获取抖音热门"""
        results = []
        
        try:
            # 使用 bird CLI 获取抖音数据
            # 热门话题：AI、赚钱、副业、创业
            topics = ['AI赚钱', '副业', '创业', 'AI工具']
            
            for topic in topics:
                try:
                    # 这里可以调用抖音 MCP 或其他方式
                    # 暂时返回示例数据
                    results.append({
                        'source': 'douyin',
                        'title': f'{topic}相关热门视频',
                        'description': f'抖音{topic}话题热门内容',
                        'url': f'https://www.douyin.com/search/{topic}',
                        'metrics': {},
                        'tags': [topic, '抖音'],
                    })
                except Exception as e:
                    print(f"抖音数据获取失败: {e}")
        
        except Exception as e:
            print(f"抖音数据获取失败: {e}")
        
        return results[:5]
    
    def _get_bilibili_hot(self) -> List[Dict]:
        """获取 B站热门"""
        results = []
        
        try:
            # B站科技区热门
            import requests
            
            url = 'https://api.bilibili.com/x/web-interface/ranking/v2'
            params = {'rid': 36, 'type': 'all'}  # 36 = 科技区
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.bilibili.com/',
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('data', {}).get('list', [])[:10]:
                    results.append({
                        'source': 'bilibili',
                        'title': item.get('title', ''),
                        'description': item.get('desc', '')[:100],
                        'url': f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                        'metrics': {
                            'play': item.get('stat', {}).get('view', 0),
                            'like': item.get('stat', {}).get('like', 0),
                        },
                        'tags': ['B站', '科技'],
                    })
        except Exception as e:
            print(f"B站数据获取失败: {e}")
        
        return results
    
    def _get_xiaohongshu_hot(self) -> List[Dict]:
        """获取小红书热门"""
        results = []
        
        # 小红书 API 需要登录，暂时使用搜索方式
        topics = ['AI赚钱', '副业', '创业', '自媒体']
        
        for topic in topics:
            results.append({
                'source': 'xiaohongshu',
                'title': f'{topic}相关热门笔记',
                'description': f'小红书{topic}话题热门内容',
                'url': f'https://www.xiaohongshu.com/search_result?keyword={topic}',
                'metrics': {},
                'tags': [topic, '小红书'],
            })
        
        return results[:5]
    
    def _get_twitter_ai(self) -> List[Dict]:
        """获取 Twitter AI trending"""
        results = []
        
        try:
            # 使用 bird CLI 搜索
            result = subprocess.run(
                ['bird', 'search', 'AI trending', '--limit', '10'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # 解析 bird 输出
                lines = result.stdout.strip().split('\n')
                for line in lines[:10]:
                    if line.strip():
                        results.append({
                            'source': 'twitter',
                            'title': line[:100],
                            'description': line,
                            'url': 'https://twitter.com/search?q=AI',
                            'metrics': {},
                            'tags': ['AI', 'Twitter'],
                        })
        except Exception as e:
            print(f"Twitter 数据获取失败: {e}")
        
        # 备用数据
        if not results:
            results.append({
                'source': 'twitter',
                'title': 'AI trending on Twitter',
                'description': 'Twitter AI trending 搜索',
                'url': 'https://twitter.com/search?q=AI%20trending',
                'metrics': {},
                'tags': ['AI', 'Twitter'],
            })
        
        return results
    
    def filter_ai_related(self, items: List[Dict]) -> List[Dict]:
        """筛选 AI 相关内容"""
        ai_keywords = [
            'ai', 'artificial intelligence', '人工智能',
            'llm', 'gpt', 'chatgpt', 'claude',
            'agent', '智能体', '自动化',
            'machine learning', 'deep learning',
            'nlp', 'computer vision',
        ]
        
        filtered = []
        for item in items:
            text = f"{item.get('title', '')} {item.get('description', '')}".lower()
            if any(k in text for k in ai_keywords):
                filtered.append(item)
        
        return filtered
    
    def generate_ideas_from_hot(self, hot_data: Dict) -> List[Dict]:
        """从热点数据生成赚钱灵感"""
        ideas = []
        
        for source, items in hot_data.items():
            for item in items:
                # 简单判断是否有变现潜力
                potential = self._analyze_potential(item)
                if potential > 0:
                    ideas.append({
                        'source': source,
                        'title': item.get('title', ''),
                        'description': item.get('description', ''),
                        'url': item.get('url', ''),
                        'potential': potential,
                        'tags': item.get('tags', []),
                    })
        
        # 按潜力排序
        ideas.sort(key=lambda x: x['potential'], reverse=True)
        
        return ideas[:10]
    
    def _analyze_potential(self, item: Dict) -> int:
        """分析变现潜力（0-100）"""
        score = 0
        
        title = item.get('title', '').lower()
        desc = item.get('description', '').lower()
        text = f"{title} {desc}"
        
        # 关键词加分
        money_keywords = ['赚钱', '副业', '创业', '变现', '商业化', '盈利']
        for k in money_keywords:
            if k in text:
                score += 20
        
        ai_keywords = ['ai', '人工智能', 'gpt', 'agent', '自动化']
        for k in ai_keywords:
            if k in text:
                score += 15
        
        tool_keywords = ['工具', '平台', '系统', '软件', 'app']
        for k in tool_keywords:
            if k in text:
                score += 10
        
        # 数据源加分
        source = item.get('source', '')
        if source == 'github':
            score += 15  # GitHub 项目更容易变现
        elif source == 'bilibili':
            score += 10  # B站科技区有参考价值
        
        return min(score, 100)


# 测试
if __name__ == '__main__':
    monitor = MultiSourceMonitor()
    
    print("=== 获取多平台热点 ===\n")
    hot_data = monitor.get_all_hot()
    
    for source, items in hot_data.items():
        print(f"【{source.upper()}】")
        for i, item in enumerate(items[:3], 1):
            print(f"  {i}. {item['title'][:50]}")
        print()
    
    print("=== 生成赚钱灵感 ===\n")
    ideas = monitor.generate_ideas_from_hot(hot_data)
    for i, idea in enumerate(ideas[:5], 1):
        print(f"【灵感 #{i}】{idea['title'][:40]}")
        print(f"  来源: {idea['source']} | 潜力: {idea['potential']}")
        print()