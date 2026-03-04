"""
Composio Composer X Skill for OpenClaw
Posts tweets to Twitter/X through Composio's integration platform.
"""

from .twitter_client import TwitterClient

__version__ = "1.0.0"

# Default configuration
DEFAULT_CONFIG = {
    "composio_api_base": "https://backend.composio.dev/api/v1",
    "twitter_api_base": "https://api.twitter.com/2",
    "timeout": 30,
}


def post_tweet(content: str, composio_auth_token: str) -> dict:
    """
    Post a tweet to Twitter/X using Composio.
    
    Args:
        content: The tweet content (max 280 characters)
        composio_auth_token: The Composio authentication token
    
    Returns:
        dict: Contains 'success' (bool), 'tweet_id' (str), 'tweet_url' (str)
              or 'error' (str) if posting fails
    """
    client = TwitterClient(auth_token=composio_auth_token)
    return client.post_tweet(content)


def get_tweet(tweet_id: str, composio_auth_token: str) -> dict:
    """
    Retrieve a tweet by ID.
    
    Args:
        tweet_id: The tweet ID to retrieve
        composio_auth_token: The Composio authentication token
    
    Returns:
        dict: Tweet data or error information
    """
    client = TwitterClient(auth_token=composio_auth_token)
    return client.get_tweet(tweet_id)


def delete_tweet(tweet_id: str, composio_auth_token: str) -> dict:
    """
    Delete a tweet by ID.
    
    Args:
        tweet_id: The tweet ID to delete
        composio_auth_token: The Composio authentication token
    
    Returns:
        dict: Contains 'success' (bool) and status message
    """
    client = TwitterClient(auth_token=composio_auth_token)
    return client.delete_tweet(tweet_id)


# For backwards compatibility with async patterns
async def post_tweet_async(content: str, composio_auth_token: str) -> dict:
    """Async wrapper for post_tweet."""
    return post_tweet(content, composio_auth_token)


async def get_tweet_async(tweet_id: str, composio_auth_token: str) -> dict:
    """Async wrapper for get_tweet."""
    return get_tweet(tweet_id, composio_auth_token)


async def delete_tweet_async(tweet_id: str, composio_auth_token: str) -> dict:
    """Async wrapper for delete_tweet."""
    return delete_tweet(tweet_id, composio_auth_token)
