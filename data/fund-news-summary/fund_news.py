#!/usr/bin/env python3
"""
基金新闻摘要生成器 - 多市场版本
支持：纳斯达克100、标普500、欧洲股市、日经225、黄金/贵金属
使用 QVeris API 和 web_search 获取新闻，生成中文摘要报告
"""

import asyncio
import json
import os
import sys
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# 添加 qveris skill 到路径
QVERIS_PATH = os.path.join(os.path.dirname(__file__), "../qveris")
sys.path.insert(0, QVERIS_PATH)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 市场配置
MARKETS = {
    "us": {
        "name": "美股市场 (纳斯达克/标普500)",
        "emoji": "🇺🇸",
        "symbols": ["QQQ", "SPY", "AAPL", "MSFT", "NVDA", "GOOGL", "META", "AMZN"],
        "keywords": ["NASDAQ", "S&P 500", "tech", "AI", "芯片"],
        "tool": "finnhub.news.retrieve.v1",
        "tool_params": {"category": "general"}
    },
    "europe": {
        "name": "欧洲股市",
        "emoji": "🇪🇺",
        "symbols": ["ASML", "SAP", "MC.PA", "AIR.PA", "NESN.SW"],  # LVMH用MC.PA代替
        "keywords": ["Europe", "ECB", "欧股", "ASML", "SAP", "LVMH"],
        "tool": "yahoo_finance.finance_news.v1",
        "tool_params": {"max_results": 5}
    },
    "japan": {
        "name": "日本股市 (日经225)",
        "emoji": "🇯🇵",
        "symbols": ["TM", "SONY", "NTDOY", "HMC", "6758.T"],  # 6758.T是索尼东京代码
        "keywords": ["Nikkei", "Japan", "日经", "丰田", "索尼", "任天堂"],
        "tool": "yahoo_finance.finance_news.v1",
        "tool_params": {"max_results": 5}
    },
    "gold": {
        "name": "黄金市场",
        "emoji": "🥇",
        "symbols": ["GC=F", "GLD", "XAUUSD"],
        "keywords": ["gold", "XAU", "COMEX", "贵金属", "现货黄金"],
        "tool": "finnhub.news.retrieve.v1",
        "tool_params": {"category": "general"}  # gold新闻在general中
    },
    "polymarket": {
        "name": "Polymarket / 预测市场",
        "emoji": "🔮",
        "keywords": ["Polymarket", "prediction market", "预测市场", "去中心化预测"],
        "tool": "web_search"
    }
}


def safe_parse_json_array(json_str: str) -> List[Dict]:
    """
    安全解析可能被截断的JSON数组
    处理 truncated_content 被截断的情况
    """
    if not json_str or not json_str.strip():
        return []
    
    json_str = json_str.strip()
    
    # 尝试直接解析
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # 如果被截断，尝试修复
    # 找到最后一个完整的对象
    if json_str.startswith('['):
        # 是一个数组，尝试找到最后一个完整的对象
        objects = []
        current_pos = 1  # 跳过开头的 [
        
        while current_pos < len(json_str):
            # 跳过空白和逗号
            while current_pos < len(json_str) and json_str[current_pos] in ' \t\n\r,':
                current_pos += 1
            
            if current_pos >= len(json_str) or json_str[current_pos] == ']':
                break
            
            # 尝试找到下一个完整的对象
            if json_str[current_pos] == '{':
                brace_count = 1
                in_string = False
                escape_next = False
                obj_start = current_pos
                current_pos += 1
                
                while current_pos < len(json_str) and brace_count > 0:
                    char = json_str[current_pos]
                    
                    if escape_next:
                        escape_next = False
                        current_pos += 1
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        current_pos += 1
                        continue
                    
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        current_pos += 1
                        continue
                    
                    if not in_string:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                    
                    current_pos += 1
                
                if brace_count == 0:
                    # 找到了一个完整的对象
                    try:
                        obj = json.loads(json_str[obj_start:current_pos])
                        objects.append(obj)
                    except:
                        pass
            else:
                current_pos += 1
        
        return objects
    
    return []


