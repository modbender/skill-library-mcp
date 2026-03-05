"""
每日热榜技能主入口示例

这个文件展示如何将三个扩展功能集成到主Skill中。
在实际使用时，可以根据需要调整和整合。
"""

import asyncio
from typing import Dict, Any, Optional

# 支持相对导入（作为包的一部分）和绝对导入（直接运行）
try:
    from .news_digest import NewsDigest, DigestConfig, create_digest as create_news_digest
    from .industry_hot import IndustryHot, IndustryConfig, create_industry_hot
    from .personalized import PersonalizedSubscription, UserPreferences, create_personalized
except ImportError:
    from news_digest import NewsDigest, DigestConfig, create_digest as create_news_digest
    from industry_hot import IndustryHot, IndustryConfig, create_industry_hot
    from personalized import PersonalizedSubscription, UserPreferences, create_personalized


class DailyHotNewsSkill:
    """每日热榜技能主类"""
    
    def __init__(self, api_client=None, formatter=None):
        """
        初始化技能
        
        Args:
            api_client: API客户端实例（用于获取热榜数据）
            formatter: 格式化器实例（用于格式化输出）
        """
        self.api_client = api_client
        self.formatter = formatter
        
        # 初始化各功能模块
        self.news_digest: Optional[NewsDigest] = None
        self.industry_hot: Optional[IndustryHot] = None
        self.personalized: Optional[PersonalizedSubscription] = None
    
    async def initialize(self):
        """初始化各模块"""
        self.news_digest = await create_news_digest(
            api_client=self.api_client, 
            formatter=self.formatter
        )
        self.industry_hot = await create_industry_hot(
            api_client=self.api_client,
            formatter=self.formatter
        )
        self.personalized = await create_personalized(
            api_client=self.api_client,
            formatter=self.formatter
        )
    
    async def handle_request(self, user_input: str, intent: str = None) -> Dict[str, Any]:
        """
        处理用户请求
        
        Args:
            user_input: 用户输入
            intent: 意图（可选，用于路由到对应功能）
            
        Returns:
            处理结果
        """
        user_input_lower = user_input.lower()
        
        # 路由到对应功能
        if intent == "news_digest" or self._is_news_digest_request(user_input_lower):
            return await self._handle_news_digest(user_input)
        
        elif intent == "industry_hot" or self._is_industry_hot_request(user_input_lower):
            return await self._handle_industry_hot(user_input)
        
        elif intent == "personalized" or self._is_personalized_request(user_input_lower):
            return await self._handle_personalized(user_input)
        
        else:
            # 默认返回功能选择引导
            return await self._show_main_menu()
    
    def _is_news_digest_request(self, user_input: str) -> bool:
        """判断是否为新闻摘要请求"""
        keywords = ["热点", "摘要", "标签", "科技", "游戏", "娱乐", "财经", "新闻"]
        return any(kw in user_input for kw in keywords)
    
    def _is_industry_hot_request(self, user_input: str) -> bool:
        """判断是否为行业热榜请求"""
        keywords = ["行业", "汽车", "金融", "医疗", "旅游", "餐饮", "房产"]
        return any(kw in user_input for kw in keywords)
    
    def _is_personalized_request(self, user_input: str) -> bool:
        """判断是否为个性化请求"""
        keywords = ["配置", "设置", "偏好", "关注", "个性化", "订阅"]
        return any(kw in user_input for kw in keywords)
    
    async def _handle_news_digest(self, user_input: str) -> Dict[str, Any]:
        """处理新闻摘要请求"""
        if not self.news_digest:
            return {"error": "模块未初始化"}
        
        return await self.news_digest.process_user_request(user_input)
    
    async def _handle_industry_hot(self, user_input: str) -> Dict[str, Any]:
        """处理行业热榜请求"""
        if not self.industry_hot:
            return {"error": "模块未初始化"}
        
        return await self.industry_hot.process_user_request(user_input)
    
    async def _handle_personalized(self, user_input: str) -> Dict[str, Any]:
        """处理个性化订阅请求"""
        if not self.personalized:
            return {"error": "模块未初始化"}
        
        return await self.personalized.process_user_request(user_input)
    
    async def _show_main_menu(self) -> Dict[str, Any]:
        """显示主菜单"""
        menu_text = """🎯 **每日热榜 - 功能选择**

请选择您想使用的功能：

1. **📰 热点新闻摘要**
   按标签浏览热点新闻（科技、游戏、娱乐、财经等）

2. **🏭 行业热榜垂直**
   按行业分类查看热榜（汽车、金融、医疗、旅游等）

3. **⚙️ 个性化订阅**
   配置您的偏好，获取定制化热榜

💡 您可以直接告诉我您想做什么，例如：
- "今天有什么科技热点"
- "看看汽车行业热榜"
- "配置个性化热榜"
"""
        return {
            "action": "show_menu",
            "message": menu_text
        }
    
    # 便捷方法
    
    async def get_news_digest_tags(self) -> str:
        """获取新闻摘要标签选项"""
        if self.news_digest:
            return await self.news_digest.get_tag_options()
        return "模块未初始化"
    
    async def get_industry_options(self) -> str:
        """获取行业选项"""
        if self.industry_hot:
            return await self.industry_hot.get_industry_options()
        return "模块未初始化"
    
    async def get_personalized_options(self) -> str:
        """获取个性化配置选项"""
        if self.personalized:
            return await self.personalized.get_config_options()
        return "模块未初始化"
    
    def get_current_config(self) -> Optional[UserPreferences]:
        """获取当前个性化配置"""
        if self.personalized:
            return self.personalized.get_current_config()
        return None


# 便捷函数
async def create_skill(api_client=None, formatter=None) -> DailyHotNewsSkill:
    """创建技能实例"""
    skill = DailyHotNewsSkill(api_client=api_client, formatter=formatter)
    await skill.initialize()
    return skill


# 示例使用
if __name__ == "__main__":
    async def example():
        # 创建技能实例（不传入api_client时的模拟示例）
        skill = await create_skill()
        
        # 示例1：展示主菜单
        result = await skill.handle_request("帮助")
        print(result["message"])
        
        print("\n" + "="*60 + "\n")
        
        # 示例2：展示标签选择
        result = await skill.get_news_digest_tags()
        print(result)
        
        print("\n" + "="*60 + "\n")
        
        # 示例3：展示行业选择
        result = await skill.get_industry_options()
        print(result)
        
        print("\n" + "="*60 + "\n")
        
        # 示例4：展示个性化配置选项
        result = await skill.get_personalized_options()
        print(result)
    
    asyncio.run(example())
