"""Match restaurants across Dianping and Xiaohongshu platforms."""

import math
import re
from typing import List, Tuple, Dict
from dataclasses import dataclass
from thefuzz import fuzz

from fetch_dianping import DianpingRestaurant
from fetch_xiaohongshu import XiaohongshuPost


@dataclass
class MatchedRestaurant:
    """Restaurant matched across both platforms."""
    name: str
    dianping_data: DianpingRestaurant
    xhs_data: XiaohongshuPost
    similarity_score: float  # 0-1, how confident the match is
    consistency_score: float = 0.0  # 显式声明，避免 hasattr 检查


class RestaurantMatcher:
    """Match restaurants from different platforms using fuzzy matching."""

    # 连锁店常见后缀，匹配时可忽略
    CHAIN_SUFFIXES = re.compile(
        r'[（(].{0,10}[)）]|'
        r'(静安|徐汇|浦东|朝阳|海淀|南山|福田|天河|武侯|锦江)'
        r'(店|分店|旗舰店|总店)?$'
    )

    def __init__(self, similarity_threshold: float = 0.6):
        self.similarity_threshold = similarity_threshold

    def match(
        self,
        dianping_restaurants: List[DianpingRestaurant],
        xhs_posts: List[XiaohongshuPost]
    ) -> List[MatchedRestaurant]:
        """
        Match Dianping restaurants with Xiaohongshu posts.

        Args:
            dianping_restaurants: List from Dianping
            xhs_posts: List from Xiaohongshu

        Returns:
            List of matched restaurants with confidence scores
        """
        matches = []
        used_xhs_indices = set()

        for dp_restaurant in dianping_restaurants:
            best_match_idx = None
            best_score = 0

            for idx, xhs_post in enumerate(xhs_posts):
                if idx in used_xhs_indices:
                    continue

                # Calculate similarity score
                score = self._calculate_similarity(dp_restaurant, xhs_post)

                if score > best_score and score >= self.similarity_threshold:
                    best_score = score
                    best_match_idx = idx

            if best_match_idx is not None:
                matches.append(MatchedRestaurant(
                    name=dp_restaurant.name,
                    dianping_data=dp_restaurant,
                    xhs_data=xhs_posts[best_match_idx],
                    similarity_score=best_score
                ))
                used_xhs_indices.add(best_match_idx)

        return matches

    def _normalize_name(self, name: str) -> str:
        """标准化餐厅名：去除分店后缀、空格、特殊符号。"""
        name = name.strip()
        name = self.CHAIN_SUFFIXES.sub('', name)
        name = re.sub(r'[\s·・\-—]+', '', name)
        return name

    def _calculate_similarity(
        self,
        dp_restaurant: DianpingRestaurant,
        xhs_post: XiaohongshuPost
    ) -> float:
        """
        Calculate similarity score between Dianping restaurant and XHS post.
        Uses multi-strategy matching for robustness.

        Returns score between 0-1.
        """
        dp_name = dp_restaurant.name
        xhs_name = xhs_post.restaurant_name

        # 标准化名称
        dp_norm = self._normalize_name(dp_name)
        xhs_norm = self._normalize_name(xhs_name)

        if not dp_norm or not xhs_norm:
            return 0.0

        # 策略1: 完全匹配（标准化后）
        if dp_norm == xhs_norm:
            return 1.0

        # 策略2: 精确比率 — 整体字符串相似度
        exact_score = fuzz.ratio(dp_norm, xhs_norm) / 100

        # 策略3: 部分匹配 — 一个名字包含另一个
        partial_score = fuzz.partial_ratio(dp_norm, xhs_norm) / 100

        # 策略4: Token排序 — 处理词序差异
        token_score = fuzz.token_sort_ratio(dp_norm, xhs_norm) / 100

        # 策略5: 包含关系 — 一个名字是另一个的子串
        containment_score = 0.0
        if dp_norm in xhs_norm or xhs_norm in dp_norm:
            shorter = min(len(dp_norm), len(xhs_norm))
            longer = max(len(dp_norm), len(xhs_norm))
            containment_score = shorter / longer if longer > 0 else 0.0

        # 取最优策略的结果
        final_score = max(
            exact_score,
            partial_score * 0.90,   # 部分匹配略降权
            token_score * 0.85,     # token匹配再降权
            containment_score * 0.88
        )

        return final_score


