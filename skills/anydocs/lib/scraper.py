"""Web scraping engine for documentation discovery and extraction."""

import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Any, Optional, Set
import logging

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logger = logging.getLogger(__name__)


class DiscoveryEngine:
    """Discovers and scrapes documentation pages."""
    
    def __init__(self, base_url: str, sitemap_url: str, rate_limit: float = 0.5, use_browser: bool = False, gateway_url: Optional[str] = None, gateway_token: Optional[str] = None):
        """
        Initialize discovery engine.
        
        Args:
            base_url: Base documentation URL
            sitemap_url: Sitemap URL
            rate_limit: Delay between requests in seconds (default 0.5s)
            use_browser: If True, use Playwright or OpenClaw browser tool to render JS-heavy pages
            gateway_url: OpenClaw gateway URL (e.g., http://localhost:18789) for browser rendering
            gateway_token: OpenClaw gateway auth token
        
        Security Notes:
            - base_url and sitemap_url must be HTTPS (HTTP is rejected for browser rendering)
            - Browser rendering requires explicit opt-in via --use-browser flag
            - Gateway token should be protected and never committed to repositories
        """
        # Validate URLs (HTTPS required for browser rendering)
        if use_browser and gateway_token:
            if not base_url.startswith("https://"):
                raise ValueError("Browser rendering requires HTTPS base_url for security. HTTP URLs are not allowed.")
            if not sitemap_url.startswith("https://"):
                raise ValueError("Browser rendering requires HTTPS sitemap_url for security. HTTP URLs are not allowed.")
        
        self.base_url = base_url.rstrip("/")
        self.sitemap_url = sitemap_url
        self.rate_limit = rate_limit
        self.use_browser = use_browser
        self.gateway_url = gateway_url or "http://127.0.0.1:18789"
        self.gateway_token = gateway_token or ""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "anydocs/1.0 (+https://github.com/Pektech/anydocs-skill)"
        })
    
    def _fetch_url(self, url: str, use_browser: bool = False) -> Optional[str]:
        """
        Fetch a URL and return HTML content.
        
        Args:
            url: URL to fetch
            use_browser: If True, use Playwright to render JS-heavy pages
        
        Returns:
            HTML content or None
        """
        if use_browser and PLAYWRIGHT_AVAILABLE:
            return self._fetch_url_with_browser(url)
        
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None
    
    def _fetch_url_with_browser(self, url: str) -> Optional[str]:
        """
        Fetch a URL using browser rendering (Playwright or OpenClaw gateway).
        
        Args:
            url: URL to fetch
        
        Returns:
            Rendered HTML content or None
        """
        # Try OpenClaw gateway first (if available)
        if self.gateway_token:
            html = self._fetch_url_with_gateway(url)
            if html:
                return html
        
        # Fallback to Playwright
        if PLAYWRIGHT_AVAILABLE:
            return self._fetch_url_with_playwright(url)
        
        # Last resort: standard HTTP
        logger.warning(f"No browser available, falling back to requests for {url}")
        return self._fetch_url(url, use_browser=False)
    
    def _fetch_url_with_gateway(self, url: str) -> Optional[str]:
        """
        Fetch a URL using OpenClaw's browser tool via gateway HTTP API.
        
        Args:
            url: URL to fetch
        
        Returns:
            Rendered HTML content or None
        """
        try:
            # Open the page via gateway browser tool
            open_payload = {
                "tool": "browser",
                "args": {
                    "action": "open",
                    "targetUrl": url
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.gateway_token}",
                "Content-Type": "application/json"
            }
            
            resp = requests.post(
                f"{self.gateway_url}/tools/invoke",
                json=open_payload,
                headers=headers,
                timeout=30
            )
            
            if resp.status_code != 200:
                logger.warning(f"Gateway browser open failed ({resp.status_code}): {resp.text[:200]}")
                return None
            
            result = resp.json()
            if not result.get("ok"):
                logger.warning(f"Gateway browser error: {result.get('error', {}).get('message')}")
                return None
            
            # Get the rendered content via snapshot
            snapshot_payload = {
                "tool": "browser",
                "args": {
                    "action": "snapshot",
                    "targetId": result["result"]["targetId"]
                }
            }
            
            resp = requests.post(
                f"{self.gateway_url}/tools/invoke",
                json=snapshot_payload,
                headers=headers,
                timeout=30
            )
            
            if resp.status_code != 200:
                logger.warning(f"Gateway snapshot failed: {resp.text[:200]}")
                return None
            
            snapshot = resp.json()
            if snapshot.get("ok") and "result" in snapshot:
                # The snapshot contains the page content/HTML
                return str(snapshot["result"])
            
            logger.warning("No snapshot result from gateway")
            return None
            
        except Exception as e:
            logger.warning(f"Failed to fetch {url} via gateway: {e}")
            return None
    
    def _fetch_url_with_playwright(self, url: str) -> Optional[str]:
        """
        Fetch a URL using local Playwright (for JS-rendered pages).
        
        Args:
            url: URL to fetch
        
        Returns:
            Rendered HTML content or None
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=30000)
                content = page.content()
                browser.close()
                return content
        except Exception as e:
            logger.warning(f"Failed to fetch {url} with Playwright: {e}")
            return None
    
    def _extract_sitemap_urls(self) -> List[str]:
        """Extract URLs from sitemap.xml."""
        try:
            content = self._fetch_url(self.sitemap_url)
            if not content:
                return []
            
            soup = BeautifulSoup(content, "xml")
            urls = []
            
            # Extract from standard <url><loc> elements
            for loc in soup.find_all("loc"):
                url = loc.get_text(strip=True)
                if url:
                    urls.append(url)
            
            logger.info(f"Found {len(urls)} URLs in sitemap")
            return urls
        except Exception as e:
            logger.warning(f"Failed to parse sitemap: {e}")
            return []
    
    def _crawl_from_base(self, max_pages: int = 100) -> List[str]:
        """
        Fallback: crawl from base URL if sitemap unavailable.
        
        Args:
            max_pages: Maximum pages to crawl
        
        Returns:
            List of discovered URLs
        """
        visited = set()
        to_visit = [self.base_url]
        urls = []
        
        while to_visit and len(urls) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue
            
            visited.add(url)
            content = self._fetch_url(url, use_browser=self.use_browser)
            if not content:
                continue
            
            # Extract links from page
            soup = BeautifulSoup(content, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link["href"]
                # Skip anchors and external links
                if href.startswith("#"):
                    continue
                
                full_url = urljoin(url, href)
                # Only follow links within base_url
                if full_url.startswith(self.base_url) and full_url not in visited:
                    to_visit.append(full_url)
            
            urls.append(url)
            time.sleep(self.rate_limit)
        
        logger.info(f"Crawled {len(urls)} pages from base URL")
        return urls
    
    def discover_urls(self) -> List[str]:
        """
        Discover documentation URLs via sitemap or crawling.
        
        Returns:
            List of documentation URLs
        """
        urls = self._extract_sitemap_urls()
        if not urls:
            logger.info("Sitemap empty or unavailable, falling back to crawl")
            urls = self._crawl_from_base()
        return urls
    
    def scrape_page(self, url: str, use_browser: Optional[bool] = None) -> Optional[Dict[str, Any]]:
        """
        Scrape a single documentation page.
        
        Args:
            url: Page URL
            use_browser: Optional override for browser rendering (uses instance setting if None)
        
        Returns:
            Dict with {url, title, content, tags, metadata}
        """
        render_with_browser = use_browser if use_browser is not None else self.use_browser
        content = self._fetch_url(url, use_browser=render_with_browser)
        if not content:
            return None
        
        try:
            soup = BeautifulSoup(content, "html.parser")
            
            # Extract title
            title = ""
            if soup.title:
                title = soup.title.get_text(strip=True)
            elif soup.h1:
                title = soup.h1.get_text(strip=True)
            
            # Remove script and style tags
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()
            
            # Extract main content
            # Try common content selectors
            content_elem = None
            for selector in ["main", "article", ".content", ".doc-content", ".documentation"]:
                content_elem = soup.select_one(selector)
                if content_elem:
                    break
            
            if not content_elem:
                content_elem = soup.body or soup
            
            # Extract text
            text = content_elem.get_text(separator=" ", strip=True)
            
            # Extract tags from meta or headings
            tags = []
            # Look for category in URL path
            path_parts = urlparse(url).path.split("/")
            tags.extend([p for p in path_parts if p and len(p) > 2])
            
            # Extract H2/H3 headings as tags
            for heading in soup.find_all(["h2", "h3"])[:5]:
                tag = heading.get_text(strip=True)
                if tag and len(tag) < 50:
                    tags.append(tag)
            
            return {
                "url": url,
                "title": title or "Untitled",
                "content": text[:5000],  # Truncate to 5k chars for storage
                "tags": list(set(tags)),
                "full_content": text,  # Keep full for search
            }
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def fetch_all(self, progress_callback=None) -> List[Dict[str, Any]]:
        """
        Discover and scrape all documentation pages.
        
        Args:
            progress_callback: Optional callback for progress updates
        
        Returns:
            List of scraped pages
        """
        logger.info(f"Starting discovery from {self.base_url}")
        urls = self.discover_urls()
        
        pages = []
        for i, url in enumerate(urls):
            if progress_callback:
                progress_callback(i + 1, len(urls), url)
            
            page = self.scrape_page(url)
            if page:
                pages.append(page)
            
            time.sleep(self.rate_limit)
        
        logger.info(f"Successfully scraped {len(pages)} pages")
        return pages
