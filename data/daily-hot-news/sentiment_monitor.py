"""
舆情监控 - Sentiment Monitoring Module

功能：
- 直接用全量数据做关键词过滤
- 监控特定关键词的舆情
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio


class SentimentType(Enum):
    """舆情类型"""
    ALL = "all"           # 全部
    POSITIVE = "positive" # 正面
    NEGATIVE = "negative" # 负面
    NEUTRAL = "neutral"   # 中性


@dataclass
class SentimentConfig:
    """舆情监控配置"""
    keywords: List[str] = field(default_factory=list)    # 监控关键词
    sentiment_type: SentimentType = SentimentType.ALL    # 舆情类型
    items_per_platform: int = 10                         # 每个平台获取的条目数
    total_items: int = 50                                # 总条目数限制
    include_platforms: List[str] = None                  # 包含的平台
    exclude_platforms: List[str] = None                 # 排除的平台


class SentimentMonitor:
    """舆情监控类"""
    
    def __init__(self, api_client=None, formatter=None):
        """
        初始化舆情监控
        
        Args:
            api_client: API客户端实例（可选）
            formatter: 格式化器实例（可选）
        """
        self.api_client = api_client
        self.formatter = formatter
        self.all_platforms = self._get_default_platforms()
    
    def _get_default_platforms(self) -> List[str]:
        """获取默认的全部平台列表"""
        return [
            "weibo", "zhihu", "douban-group", "douban-movie",
            "ithome", "36kr", "sspai", "csdn", "juejin",
            "genshin", "miyoushe", "bilibili", "hupu",
            "sina-news", "netease-news", "qq-news",
            "sina-money", "eastmoney", "xueqiu",
            "autohome", "懂车帝", "mafengwo", "ctrip",
            "dianping", "xiaohongshu", "weibo"
        ]
    
    async def fetch_all_hot_data(self, limit_per_platform: int = 10) -> List[Dict[str, Any]]:
        """
        一次性获取全部平台的热榜数据
        
        Args:
            limit_per_platform: 每个平台获取的条目数
            
        Returns:
            全部平台的热榜数据列表
        """
        all_items = []
        
        if self.api_client:
            for platform in self.all_platforms:
                try:
                    items = await self.api_client.get_hot榜单(platform, limit=limit_per_platform)
                    if items:
                        for item in items:
                            item["source_platform"] = platform
                        all_items.extend(items)
                except Exception as e:
                    print(f"Error fetching {platform}: {e}")
                    continue
        
        return all_items
    
    async def monitor_keywords(self, keywords: List[str], config: Optional[SentimentConfig] = None) -> Dict[str, Any]:
        """
        监控关键词舆情（新版：先全部获取，再关键词过滤）
        
        Args:
            keywords: 关键词列表
            config: 配置对象（可选）
            
        Returns:
            舆情监控数据
        """
        if config is None:
            config = SentimentConfig(keywords=keywords)
        
        # 步骤1：全部获取
        all_items = await self.fetch_all_hot_data(limit_per_platform=config.items_per_platform)
        
        # 步骤2：关键词过滤
        filtered_items = self._filter_by_keywords(all_items, config.keywords)
        
        # 平台过滤
        if config.include_platforms:
            filtered_items = [item for item in filtered_items if item.get("source_platform") in config.include_platforms]
        if config.exclude_platforms:
            filtered_items = [item for item in filtered_items if item.get("source_platform") not in config.exclude_platforms]
        
        # 限制总数
        filtered_items = filtered_items[:config.total_items]
        
        return {
            "keywords": config.keywords,
            "total_items": len(filtered_items),
            "items": filtered_items
        }
    
    def _filter_by_keywords(self, items: List[Dict], keywords: List[str]) -> List[Dict]:
        """
        按关键词过滤
        
        Args:
            items: 条目列表
            keywords: 关键词列表
            
        Returns:
            过滤后的条目列表
        """
        if not keywords:
            return items
        
        filtered = []
        
        for item in items:
            title = item.get("title", "").lower()
            desc = item.get("description", "").lower()
            
            # 检查是否匹配任何关键词
            matches = False
            for kw in keywords:
                if kw.lower() in title or kw.lower() in desc:
                    matches = True
                    break
            
            if matches:
                filtered.append(item)
        
        # 按热度排序
        filtered.sort(key=lambda x: x.get("hot", 0) or x.get("score", 0), reverse=True)
        
        return filtered
    
    def format_monitoring_response(self, monitor_data: Dict[str, Any]) -> str:
        """
        格式化监控响应
        
        Args:
            monitor_data: 监控数据
            
        Returns:
            格式化的响应文本
        """
        items = monitor_data.get("items", [])
        keywords = monitor_data.get("keywords", [])
        
        if not items:
            return f"❌ 暂无关于「{', '.join(keywords)}」的舆情数据"
        
        response = f"🔍 **舆情监控 - {', '.join(keywords)}**\n"
        response += f"共 {monitor_data['total_items']} 条相关内容\n"
        response += "-" * 40 + "\n\n"
        
        for i, item in enumerate(items, 1):
            title = item.get("title", "无标题")
            hot = item.get("hot", item.get("score", ""))
            platform = item.get("source_platform", "")
            
            response += f"{i}. {title}\n"
            if hot:
                response += f"   🔥 热度: {hot}"
            if platform:
                response += f" | 📱 {platform}"
            response += "\n\n"
        
        return response
    
    def parse_keywords_from_input(self, user_input: str) -> List[str]:
        """
        从用户输入解析关键词
        
        Args:
            user_input: 用户输入
            
        Returns:
            关键词列表
        """
        user_input = user_input.strip()
        
        # 常用监控关键词
        common_keywords = [
            "AI", "人工智能", "ChatGPT", "大模型",
            "特斯拉", "比亚迪", "新能源汽车",
            "华为", "iPhone", "小米",
            "直播", "电商", "网红",
            "房价", "股票", "基金",
            "高考", "考研", "留学"
        ]
        
        matched_keywords = []
        
        for kw in common_keywords:
            if kw.lower() in user_input.lower():
                matched_keywords.append(kw)
        
        # 如果没有匹配到常用关键词，尝试提取用户输入的词
        if not matched_keywords:
            # 按逗号、空格等分隔
            import re
            words = re.split(r'[,，\s]+', user_input)
            matched_keywords = [w for w in words if w.strip()]
        
        return matched_keywords
    
    async def process_user_request(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户请求
        
        Args:
            user_input: 用户输入
            
        Returns:
            处理结果
        """
        # 解析关键词
        keywords = self.parse_keywords_from_input(user_input)
        
        if not keywords:
            # 返回引导信息
            return {
                "action": "ask_keywords",
                "message": "🔍 **舆情监控**\n\n"
                          "请输入您想监控的关键词，例如：\n"
                          "• AI、人工智能、ChatGPT\n"
                          "• 特斯拉、比亚迪、新能源汽车\n"
                          "• 华为、iPhone、小米\n"
                          "• 直播、电商、网红\n"
                          "• 房价、股票、基金\n\n"
                          "💡 您可以直接输入任意关键词进行监控"
            }
        
        # 获取监控数据
        monitor_data = await self.monitor_keywords(keywords)
        
        # 格式化响应
        response_text = self.format_monitoring_response(monitor_data)
        
        return {
            "action": "show_monitoring",
            "data": monitor_data,
            "message": response_text
        }


# 便捷函数
async def create_sentiment_monitor(api_client=None, formatter=None) -> SentimentMonitor:
    """创建舆情监控实例"""
    return SentimentMonitor(api_client=api_client, formatter=formatter)


if __name__ == "__main__":
    # 测试代码
    async def test():
        monitor = await create_sentiment_monitor()
        
        print("测试舆情监控...")
        result = await monitor.process_user_request("监控AI和特斯拉")
        print(result["message"])
    
    asyncio.run(test())
