"""
热点新闻摘要（增强版） - News Digest Module

功能：
- 15种标签分类：科技、互联网、游戏、娱乐、社会、财经、汽车、体育、教育、健康、国际、房产、数码、时尚、美食
- AI主动引导用户选择标签
- 按标签获取和合并热榜
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio

# 标签到平台的映射
TAG_MAPPING: Dict[str, List[str]] = {
    "科技": ["ithome", "36kr", "sspai", "csdn", "juejin", "51cto", "oschina", "infoq"],
    "互联网": ["sina-news", "netease-news", "qq-news", "sohu-news", "ifeng"],
    "游戏": ["genshin", "miyoushe", "lol", "hupu", "bilibili", "douyu", "huya", "netease-game"],
    "娱乐": ["weibo", "douban-group", "douban-movie", "mtime", "movie"],
    "社会": ["sina-news", "netease-news", "qq-news", "sohu-news", "ifeng", "qq"],
    "财经": ["sina-money", "eastmoney", "xueqiu", "jrj", "cnstock", "wallstreetcn"],
    "汽车": ["autohome", "car", "懂车帝", "bitauto", "car1"],
    "体育": ["hupu", "sports", "sina-sports", "qq-sports", "zhibo8"],
    "教育": ["zhihu", "知乎", "bilibili", "jike", "dazhihui"],
    "健康": ["zhihu", "知乎", "sina-health", "health", "baikemy"],
    "国际": ["sina-news", "netease-news", "qq-news", "ifeng", "cnn", "bbc"],
    "房产": ["lfang", "soufunianjia", "anjuke", "house"],
    "数码": ["ithome", "coolapk", "sspai", "geekpark", "少数派"],
    "时尚": ["mogujie", "meilishuo", "xiaohongshu", "微博时尚", "yoho"],
    "美食": ["dianping", "xiaohongshu", "大众点评", "maoyan", "ele.me"]
}

# 所有可用的标签
ALL_TAGS = list(TAG_MAPPING.keys())


class DigestMode(Enum):
    """摘要模式"""
    SINGLE = "single"  # 单标签
    MULTI = "multi"    # 多标签


@dataclass
class DigestConfig:
    """摘要配置"""
    tags: List[str]          # 选择的标签列表
    mode: DigestMode = DigestMode.MULTI
    items_per_platform: int = 10  # 每个平台显示的条目数
    total_items: int = 50         # 总条目数限制
    merge_strategy: str = "score"  # 合并策略：score(按热度), time(按时间), random(随机)


class NewsDigest:
    """热点新闻摘要类"""
    
    def __init__(self, api_client=None, formatter=None):
        """
        初始化新闻摘要
        
        Args:
            api_client: API客户端实例（可选，如果不提供则需要外部传入）
            formatter: 格式化器实例（可选）
        """
        self.api_client = api_client
        self.formatter = formatter
        self.platforms = self._get_all_platforms()
    
    def _get_all_platforms(self) -> List[str]:
        """获取所有可用的平台"""
        platforms = set()
        for tag, plats in TAG_MAPPING.items():
            platforms.update(plats)
        return list(platforms)
    
    async def fetch_all_hot_data(self, limit_per_platform: int = 10) -> List[Dict[str, Any]]:
        """
        一次性获取全部54个平台的热榜数据
        
        Args:
            limit_per_platform: 每个平台获取的条目数
            
        Returns:
            全部平台的热榜数据列表
        """
        all_items = []
        
        if self.api_client:
            for platform in self.platforms:
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
    
    async def get_tag_options(self) -> str:
        """
        获取标签选择选项（AI引导话术）
        
        Returns:
            格式化的标签选择文本
        """
        options_text = "📊 **请选择您感兴趣的标签**\n\n"
        
        # 分两列显示
        tags_left = ALL_TAGS[:8]
        tags_right = ALL_TAGS[8:]
        
        for i, tag in enumerate(tags_left):
            right_tag = tags_right[i] if i < len(tags_right) else ""
            left_plats = ", ".join(TAG_MAPPING[tag][:3])
            right_plats = f"│ {i+8+1}. {right_tag}: {', '.join(TAG_MAPPING[right_tag][:3])}" if right_tag else ""
            options_text += f"{i+1}. {tag} ({left_plats}) {right_plats}\n"
        
        options_text += "\n💡 您可以输入标签名称或数字编号，支持多选（如：1,3或科技+游戏）"
        return options_text
    
    def parse_tags_from_input(self, user_input: str) -> List[str]:
        """
        解析用户输入的标签
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            匹配的标签列表
        """
        user_input = user_input.strip().lower()
        matched_tags = []
        
        # 处理数字选择
        numbers = []
        import re
        number_pattern = re.findall(r'\d+', user_input)
        for num in number_pattern:
            idx = int(num) - 1
            if 0 <= idx < len(ALL_TAGS):
                numbers.append(ALL_TAGS[idx])
        
        # 处理标签名称
        for tag in ALL_TAGS:
            if tag.lower() in user_input or tag in user_input:
                if tag not in matched_tags and tag not in numbers:
                    matched_tags.append(tag)
        
        # 合并数字选择的结果
        matched_tags.extend([t for t in numbers if t not in matched_tags])
        
        return matched_tags if matched_tags else []
    
    async def get_digest_by_tags(self, tags: List[str], config: Optional[DigestConfig] = None) -> Dict[str, Any]:
        """
        按标签获取新闻摘要（新版：先全部获取，再按标签筛选）
        
        Args:
            tags: 标签列表
            config: 配置对象（可选）
            
        Returns:
            合并后的热榜数据
        """
        if config is None:
            config = DigestConfig(tags=tags)
        
        # 步骤1：全部获取
        all_items = await self.fetch_all_hot_data(limit_per_platform=config.items_per_platform)
        
        # 步骤2：按标签筛选
        # 获取所有相关平台
        target_platforms = set()
        for tag in tags:
            if tag in TAG_MAPPING:
                target_platforms.update(TAG_MAPPING[tag])
        
        filtered_items = []
        for item in all_items:
            platform = item.get("source_platform", "")
            if platform in target_platforms:
                item["source_tag"] = next((t for t in tags if t in TAG_MAPPING and platform in TAG_MAPPING[t]), tags[0])
                filtered_items.append(item)
        
        # 去重和合并
        merged_items = self._merge_items(filtered_items, config.merge_strategy)
        
        # 限制总数
        merged_items = merged_items[:config.total_items]
        
        return {
            "tags": tags,
            "platforms": list(target_platforms),
            "total_items": len(merged_items),
            "items": merged_items
        }
    
    def _merge_items(self, items: List[Dict], strategy: str = "score") -> List[Dict]:
        """
        合并和去重条目
        
        Args:
            items: 条目列表
            strategy: 合并策略
            
        Returns:
            合并后的条目列表
        """
        if not items:
            return []
        
        # 按标题去重
        seen_titles = set()
        unique_items = []
        
        for item in items:
            title = item.get("title", "").strip().lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_items.append(item)
        
        # 根据策略排序
        if strategy == "score":
            # 按热度/分数排序
            unique_items.sort(key=lambda x: x.get("hot", 0) or x.get("score", 0), reverse=True)
        elif strategy == "time":
            # 按时间排序
            unique_items.sort(key=lambda x: x.get("time", "") or "", reverse=True)
        
        return unique_items
    
    def format_digest_response(self, digest_data: Dict[str, Any]) -> str:
        """
        格式化摘要响应
        
        Args:
            digest_data: 摘要数据
            
        Returns:
            格式化的响应文本
        """
        if not digest_data.get("items"):
            return "❌ 暂无热点数据"
        
        tags = digest_data["tags"]
        items = digest_data["items"]
        
        response = f"📰 **热点摘要 - {', '.join(tags)}**\n"
        response += f"来源平台: {', '.join(digest_data['platforms'])}\n"
        response += f"共 {digest_data['total_items']} 条热点\n"
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
    
    async def process_user_request(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户请求
        
        Args:
            user_input: 用户输入
            
        Returns:
            处理结果
        """
        # 解析标签
        tags = self.parse_tags_from_input(user_input)
        
        if not tags:
            # 返回引导信息
            return {
                "action": "ask_tag",
                "message": await self.get_tag_options()
            }
        
        # 获取摘要
        digest_data = await self.get_digest_by_tags(tags)
        
        # 格式化响应
        response_text = self.format_digest_response(digest_data)
        
        return {
            "action": "show_digest",
            "data": digest_data,
            "message": response_text
        }


# 便捷函数
async def create_digest(api_client=None, formatter=None) -> NewsDigest:
    """创建新闻摘要实例"""
    return NewsDigest(api_client=api_client, formatter=formatter)


if __name__ == "__main__":
    # 测试代码
    async def test():
        digest = await create_digest()
        print(await digest.get_tag_options())
        
        print("\n" + "="*50 + "\n")
        
        result = await digest.process_user_request("科技和游戏")
        print(result["message"])
    
    asyncio.run(test())