class QVerisToolRunner:
    """
    通过命令行调用 QVeris 工具
    """
    
    QVERIS_DIR = "/root/clawd/skills/qveris"
    
    async def search_tools(self, query: str, limit: int = 5) -> tuple:
        """
        搜索可用工具，返回 (search_id, tools)
        """
        try:
            cmd = [
                "python3", "scripts/qveris_tool.py", "search", query,
                "--limit", str(limit)
            ]
            result = subprocess.run(
                cmd, cwd=self.QVERIS_DIR,
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"搜索工具失败: {result.stderr}")
                return None, []
            
            # 解析输出
            output = result.stdout
            search_id = None
            tools = []
            
            for line in output.split('\n'):
                if line.startswith("Search ID:"):
                    search_id = line.split(":")[1].strip()
                elif line.startswith("[") and "]" in line:
                    # 解析工具信息
                    tool_id = None
                    tool_name = ""
                    
            logger.info(f"搜索到工具，search_id: {search_id}")
            return search_id, tools
            
        except Exception as e:
            logger.error(f"搜索工具异常: {e}")
            return None, []
    
    async def execute_tool(self, tool_id: str, search_id: str, params: Dict) -> Dict:
        """
        执行指定工具
        """
        try:
            cmd = [
                "python3", "scripts/qveris_tool.py", "execute", tool_id,
                "--search-id", search_id,
                "--params", json.dumps(params)
            ]
            
            result = subprocess.run(
                cmd, cwd=self.QVERIS_DIR,
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"执行工具失败: {result.stderr}")
                return {"success": False, "error": result.stderr}
            
            # 解析输出中的 JSON
            output = result.stdout
            logger.debug(f"工具输出: {output[:500]}...")
            
            # 找到 JSON 开始的位置 (在 "Result:" 之后)
            if "Result:" in output:
                json_start = output.find("Result:") + len("Result:")
                json_str = output[json_start:].strip()
                
                # 尝试找到 JSON 的结束位置（查找第一个闭合括号后的换行）
                try:
                    data = json.loads(json_str)
                    return {"success": True, "data": data}
                except json.JSONDecodeError as je:
                    # 可能是部分 JSON，尝试提取有效部分
                    logger.warning(f"JSON解析失败，尝试提取有效部分: {je}")
                    # 尝试找到第一个完整的 JSON 对象
                    brace_count = 0
                    in_string = False
                    escape_next = False
                    end_pos = 0
                    
                    for i, char in enumerate(json_str):
                        if escape_next:
                            escape_next = False
                            continue
                        if char == '\\':
                            escape_next = True
                            continue
                        if char == '"' and not escape_next:
                            in_string = not in_string
                            continue
                        if not in_string:
                            if char in '{[':
                                brace_count += 1
                            elif char in '}]':
                                brace_count -= 1
                                if brace_count == 0:
                                    end_pos = i + 1
                                    break
                    
                    if end_pos > 0:
                        try:
                            data = json.loads(json_str[:end_pos])
                            return {"success": True, "data": data}
                        except:
                            pass
                    
                    return {"success": True, "raw": output}
            
            return {"success": True, "raw": output}
            
        except Exception as e:
            logger.error(f"执行工具异常: {e}")
            return {"success": False, "error": str(e)}


