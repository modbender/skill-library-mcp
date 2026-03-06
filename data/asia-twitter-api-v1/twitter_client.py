#!/usr/bin/env python3
"""
OpenClaw Twitter - AIsa API Client
Twitter/X data and automation for autonomous agents.

SECURITY NOTICE:
===============
This client provides both READ (safe) and WRITE (high-risk) operations.

READ OPERATIONS (SAFE):
- user-info, tweets, search, trends, followers, followings, user-search
- No authentication required
- No credentials transmitted
- Safe for production use

WRITE OPERATIONS (HIGH RISK):
- login, post, like, retweet
- Requires transmitting email + password + proxy to api.aisa.one
- NEVER use with your primary Twitter account
- Only use with dedicated test/automation accounts
- You assume all responsibility and risk

Usage Examples (Safe Read Operations):
    python twitter_client.py user-info --username <username>
    python twitter_client.py tweets --username <username>
    python twitter_client.py search --query <query> [--type Latest|Top]
    python twitter_client.py trends [--woeid <woeid>]
    python twitter_client.py user-search --keyword <keyword>
    python twitter_client.py followers --username <username>
    python twitter_client.py followings --username <username>

High-Risk Write Operations (Use Only with Test Accounts):
    python twitter_client.py login --username <u> --email <e> --password <p> --proxy <proxy>
    python twitter_client.py post --username <u> --text <text>
    python twitter_client.py like --username <u> --tweet-id <id>
    python twitter_client.py retweet --username <u> --tweet-id <id>
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
from typing import Any, Dict, Optional


class TwitterClient:
    """
    OpenClaw Twitter - Twitter/X API Client.
    
    Security Notes:
    - Read operations are safe and require only AISA_API_KEY
    - Write operations transmit credentials to third-party API
    - Never use write operations with primary Twitter accounts
    """
    
    BASE_URL = "https://api.aisa.one/apis/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the client with an API key.
        
        Args:
            api_key: AIsa API key (defaults to AISA_API_KEY environment variable)
        
        Raises:
            ValueError: If no API key is provided
        """
        self.api_key = api_key or os.environ.get("AISA_API_KEY")
        if not self.api_key:
            raise ValueError(
                "AISA_API_KEY is required. Set it via environment variable or pass to constructor."
            )
    
    def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the AIsa API.
        
        Args:
            method: HTTP method (GET or POST)
            endpoint: API endpoint path
            params: URL query parameters
            data: JSON request body
        
        Returns:
            API response as dictionary
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        if params:
            query_string = urllib.parse.urlencode(
                {k: v for k, v in params.items() if v is not None}
            )
            url = f"{url}?{query_string}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "OpenClaw-Twitter/1.0"
        }
        
        request_data = None
        if data:
            request_data = json.dumps(data).encode("utf-8")
        
        if method == "POST" and request_data is None:
            request_data = b"{}"
        
        req = urllib.request.Request(url, data=request_data, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            try:
                return json.loads(error_body)
            except json.JSONDecodeError:
                return {"success": False, "error": {"code": str(e.code), "message": error_body}}
        except urllib.error.URLError as e:
            return {"success": False, "error": {"code": "NETWORK_ERROR", "message": str(e.reason)}}
    
    # ==================== Read APIs (SAFE) ====================
    
    def user_info(self, username: str) -> Dict[str, Any]:
        """
        Get Twitter user information by username.
        
        This is a SAFE read operation - no authentication required.
        
        Args:
            username: Twitter username (without @)
        
        Returns:
            User profile information
        """
        return self._request("GET", "/twitter/user/info", params={"userName": username})
    
    def user_tweets(self, username: str) -> Dict[str, Any]:
        """
        Get tweets from a specific user.
        
        This is a SAFE read operation - no authentication required.
        
        Args:
            username: Twitter username (without @)
        
        Returns:
            User's recent tweets
        """
        return self._request("GET", "/twitter/user/user_last_tweet", params={"userName": username})
    
    def search(self, query: str, query_type: str = "Latest") -> Dict[str, Any]:
        """
        Search for tweets matching a query.
        
        This is a SAFE read operation - no authentication required.
        
        Args:
            query: Search query string
            query_type: "Latest" or "Top" (default: "Latest")
        
        Returns:
            Search results
        """
        return self._request("GET", "/twitter/tweet/advanced_search", params={
            "query": query,
            "queryType": query_type
        })
    
    def tweet_detail(self, tweet_ids: str) -> Dict[str, Any]:
        """
        Get detailed information about tweets by IDs.
        
        This is a SAFE read operation - no authentication required.
        
        Args:
            tweet_ids: Comma-separated tweet IDs
        
        Returns:
            Tweet details
        """
        return self._request("GET", "/twitter/tweet/tweetById", params={"tweet_ids": tweet_ids})
    
    def trends(self, woeid: int = 1) -> Dict[str, Any]:
        """
        Get current Twitter trending topics.
        
        This is a SAFE read operation - no authentication required.
        
        Args:
            woeid: Where On Earth ID (1 = worldwide, 23424977 = USA)
        
        Returns:
            Trending topics
        """
        return self._request("GET", "/twitter/trends", params={"woeid": woeid})
    
    def user_search(self, keyword: str) -> Dict[str, Any]:
        """
        Search for Twitter users by keyword.
        
        This is a SAFE read operation - no authentication required.
        
        Args:
            keyword: Search keyword
        
        Returns:
            Matching users
        """
        return self._request("GET", "/twitter/user/search_user", params={"keyword": keyword})
    
    def followers(self, username: str) -> Dict[str, Any]:
        """
        Get user followers.
        
        This is a SAFE read operation - no authentication required.
        
        Args:
            username: Twitter username (without @)
        
        Returns:
            User's followers
        """
        return self._request("GET", "/twitter/user/user_followers", params={"userName": username})
    
    def followings(self, username: str) -> Dict[str, Any]:
        """
        Get user followings.
        
        This is a SAFE read operation - no authentication required.
        
        Args:
            username: Twitter username (without @)
        
        Returns:
            Users followed by the specified user
        """
        return self._request("GET", "/twitter/user/user_followings", params={"userName": username})
    
    # ==================== Write APIs (HIGH RISK - V3) ====================
    
    def login(self, username: str, email: str, password: str, proxy: str, totp_code: str = None) -> Dict[str, Any]:
        """
        Login to Twitter account.
        
        ⚠️ HIGH RISK OPERATION ⚠️
        
        This operation transmits your Twitter credentials to api.aisa.one.
        
        SECURITY WARNINGS:
        - NEVER use this with your primary Twitter account
        - Use only with dedicated test/automation accounts
        - Use unique passwords not used elsewhere
        - You assume all responsibility and risk
        
        Args:
            username: Twitter username
            email: Account email
            password: Account password
            proxy: Proxy URL (format: http://user:pass@ip:port)
            totp_code: Optional 2FA TOTP code
        
        Returns:
            Login status (async operation - check status separately)
        """
        print("⚠️  WARNING: Transmitting credentials to third-party API", file=sys.stderr)
        print("⚠️  Ensure you are using a dedicated test account only!", file=sys.stderr)
        
        data = {
            "user_name": username,
            "email": email,
            "password": password,
            "proxy": proxy
        }
        if totp_code:
            data["totp_code"] = totp_code
        return self._request("POST", "/twitter/user_login_v3", data=data)
    
    def get_account(self, username: str) -> Dict[str, Any]:
        """
        Get logged-in account details.
        
        Requires prior login via login() method.
        
        Args:
            username: Twitter username used during login
        
        Returns:
            Account details and login status
        """
        return self._request("GET", "/twitter/get_my_x_account_detail_v3", params={"user_name": username})
    
    def send_tweet(self, username: str, text: str, media_base64: str = None, media_type: str = None) -> Dict[str, Any]:
        """
        Send a tweet.
        
        ⚠️ HIGH RISK OPERATION ⚠️
        
        Requires prior login. Use only with dedicated test accounts.
        
        Args:
            username: Twitter username (must be logged in)
            text: Tweet text
            media_base64: Optional base64-encoded media
            media_type: Optional media MIME type
        
        Returns:
            Tweet post result
        """
        data = {"user_name": username, "text": text}
        if media_base64:
            data["media_data_base64"] = media_base64
        if media_type:
            data["media_type"] = media_type
        return self._request("POST", "/twitter/send_tweet_v3", data=data)
    
    def like(self, username: str, tweet_id: str) -> Dict[str, Any]:
        """
        Like a tweet.
        
        ⚠️ HIGH RISK OPERATION ⚠️
        
        Requires prior login. Use only with dedicated test accounts.
        
        Args:
            username: Twitter username (must be logged in)
            tweet_id: Tweet ID to like
        
        Returns:
            Like operation result
        """
        return self._request("POST", "/twitter/like_tweet_v3", data={
            "user_name": username,
            "tweet_id": tweet_id
        })
    
    def retweet(self, username: str, tweet_id: str) -> Dict[str, Any]:
        """
        Retweet a tweet.
        
        ⚠️ HIGH RISK OPERATION ⚠️
        
        Requires prior login. Use only with dedicated test accounts.
        
        Args:
            username: Twitter username (must be logged in)
            tweet_id: Tweet ID to retweet
        
        Returns:
            Retweet operation result
        """
        return self._request("POST", "/twitter/retweet_v3", data={
            "user_name": username,
            "tweet_id": tweet_id
        })


def print_security_warning():
    """Print security warning for write operations."""
    print("\n" + "="*70, file=sys.stderr)
    print("⚠️  SECURITY WARNING", file=sys.stderr)
    print("="*70, file=sys.stderr)
    print("You are about to use a HIGH RISK write operation.", file=sys.stderr)
    print("", file=sys.stderr)
    print("This will transmit your Twitter credentials to api.aisa.one.", file=sys.stderr)
    print("", file=sys.stderr)
    print("NEVER use this with your primary Twitter account!", file=sys.stderr)
    print("Only use with dedicated test/automation accounts.", file=sys.stderr)
    print("", file=sys.stderr)
    print("You assume all responsibility and risk.", file=sys.stderr)
    print("="*70 + "\n", file=sys.stderr)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OpenClaw Twitter - Twitter/X data and automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Security Notice:
  READ operations (user-info, tweets, search, etc.) are SAFE
  WRITE operations (login, post, like, retweet) are HIGH RISK
  
  Never use write operations with your primary Twitter account!
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # ==================== Safe Read Commands ====================
    
    # user-info
    user_info = subparsers.add_parser("user-info", help="Get user information (SAFE)")
    user_info.add_argument("--username", "-u", required=True, help="Twitter username")
    
    # tweets
    tweets = subparsers.add_parser("tweets", help="Get user's tweets (SAFE)")
    tweets.add_argument("--username", "-u", required=True, help="Twitter username")
    
    # search
    search = subparsers.add_parser("search", help="Search tweets (SAFE)")
    search.add_argument("--query", "-q", required=True, help="Search query")
    search.add_argument("--type", "-t", choices=["Latest", "Top"], default="Latest", help="Query type")
    
    # detail
    detail = subparsers.add_parser("detail", help="Get tweets by IDs (SAFE)")
    detail.add_argument("--tweet-ids", "-t", required=True, help="Tweet IDs (comma-separated)")
    
    # trends
    trends = subparsers.add_parser("trends", help="Get trending topics (SAFE)")
    trends.add_argument("--woeid", "-w", type=int, default=1, help="WOEID (1=worldwide)")
    
    # user-search
    user_search = subparsers.add_parser("user-search", help="Search users (SAFE)")
    user_search.add_argument("--keyword", "-k", required=True, help="Search keyword")
    
    # followers
    followers = subparsers.add_parser("followers", help="Get user followers (SAFE)")
    followers.add_argument("--username", "-u", required=True, help="Twitter username")
    
    # followings
    followings = subparsers.add_parser("followings", help="Get user followings (SAFE)")
    followings.add_argument("--username", "-u", required=True, help="Twitter username")
    
    # ==================== High Risk Write Commands ====================
    
    # login
    login = subparsers.add_parser("login", help="Login to Twitter account (⚠️ HIGH RISK)")
    login.add_argument("--username", "-u", required=True, help="Twitter username")
    login.add_argument("--email", "-e", required=True, help="Account email")
    login.add_argument("--password", "-p", required=True, help="Account password")
    login.add_argument("--proxy", required=True, help="Proxy URL")
    login.add_argument("--totp", help="TOTP 2FA code")
    
    # account
    account = subparsers.add_parser("account", help="Check account status")
    account.add_argument("--username", "-u", required=True, help="Twitter username")
    
    # post
    post = subparsers.add_parser("post", help="Send a tweet (⚠️ HIGH RISK)")
    post.add_argument("--username", "-u", required=True, help="Twitter username")
    post.add_argument("--text", "-t", required=True, help="Tweet text")
    post.add_argument("--media", help="Base64 encoded media")
    post.add_argument("--media-type", choices=["image/jpeg", "image/png", "image/gif", "video/mp4"])
    
    # like
    like = subparsers.add_parser("like", help="Like a tweet (⚠️ HIGH RISK)")
    like.add_argument("--username", "-u", required=True, help="Twitter username")
    like.add_argument("--tweet-id", "-t", required=True, help="Tweet ID")
    
    # retweet
    retweet = subparsers.add_parser("retweet", help="Retweet a tweet (⚠️ HIGH RISK)")
    retweet.add_argument("--username", "-u", required=True, help="Twitter username")
    retweet.add_argument("--tweet-id", "-t", required=True, help="Tweet ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Show security warning for write operations
    if args.command in ["login", "post", "like", "retweet"]:
        print_security_warning()
    
    try:
        client = TwitterClient()
    except ValueError as e:
        print(json.dumps({"success": False, "error": {"code": "AUTH_ERROR", "message": str(e)}}))
        sys.exit(1)
    
    result = None
    
    # Execute command
    if args.command == "user-info":
        result = client.user_info(args.username)
    elif args.command == "tweets":
        result = client.user_tweets(args.username)
    elif args.command == "search":
        result = client.search(args.query, args.type)
    elif args.command == "detail":
        result = client.tweet_detail(args.tweet_ids)
    elif args.command == "trends":
        result = client.trends(args.woeid)
    elif args.command == "user-search":
        result = client.user_search(args.keyword)
    elif args.command == "followers":
        result = client.followers(args.username)
    elif args.command == "followings":
        result = client.followings(args.username)
    elif args.command == "login":
        result = client.login(args.username, args.email, args.password, args.proxy, args.totp)
    elif args.command == "account":
        result = client.get_account(args.username)
    elif args.command == "post":
        result = client.send_tweet(args.username, args.text, args.media, args.media_type)
    elif args.command == "like":
        result = client.like(args.username, args.tweet_id)
    elif args.command == "retweet":
        result = client.retweet(args.username, args.tweet_id)
    
    if result:
        output = json.dumps(result, indent=2, ensure_ascii=False)
        try:
            print(output)
        except UnicodeEncodeError:
            print(json.dumps(result, indent=2, ensure_ascii=True))
        sys.exit(0 if result.get("success", True) else 1)


if __name__ == "__main__":
    main()
