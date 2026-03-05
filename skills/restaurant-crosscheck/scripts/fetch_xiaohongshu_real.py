"""
Real Xiaohongshu scraper using Playwright with persistent sessions.
"""

import asyncio
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from playwright.async_api import async_playwright, Page, BrowserContext

from session_manager import BrowserSessionManager
from fetch_xiaohongshu import XiaohongshuPost


class XiaohongshuRealFetcher:
    """Fetch real restaurant data from Xiaohongshu using Playwright."""

    def __init__(self, config: Dict):
        self.config = config
        self.session_manager = BrowserSessionManager()
        self.base_url = "https://www.xiaohongshu.com"

    async def search(self, location: str, cuisine: str, min_notes: int = 20) -> List[XiaohongshuPost]:
        """
        Search for restaurant posts by location and cuisine.

        Args:
            location: Geographic area (e.g., "上海静安区")
            cuisine: Cuisine type (e.g., "日式料理")
            min_notes: Minimum number of notes/posts to include

        Returns:
            List of aggregated XiaohongshuPost objects
        """
        # Ensure session is valid
        await self.session_manager.refresh_session_if_needed("xiaohongshu")

        # Get browser context with persistent session
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.session_manager.xhs_session_dir),
                headless=True,
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'
            )

            try:
                # Build search URL
                search_url = self._build_search_url(location, cuisine)

                # Navigate to search page
                page = await context.new_page()
                await page.goto(search_url, wait_until='networkidle')

                # Wait for page to load
                await asyncio.sleep(5)  # Xiaohongshu needs more time

                # Extract post data
                posts = await self._extract_posts(page)

                # Aggregate posts by restaurant name
                aggregated = self._aggregate_by_restaurant(posts)

                # Filter by minimum notes
                filtered = {name: data for name, data in aggregated.items()
                           if len(data['posts']) >= min_notes}

                # Convert to list of aggregated posts
                result = []
                for name, data in filtered.items():
                    avg_post = self._aggregate_post_data(data['posts'])
                    avg_post.restaurant_name = name
                    result.append(avg_post)

                return result

            finally:
                await context.close()

    def _build_search_url(self, location: str, cuisine: str) -> str:
        """Build Xiaohongshu search URL."""
        query = f"{location} {cuisine}".replace(' ', '%20')
        return f"{self.base_url}/search_result?keyword={query}"

    async def _extract_posts(self, page: Page) -> List[XiaohongshuPost]:
        """Extract post data from page."""
        posts = []

        try:
            # Wait for search results to load
            await page.wait_for_selector('.note-item', timeout=15000)

            # Get all note items
            note_items = await page.query_selector_all('.note-item')

            for item in note_items[:30]:  # Limit to first 30
                try:
                    post = await self._parse_post_item(item)
                    if post and self._is_restaurant_post(post):
                        posts.append(post)
                except Exception as e:
                    print(f"⚠️ 解析笔记失败: {e}")
                    continue

        except Exception as e:
            print(f"⚠️ 提取笔记列表失败: {e}")
            # Return empty list on failure
            return []

        return posts

    async def _parse_post_item(self, item) -> Optional[XiaohongshuPost]:
        """Parse a single post item."""
        try:
            # Extract title (may contain restaurant name)
            title_elem = await item.query_selector('.title')
            title = await title_elem.inner_text() if title_elem else ""

            # Extract engagement metrics
            likes_elem = await item.query_selector('.like-count')
            likes_text = await likes_elem.inner_text() if likes_elem else "0"
            likes = self._parse_count(likes_text)

            saves_elem = await item.query_selector('.collect-count')
            saves_text = await saves_elem.inner_text() if saves_elem else "0"
            saves = self._parse_count(saves_text)

            comments_elem = await item.query_selector('.comment-count')
            comments_text = await comments_elem.inner_text() if comments_elem else "0"
            comments = self._parse_count(comments_text)

            # Extract URL
            url_elem = await item.query_selector('a')
            url = await url_elem.get_attribute('href') if url_elem else ""
            if url and not url.startswith('http'):
                url = self.base_url + url

            # Extract restaurant name from title
            restaurant_name = self._extract_restaurant_name(title)

            # Simple sentiment analysis based on title
            sentiment_score = self._analyze_sentiment(title)

            # Extract keywords from title
            keywords = self._extract_keywords(title)

            return XiaohongshuPost(
                restaurant_name=restaurant_name,
                likes=likes,
                saves=saves,
                comments=comments,
                sentiment_score=sentiment_score,
                keywords=keywords,
                url=url
            )

        except Exception as e:
            print(f"⚠️ 解析笔记详情失败: {e}")
            return None

    def _parse_count(self, count_text: str) -> int:
        """Parse count from text (handles 1.2万, etc)."""
        count_text = count_text.strip()
        if '万' in count_text:
            match = re.search(r'([\d.]+)万', count_text)
            if match:
                return int(float(match.group(1)) * 10000)
        match = re.search(r'(\d+)', count_text.replace(',', ''))
        if match:
            return int(match.group(1))
        return 0

    def _extract_restaurant_name(self, title: str) -> str:
        """Extract restaurant name from post title."""
        # Remove common prefixes and suffixes
        name = title.strip()

        # Remove common patterns
        patterns_to_remove = [
            r'^.{0,5}(在|去|打卡|探店)',
            r'(太好吃了|超赞|推荐|必吃).{0,10}$',
            r'[💕🔥✨🌟📍]'
        ]

        for pattern in patterns_to_remove:
            name = re.sub(pattern, '', name)

        return name.strip()

    def _is_restaurant_post(self, post: XiaohongshuPost) -> bool:
        """Check if post is about a restaurant."""
        # Simple heuristic: contains food-related keywords
        food_keywords = ['店', '餐厅', '料理', '火锅', '烤肉', '日料', '西餐']
        return any(kw in post.restaurant_name for kw in food_keywords)

    def _analyze_sentiment(self, text: str) -> float:
        """Simple sentiment analysis."""
        positive_keywords = ['好吃', '美味', '推荐', '值得', '喜欢', '棒', '赞', '完美', '正宗']
        negative_keywords = ['难吃', '失望', '差评', '不推荐', '避雷', '贵', '差']

        positive_count = sum(1 for kw in positive_keywords if kw in text)
        negative_count = sum(1 for kw in negative_keywords if kw in text)

        total = positive_count + negative_count
        if total == 0:
            return 0.0

        return (positive_count - negative_count) / total

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        keywords = []
        keyword_list = ['好吃', '美味', '环境', '服务', '性价比', '新鲜', '正宗', '值得']
        for kw in keyword_list:
            if kw in text:
                keywords.append(kw)
        return keywords[:5]

    def _aggregate_by_restaurant(self, posts: List[XiaohongshuPost]) -> Dict[str, Dict]:
        """Group posts by restaurant name."""
        aggregated = {}
        for post in posts:
            if post.restaurant_name not in aggregated:
                aggregated[post.restaurant_name] = {'posts': []}
            aggregated[post.restaurant_name]['posts'].append(post)
        return aggregated

    def _aggregate_post_data(self, posts: List[XiaohongshuPost]) -> XiaohongshuPost:
        """Calculate average metrics from multiple posts."""
        total_posts = len(posts)
        avg_likes = sum(p.likes for p in posts) // total_posts
        avg_saves = sum(p.saves for p in posts) // total_posts
        avg_comments = sum(p.comments for p in posts) // total_posts
        avg_sentiment = sum(p.sentiment_score for p in posts) / total_posts

        # Combine keywords
        all_keywords = []
        for post in posts:
            all_keywords.extend(post.keywords)
        # Get top keywords
        keyword_counts = {}
        for kw in all_keywords:
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_keywords_list = [kw for kw, count in top_keywords]

        return XiaohongshuPost(
            restaurant_name="",  # Will be set by caller
            likes=avg_likes,
            saves=avg_saves,
            comments=avg_comments,
            sentiment_score=avg_sentiment,
            keywords=top_keywords_list,
            url=posts[0].url  # First post URL
        )


async def fetch_xiaohongshu_real(location: str, cuisine: str, config: Dict) -> List[XiaohongshuPost]:
    """Convenience function to fetch Xiaohongshu data with real scraping."""
    fetcher = XiaohongshuRealFetcher(config)
    return await fetcher.search(location, cuisine)