class MarketNewsFetcher:
    """
    多市场新闻获取器
    """
    
    # 已知可用的工具ID（基于搜索结果）
    FINNHUB_NEWS_TOOL = "finnhub.news.retrieve.v1.51b2567e"
    YAHOO_NEWS_TOOL = "yahoo_finance.finance_news.v1"
    
    def __init__(self):
        self.qveris = QVerisToolRunner()
        self.search_cache = {}  # 缓存搜索结果
    
    async def get_us_news(self) -> List[Dict]:
        """
        获取美股新闻 (纳斯达克/标普500)
        使用 finnhub.news.retrieve.v1
        """
        logger.info("获取美股新闻...")
        try:
            # 搜索工具获取 search_id
            search_id, _ = await self.qveris.search_tools("US stock market news")
            if not search_id:
                logger.warning("无法获取 search_id，使用备用搜索ID")
                search_id = "0c006ed7-e7cb-4939-93aa-a3fb2cf69d7b"
            
            result = await self.qveris.execute_tool(
                self.FINNHUB_NEWS_TOOL,
                search_id,
                {"category": "general"}
            )
            
            if not result.get("success"):
                logger.error(f"获取美股新闻失败: {result.get('error')}")
                return []
            
            data = result.get("data", {})
            
            # 解析新闻数据
            if data.get("status_code") == 200:
                news_list = data.get("data", [])
                if not news_list:
                    # 尝试解析 truncated_content (它是一个JSON字符串)
                    content = data.get("truncated_content", "")
                    if content:
                        news_list = safe_parse_json_array(content)
                        logger.info(f"从 truncated_content 解析到 {len(news_list)} 条新闻")
                else:
                    logger.info(f"从 data 字段获取到 {len(news_list)} 条新闻")
                
                # 确保 news_list 是列表
                if not isinstance(news_list, list):
                    logger.warning(f"news_list 不是列表类型: {type(news_list)}")
                    return []
                
                # 过滤与科技/纳指相关的新闻
                tech_keywords = ["tech", "AI", "artificial", "chip", "semiconductor", 
                                "nvidia", "apple", "microsoft", "google", "meta", "amazon",
                                "半导体", "芯片", "人工智能", "科技", "纳斯达克", "nasdaq",
                                "cisco", "micron", "memory", "data center"]
                
                filtered_news = []
                for news in news_list[:20]:  # 取前20条
                    if not isinstance(news, dict):
                        continue
                    headline = news.get("headline", "").lower()
                    summary = news.get("summary", "").lower()
                    text = headline + " " + summary
                    
                    # 检查是否与科技股相关
                    is_tech = any(kw.lower() in text for kw in tech_keywords)
                    
                    news_item = {
                        "title": news.get("headline", ""),
                        "summary": news.get("summary", ""),
                        "source": news.get("source", "Unknown"),
                        "datetime": news.get("datetime", 0),
                        "url": news.get("url", ""),
                        "is_tech": is_tech
                    }
                    filtered_news.append(news_item)
                
                logger.info(f"美股新闻筛选完成，共 {len(filtered_news)} 条")
                
                # 优先返回科技股相关新闻
                tech_news = [n for n in filtered_news if n["is_tech"]]
                if tech_news:
                    return tech_news[:5]
                return filtered_news[:5]
            else:
                logger.warning(f"API返回非200状态码: {data.get('status_code')}")
            
            return []
            
        except Exception as e:
            logger.error(f"获取美股新闻异常: {e}")
            return []
    
    async def get_europe_news(self) -> List[Dict]:
        """
        获取欧洲股市新闻
        使用 yahoo_finance 获取 ASML, SAP, LVMH 等股票新闻
        """
        logger.info("获取欧洲股市新闻...")
        try:
            # 搜索工具获取 search_id
            search_id, _ = await self.qveris.search_tools("yahoo finance news ASML")
            if not search_id:
                search_id = "a0cdc077-ed28-47a4-88b1-b656ed1b41a6"
            
            all_news = []
            symbols = ["ASML", "SAP"]  # 主要关注 ASML 和 SAP
            
            for symbol in symbols:
                try:
                    result = await self.qveris.execute_tool(
                        self.YAHOO_NEWS_TOOL,
                        search_id,
                        {"symbol": symbol, "max_results": 3}
                    )
                    
                    if result.get("success"):
                        data = result.get("data", {})
                        articles = data.get("data", {}).get("articles", [])
                        
                        for article in articles[:3]:
                            news_item = {
                                "title": article.get("title", ""),
                                "summary": "",  # Yahoo新闻可能没有摘要
                                "source": article.get("publisher", "Yahoo Finance"),
                                "datetime": article.get("pubDate", ""),
                                "url": article.get("link", ""),
                                "symbol": symbol,
                                "is_key_stock": symbol in ["ASML", "SAP"]
                            }
                            all_news.append(news_item)
                            
                except Exception as e:
                    logger.warning(f"获取 {symbol} 新闻失败: {e}")
                    continue
            
            return all_news[:5]
            
        except Exception as e:
            logger.error(f"获取欧洲新闻异常: {e}")
            return []
    
    async def get_japan_news(self) -> List[Dict]:
        """
        获取日本股市新闻
        使用 yahoo_finance 获取丰田、索尼、任天堂等股票新闻
        """
        logger.info("获取日本股市新闻...")
        try:
            search_id, _ = await self.qveris.search_tools("yahoo finance news SONY")
            if not search_id:
                search_id = "a0cdc077-ed28-47a4-88b1-b656ed1b41a6"
            
            all_news = []
            symbols = ["SONY", "NTDOY", "TM"]  # 索尼、任天堂、丰田
            
            for symbol in symbols:
                try:
                    result = await self.qveris.execute_tool(
                        self.YAHOO_NEWS_TOOL,
                        search_id,
                        {"symbol": symbol, "max_results": 3}
                    )
                    
                    if result.get("success"):
                        data = result.get("data", {})
                        articles = data.get("data", {}).get("articles", [])
                        
                        for article in articles[:2]:
                            news_item = {
                                "title": article.get("title", ""),
                                "summary": "",
                                "source": article.get("publisher", "Yahoo Finance"),
                                "datetime": article.get("pubDate", ""),
                                "url": article.get("link", ""),
                                "symbol": symbol
                            }
                            all_news.append(news_item)
                            
                except Exception as e:
                    logger.warning(f"获取 {symbol} 新闻失败: {e}")
                    continue
            
            return all_news[:5]
            
        except Exception as e:
            logger.error(f"获取日本新闻异常: {e}")
            return []
    
    async def get_gold_news(self) -> List[Dict]:
        """
        获取黄金市场新闻
        从 Finnhub general 新闻中筛选黄金相关内容，或搜索
        """
        logger.info("获取黄金市场新闻...")
        try:
            # 尝试从 Finnhub 获取新闻并筛选
            search_id, _ = await self.qveris.search_tools("gold commodity news")
            if not search_id:
                search_id = "0c006ed7-e7cb-4939-93aa-a3fb2cf69d7b"
            
            result = await self.qveris.execute_tool(
                self.FINNHUB_NEWS_TOOL,
                search_id,
                {"category": "general"}
            )
            
            gold_news = []
            
            if result.get("success"):
                data = result.get("data", {})
                
                if data.get("status_code") == 200:
                    news_list = data.get("data", [])
                    if not news_list:
                        content = data.get("truncated_content", "")
                        if content:
                            news_list = safe_parse_json_array(content)
                            logger.info(f"黄金新闻: 从 truncated_content 解析到 {len(news_list)} 条新闻")
                    else:
                        logger.info(f"黄金新闻: 从 data 字段获取到 {len(news_list)} 条新闻")
                    
                    # 确保 news_list 是列表
                    if not isinstance(news_list, list):
                        logger.warning(f"黄金新闻 news_list 不是列表类型: {type(news_list)}")
                        return []
                    
                    # 筛选黄金相关新闻
                    gold_keywords = ["gold", "xau", "precious", "metal", "bullion", 
                                     "黄金", "贵金属", "comex"]
                    
                    for news in news_list:
                        if not isinstance(news, dict):
                            continue
                        headline = news.get("headline", "").lower()
                        summary = news.get("summary", "").lower()
                        text = headline + " " + summary
                        
                        if any(kw.lower() in text for kw in gold_keywords):
                            news_item = {
                                "title": news.get("headline", ""),
                                "summary": news.get("summary", ""),
                                "source": news.get("source", "Unknown"),
                                "datetime": news.get("datetime", 0),
                                "url": news.get("url", "")
                            }
                            gold_news.append(news_item)
                            
                            if len(gold_news) >= 5:
                                break
                    
                    logger.info(f"黄金新闻筛选完成，共 {len(gold_news)} 条")
                else:
                    logger.warning(f"黄金新闻 API返回非200状态码: {data.get('status_code')}")
            
            return gold_news[:5]
            
        except Exception as e:
            logger.error(f"获取黄金新闻异常: {e}")
            return []

    async def get_polymarket_news(self) -> List[Dict]:
        """
        获取 Polymarket / 预测市场相关新闻
        使用 brave_search.web.search.list.v1 工具搜索最新新闻
        """
        logger.info("获取 Polymarket / 预测市场新闻...")
        try:
            # 搜索 brave 工具
            search_id, _ = await self.qveris.search_tools("brave web search")
            if not search_id:
                logger.warning("无法获取搜索ID，使用默认ID")
                search_id = "pm-search-default"
            
            pm_news = []
            brave_tool = "brave_search.web.search.list.v1"
            
            # 搜索1: Polymarket 最新新闻
            try:
                result = await self.qveris.execute_tool(
                    brave_tool,
                    search_id,
                    {"q": "Polymarket news latest today", "count": 5}
                )
                
                if result.get("success"):
                    data = result.get("data", {})
                    results = self._parse_search_results(data)
                    
                    logger.info(f"Polymarket 新闻搜索原始结果数: {len(results)}")
                    
                    for item in results[:5]:
                        if isinstance(item, dict):
                            title = item.get("title", item.get("name", ""))
                            # 过滤掉介绍性/非新闻内容
                            if self._is_news_content(title, item.get("url", "")):
                                desc = item.get("snippet", item.get("description", item.get("content", "")))
                                url = item.get("url", item.get("link", ""))
                                source = self._extract_source(item, url)
                                
                                news_item = {
                                    "title": title,
                                    "summary": desc[:150] if len(desc) > 150 else desc,
                                    "source": source,
                                    "url": url,
                                    "category": "news"
                                }
                                pm_news.append(news_item)
                    
                    logger.info(f"Polymarket 新闻筛选完成，共 {len(pm_news)} 条")
                else:
                    logger.warning(f"Polymarket 搜索未成功: {result.get('error', 'unknown')}")
            except Exception as e:
                logger.warning(f"Polymarket 搜索失败: {e}")
            
            # 搜索2: 预测市场行业动态
            if len(pm_news) < 3:
                try:
                    result = await self.qveris.execute_tool(
                        brave_tool,
                        search_id,
                        {"q": "prediction market crypto betting news 2025 2026", "count": 4}
                    )
                    
                    if result.get("success"):
                        data = result.get("data", {})
                        results = self._parse_search_results(data)
                        
                        for item in results[:4]:
                            if isinstance(item, dict):
                                title = item.get("title", item.get("name", ""))
                                # 避免重复且过滤非新闻内容
                                if not any(n["title"] == title for n in pm_news) and self._is_news_content(title, item.get("url", "")):
                                    desc = item.get("snippet", item.get("description", ""))
                                    url = item.get("url", item.get("link", ""))
                                    source = self._extract_source(item, url)
                                    
                                    news_item = {
                                        "title": title,
                                        "summary": desc[:150] if len(desc) > 150 else desc,
                                        "source": source,
                                        "url": url,
                                        "category": "industry"
                                    }
                                    pm_news.append(news_item)
                        
                        logger.info(f"预测市场行业新闻补充完成，共 {len(pm_news)} 条")
                except Exception as e:
                    logger.warning(f"预测市场行业新闻搜索失败: {e}")
            
            # 搜索3: 预测市场特定事件新闻
            if len(pm_news) < 3:
                try:
                    result = await self.qveris.execute_tool(
                        brave_tool,
                        search_id,
                        {"q": "Polymarket election crypto price prediction results", "count": 3}
                    )
                    
                    if result.get("success"):
                        data = result.get("data", {})
                        results = self._parse_search_results(data)
                        
                        for item in results[:3]:
                            if isinstance(item, dict):
                                title = item.get("title", item.get("name", ""))
                                if not any(n["title"] == title for n in pm_news) and self._is_news_content(title, item.get("url", "")):
                                    desc = item.get("snippet", item.get("description", ""))
                                    url = item.get("url", item.get("link", ""))
                                    source = self._extract_source(item, url)
                                    
                                    news_item = {
                                        "title": title,
                                        "summary": desc[:150] if len(desc) > 150 else desc,
                                        "source": source,
                                        "url": url,
                                        "category": "events"
                                    }
                                    pm_news.append(news_item)
                        
                        logger.info(f"预测市场事件新闻补充完成，共 {len(pm_news)} 条")
                except Exception as e:
                    logger.warning(f"预测市场事件新闻搜索失败: {e}")
            
            return pm_news[:6]
            
        except Exception as e:
            logger.error(f"获取 Polymarket 新闻异常: {e}")
            return []
    
    def _parse_search_results(self, data: dict) -> list:
        """解析搜索结果"""
        results = []
        if isinstance(data, dict):
            if "data" in data and isinstance(data["data"], dict):
                results = data["data"].get("results", data["data"].get("web", {}).get("results", []))
            elif "results" in data:
                results = data["results"]
            elif "web" in data and isinstance(data["web"], dict):
                results = data["web"].get("results", [])
            elif "organic" in data:
                results = data["organic"]
        return results
    
    def _is_news_content(self, title: str, url: str) -> bool:
        """判断是否为新闻内容而非介绍页面"""
        if not title:
            return False
        
        title_lower = title.lower()
        url_lower = url.lower() if url else ""
        
        # 排除介绍性/主页内容
        exclude_patterns = [
            "| the world's largest prediction market",
            "| polymarket",
            "- wikipedia",
            "home | ",
            "official site",
            "about us",
            "what is",
            "how to",
            "guide to",
            "tutorial",
            "wiki",
            "definition",
            "meaning of"
        ]
        
        for pattern in exclude_patterns:
            if pattern in title_lower:
                return False
        
        # 排除官网主页和维基百科
        if "polymarket.com" in url_lower and ("blog" not in url_lower and "news" not in url_lower):
            return False
        if "wikipedia.org" in url_lower:
            return False
        
        # 包含新闻特征
        news_indicators = [
            "news", "report", "says", "announces", "launches", "raises", 
            "acquires", "partners", "expands", "grows", "surges", "drops",
            "regulators", "sec", "cftc", "lawsuit", "legal", "ban", "approval",
            "trading", "volume", "market", "prediction", "betting", "election",
            "crypto", "blockchain", "defi", "web3"
        ]
        
        return any(ind in title_lower for ind in news_indicators)
    
    def _extract_source(self, item: dict, url: str) -> str:
        """提取新闻来源"""
        source = item.get("source", item.get("domain", ""))
        if not source and url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                source = parsed.netloc.replace("www.", "")
            except:
                source = "News"
        if not source:
            source = "News"
        return source


