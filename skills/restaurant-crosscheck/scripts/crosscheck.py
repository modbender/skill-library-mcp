"""Main script for cross-referencing restaurant reviews from multiple platforms."""

import sys
from typing import List, Dict
from dataclasses import dataclass

from config import DEFAULT_THRESHOLDS, SCORING_WEIGHTS, OUTPUT_CONFIG
from fetch_dianping import fetch_dianping, DianpingRestaurant
from fetch_xiaohongshu import fetch_xiaohongshu, XiaohongshuPost
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


class RestaurantCrossChecker:
    """Cross-reference restaurant data from multiple platforms."""

    def __init__(self, config: Dict = None):
        self.config = config or DEFAULT_THRESHOLDS
        self.scoring_weights = SCORING_WEIGHTS

    def search(self, location: str, cuisine: str) -> List[RecommendationResult]:
        """
        Search and cross-reference restaurants.

        Args:
            location: Geographic area (e.g., "上海静安区")
            cuisine: Cuisine type (e.g., "日式料理")

        Returns:
            List of recommendation results sorted by score
        """
        print(f"\n🔍 开始搜索: {location} - {cuisine}\n")

        # Fetch data from both platforms
        dp_restaurants = fetch_dianping(location, cuisine, self.config)
        xhs_posts = fetch_xiaohongshu(location, cuisine, self.config)

        print(f"✅ 大众点评: 找到 {len(dp_restaurants)} 家餐厅")
        print(f"✅ 小红书: 找到 {len(xhs_posts)} 家餐厅\n")

        if not dp_restaurants or not xhs_posts:
            print("⚠️ 数据不足，无法进行交叉验证")
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
        print("Usage: python crosscheck.py <location> <cuisine>")
        print("Example: python crosscheck.py '上海静安区' '日式料理'")
        sys.exit(1)

    location = sys.argv[1]
    cuisine = sys.argv[2]

    checker = RestaurantCrossChecker()
    results = checker.search(location, cuisine)
    output = checker.format_output(results, location, cuisine)

    print(output)


if __name__ == "__main__":
    main()