def normalize_engagement(xhs_post: XiaohongshuPost, all_posts: List = None) -> float:
    """
    Normalize Xiaohongshu engagement to a 0-5 rating scale.
    Uses log normalization to handle extreme values gracefully.

    Args:
        xhs_post: Post with engagement metrics
        all_posts: Optional list of all posts for dynamic normalization

    Returns:
        Normalized rating (0-5)
    """
    # Weight different engagement metrics
    engagement_score = (
        (xhs_post.likes * 1.0) +
        (xhs_post.saves * 2.0) +  # Saves are worth more
        (xhs_post.comments * 1.5)
    )

    if all_posts and len(all_posts) > 1:
        # 动态归一化：基于当前批次数据
        all_scores = [
            p.likes * 1.0 + p.saves * 2.0 + p.comments * 1.5
            for p in all_posts
        ]
        max_score = max(all_scores) if all_scores else 1
        if max_score > 0:
            normalized = (engagement_score / max_score) * 5
        else:
            normalized = 0
    else:
        # 对数归一化：避免极端值影响，适应不同量级
        # log1p(5000) ≈ 8.52，作为"满分"参考点
        if engagement_score <= 0:
            normalized = 0
        else:
            normalized = math.log1p(engagement_score) / math.log1p(5000) * 5

    # Clamp to 0-5 range
    return max(0.0, min(5.0, normalized))


def calculate_consistency(
    dp_rating: float,
    xhs_engagement_normalized: float,
    xhs_sentiment: float
) -> float:
    """
    Calculate consistency score between platforms.

    Args:
        dp_rating: Dianping rating (0-5)
        xhs_engagement_normalized: XHS engagement normalized to 0-5
        xhs_sentiment: XHS sentiment score (-1 to 1)

    Returns:
        Consistency score (0-1)
    """
    # 输入安全 clamp
    dp_rating = max(0.0, min(5.0, dp_rating))
    xhs_engagement_normalized = max(0.0, min(5.0, xhs_engagement_normalized))
    xhs_sentiment = max(-1.0, min(1.0, xhs_sentiment))

    # Rating correlation (0-1)
    rating_diff = abs(dp_rating - xhs_engagement_normalized)
    rating_correlation = max(0.0, 1.0 - (rating_diff / 2.5))  # 更宽容的差值容忍度

    # Sentiment alignment (convert -1 to 1 range to 0 to 1)
    sentiment_normalized = (xhs_sentiment + 1) / 2  # -1 to 1 -> 0 to 1
    sentiment_alignment = sentiment_normalized

    # Combine metrics
    consistency = (rating_correlation * 0.6) + (sentiment_alignment * 0.4)

    # 最终 clamp
    return max(0.0, min(1.0, consistency))


def match_and_score(
    dianping_restaurants: List[DianpingRestaurant],
    xhs_posts: List[XiaohongshuPost],
    config: Dict
) -> List[MatchedRestaurant]:
    """
    Match restaurants and calculate scores.

    Returns list sorted by recommendation score.
    """
    # Match restaurants
    matcher = RestaurantMatcher(
        similarity_threshold=config.get('similarity_threshold', 0.6)
    )
    matches = matcher.match(dianping_restaurants, xhs_posts)

    # Calculate consistency for each match
    for match in matches:
        xhs_engagement_norm = normalize_engagement(match.xhs_data)
        consistency = calculate_consistency(
            match.dianping_data.rating,
            xhs_engagement_norm,
            match.xhs_data.sentiment_score
        )
        # Store consistency for later use
        match.consistency_score = consistency

    return matches
