"""
Twitter/X Client for Composio Composer X Skill.
Uses HTTP requests with BeautifulSoup to emulate Twitter/X interaction through Composio.
"""

import os
import re
import json
import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterClient:
    """Client for posting tweets to Twitter/X through Composio."""
    
    def __init__(self, auth_token: str, config: Optional[Dict] = None):
        """
        Initialize the Twitter client.
        
        Args:
            auth_token: Composio authentication token
            config: Optional configuration dictionary
        """
        self.auth_token = auth_token
        self.config = config or {}
        
        # Configuration defaults
        self.api_base = self.config.get(
            "composio_api_base", 
            "https://backend.composio.dev/api/v1"
        )
        self.twitter_api_base = self.config.get(
            "twitter_api_base",
            "https://api.twitter.com/2"
        )
        self.timeout = self.config.get("timeout", 30)
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "en-US,en;q=0.9",
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # seconds
        
    def _rate_limit(self):
        """Apply rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
        
    def _make_request(
        self, 
        method: str, 
        url: str, 
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> requests.Response:
        """
        Make an HTTP request with error handling.
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            url: Request URL
            headers: Optional headers
            data: Form data
            json_data: JSON payload
            params: Query parameters
        
        Returns:
            Response object
        
        Raises:
            TwitterClientError: On request failure
        """
        self._rate_limit()
        
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Add auth token
        request_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                data=data,
                json=json_data,
                params=params,
                timeout=self.timeout
            )
            
            # Log response status
            logger.debug(f"{method} {url} -> {response.status_code}")
            
            return response
            
        except requests.exceptions.Timeout:
            raise TwitterClientError("Request timed out")
        except requests.exceptions.ConnectionError as e:
            raise TwitterClientError(f"Connection failed: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise TwitterClientError(f"Request failed: {str(e)}")
            
    def _parse_html_response(self, html: str) -> Dict[str, Any]:
        """
        Parse HTML response using BeautifulSoup.
        
        Args:
            html: HTML content to parse
        
        Returns:
            Parsed data dictionary
        """
        soup = BeautifulSoup(html, "html.parser")
        
        # Try to find JSON data in script tags
        for script in soup.find_all("script"):
            if script.string and "window.__INITIAL_STATE__" in script.string:
                # Extract JSON from JavaScript
                match = re.search(
                    r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                    script.string,
                    re.DOTALL
                )
                if match:
                    try:
                        return json.loads(match.group(1))
                    except json.JSONDecodeError:
                        pass
        
        # Try to find error messages
        error_div = soup.find("div", class_=re.compile(r"error|Error"))
        if error_div:
            return {"error": error_div.get_text(strip=True)}
            
        # Return parsed HTML elements
        return {
            "html": str(soup),
            "title": soup.title.string if soup.title else None,
        }
        
    def post_tweet(self, content: str) -> Dict[str, Any]:
        """
        Post a tweet to Twitter/X.
        
        Args:
            content: Tweet content (max 280 characters)
        
        Returns:
            Dictionary with success status and tweet info
        """
        # Validate content
        if not content or not content.strip():
            return {
                "success": False,
                "error": "Tweet content cannot be empty"
            }
            
        if len(content) > 280:
            return {
                "success": False,
                "error": f"Tweet exceeds 280 characters (got {len(content)})"
            }
        
        # Try Composio API endpoint first
        try:
            response = self._make_request(
                method="POST",
                url=f"{self.api_base}/twitter/tweets",
                json_data={"text": content}
            )
            
            if response.status_code == 200 or response.status_code == 201:
                try:
                    data = response.json()
                    return {
                        "success": True,
                        "tweet_id": data.get("data", {}).get("id", ""),
                        "tweet_url": f"https://twitter.com/i/status/{data.get('data', {}).get('id', '')}",
                        "content": content
                    }
                except json.JSONDecodeError:
                    pass
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "Authentication failed. Check your Composio auth token."
                }
            elif response.status_code == 429:
                return {
                    "success": False,
                    "error": "Rate limit exceeded. Please try again later."
                }
                
        except TwitterClientError as e:
            logger.warning(f"Composio API failed: {e}, trying web scraping method")
        
        # Fallback: Try to post through Composio web interface
        return self._post_tweet_web(content)
        
    def _post_tweet_web(self, content: str) -> Dict[str, Any]:
        """
        Post tweet through Composio web interface (fallback method).
        Uses BeautifulSoup to interact with the web interface.
        
        Args:
            content: Tweet content
        
        Returns:
            Dictionary with success status and tweet info
        """
        try:
            # First, get the web interface to establish session
            response = self._make_request(
                method="GET",
                url=f"{self.api_base}/integrations/twitter",
                headers={"Accept": "text/html"}
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to load Composio interface: {response.status_code}"
                }
            
            # Parse HTML to find CSRF token or action URLs
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Look for forms and action URLs
            forms = soup.find_all("form")
            for form in forms:
                action = form.get("action", "")
                if "twitter" in action.lower() or "tweet" in action.lower():
                    # Found a relevant form, try to submit
                    inputs = {}
                    for input_tag in form.find_all("input"):
                        name = input_tag.get("name")
                        value = input_tag.get("value", "")
                        if name:
                            inputs[name] = value
                    
                    # Add tweet content
                    inputs["text"] = content
                    
                    # Submit the form
                    form_response = self._make_request(
                        method="POST",
                        url=action,
                        data=inputs,
                        headers={"Content-Type": "application/x-www-form-urlencoded"}
                    )
                    
                    if form_response.status_code in [200, 201]:
                        # Try to extract tweet ID from response
                        tweet_match = re.search(
                            r'(?:tweet|id|status)[/=](\d{10,})',
                            form_response.text,
                            re.IGNORECASE
                        )
                        if tweet_match:
                            tweet_id = tweet_match.group(1)
                            return {
                                "success": True,
                                "tweet_id": tweet_id,
                                "tweet_url": f"https://twitter.com/i/status/{tweet_id}",
                                "content": content
                            }
            
            # If we got here, the web method also failed
            # Try direct Twitter API as last resort
            return self._post_tweet_direct(content)
            
        except Exception as e:
            logger.error(f"Web posting failed: {e}")
            return {
                "success": False,
                "error": f"Failed to post tweet: {str(e)}"
            }
            
    def _post_tweet_direct(self, content: str) -> Dict[str, Any]:
        """
        Direct Twitter API posting as final fallback.
        
        Args:
            content: Tweet content
        
        Returns:
            Dictionary with success status and tweet info
        """
        try:
            # Try Twitter API v2
            response = self._make_request(
                method="POST",
                url=f"{self.twitter_api_base}/tweets",
                json_data={"text": content}
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    "success": True,
                    "tweet_id": data.get("data", {}).get("id", ""),
                    "tweet_url": f"https://twitter.com/i/status/{data.get('data', {}).get('id', '')}",
                    "content": content
                }
            else:
                return {
                    "success": False,
                    "error": f"Twitter API error: {response.status_code} - {response.text[:200]}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"All posting methods failed: {str(e)}"
            }
            
    def get_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Retrieve a tweet by ID.
        
        Args:
            tweet_id: The tweet ID to retrieve
        
        Returns:
            Dictionary with tweet data or error
        """
        try:
            response = self._make_request(
                method="GET",
                url=f"{self.api_base}/twitter/tweets/{tweet_id}"
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {
                        "success": True,
                        "tweet": data.get("data", {})
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Failed to parse tweet data"
                    }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get tweet: {response.status_code}"
                }
                
        except TwitterClientError as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    def delete_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Delete a tweet by ID.
        
        Args:
            tweet_id: The tweet ID to delete
        
        Returns:
            Dictionary with success status
        """
        try:
            response = self._make_request(
                method="DELETE",
                url=f"{self.api_base}/twitter/tweets/{tweet_id}"
            )
            
            if response.status_code in [200, 204]:
                return {
                    "success": True,
                    "message": f"Tweet {tweet_id} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to delete tweet: {response.status_code}"
                }
                
        except TwitterClientError as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    def close(self):
        """Close the HTTP session."""
        self.session.close()


class TwitterClientError(Exception):
    """Custom exception for Twitter client errors."""
    pass


# Convenience function for quick posting
def quick_post(content: str, auth_token: str) -> Dict[str, Any]:
    """
    Quick function to post a tweet.
    
    Args:
        content: Tweet content
        auth_token: Composio auth token
    
    Returns:
        Result dictionary
    """
    client = TwitterClient(auth_token=auth_token)
    try:
        return client.post_tweet(content)
    finally:
        client.close()
