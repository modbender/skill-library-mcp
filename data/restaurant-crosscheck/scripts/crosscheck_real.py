#!/usr/bin/env python3
"""
Main script for cross-referencing restaurant reviews using real data.
Uses Playwright with persistent sessions for automated login.
"""

import sys
import asyncio
from typing import List, Dict
from dataclasses import dataclass

from config import DEFAULT_THRESHOLDS, SCORING_WEIGHTS, OUTPUT_CONFIG
from session_manager import BrowserSessionManager
from fetch_dianping_real import fetch_dianping_real
from fetch_xiaohongshu_real import fetch_xiaohongshu_real
from fetch_dianping import DianpingRestaurant
from fetch_xiaohongshu import XiaohongshuPost
from match_restaurants import (
    match_and_score,
    MatchedRestaurant,
    normalize_engagement,
    calculate_consistency
)


@dataclass
class RecommendationResult:
    """Final recommendation with scores."""
    restaurant: MatchedRestaurant
    recommendation_score: float  # 0-10
    consistency_level: str  # "高", "中", "低"


class RestaurantCrossCheckerReal:
    """Cross-reference restaurant data from multiple platforms using real scraping."""

    def __init__(self, config: Dict = None):
        self.config = config or DEFAULT_THRESHOLDS
        self.scoring_weights = SCORING_WEIGHTS
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

        # Calculate recommendation scores
        results = []
        for match in matches:
            result = self._calculate_recommendation(match)
            results.append(result)

        # Sort by recommendation score
        results.sort(key=lambda x: x.recommendation_score, reverse=True)

        return results

    def search(self, location: str, cuisine: str) -> List[RecommendationResult]:
        """Synchronous wrapper for search."""
        return asyncio.run(self.search_async(location, cuisine))

    def _calculate_recommendation(self, match: MatchedRestaurant) -> RecommendationResult:
        """Calculate final recommendation score."""
        # Normalize XHS engagement to 0-5 scale
        xhs_rating = normalize_engagement(match.xhs_data)

        # Calculate consistency if not already done
        if not hasattr(match, 'consistency_score'):
            match.consistency_score = calculate_consistency(
                match.dianping_data.rating,
                xhs_rating,
                match.xhs_data.sentiment_score
            )

        # Calculate recommendation score (0-10)
        recommendation_score = (
            (match.dianping_data.rating * self.scoring_weights['dianping_rating']) +
            (xhs_rating * self.scoring_weights['xhs_engagement']) +
            (match.consistency_score * 5 * self.scoring_weights['consistency'])
        ) * 2  # Scale to 0-10

        # Determine consistency level
        if match.consistency_score >= 0.7:
            consistency_level = "高"
        elif match.consistency_score >= 0.5:
            consistency_level = "中"
        else:
            consistency_level = "低"

        return RecommendationResult(
            restaurant=match,
            recommendation_score=round(recommendation_score, 1),
            consistency_level=consistency_level
        )

    def format_output(self, results: List[RecommendationResult], location: str, cuisine: str) -> str:
        """Format results for display."""
        if not results:
            return f"❌ 未找到符合条件的餐厅: {location} - {cuisine}"

        output = []
        output.append(f"📍 {location} {cuisine} 餐厅推荐\n")
        output.append("=" * 60 + "\n")

        for i, result in enumerate(results[:OUTPUT_CONFIG['max_restaurants']], 1):
            r = result.restaurant
            dp = r.dianping_data
            xhs = r.xhs_data

            output.append(f"{i}. {dp.name}")
            output.append(f"   🏆 推荐指数: {result.recommendation_score}/10")
            output.append(f"   ⭐ 大众点评: {dp.rating}⭐ ({dp.review_count}评价)")
            output.append(f"   💬 小红书: {normalize_engagement(xhs):.1f}⭐ ({xhs.likes}赞/{xhs.saves}收藏)")
            output.append(f"   📍 地址: {dp.address}")
            output.append(f"   💰 人均: {dp.price_range}")
            output.append(f"   ✅ 一致性: {result.consistency_level} ({r.consistency_score:.2f})")

            # Platform comparison
            if OUTPUT_CONFIG['show_details']:
                output.append(f"\n   📊 平台对比:")
                output.append(f"   - 大众点评标签: {', '.join(dp.tags)}")
                output.append(f"   - 小红书热词: {', '.join(xhs.keywords)}")

                # Warnings for low consistency
                if result.consistency_level == "低":
                    output.append(f"\n   ⚠️ 注意: 两平台评价差异较大，建议进一步了解")

            output.append("")

        return "\n".join(output)


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
