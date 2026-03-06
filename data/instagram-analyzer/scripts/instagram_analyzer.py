#!/usr/bin/env python3
"""
Instagram Analyzer - Profile and Post Analytics Tool
Analyzes Instagram profiles and posts with engagement metrics.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from playwright.sync_api import sync_playwright
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Install with: pip install playwright beautifulsoup4 lxml")
    print("Then run: playwright install chromium")
    sys.exit(1)


class InstagramAnalyzer:
    """Instagram Profile and Post Analyzer"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.data_dir = Path(self.config.get("output", {}).get("data_dir", "data"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, config_path: str = None) -> dict:
        """Load configuration from JSON file"""
        if not config_path:
            config_path = os.environ.get(
                "INSTAGRAM_ANALYZER_CONFIG",
                "config/analyzer_config.json"
            )
        
        default_config = {
            "scraper": {
                "headless": True,
                "min_followers": 1000,
                "posts_to_analyze": 60,
                "reels_only": False,
                "scroll_pause": 2,
                "timeout": 30000
            },
            "browser": {
                "stealth_mode": True,
                "human_behavior": True,
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)"
            },
            "output": {
                "default_format": "json",
                "save_reels_links": True,
                "export_csv": False
            }
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _parse_number(self, text: str) -> int:
        """Parse Instagram number format (K, M, B suffixes)"""
        text = text.strip().upper().replace(',', '')
        
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
        
        for suffix, multiplier in multipliers.items():
            if suffix in text:
                return int(float(text.replace(suffix, '')) * multiplier)
        
        try:
            return int(text)
        except ValueError:
            return 0
    
    def _parse_time_ago(self, time_text: str) -> dict:
        """Parse '2 hours ago', '3 days ago', etc."""
        time_text = time_text.lower().strip()
        
        # Extract number
        import re
        match = re.search(r'(\d+)', time_text)
        if not match:
            return {"raw": time_text, "hours": 0, "days": 0, "text": time_text}
        
        number = int(match.group(1))
        
        if 'hour' in time_text:
            hours = number
            days = round(number / 24, 1)
        elif 'day' in time_text:
            hours = number * 24
            days = number
        elif 'week' in time_text:
            hours = number * 24 * 7
            days = number * 7
        elif 'month' in time_text:
            hours = number * 24 * 30
            days = number * 30
        else:
            hours = 0
            days = 0
        
        return {
            "raw": time_text,
            "hours": hours,
            "days": days,
            "text": time_text
        }
    
    def analyze_post(self, post_url: str, output_format: str = "json") -> dict:
        """Analyze a single Instagram post/Reel"""
        result = {
            "url": post_url,
            "post_type": "reel" if "/reel/" in post_url else "post",
            "username": "",
            "metrics": {},
            "ratios": {},
            "timing": {},
            "error": None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"📊 Analyzing: {post_url}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.config["scraper"]["headless"])
            context = browser.new_context(
                user_agent=self.config["browser"]["user_agent"],
                viewport={"width": 390, "height": 844}  # iPhone dimensions
            )
            page = context.new_page()
            
            try:
                page.goto(post_url, timeout=self.config["scraper"]["timeout"])
                time.sleep(3)  # Wait for page load
                
                # Extract username from page
                username_elem = page.query_selector('header a[href^="/"]')
                if username_elem:
                    href = username_elem.get_attribute("href")
                    result["username"] = href.strip("/")
                
                # Get page content
                content = page.content()
                soup = BeautifulSoup(content, 'lxml')
                
                # Extract metrics - this is a simplified version
                # Real implementation would need more sophisticated selectors
                metrics = {}
                
                # Views (for Reels)
                view_elem = page.query_selector('span[class*="view"]')
                if view_elem:
                    view_text = view_elem.inner_text()
                    metrics["views"] = self._parse_number(view_text)
                
                # Likes
                like_elem = page.query_selector('section span[class*="like"]')
                if not like_elem:
                    like_elem = page.query_selector('svg[aria-label="Like"]')
                if like_elem:
                    like_text = like_elem.inner_text()
                    metrics["likes"] = self._parse_number(like_text)
                
                # Comments
                comment_elem = page.query_selector('li[class*="comment"]')
                if comment_elem:
                    comment_text = comment_elem.inner_text()
                    metrics["comments"] = self._parse_number(comment_text)
                
                result["metrics"] = metrics
                
                # Calculate ratios if followers known
                if metrics.get("views") and result["username"]:
                    followers = self.get_follower_count(result["username"])
                    if followers:
                        result["metrics"]["followers"] = followers
                        result["ratios"]["view_to_follower_percent"] = round(
                            (metrics["views"] / followers) * 100, 2
                        )
                
                # Time posted
                time_elem = page.query_selector('time')
                if time_elem:
                    datetime_attr = time_elem.get_attribute("datetime")
                    if datetime_attr:
                        result["timing"]["posted_at"] = datetime_attr
                    
                    time_text = time_elem.get_attribute("title") or time_elem.inner_text()
                    if time_text:
                        result["timing"]["time_ago"] = time_text
                        result["timing"]["parsed"] = self._parse_time_ago(time_text)
                
                # Save result
                output_file = self.data_dir / "posts" / f"post_{int(time.time())}.json"
                output_file.parent.mkdir(exist_ok=True)
                
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                
                print(f"✅ Analysis saved to: {output_file}")
                
            except Exception as e:
                result["error"] = str(e)
                print(f"❌ Error analyzing post: {e}")
            
            finally:
                browser.close()
        
        # Output
        if output_format == "json":
            print("\n" + json.dumps(result, indent=2))
        
        return result
    
    def get_follower_count(self, username: str) -> int:
        """Get follower count for a username"""
        # This would need full profile page scraping
        # Simplified placeholder
        return 0
    
    def analyze_profile(self, username: str, posts_limit: int = 60, 
                       reels_only: bool = True, output_format: str = "json") -> dict:
        """Analyze an Instagram profile with multiple posts (DEFAULT: Reels Only!)"""
        
        result = {
            "profile": {
                "username": username,
                "full_name": "",
                "followers": 0,
                "following": 0,
                "posts_count": 0,
                "is_verified": False
            },
            "analysis": {
                "posts_analyzed": 0,
                "reels_analyzed": 0,
                "posts": [],
                "reels_links": [],
                "engagement_summary": {}
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"👤 Analyzing profile: @{username}")
        
        profile_url = f"https://www.instagram.com/{username}/"
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.config["scraper"]["headless"])
            context = browser.new_context(
                user_agent=self.config["browser"]["user_agent"]
            )
            page = context.new_page()
            
            try:
                page.goto(profile_url, timeout=self.config["scraper"]["timeout"])
                time.sleep(3)
                
                # Extract profile info
                content = page.content()
                soup = BeautifulSoup(content, 'lxml')
                
                # Profile stats would be extracted here
                # This is a placeholder for the actual scraping logic
                
                print(f"📊 Analyzing posts (limit: {posts_limit})")
                
                # Scroll and collect post links
                posts_collected = []
                scroll_count = 0
                max_scrolls = posts_limit // 12 + 5  # ~12 posts per scroll
                
                while len(posts_collected) < posts_limit and scroll_count < max_scrolls:
                    # Extract post links from page
                    post_links = page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
                    
                    for link in post_links:
                        href = link.get_attribute("href")
                        if href and href not in [p["url"] for p in posts_collected]:
                            posts_collected.append({
                                "url": f"https://instagram.com{href}",
                                "type": "reel" if "/reel/" in href else "post"
                            })
                    
                    # Scroll down
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(self.config["scraper"]["scroll_pause"])
                    scroll_count += 1
                    
                    print(f"   Scroll {scroll_count}: {len(posts_collected)} posts found")
                
                # Filter and limit
                if reels_only:
                    posts_collected = [p for p in posts_collected if p["type"] == "reel"]
                
                posts_collected = posts_collected[:posts_limit]
                
                # Analyze each post
                total_likes = 0
                total_comments = 0
                total_saves = 0
                total_views = 0
                
                for i, post in enumerate(posts_collected, 1):
                    print(f"   [{i}/{len(posts_collected)}] Analyzing: {post['url']}")
                    
                    # Analyze post (simplified - would need full page load)
                    post_data = self.analyze_post(post["url"], output_format="json")
                    
                    if post["type"] == "reel":
                        result["analysis"]["reels_links"].append(post["url"])
                        result["analysis"]["reels_analyzed"] += 1
                        
                        metrics = post_data.get("metrics", {})
                        total_views += metrics.get("views", 0)
                    
                    total_likes += post_data.get("metrics", {}).get("likes", 0)
                    total_comments += post_data.get("metrics", {}).get("comments", 0)
                    total_saves += post_data.get("metrics", {}).get("saves", 0)
                    
                    result["analysis"]["posts"].append(post_data)
                
                result["analysis"]["posts_analyzed"] = len(posts_collected)
                
                # Calculate engagement summary
                posts_count = len(posts_collected)
                if posts_count > 0:
                    result["analysis"]["engagement_summary"] = {
                        "total_likes": total_likes,
                        "total_comments": total_comments,
                        "total_saves": total_saves,
                        "avg_likes": round(total_likes / posts_count, 0),
                        "avg_comments": round(total_comments / posts_count, 0),
                        "avg_saves": round(total_saves / posts_count, 0),
                        "total_views": total_views,
                        "avg_views": round(total_views / posts_count, 0) if total_views > 0 else 0
                    }
                
                # Save results
                output_file = self.data_dir / "profiles" / f"{username}_{int(time.time())}.json"
                output_file.parent.mkdir(exist_ok=True)
                
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                
                print(f"✅ Profile analysis saved to: {output_file}")
                
                # Save reels links separately
                if result["analysis"]["reels_links"]:
                    reels_file = self.data_dir / "output" / f"{username}_reels.txt"
                    reels_file.parent.mkdir(exist_ok=True)
                    
                    with open(reels_file, 'w') as f:
                        f.write("\n".join(result["analysis"]["reels_links"]))
                    
                    print(f"✅ Reels links saved to: {reels_file}")
                
            except Exception as e:
                result["error"] = str(e)
                print(f"❌ Error analyzing profile: {e}")
            
            finally:
                browser.close()
        
        # Output
        if output_format == "json":
            print("\n" + json.dumps(result, indent=2))
        
        return result


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Instagram Analyzer - Profile and Post Analytics"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Post analysis
    post_parser = subparsers.add_parser("post", help="Analyze single post")
    post_parser.add_argument("url", help="Instagram post/Reel URL")
    post_parser.add_argument("--output", "-o", default="json", choices=["json", "csv"])
    
    # Profile analysis
    profile_parser = subparsers.add_parser("profile", help="Analyze Instagram profile (DEFAULT: Reels Only!)")
    profile_parser.add_argument("username", help="Instagram username")
    profile_parser.add_argument("--posts", "-p", type=int, default=60, 
                               help="Number of posts to analyze (default: 60)")
    profile_parser.add_argument("--include-posts", "-i", action="store_true",
                              help="Include regular posts (default: Reels only)")
    profile_parser.add_argument("--output", "-o", default="json", choices=["json", "csv"])
    
    # Config
    parser.add_argument("--config", "-c", help="Config file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    analyzer = InstagramAnalyzer(config_path=args.config)
    
    if args.command == "post":
        result = analyzer.analyze_post(args.url, args.output)
        sys.exit(0 if not result.get("error") else 1)
    
    elif args.command == "profile":
        result = analyzer.analyze_profile(
            args.username, 
            posts_limit=args.posts,
            reels_only=not args.include_posts,  # Default: Reels Only!
            output_format=args.output
        )
        sys.exit(0 if not result.get("error") else 1)


if __name__ == "__main__":
    main()
