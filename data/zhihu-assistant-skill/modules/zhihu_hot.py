"""
知乎热榜抓取模块

功能：
- 抓取知乎热榜前 N 条问题
- 解析问题标题、链接、热度等信息
- 支持测试模式（无 Cookie 时使用模拟数据）

使用方法：
    from zhihu_hot import ZhihuHotFetcher
    
    fetcher = ZhihuHotFetcher(cookie='your_cookie')
    hot_list = fetcher.fetch_hot_list(limit=10)
    
    for question in hot_list:
        print(f"[{question['heat']}万] {question['title']}")
"""
import requests
import json
import re
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# 测试数据 - 用于未配置 Cookie 时的演示
TEST_HOT_LIST = [
    {
        "id": "1234567890",
        "title": "为什么现在的年轻人都不爱结婚了？",
        "url": "https://www.zhihu.com/question/1234567890",
        "heat": 1250.5,
        "heat_text": "1250万",
        "excerpt": "最近发现身边很多90后、00后都没有结婚打算...",
        "fetched_at": datetime.now().isoformat()
    },
    {
        "id": "1234567891",
        "title": "如何看待2024年人工智能的爆发式发展？",
        "url": "https://www.zhihu.com/question/1234567891",
        "heat": 980.2,
        "heat_text": "980万",
        "excerpt": "从ChatGPT到各种AI工具，人工智能似乎在一夜之间改变了我们的生活...",
        "fetched_at": datetime.now().isoformat()
    },
    {
        "id": "1234567892",
        "title": "长期熬夜对身体有哪些不可逆的伤害？",
        "url": "https://www.zhihu.com/question/1234567892",
        "heat": 756.8,
        "heat_text": "756万",
        "excerpt": "作为一个经常熬夜的程序员，想知道长期熬夜到底会对身体造成什么影响...",
        "fetched_at": datetime.now().isoformat()
    }
]


class ZhihuHotFetcher:
    """
    知乎热榜抓取器
    
    Attributes:
        cookie: 知乎登录 Cookie
        user_agent: 请求 User-Agent
        test_mode: 是否为测试模式（无有效 Cookie 时使用模拟数据）
        session: requests.Session 对象
    """
    
    def __init__(self, cookie: str = None, user_agent: str = None, test_mode: bool = False):
        """
        初始化抓取器
        
        Args:
            cookie: 知乎 Cookie 字符串
            user_agent: 请求 User-Agent，默认使用 Chrome
        """
        self.cookie = cookie or ''
        self.user_agent = user_agent or 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        # 如果没有 Cookie 或 Cookie 是占位符，使用测试模式
        self.test_mode = test_mode or (not cookie or cookie == 'your_zhihu_cookie_here')
        self.session = requests.Session()
        self._setup_headers()
        
    def _setup_headers(self):
        """设置 HTTP 请求头"""
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.zhihu.com/hot',
            'X-Requested-With': 'fetch'
        }
        # 只在非测试模式时添加 Cookie
        if self.cookie and not self.test_mode:
            headers['Cookie'] = self.cookie
        self.session.headers.update(headers)
    
    def fetch_hot_list(self, limit: int = 10) -> List[Dict]:
        """
        抓取知乎热榜
        
        Args:
            limit: 返回前 N 条热榜
            
        Returns:
            热榜问题列表，每项包含：
            - id: 问题ID
            - title: 问题标题
            - url: 问题链接
            - heat: 热度值（万）
            - excerpt: 问题摘要
            - fetched_at: 抓取时间
        """
        # 测试模式：返回模拟数据
        if self.test_mode:
            logger.info("使用测试模式（未配置知乎Cookie）")
            return TEST_HOT_LIST[:limit]
        
        try:
            url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
            params = {
                'limit': 50,  # 多取一些用于过滤
                'desktop': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            questions = []
            
            for item in data.get('data', [])[:limit]:
                target = item.get('target', {})
                question = self._parse_question(item, target)
                if question:
                    questions.append(question)
            
            logger.info(f"成功抓取 {len(questions)} 条热榜问题")
            return questions
            
        except requests.RequestException as e:
            logger.error(f"抓取热榜失败: {e}")
            # 真实抓取失败时，降级到测试数据
            logger.info("使用测试数据作为降级")
            return TEST_HOT_LIST[:limit]
        except json.JSONDecodeError as e:
            logger.error(f"解析JSON失败: {e}")
            return TEST_HOT_LIST[:limit]
    
    def _parse_question(self, item: Dict, target: Dict) -> Optional[Dict]:
        """
        解析单条热榜数据
        
        Args:
            item: API 返回的原始数据项
            target: 目标对象数据
            
        Returns:
            解析后的问题字典，解析失败返回 None
        """
        try:
            # 提取问题ID
            question_id = target.get('id') or target.get('question', {}).get('id')
            if not question_id:
                return None
            
            # 提取热度
            heat_text = item.get('detail_text', '0')
            heat = self._parse_heat(heat_text)
            
            # 提取标题
            title = target.get('title') or target.get('question', {}).get('title', '')
            
            # 提取摘要
            excerpt = target.get('excerpt', '')
            
            return {
                'id': str(question_id),
                'title': title,
                'url': f"https://www.zhihu.com/question/{question_id}",
                'heat': heat,
                'heat_text': heat_text,
                'excerpt': excerpt,
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"解析问题数据失败: {e}")
            return None
    
    def _parse_heat(self, heat_text: str) -> float:
        """
        解析热度值，统一转换为万为单位
        
        Args:
            heat_text: 热度文本，如 "1250万" 或 "12500000"
            
        Returns:
            热度值（万）
        """
        try:
            heat_text = heat_text.strip()
            
            # 匹配 "1234 万热度" 或 "1234万"
            if '万' in heat_text:
                match = re.search(r'(\d+\.?\d*)', heat_text)
                if match:
                    return float(match.group(1))
            
            # 匹配纯数字
            match = re.search(r'(\d+)', heat_text)
            if match:
                num = int(match.group(1))
                # 如果数字很大，转换为万
                if num > 10000:
                    return round(num / 10000, 1)
                return num
                
            return 0.0
            
        except Exception:
            return 0.0


if __name__ == '__main__':
    # 测试代码
    fetcher = ZhihuHotFetcher(cookie='', user_agent='Test')
    hot_list = fetcher.fetch_hot_list(limit=3)
    for q in hot_list:
        print(f"[{q['heat']}万] {q['title']}")
        print(f"   {q['url']}")
        print()