class FundNewsGenerator:
    """基金新闻生成器 - 多市场版本"""
    
    def __init__(self):
        self.fetcher = MarketNewsFetcher()
    
    def translate_to_chinese(self, text: str) -> str:
        """
        简单的英文新闻标题/摘要翻译逻辑
        这里可以接入翻译API，暂时返回原文并做简单处理
        """
        if not text:
            return "暂无摘要"
        
        # 如果已经是中文，直接返回
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            return text
        
        # 返回原文（截断）
        return text[:120] + "..." if len(text) > 120 else text
    
    async def generate_market_report(self) -> str:
        """
        生成完整的市场新闻摘要报告
        """
        logger.info("开始收集各市场新闻...")
        start_time = time.monotonic()
        
        # 并行获取所有市场新闻
        results = await asyncio.gather(
            self.fetcher.get_us_news(),
            self.fetcher.get_europe_news(),
            self.fetcher.get_japan_news(),
            self.fetcher.get_gold_news(),
            self.fetcher.get_polymarket_news(),
            return_exceptions=True
        )
        
        us_news = results[0] if not isinstance(results[0], Exception) else []
        europe_news = results[1] if not isinstance(results[1], Exception) else []
        japan_news = results[2] if not isinstance(results[2], Exception) else []
        gold_news = results[3] if not isinstance(results[3], Exception) else []
        polymarket_news = results[4] if not isinstance(results[4], Exception) else []
        
        elapsed = time.monotonic() - start_time
        logger.info(f"新闻获取完成，耗时: {elapsed:.2f} 秒")
        
        # 构建报告
        today_str = datetime.now().strftime("%Y-%m-%d")
        report_lines = [
            f"📊 **基金新闻摘要** ({today_str})",
            ""
        ]
        
        # 🇺🇸 美股市场
        report_lines.extend([
            "🇺🇸 **美股市场 (纳斯达克/标普500)**",
            ""
        ])
        if us_news:
            for news in us_news[:4]:
                title = news.get("title", "无标题")
                summary = self.translate_to_chinese(news.get("summary", ""))
                source = news.get("source", "未知")
                report_lines.append(f"• **{title}**")
                report_lines.append(f"  └ {summary} (*{source}*)")
                report_lines.append("")
        else:
            report_lines.append("• 暂无最新美股新闻")
            report_lines.append("")
        
        # 🇪🇺 欧洲股市
        report_lines.extend([
            "🇪🇺 **欧洲股市**",
            ""
        ])
        if europe_news:
            for news in europe_news[:4]:
                title = news.get("title", "无标题")
                source = news.get("source", "未知")
                symbol = news.get("symbol", "")
                symbol_tag = f" [{symbol}]" if symbol else ""
                report_lines.append(f"• **{title}**{symbol_tag}")
                report_lines.append(f"  └ (*{source}*)")
                report_lines.append("")
        else:
            report_lines.append("• 暂无最新欧洲股市新闻")
            report_lines.append("")
        
        # 🇯🇵 日本股市
        report_lines.extend([
            "🇯🇵 **日本股市 (日经225)**",
            ""
        ])
        if japan_news:
            for news in japan_news[:4]:
                title = news.get("title", "无标题")
                source = news.get("source", "未知")
                symbol = news.get("symbol", "")
                symbol_tag = f" [{symbol}]" if symbol else ""
                report_lines.append(f"• **{title}**{symbol_tag}")
                report_lines.append(f"  └ (*{source}*)")
                report_lines.append("")
        else:
            report_lines.append("• 暂无最新日本股市新闻")
            report_lines.append("")
        
        # 🥇 黄金市场
        report_lines.extend([
            "🥇 **黄金市场**",
            ""
        ])
        if gold_news:
            for news in gold_news[:4]:
                title = news.get("title", "无标题")
                summary = self.translate_to_chinese(news.get("summary", ""))
                source = news.get("source", "未知")
                report_lines.append(f"• **{title}**")
                report_lines.append(f"  └ {summary} (*{source}*)")
                report_lines.append("")
        else:
            report_lines.append("• 暂无最新黄金新闻")
            report_lines.append("")
        
        # 🔮 Polymarket / 预测市场
        report_lines.extend([
            "🔮 **Polymarket / 预测市场**",
            ""
        ])
        if polymarket_news:
            for news in polymarket_news[:4]:
                title = news.get("title", "无标题")
                summary = news.get("summary", "")[:100]
                if summary and len(news.get("summary", "")) > 100:
                    summary += "..."
                source = news.get("source", "未知")
                category = news.get("category", "")
                cat_tag = f" [{category}]" if category else ""
                report_lines.append(f"• **{title}**{cat_tag}")
                if summary:
                    report_lines.append(f"  └ {summary} (*{source}*)")
                else:
                    report_lines.append(f"  └ (*{source}*)")
                report_lines.append("")
        else:
            report_lines.append("• 暂无最新预测市场新闻")
            report_lines.append("")
        
        # 🎯 基金相关要点
        report_lines.extend([
            "🎯 **基金相关要点**",
            ""
        ])
        
        # 根据获取到的新闻生成要点
        if us_news:
            report_lines.append("• 纳斯达克100: AI板块持续受关注，科技股波动需留意")
        else:
            report_lines.append("• 纳斯达克100: 关注AI和芯片板块动态")
            
        report_lines.append("• 标普500: 关注美联储政策和企业财报季表现")
        
        if europe_news:
            report_lines.append("• 欧洲动力: ASML、SAP等龙头企业订单及业绩表现")
        else:
            report_lines.append("• 欧洲动力: 关注欧洲央行货币政策及制造业数据")
            
        if japan_news:
            report_lines.append("• 日本精选: 丰田、索尼、任天堂等核心持仓动态")
        else:
            report_lines.append("• 日本精选: 关注日元汇率和日本央行政策动向")
            
        if gold_news:
            report_lines.append("• 黄金ETF: 避险需求推动金价波动")
        else:
            report_lines.append("• 黄金ETF: 关注地缘政治风险和美元指数走势")
        
        # Polymarket / 预测市场要点
        if polymarket_news:
            report_lines.append("• 预测市场: Polymarket 平台活跃度及热门事件值得跟踪")
            report_lines.append("• 加密预测: 去中心化预测市场与加密货币联动性增强")
        else:
            report_lines.append("• 预测市场: 关注 Polymarket 等平台热门预测事件")
            report_lines.append("• 自动化交易: 预测市场量化策略及跟单机会")
        
        report_lines.append("")
        
        # ⚠️ 风险提示
        report_lines.extend([
            "⚠️ **风险提示**",
            ""
        ])
        report_lines.append("• 美股市场波动可能受美联储政策及科技股表现影响")
        report_lines.append("• 欧洲股市受地缘政治及欧洲央行货币政策影响")
        report_lines.append("• 日本股市受日元汇率波动及日本央行政策影响")
        report_lines.append("• 黄金价格受地缘政治风险及美元指数走势影响")
        report_lines.append("• 预测市场存在流动性风险及监管不确定性")
        report_lines.append("• 自动化交易策略需严格风控，避免过度杠杆")
        report_lines.append("• QDII基金受汇率波动影响，投资需谨慎")
        report_lines.append("")
        
        # 数据来源
        report_lines.append(f"⏱️ 获取耗时: {elapsed:.1f}秒 | 📰 数据来源: QVeris API / Finnhub / Yahoo Finance")
        
        return "\n".join(report_lines)
    
    async def generate_simple_report(self) -> str:
        """
        生成简化版报告（当API不可用时）
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        report_lines = [
            f"📊 **基金新闻摘要** ({today_str})",
            "",
            "🇺🇸 **美股市场 (纳斯达克/标普500)**",
            "• AI板块持续受关注，科技股波动需留意",
            "• 美联储政策预期影响市场情绪",
            "",
            "🇪🇺 **欧洲股市**",
            "• 关注ASML、SAP等龙头企业动态",
            "• 欧洲央行货币政策维持宽松预期",
            "",
            "🇯🇵 **日本股市 (日经225)**",
            "• 关注日元汇率和日本央行政策动向",
            "• 出口企业受益于汇率变化",
            "",
            "🥇 **黄金市场**",
            "• 地缘政治风险推升避险需求",
            "• 关注美元指数走势",
            "",
            "🔮 **Polymarket / 预测市场**",
            "• 关注平台热门预测事件及交易量变化",
            "• 去中心化预测市场与加密货币联动",
            "",
            "⚠️ **风险提示**",
            "• 预测市场存在监管不确定性和流动性风险",
            "• 自动化交易需严格风控",
            "• QDII基金受汇率波动影响，投资需谨慎",
            "",
            "📊 数据来源: 备用数据"
        ]
        return "\n".join(report_lines)


async def main():
    """主函数"""
    generator = FundNewsGenerator()
    
    try:
        # 尝试生成完整报告
        report = await generator.generate_market_report()
        
        print(report)
        
        # 保存到 Obsidian vault (中文版本)
        today_str = datetime.now().strftime("%Y-%m-%d")
        obsidian_dir = "/root/clawd/obsidian-vault/reports/fund"
        os.makedirs(obsidian_dir, exist_ok=True)
        output_path = os.path.join(obsidian_dir, f"{today_str}.md")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        logger.info(f"报告已保存到 {output_path}")
        
        # 自动同步到 GitHub (先提交本地更改，再 pull，再 push)
        try:
            import subprocess
            os.chdir("/root/clawd/obsidian-vault")
            
            # 先提交本地更改
            logger.info("正在提交本地更改...")
            subprocess.run(["git", "add", "-A"], check=False)
            commit_result = subprocess.run(
                ["git", "commit", "-m", f"Update fund report {today_str}"],
                capture_output=True, text=True
            )
            if commit_result.returncode == 0:
                logger.info("本地更改已提交")
            
            # 获取远程更新 (使用 merge 策略)
            logger.info("正在同步 GitHub 仓库...")
            pull_result = subprocess.run(
                ["git", "pull", "origin", "master", "--no-rebase"],
                capture_output=True, text=True
            )
            if pull_result.returncode == 0:
                logger.info("成功拉取远程更新")
            else:
                logger.warning(f"拉取远程更新失败: {pull_result.stderr}")
            
            # 推送
            push_result = subprocess.run(
                ["git", "push", "origin", "master"],
                capture_output=True, text=True
            )
            
            if push_result.returncode == 0:
                logger.info("✅ 已自动同步到 GitHub")
            else:
                logger.warning(f"GitHub 推送失败: {push_result.stderr}")
                
        except Exception as e:
            logger.warning(f"GitHub 同步失败: {e}")
        
        return report
        
    except Exception as e:
        logger.exception("生成报告失败，使用简化版")
        # 降级到简化报告
        try:
            report = await generator.generate_simple_report()
            print(report)
            return report
        except Exception as e2:
            logger.error(f"简化报告也失败: {e2}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
