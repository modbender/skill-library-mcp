"""Match restaurants across Dianping and Xiaohongshu platforms."""

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


class RestaurantMatcher:
    """Match restaurants from different platforms using fuzzy matching."""

    def __init__(self, similarity_threshold: float = 0.7):
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

    def _calculate_similarity(
        self,
        dp_restaurant: DianpingRestaurant,
        xhs_post: XiaohongshuPost
    ) -> float:
        """
        Calculate similarity score between Dianping restaurant and XHS post.

        Returns score between 0-1.
        """
        # Name similarity (weighted 70%)
        name_score = fuzz.ratio(dp_restaurant.name, xhs_post.restaurant_name) / 100

        # Address similarity (weighted 30%) - if available
        # Note: Xiaohongshu posts typically don't have structured address data
        # This is a placeholder for future enhancement

        # For now, use only name similarity
        final_score = name_score * 0.7

        return final_score


def normalize_engagement(xhs_post: XiaohongshuPost, max_likes: int = 500) -> float:
    """
    Normalize Xiaohongshu engagement to a 0-5 rating scale.

    Args:
        xhs_post: Post with engagement metrics
        max_likes: Expected maximum likes for normalization

    Returns:
        Normalized rating (0-5)
    """
    # Weight different engagement metrics
    engagement_score = (
        (xhs_post.likes * 1.0) +
        (xhs_post.saves * 2.0) +  # Saves are worth more
        (xhs_post.comments * 1.5)
    )

    # Normalize to 0-5 scale
    # For a post with 300 likes, 80 saves, 40 comments:
    # engagement = 300 + 160 + 60 = 520
    # max_engagement = 500 * 4.5 = 2250 (but we use a more reasonable 1000)
    max_engagement = max_likes * 2.0  # More realistic denominator
    normalized = (engagement_score / max_engagement) * 5

    # Clamp to 0-5 range
    return max(0, min(5, normalized))


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
    # Rating correlation (0-1)
    rating_diff = abs(dp_rating - xhs_engagement_normalized)
    rating_correlation = max(0, 1 - (rating_diff / 2))  # Max diff of 2 = 0 correlation

    # Sentiment alignment (convert -1 to 1 range to 0 to 1)
    sentiment_normalized = (xhs_sentiment + 1) / 2  # -1 to 1 -> 0 to 1
    sentiment_alignment = sentiment_normalized

    # Combine metrics
    consistency = (rating_correlation * 0.6) + (sentiment_alignment * 0.4)

    return consistency


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
        similarity_threshold=config.get('similarity_threshold', 0.7)
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
