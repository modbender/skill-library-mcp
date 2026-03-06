#!/usr/bin/env python3
"""
Main script for cross-referencing restaurant reviews using real data.
Uses Playwright with persistent sessions for automated login.
"""

import sys
import asyncio
from typing import List, Dict

from config import DEFAULT_THRESHOLDS
from session_manager import BrowserSessionManager
from fetch_dianping_real import fetch_dianping_real
from fetch_xiaohongshu_real import fetch_xiaohongshu_real
from match_restaurants import match_and_score
from crosscheck_base import CrossCheckBase, RecommendationResult


class RestaurantCrossCheckerReal(CrossCheckBase):
    """Cross-reference restaurant data from multiple platforms using real scraping."""

    def __init__(self, config: Dict = None):
        super().__init__()
        self.config = config or DEFAULT_THRESHOLDS
        self.session_manager = BrowserSessionManager()

    async def search_async(self, location: str, cuisine: str) -> List[RecommendationResult]:
        """
        Search and cross-reference restaurants (async version).

        Args:
            location: Geographic area (e.g., "上海静安区")
            cuisine: Cuisine type (e.g., "日式料理")

        Returns:
            List of recommendation results sorted by score
        """
        print(f"\n🔍 开始搜索: {location} - {cuisine}\n")
        print("⏳ 正在从大众点评获取数据...")
        print("⏳ 正在从小红书获取数据...")
        print("（使用已保存的登录会话，如未登录将自动提示）\n")

        # Fetch data from both platforms concurrently
        dp_task = fetch_dianping_real(location, cuisine, self.config)
        xhs_task = fetch_xiaohongshu_real(location, cuisine, self.config)

        dp_restaurants, xhs_posts = await asyncio.gather(
            dp_task,
            xhs_task,
            return_exceptions=True
        )

        # Handle exceptions
        if isinstance(dp_restaurants, Exception):
            print(f"⚠️ 大众点评抓取失败: {dp_restaurants}")
            dp_restaurants = []
        if isinstance(xhs_posts, Exception):
            print(f"⚠️ 小红书抓取失败: {xhs_posts}")
            xhs_posts = []

        print(f"✅ 大众点评: 找到 {len(dp_restaurants)} 家餐厅")
        print(f"✅ 小红书: 找到 {len(xhs_posts)} 家餐厅\n")

        if not dp_restaurants or not xhs_posts:
            print("⚠️ 数据不足，无法进行交叉验证")
            print("💡 提示：")
            print("  - 如果是首次使用，请先运行: python3 scripts/session_manager.py")
            print("  - 检查网络连接")
            print("  - 尝试更换搜索关键词")
            return []

        # Match restaurants across platforms
        matches = match_and_score(dp_restaurants, xhs_posts, self.config)

        print(f"🔗 匹配成功: {len(matches)} 家餐厅\n")

        return self.build_results(matches)

    def search(self, location: str, cuisine: str) -> List[RecommendationResult]:
        """Synchronous wrapper for search."""
        return asyncio.run(self.search_async(location, cuisine))


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: python3 crosscheck_real.py <location> <cuisine>")
        print("Example: python3 crosscheck_real.py '上海静安区' '日式料理'")
        print()
        print("⚠️ 首次使用前，请先配置登录会话：")
        print("   python3 scripts/session_manager.py")
        sys.exit(1)

    location = sys.argv[1]
    cuisine = sys.argv[2]

    checker = RestaurantCrossCheckerReal()
    results = checker.search(location, cuisine)
    output = checker.format_output(results, location, cuisine)

    print(output)


if __name__ == "__main__":
    main()
