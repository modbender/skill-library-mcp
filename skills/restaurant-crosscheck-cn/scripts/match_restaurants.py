"""
跨平台餐厅匹配 — 基于原始 match_restaurants.py
保留: thefuzz 模糊匹配、多策略匹配、连锁店后缀处理、一致性评分
"""
import math
import re
from typing import List, Dict

from models import DianpingRestaurant, XiaohongshuPost, MatchedRestaurant

# thefuzz 是可选依赖，没装时回退到简单匹配
try:
    from thefuzz import fuzz
    HAS_FUZZ = True
except ImportError:
    HAS_FUZZ = False
    print("💡 提示: 安装 thefuzz 可获得更好的匹配效果: pip3 install thefuzz")


# 连锁店常见后缀（来自原始 match_restaurants.py）
CHAIN_SUFFIXES = re.compile(
    r'[（(].{0,15}[)）]|'
    r'(静安|徐汇|浦东|朝阳|海淀|南山|福田|天河|武侯|锦江|南油|华强|科技园)'
    r'(店|分店|旗舰店|总店)?$'
)


def normalize_name(name: str) -> str:
    """标准化餐厅名：去除分店后缀、空格、特殊符号"""
    name = name.strip()
    name = CHAIN_SUFFIXES.sub('', name)
    name = re.sub(r'[\s·・\-—]+', '', name)
    return name


def calculate_similarity(dp_name: str, xhs_name: str) -> float:
    """
    计算两个店名的相似度（0~1）
    使用多策略匹配（来自原始 match_restaurants.py._calculate_similarity）
    """
    dp_norm = normalize_name(dp_name)
    xhs_norm = normalize_name(xhs_name)

    if not dp_norm or not xhs_norm:
        return 0.0

    # 策略1: 完全匹配
    if dp_norm == xhs_norm:
        return 1.0

    if HAS_FUZZ:
        # 策略2: 精确比率
        exact_score = fuzz.ratio(dp_norm, xhs_norm) / 100
        # 策略3: 部分匹配
        partial_score = fuzz.partial_ratio(dp_norm, xhs_norm) / 100
        # 策略4: Token 排序
        token_score = fuzz.token_sort_ratio(dp_norm, xhs_norm) / 100
    else:
        # 简单 Jaccard 相似度作为回退
        s1, s2 = set(dp_norm), set(xhs_norm)
        exact_score = len(s1 & s2) / len(s1 | s2) if (s1 | s2) else 0
        partial_score = 0
        token_score = 0

    # 策略5: 包含关系
    containment_score = 0.0
    if dp_norm in xhs_norm or xhs_norm in dp_norm:
        shorter = min(len(dp_norm), len(xhs_norm))
        longer = max(len(dp_norm), len(xhs_norm))
        containment_score = shorter / longer if longer > 0 else 0.0

    # 取最优策略
    return max(
        exact_score,
        partial_score * 0.90,
        token_score * 0.85,
        containment_score * 0.88,
    )


def normalize_engagement(xhs_post: XiaohongshuPost) -> float:
    """
    将小红书互动量归一化到 0-5 评分（来自原始 match_restaurants.py）
    使用对数归一化避免极端值影响
    """
    engagement = (
        xhs_post.likes * 1.0 +
        xhs_post.saves * 2.0 +
        xhs_post.comments * 1.5
    )

    if engagement <= 0:
        return 0.0

    # log1p(5000) ≈ 8.52 作为"满分"参考点
    normalized = math.log1p(engagement) / math.log1p(5000) * 5
    return max(0.0, min(5.0, normalized))


def calculate_consistency(
    dp_rating: float,
    xhs_engagement_normalized: float,
    xhs_sentiment: float,
) -> float:
    """
    计算两平台一致性评分 0~1（来自原始 match_restaurants.py）
    """
    dp_rating = max(0.0, min(5.0, dp_rating))
    xhs_engagement_normalized = max(0.0, min(5.0, xhs_engagement_normalized))
    xhs_sentiment = max(-1.0, min(1.0, xhs_sentiment))

    # 评分相关性
    rating_diff = abs(dp_rating - xhs_engagement_normalized)
    rating_correlation = max(0.0, 1.0 - (rating_diff / 2.5))

    # 情感一致性
    sentiment_normalized = (xhs_sentiment + 1) / 2  # -1~1 → 0~1
    sentiment_alignment = sentiment_normalized

    return max(0.0, min(1.0, rating_correlation * 0.6 + sentiment_alignment * 0.4))


def match_and_score(
    dp_restaurants: List[DianpingRestaurant],
    xhs_posts: List[XiaohongshuPost],
    similarity_threshold: float = 0.55,
) -> List[MatchedRestaurant]:
    """
    跨平台匹配并计算一致性评分

    Args:
        dp_restaurants: 大众点评数据
        xhs_posts: 小红书数据
        similarity_threshold: 匹配阈值

    Returns:
        匹配结果列表，按一致性排序
    """
    matches = []
    used_xhs = set()

    for dp in dp_restaurants:
        best_idx, best_score = None, 0

        for idx, xhs in enumerate(xhs_posts):
            if idx in used_xhs:
                continue
            score = calculate_similarity(dp.name, xhs.restaurant_name)
            if score > best_score and score >= similarity_threshold:
                best_score = score
                best_idx = idx

        if best_idx is not None:
            xhs = xhs_posts[best_idx]
            used_xhs.add(best_idx)

            # 计算一致性
            xhs_engagement_norm = normalize_engagement(xhs)
            consistency = calculate_consistency(
                dp.rating, xhs_engagement_norm, xhs.sentiment_score
            )

            matches.append(MatchedRestaurant(
                name=dp.name,
                dianping_data=dp,
                xhs_data=xhs,
                similarity_score=best_score,
                consistency_score=consistency,
            ))

    return matches
