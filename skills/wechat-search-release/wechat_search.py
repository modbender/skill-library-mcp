#!/usr/bin/env python3
"""
WeChat Search Skill - Search WeChat Official Account articles using OpenClaw's web search and fetch tools.
Returns the most recent 5 articles by default, with configurable options.
"""

import json
import sys
import os
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import subprocess


class WeChatSearch:
    def __init__(self, config_path=None):
        self.config = self.load_config(config_path)
        
    def load_config(self, config_path):
        """Load configuration from file or use defaults"""
        default_config = {
            "max_results": 5,
            "search_strategy": "web_search_first",
            "cache_duration_hours": 1,
            "request_delay_ms": 5000,
            "user_agent": "OpenClaw-WeChat-Search-Bot/1.0"
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Failed to load config file: {e}", file=sys.stderr)
                
        return default_config

    def web_search_wechat(self, query, max_results=5):
        """Use OpenClaw's web_search tool to search WeChat articles"""
        try:
            # Construct search query with site restriction
            search_query = f'{query} site:mp.weixin.qq.com'
            
            # Call OpenClaw's web_search tool
            result = subprocess.run([
                'openclaw', 'tool', 'web_search',
                '--query', search_query,
                '--count', str(max_results)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                search_data = json.loads(result.stdout)
                return self.parse_search_results(search_data, max_results)
            else:
                print(f"Web search failed: {result.stderr}", file=sys.stderr)
                return []
                
        except Exception as e:
            print(f"Web search error: {e}", file=sys.stderr)
            return []

    def web_fetch_wechat(self, query, max_results=5):
        """Use OpenClaw's web_fetch tool to fetch WeChat search results"""
        try:
            # Construct WeChat search URL
            search_url = f"https://weixin.sogou.com/weixin?type=2&query={query}"
            
            # Call OpenClaw's web_fetch tool
            result = subprocess.run([
                'openclaw', 'tool', 'web_fetch',
                '--url', search_url,
                '--extract-mode', 'markdown'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                content = result.stdout
                return self.parse_fetch_results(content, max_results)
            else:
                print(f"Web fetch failed: {result.stderr}", file=sys.stderr)
                return []
                
        except Exception as e:
            print(f"Web fetch error: {e}", file=sys.stderr)
            return []

    def parse_search_results(self, search_data, max_results):
        """Parse web search results into standardized format"""
        articles = []
        
        for item in search_data.get('results', []):
            article = {
                'title': item.get('title', '').strip(),
                'url': item.get('url', '').strip(),
                'snippet': item.get('snippet', '').strip(),
                'source': 'web_search',
                'published_at': None  # Web search doesn't provide precise dates
            }
            
            # Extract official account name from title or URL
            if ' - ' in article['title']:
                parts = article['title'].split(' - ')
                article['official_account'] = parts[-1]
                article['title'] = ' - '.join(parts[:-1])
            else:
                article['official_account'] = self.extract_account_from_url(article['url'])
            
            # Validate WeChat article URL
            if self.is_valid_wechat_url(article['url']):
                articles.append(article)
                
            if len(articles) >= max_results:
                break
                
        return articles

    def parse_fetch_results(self, content, max_results):
        """Parse web fetch results (placeholder - would need HTML parsing)"""
        # This is a simplified version - actual implementation would need
        # proper HTML parsing of WeChat search results
        articles = []
        
        # For now, return empty list as web_fetch requires complex HTML parsing
        # In practice, this would use BeautifulSoup or similar
        print("Note: Web fetch parsing not fully implemented in this version", file=sys.stderr)
        
        return articles

    def extract_account_from_url(self, url):
        """Extract official account name from WeChat URL"""
        try:
            parsed = urlparse(url)
            if 'mp.weixin.qq.com' in parsed.netloc:
                # Try to extract from query parameters or path
                query_params = parse_qs(parsed.query)
                if 'account' in query_params:
                    return query_params['account'][0]
            return "Unknown Account"
        except:
            return "Unknown Account"

    def is_valid_wechat_url(self, url):
        """Check if URL is a valid WeChat Official Account article"""
        try:
            parsed = urlparse(url)
            if 'mp.weixin.qq.com' not in parsed.netloc:
                return False
            # Valid WeChat URLs have /s in the path (covers /s/, /s?, /s/xxx, etc.)
            return '/s' in parsed.path
        except:
            return False

    def search(self, query, max_results=None, strategy=None):
        """Main search function with fallback logic"""
        if max_results is None:
            max_results = self.config['max_results']
        if strategy is None:
            strategy = self.config['search_strategy']
            
        articles = []
        
        if strategy in ['web_search_first', 'web_search_only']:
            # Try web search first
            articles = self.web_search_wechat(query, max_results)
            
            # Fallback to web fetch if needed
            if not articles and strategy == 'web_search_first':
                print("Web search returned no results, trying web fetch...", file=sys.stderr)
                articles = self.web_fetch_wechat(query, max_results)
                
        elif strategy == 'web_fetch_only':
            articles = self.web_fetch_wechat(query, max_results)
            
        # Ensure we return exactly max_results articles
        return articles[:max_results]

    def format_results(self, articles, brief=False):
        """Format search results for display"""
        if not articles:
            return "No WeChat Official Account articles found for your query."
            
        output = []
        for i, article in enumerate(articles, 1):
            if brief:
                output.append(f"{i}. {article['title']}")
                output.append(f"   {article['url']}")
            else:
                # Extract date from snippet if possible (simplified)
                date_info = "Unknown date"
                if article.get('published_at'):
                    date_info = article['published_at'].strftime('%Y-%m-%d')
                elif '...' in article['snippet']:
                    # Try to find date pattern in snippet
                    date_match = re.search(r'\d{4}-\d{2}-\d{2}', article['snippet'])
                    if date_match:
                        date_info = date_match.group()
                
                output.append(f"{i}. [{article['official_account']}] {article['title']} - {date_info}")
                snippet_preview = article['snippet'][:100] + "..." if len(article['snippet']) > 100 else article['snippet']
                output.append(f"   {snippet_preview}")
                output.append(f"   {article['url']}")
                output.append("")
                
        return "\n".join(output).strip()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Search WeChat Official Account articles")
    parser.add_argument('query', help="Search query")
    parser.add_argument('--max-results', type=int, default=5, 
                       help="Maximum number of results (default: 5, max: 20)")
    parser.add_argument('--strategy', choices=['web_search_first', 'web_search_only', 'web_fetch_only'],
                       default='web_search_first', help="Search strategy")
    parser.add_argument('--brief', action='store_true', help="Brief output (title and URL only)")
    parser.add_argument('--config', help="Path to configuration file")
    
    args = parser.parse_args()
    
    # Validate max_results
    if args.max_results < 1 or args.max_results > 20:
        print("Error: --max-results must be between 1 and 20", file=sys.stderr)
        sys.exit(1)
    
    try:
        searcher = WeChatSearch(args.config)
        articles = searcher.search(args.query, args.max_results, args.strategy)
        output = searcher.format_results(articles, args.brief)
        print(output)
        
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()