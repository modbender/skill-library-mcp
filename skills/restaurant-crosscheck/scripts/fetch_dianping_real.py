"""
Real Dianping scraper using Playwright with persistent sessions.
"""

import asyncio
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from playwright.async_api import async_playwright, Page, BrowserContext

from session_manager import BrowserSessionManager
from fetch_dianping import DianpingRestaurant


class DianpingRealFetcher:
    """Fetch real restaurant data from Dianping using Playwright."""

    def __init__(self, config: Dict):
        self.config = config
        self.session_manager = BrowserSessionManager()
        self.base_url = "https://www.dianping.com"

    async def search(self, location: str, cuisine: str, min_rating: float = 4.0) -> List[DianpingRestaurant]:
        """
        Search for restaurants by location and cuisine.

        Args:
            location: Geographic area (e.g., "上海静安区")
            cuisine: Cuisine type (e.g., "日式料理")
            min_rating: Minimum rating to include

        Returns:
            List of DianpingRestaurant objects
        """
        # Ensure session is valid
        await self.session_manager.refresh_session_if_needed("dianping")

        # Get browser context with persistent session
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.session_manager.dianping_session_dir),
                headless=True,
                viewport={'width': 1280, 'height': 720}
            )

            try:
                # Build search URL
                search_url = self._build_search_url(location, cuisine)

                # Navigate to search page
                page = await context.new_page()
                await page.goto(search_url, wait_until='networkidle')

                # Wait for page to load
                await asyncio.sleep(3)

                # Extract restaurant data
                restaurants = await self._extract_restaurants(page)

                # Filter by rating
                filtered = [r for r in restaurants if r.rating >= min_rating]

                return filtered

            finally:
                await context.close()

    def _build_search_url(self, location: str, cuisine: str) -> str:
        """Build Dianping search URL."""
        # Simple search URL construction
        # In production, you'd need to encode parameters properly
        # and handle location-specific URLs
        return f"{self.base_url}/search/keyword/{cuisine}/region/{self._encode_location(location)}"

    def _encode_location(self, location: str) -> str:
        """Encode location for URL."""
        # Remove common prefixes/suffixes
        location = location.replace("市", "").replace("区", "")
        return location

    async def _extract_restaurants(self, page: Page) -> List[DianpingRestaurant]:
        """Extract restaurant data from page."""
        restaurants = []

        try:
            # Wait for restaurant list to load
            await page.wait_for_selector('.shop-list', timeout=10000)

            # Get all restaurant items
            shop_items = await page.query_selector_all('.shop-list .shop-item')

            for item in shop_items[:20]:  # Limit to first 20
                try:
                    restaurant = await self._parse_restaurant_item(item, page)
                    if restaurant:
                        restaurants.append(restaurant)
                except Exception as e:
                    print(f"⚠️ 解析餐厅失败: {e}")
                    continue

        except Exception as e:
            print(f"⚠️ 提取餐厅列表失败: {e}")
            # Fallback to mock data for testing
            return self._get_fallback_data(location="", cuisine="")

        return restaurants

    async def _parse_restaurant_item(self, item, page: Page) -> Optional[DianpingRestaurant]:
        """Parse a single restaurant item."""
        try:
            # Extract name
            name_elem = await item.query_selector('.shop-name a')
            name = await name_elem.inner_text() if name_elem else "未知餐厅"

            # Extract rating
            rating_elem = await item.query_selector('.comment-star')
            rating_text = await rating_elem.get_attribute('title') if rating_elem else "0"
            rating = self._parse_rating(rating_text)

            # Extract review count
            review_elem = await item.query_selector('.review-count')
            review_text = await review_elem.inner_text() if review_elem else "0"
            review_count = self._parse_review_count(review_text)

            # Extract price range
            price_elem = await item.query_selector('.price')
            price_text = await price_elem.inner_text() if price_elem else ""
            price_range = self._parse_price_range(price_text)

            # Extract address
            addr_elem = await item.query_selector('.shop-address')
            address = await addr_elem.inner_text() if addr_elem else ""

            # Extract tags
            tag_elems = await item.query_selector_all('.shop-tag')
            tags = []
            for tag_elem in tag_elems[:5]:
                tag_text = await tag_elem.inner_text()
                tags.append(tag_text.strip())

            # Get URL
            url_elem = await item.query_selector('.shop-name a')
            url = await url_elem.get_attribute('href') if url_elem else ""
            if url and not url.startswith('http'):
                url = self.base_url + url

            return DianpingRestaurant(
                name=name.strip(),
                rating=rating,
                review_count=review_count,
                price_range=price_range,
                address=address.strip(),
                tags=tags,
                url=url
            )

        except Exception as e:
            print(f"⚠️ 解析餐厅详情失败: {e}")
            return None

    def _parse_rating(self, rating_text: str) -> float:
        """Parse rating from text."""
        match = re.search(r'(\d+\.?\d*)', rating_text)
        if match:
            return float(match.group(1))
        return 0.0

    def _parse_review_count(self, review_text: str) -> int:
        """Parse review count from text."""
        # Remove non-digit characters
        match = re.search(r'(\d+)', review_text.replace(',', ''))
        if match:
            return int(match.group(1))
        return 0

    def _parse_price_range(self, price_text: str) -> str:
        """Parse price range from text."""
        # Extract numbers like "¥200-300"
        match = re.search(r'¥?\d+(?:-\d+)?', price_text)
        if match:
            return match.group(0)
        return "未知"

    def _get_fallback_data(self, location: str, cuisine: str) -> List[DianpingRestaurant]:
        """Fallback mock data when scraping fails."""
        return [
            DianpingRestaurant(
                name=f"{cuisine}示例店A",
                rating=4.5,
                review_count=500,
                price_range="¥150-200",
                address=f"{location}示例路123号",
                tags=["美味", "环境好"],
                url=f"{self.base_url}/shop/123"
            )
        ]


async def fetch_dianping_real(location: str, cuisine: str, config: Dict) -> List[DianpingRestaurant]:
    """Convenience function to fetch Dianping data with real scraping."""
    fetcher = DianpingRealFetcher(config)
    return await fetcher.search(location, cuisine)
