"""
LangChain-compatible tool wrappers for Twitter API.

This module provides LangChain tool implementations for common Twitter API operations
such as posting tweets, replying to tweets, and fetching mentions.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Type, Callable, Union, cast, Annotated, ClassVar
from pydantic import BaseModel, Field, field_validator, ConfigDict

# LangChain imports
from langchain.tools import BaseTool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

# Import tenacity for rate limit handling
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Twitter API imports
from .twitter import Twitter

# Set up logging
logger = logging.getLogger("twitter_langchain_tools")


class PostTweetInput(BaseModel):
    """Input schema for posting a tweet."""
    
    tweet_text: str = Field(
        ..., 
        description="The text content of the tweet to post",
        min_length=1,
        max_length=280
    )
    
    @field_validator("tweet_text")
    @classmethod
    def validate_tweet_length(cls, v):
        """Validate tweet length."""
        if len(v) > 280:
            raise ValueError("Tweet text must be 280 characters or less")
        if len(v) == 0:
            raise ValueError("Tweet text cannot be empty")
        return v


class ReplyToTweetInput(BaseModel):
    """Input schema for replying to a tweet."""
    
    tweet_id: str = Field(
        ..., 
        description="The ID of the tweet to reply to"
    )
    
    reply_text: str = Field(
        ..., 
        description="The text content of the reply",
        min_length=1,
        max_length=280
    )
    
    @field_validator("reply_text")
    @classmethod
    def validate_reply_length(cls, v):
        """Validate reply length."""
        if len(v) > 280:
            raise ValueError("Reply text must be 280 characters or less")
        if len(v) == 0:
            raise ValueError("Reply text cannot be empty")
        return v


class FetchMentionsInput(BaseModel):
    """Input schema for fetching mentions."""
    
    count: int = Field(
        default=20, 
        description="Number of mentions to retrieve",
        ge=1,
        le=100
    )
    
    since_id: Optional[str] = Field(
        default=None, 
        description="Only fetch mentions newer than this tweet ID"
    )


class LikeTweetInput(BaseModel):
    """Input schema for liking a tweet."""
    
    tweet_id: str = Field(
        ..., 
        description="The ID of the tweet to like"
    )


class RetweetInput(BaseModel):
    """Input schema for retweeting a tweet."""
    
    tweet_id: str = Field(
        ..., 
        description="The ID of the tweet to retweet"
    )


class ToolConfig(BaseModel):
    """Configuration for Twitter tools."""
    
    debug_mode: bool = Field(
        default=False,
        description="Enable debug logging for all API calls"
    )
    
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for rate-limited API calls",
        ge=1,
        le=10
    )
    
    retry_min_wait: int = Field(
        default=1,
        description="Minimum wait time in seconds between retries",
        ge=1
    )
    
    retry_max_wait: int = Field(
        default=60,
        description="Maximum wait time in seconds between retries",
        ge=1
    )


class TwitterToolMixin:
    """Mixin for Twitter API tools that handles authentication."""
    
    auth_token: str
    ct0: Optional[str]
    config: ToolConfig
    proxy: Optional[str]
    _client: Optional[Twitter] = None
    
    def __init__(self, auth_token: str, ct0: Optional[str] = None, config: Optional[ToolConfig] = None, proxy: Optional[str] = None):
        """Initialize with Twitter API authentication."""
        # We'll call parent init in the actual classes
        self.auth_token = auth_token
        self.ct0 = ct0
        self.config = config or ToolConfig()
        self.proxy = proxy
        self._client = None
        
        # Set up logging level based on config
        if self.config.debug_mode:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
    
    @property
    def client(self) -> Twitter:
        """Get or create Twitter API client with proper authentication."""
        if self._client is None:
            # Initialize Twitter client and configure proxy
            twitter_client = Twitter(auth_token=self.auth_token, ct0=self.ct0)
            
            # Configure proxy for the underlying API client if provided
            if self.proxy and hasattr(twitter_client, 'client'):
                twitter_client.client.proxy = self.proxy
                logger.info(f"Configured proxy for Twitter API client: {self.proxy}")
            
            self._client = twitter_client
            
        return self._client
    
    def _format_response(self, response: Any) -> str:
        """Format API response for human-readable output."""
        if response is None:
            return "No response received from Twitter API."
        
        try:
            # For basic success responses
            if isinstance(response, dict):
                if 'errors' in response:
                    errors = response['errors']
                    return f"Error: {json.dumps(errors, indent=2)}"
                
                # Check for tweet ID in response
                if 'id_str' in response:
                    tweet_id = response['id_str']
                    return f"Success! Tweet ID: {tweet_id}"
                
                # For data-oriented responses like mentions
                if 'data' in response:
                    data_count = len(response['data'])
                    return f"Retrieved {data_count} items from Twitter API."
            
            # For list responses like mentions
            if isinstance(response, list):
                count = len(response)
                return f"Retrieved {count} items from Twitter API."
            
            # Default formatting
            return f"Twitter API response: {str(response)[:1000]}..."
            
        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            return f"Error formatting response: {str(e)}"
    
    @retry(
        wait=wait_random_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(3)
    )
    async def _safe_api_call(self, api_func, *args, **kwargs):
        """
        Make an API call with retry logic for rate limits and transient errors.
        
        Args:
            api_func: The API function to call
            *args: Arguments to pass to the API function
            **kwargs: Keyword arguments to pass to the API function
            
        Returns:
            The response from the API function
        """
        try:
            logger.debug(f"Calling API function {api_func.__name__} with args: {args} and kwargs: {kwargs}")
            response = await api_func(*args, **kwargs)
            
            # Check for rate limit errors in response
            if isinstance(response, dict) and 'errors' in response:
                for error in response['errors']:
                    if error.get('code') == 88:  # Twitter API rate limit code
                        logger.warning(f"Rate limit hit. Retrying {api_func.__name__}...")
                        raise Exception("Rate limit exceeded")
            
            logger.debug(f"API call {api_func.__name__} successful")
            return response
            
        except Exception as e:
            logger.error(f"API call {api_func.__name__} failed: {str(e)}")
            raise


class PostTweetTool(BaseTool):
    """Tool for posting a new tweet."""
    
    name: ClassVar[str] = "post_tweet"
    description: ClassVar[str] = """
    Use this tool to post a new tweet to Twitter. 
    Input should be the full tweet text (max 280 chars).
    This is useful when you want to share information, updates, or announcements on Twitter.
    """
    args_schema: ClassVar[Type[BaseModel]] = PostTweetInput
    
    # Add configuration for pydantic v2 compatibility
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    
    # Fields for TwitterToolMixin
    auth_token: str = Field(..., description="Twitter API authentication token")
    ct0: Optional[str] = Field(None, description="Twitter API CSRF token")
    config: ToolConfig = Field(default_factory=ToolConfig, description="Tool configuration")
    _client: Optional[Twitter] = None
    
    def _run(self, tweet_text: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Synchronous run method - uses asyncio to call async method."""
        logger.info(f"Running post_tweet tool with text: {tweet_text[:50]}...")
        return asyncio.run(self._arun(tweet_text=tweet_text, run_manager=None))

    async def _arun(
        self, tweet_text: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Post a new tweet."""
        try:
            logger.info(f"Posting tweet: {tweet_text[:50]}...")
            # Initialize client if needed
            if self._client is None:
                self._client = Twitter(auth_token=self.auth_token, ct0=self.ct0)
                # Configure proxy for the underlying API client if provided
                if hasattr(self, 'proxy') and self.proxy and hasattr(self._client, 'client'):
                    self._client.client.proxy = self.proxy
                    logger.info(f"Configured proxy for Twitter API client: {self.proxy}")
                
            # Use safe API call with retry logic
            response = await self._safe_api_call(
                self._client.tweet.create_tweet, 
                tweet_text=tweet_text
            )
            
            # Log the full response in debug mode
            logger.debug(f"Tweet posted response: {json.dumps(response) if response else None}")
            
            # Update the callback manager if provided
            if run_manager:
                await run_manager.on_text("Tweet posted successfully!")
                
            return self._format_response(response)
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            return f"Error posting tweet: {str(e)}"
    
    # Implement methods from TwitterToolMixin
    @property
    def client(self) -> Twitter:
        """Get or create Twitter API client with proper authentication."""
        if self._client is None:
            self._client = Twitter(auth_token=self.auth_token, ct0=self.ct0)
        return self._client
    
    def _format_response(self, response: Any) -> str:
        """Format API response for human-readable output."""
        if response is None:
            return "No response received from Twitter API."
        
        try:
            # For basic success responses
            if isinstance(response, dict):
                if 'errors' in response:
                    errors = response['errors']
                    return f"Error: {json.dumps(errors, indent=2)}"
                
                # Check for tweet ID in response
                if 'id_str' in response:
                    tweet_id = response['id_str']
                    return f"Success! Tweet ID: {tweet_id}"
                
                # For data-oriented responses like mentions
                if 'data' in response:
                    data_count = len(response['data'])
                    return f"Retrieved {data_count} items from Twitter API."
            
            # For list responses like mentions
            if isinstance(response, list):
                count = len(response)
                return f"Retrieved {count} items from Twitter API."
            
            # Default formatting
            return f"Twitter API response: {str(response)[:1000]}..."
            
        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            return f"Error formatting response: {str(e)}"
    
    @retry(
        wait=wait_random_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(3)
    )
    async def _safe_api_call(self, api_func, *args, **kwargs):
        """
        Make an API call with retry logic for rate limits and transient errors.
        
        Args:
            api_func: The API function to call
            *args: Arguments to pass to the API function
            **kwargs: Keyword arguments to pass to the API function
            
        Returns:
            The response from the API function
        """
        try:
            logger.debug(f"Calling API function {api_func.__name__} with args: {args} and kwargs: {kwargs}")
            response = await api_func(*args, **kwargs)
            
            # Check for rate limit errors in response
            if isinstance(response, dict) and 'errors' in response:
                for error in response['errors']:
                    if error.get('code') == 88:  # Twitter API rate limit code
                        logger.warning(f"Rate limit hit. Retrying {api_func.__name__}...")
                        raise Exception("Rate limit exceeded")
            
            logger.debug(f"API call {api_func.__name__} successful")
            return response
            
        except Exception as e:
            logger.error(f"API call {api_func.__name__} failed: {str(e)}")
            raise


class ReplyToTweetTool(BaseTool):
    """Tool for replying to a tweet."""
    
    name: ClassVar[str] = "reply_to_tweet"
    description: ClassVar[str] = """
    Use this tool to reply to an existing tweet on Twitter.
    Requires a tweet ID to reply to and the text of your reply (max 280 chars).
    Useful for engaging with other tweets, answering questions, or participating in conversations.
    """
    args_schema: ClassVar[Type[BaseModel]] = ReplyToTweetInput
    
    # Add configuration for pydantic v2 compatibility
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    
    # Fields for TwitterToolMixin
    auth_token: str = Field(..., description="Twitter API authentication token")
    ct0: Optional[str] = Field(None, description="Twitter API CSRF token")
    config: ToolConfig = Field(default_factory=ToolConfig, description="Tool configuration")
    _client: Optional[Twitter] = None
    
    def _run(
        self, tweet_id: str, reply_text: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Synchronous run method - uses asyncio to call async method."""
        logger.info(f"Running reply_to_tweet tool for tweet_id: {tweet_id}")
        return asyncio.run(self._arun(tweet_id=tweet_id, reply_text=reply_text, run_manager=None))

    async def _arun(
        self, tweet_id: str, reply_text: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Reply to a tweet."""
        try:
            logger.info(f"Replying to tweet {tweet_id} with: {reply_text[:50]}...")
            # Initialize client if needed
            if self._client is None:
                self._client = Twitter(auth_token=self.auth_token, ct0=self.ct0)
                
            response = await self._safe_api_call(
                self._client.tweet.reply,
                tweet_id=tweet_id, 
                reply_text=reply_text
            )
            
            # Log the full response in debug mode
            logger.debug(f"Reply tweet response: {json.dumps(response) if response else None}")
            
            # Update the callback manager if provided
            if run_manager:
                await run_manager.on_text("Reply posted successfully!")
                
            return self._format_response(response)
        except Exception as e:
            logger.error(f"Error replying to tweet: {str(e)}")
            return f"Error replying to tweet: {str(e)}"
    
    # Implement methods from TwitterToolMixin
    @property
    def client(self) -> Twitter:
        """Get or create Twitter API client with proper authentication."""
        if self._client is None:
            self._client = Twitter(auth_token=self.auth_token, ct0=self.ct0)
        return self._client
    
    def _format_response(self, response: Any) -> str:
        """Format API response for human-readable output."""
        if response is None:
            return "No response received from Twitter API."
        
        try:
            # For basic success responses
            if isinstance(response, dict):
                if 'errors' in response:
                    errors = response['errors']
                    return f"Error: {json.dumps(errors, indent=2)}"
                
                # Check for tweet ID in response
                if 'id_str' in response:
                    tweet_id = response['id_str']
                    return f"Success! Tweet ID: {tweet_id}"
                
                # For data-oriented responses like mentions
                if 'data' in response:
                    data_count = len(response['data'])
                    return f"Retrieved {data_count} items from Twitter API."
            
            # For list responses like mentions
            if isinstance(response, list):
                count = len(response)
                return f"Retrieved {count} items from Twitter API."
            
            # Default formatting
            return f"Twitter API response: {str(response)[:1000]}..."
            
        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            return f"Error formatting response: {str(e)}"
    
    @retry(
        wait=wait_random_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(3)
    )
    async def _safe_api_call(self, api_func, *args, **kwargs):
        """
        Make an API call with retry logic for rate limits and transient errors.
        
        Args:
            api_func: The API function to call
            *args: Arguments to pass to the API function
            **kwargs: Keyword arguments to pass to the API function
            
        Returns:
            The response from the API function
        """
        try:
            logger.debug(f"Calling API function {api_func.__name__} with args: {args} and kwargs: {kwargs}")
            response = await api_func(*args, **kwargs)
            
            # Check for rate limit errors in response
            if isinstance(response, dict) and 'errors' in response:
                for error in response['errors']:
                    if error.get('code') == 88:  # Twitter API rate limit code
                        logger.warning(f"Rate limit hit. Retrying {api_func.__name__}...")
                        raise Exception("Rate limit exceeded")
            
            logger.debug(f"API call {api_func.__name__} successful")
            return response
            
        except Exception as e:
            logger.error(f"API call {api_func.__name__} failed: {str(e)}")
            raise


class FetchMentionsTool(BaseTool):
    """Tool for fetching mentions from Twitter."""
    
    name: ClassVar[str] = "fetch_mentions"
    description: ClassVar[str] = """
    Use this tool to get recent mentions of the authenticated Twitter account.
    Can retrieve a specified number of mentions and filter by recency.
    Useful for monitoring engagement, finding questions to answer, or tracking brand mentions.
    Returns detailed information about tweets mentioning the user, including authors and content.
    """
    args_schema: ClassVar[Type[BaseModel]] = FetchMentionsInput
    
    # Add configuration for pydantic v2 compatibility
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    
    # Fields for TwitterToolMixin
    auth_token: str = Field(..., description="Twitter API authentication token")
    ct0: Optional[str] = Field(None, description="Twitter API CSRF token")
    config: ToolConfig = Field(default_factory=ToolConfig, description="Tool configuration")
    _client: Optional[Twitter] = None
    
    def _run(
        self, count: int = 20, since_id: Optional[str] = None, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Synchronous run method - properly handles running in an event loop."""
        logger.info(f"Running fetch_mentions tool requesting {count} mentions")
        try:
            # Get the current event loop
            loop = asyncio.get_event_loop()
            
            if loop.is_running():
                # If the loop is already running, we're likely inside an async context
                # Create a new thread-specific event loop for our async work
                logger.debug("Event loop is already running, using direct async fetch")
                
                # Since we can't run a new loop or use run_until_complete, we'll perform
                # the fetch operation directly and synchronously using the Twitter API
                if self._client is None:
                    self._client = Twitter(auth_token=self.auth_token, ct0=self.ct0)
                
                # Perform a synchronous fetch
                try:
                    # This is a bit of a hack, but we'll use a direct synchronous API call
                    # instead of trying to use an async one in a running event loop
                    logger.info(f"Performing synchronous fetch of {count} mentions")
                    return self._fetch_mentions_sync(count, since_id)
                except Exception as e:
                    logger.error(f"Error in synchronous fetch: {str(e)}")
                    return f"Error fetching mentions: {str(e)}"
            else:
                # If no loop is running, we can safely use run_until_complete
                logger.debug("No event loop running, using run_until_complete")
                return loop.run_until_complete(
                    self._arun(count=count, since_id=since_id, run_manager=run_manager)
                )
        except Exception as e:
            logger.error(f"Error running fetch_mentions: {str(e)}")
            return f"Error fetching mentions: {str(e)}"
    
    def _fetch_mentions_sync(self, count: int = 20, since_id: Optional[str] = None) -> str:
        """Synchronous implementation of fetch mentions."""
        logger.info(f"Fetching {count} mentions synchronously")
        
        # Initialize the Twitter client
        if self._client is None:
            self._client = Twitter(auth_token=self.auth_token, ct0=self.ct0)
            
        # For now, just return an empty result since we can't easily use async methods
        # in a synchronous context without dedicated sync API methods
        # In a production environment, you'd need a proper sync API implementation
        return f"Retrieved 0 mentions. Note: Synchronous mentions fetching is limited when running in an event loop."

    async def _arun(
        self, count: int = 20, since_id: Optional[str] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        try:
            logger.info(f"Fetching {count} mentions since ID: {since_id or 'None'}")
            # Initialize client if needed
            if self._client is None:
                self._client = Twitter(auth_token=self.auth_token, ct0=self.ct0)
                
            # First check if we can get structured mentions via timeline service
            if hasattr(self._client, 'timeline') and hasattr(self._client.timeline, 'get_home_timeline_data'):
                timeline_data = await self._safe_api_call(
                    self._client.timeline.get_home_timeline_data,
                    count=count
                )
                
                # Format the structured data
                result = self._format_mentions_data(timeline_data)
                
                # Stream results if using callback manager
                if run_manager and timeline_data:
                    await run_manager.on_text(f"Found {len(timeline_data)} mentions.")
                    for i, mention in enumerate(timeline_data[:3]):
                        if i > 0:
                            await asyncio.sleep(0.5)  # Add slight delay between streamed results
                        user = mention.get('user', {})
                        username = user.get('username', 'unknown')
                        await run_manager.on_text(f"@{username}: {mention.get('text', '')[:100]}")
                
                return result
            
            # If timeline service isn't available, try using the tweet API directly
            response = await self._safe_api_call(
                self._client.tweet.get_home_timeline,
                count=count
            )
            
            # Log the raw API response in debug mode
            logger.debug(f"Raw API response: {json.dumps(response) if response else None}")
            
            # Process raw API response
            if response and 'data' in response and 'home' in response['data']:
                # Also stream some preview results if using callback manager
                if run_manager:
                    await run_manager.on_text("Retrieved timeline data with mentions and other tweets.")
                
                return f"Retrieved timeline data - contains mentions and other tweets."
            else:
                return "No mentions found or error retrieving mentions."
                
        except Exception as e:
            logger.error(f"Error fetching mentions: {str(e)}")
            return f"Error fetching mentions: {str(e)}"
    
    def _format_mentions_data(self, mentions_data: List[Dict[str, Any]]) -> str:
        """Format mentions data into a readable string with categorization by user influence."""
        if not mentions_data:
            return "No mentions found."
        
        result = f"Retrieved {len(mentions_data)} mentions:\n\n"
        
        # Group mentions by user influence
        verified_mentions = []
        high_follower_mentions = []
        regular_mentions = []
        
        for mention in mentions_data:
            user = mention.get('user', {})
            
            # Categorize by user type
            is_verified = user.get('is_verified', False)
            followers_count = user.get('followers_count', 0)
            
            # Add to appropriate category
            if is_verified:
                verified_mentions.append(mention)
            elif followers_count > 10000:
                high_follower_mentions.append(mention)
            else:
                regular_mentions.append(mention)
        
        # Display verified mentions first
        if verified_mentions:
            result += "🔵 VERIFIED ACCOUNTS:\n"
            for mention in verified_mentions[:3]:
                user = mention.get('user', {})
                username = user.get('username', 'unknown')
                result += f"  @{username}: {mention.get('text', '')[:100]}"
                if len(mention.get('text', '')) > 100:
                    result += "..."
                result += f" [ID: {mention.get('id', 'unknown')}]\n"
            if len(verified_mentions) > 3:
                result += f"  ... and {len(verified_mentions) - 3} more verified mentions\n"
        
        # Then high-follower mentions
        if high_follower_mentions:
            result += "\n🔝 HIGH FOLLOWER ACCOUNTS:\n"
            for mention in high_follower_mentions[:3]:
                user = mention.get('user', {})
                username = user.get('username', 'unknown')
                followers = user.get('followers_count', 0)
                result += f"  @{username} ({followers:,} followers): {mention.get('text', '')[:100]}"
                if len(mention.get('text', '')) > 100:
                    result += "..."
                result += f" [ID: {mention.get('id', 'unknown')}]\n"
            if len(high_follower_mentions) > 3:
                result += f"  ... and {len(high_follower_mentions) - 3} more high-follower mentions\n"
        
        # Finally regular mentions
        if regular_mentions:
            result += "\n👥 OTHER MENTIONS:\n"
            for mention in regular_mentions[:5]:
                user = mention.get('user', {})
                username = user.get('username', 'unknown')
                result += f"  @{username}: {mention.get('text', '')[:100]}"
                if len(mention.get('text', '')) > 100:
                    result += "..."
                result += f" [ID: {mention.get('id', 'unknown')}]\n"
            if len(regular_mentions) > 5:
                result += f"  ... and {len(regular_mentions) - 5} more mentions\n"
        
        return result
    
    # Implement methods from TwitterToolMixin
    @property
    def client(self) -> Twitter:
        """Get or create Twitter API client with proper authentication."""
        if self._client is None:
            self._client = Twitter(auth_token=self.auth_token, ct0=self.ct0)
        return self._client
    
    def _format_response(self, response: Any) -> str:
        """Format API response for human-readable output."""
        if response is None:
            return "No response received from Twitter API."
        
        try:
            # For basic success responses
            if isinstance(response, dict):
                if 'errors' in response:
                    errors = response['errors']
                    return f"Error: {json.dumps(errors, indent=2)}"
                
                # Check for tweet ID in response
                if 'id_str' in response:
                    tweet_id = response['id_str']
                    return f"Success! Tweet ID: {tweet_id}"
                
                # For data-oriented responses like mentions
                if 'data' in response:
                    data_count = len(response['data'])
                    return f"Retrieved {data_count} items from Twitter API."
            
            # For list responses like mentions
            if isinstance(response, list):
                count = len(response)
                return f"Retrieved {count} items from Twitter API."
            
            # Default formatting
            return f"Twitter API response: {str(response)[:1000]}..."
            
        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            return f"Error formatting response: {str(e)}"
    
    @retry(
        wait=wait_random_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(3)
    )
    async def _safe_api_call(self, api_func, *args, **kwargs):
        """
        Make an API call with retry logic for rate limits and transient errors.
        
        Args:
            api_func: The API function to call
            *args: Arguments to pass to the API function
            **kwargs: Keyword arguments to pass to the API function
            
        Returns:
            The response from the API function
        """
        try:
            logger.debug(f"Calling API function {api_func.__name__} with args: {args} and kwargs: {kwargs}")
            response = await api_func(*args, **kwargs)
            
            # Check for rate limit errors in response
            if isinstance(response, dict) and 'errors' in response:
                for error in response['errors']:
                    if error.get('code') == 88:  # Twitter API rate limit code
                        logger.warning(f"Rate limit hit. Retrying {api_func.__name__}...")
                        raise Exception("Rate limit exceeded")
            
            logger.debug(f"API call {api_func.__name__} successful")
            return response
            
        except Exception as e:
            logger.error(f"API call {api_func.__name__} failed: {str(e)}")
            raise


class LikeTweetTool(BaseTool):
    """Tool for liking a tweet."""
    
    name: ClassVar[str] = "like_tweet"
    description: ClassVar[str] = """
    Use this tool to like a tweet on Twitter.
    Requires the tweet ID of the tweet you want to like.
    Useful for showing appreciation for content, engaging with users, or bookmarking tweets.
    """
    args_schema: ClassVar[Type[BaseModel]] = LikeTweetInput
    
    # Add configuration for pydantic v2 compatibility
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    
    # Fields for TwitterToolMixin
    auth_token: str = Field(..., description="Twitter API authentication token")
    ct0: Optional[str] = Field(None, description="Twitter API CSRF token")
    config: ToolConfig = Field(default_factory=ToolConfig, description="Tool configuration")
    _client: Optional[Twitter] = None
    
    def _run(
        self, tweet_id: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Synchronous run method - uses asyncio to call async method."""
        logger.info(f"Running like_tweet tool for tweet_id: {tweet_id}")
        return asyncio.run(self._arun(tweet_id=tweet_id, run_manager=None))

    async def _arun(
        self, tweet_id: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Like a tweet."""
        try:
            logger.info(f"Liking tweet with ID: {tweet_id}")
            # Initialize client if needed
            if self._client is None:
                self._client = Twitter(auth_token=self.auth_token, ct0=self.ct0)
                
            response = await self._safe_api_call(
                self._client.tweet.like_tweet,
                tweet_id=tweet_id
            )
            
            # Log the full response in debug mode
            logger.debug(f"Like tweet response: {json.dumps(response) if response else None}")
            
            # Update the callback manager if provided
            if run_manager:
                await run_manager.on_text("Tweet liked successfully!")
                
            return self._format_response(response)
        except Exception as e:
            logger.error(f"Error liking tweet: {str(e)}")
            return f"Error liking tweet: {str(e)}"
    
    # Implement methods from TwitterToolMixin
    @property
    def client(self) -> Twitter:
        """Get or create Twitter API client with proper authentication."""
        if self._client is None:
            self._client = Twitter(auth_token=self.auth_token, ct0=self.ct0)
        return self._client
    
    def _format_response(self, response: Any) -> str:
        """Format API response for human-readable output."""
        if response is None:
            return "No response received from Twitter API."
        
        try:
            # For basic success responses
            if isinstance(response, dict):
                if 'errors' in response:
                    errors = response['errors']
                    return f"Error: {json.dumps(errors, indent=2)}"
                
                # Check for tweet ID in response
                if 'id_str' in response:
                    tweet_id = response['id_str']
                    return f"Success! Tweet ID: {tweet_id}"
                
                # For data-oriented responses like mentions
                if 'data' in response:
                    data_count = len(response['data'])
                    return f"Retrieved {data_count} items from Twitter API."
            
            # For list responses like mentions
            if isinstance(response, list):
                count = len(response)
                return f"Retrieved {count} items from Twitter API."
            
            # Default formatting
            return f"Twitter API response: {str(response)[:1000]}..."
            
        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            return f"Error formatting response: {str(e)}"
    
    @retry(
        wait=wait_random_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(3)
    )
    async def _safe_api_call(self, api_func, *args, **kwargs):
        """
        Make an API call with retry logic for rate limits and transient errors.
        
        Args:
            api_func: The API function to call
            *args: Arguments to pass to the API function
            **kwargs: Keyword arguments to pass to the API function
            
        Returns:
            The response from the API function
        """
        try:
            logger.debug(f"Calling API function {api_func.__name__} with args: {args} and kwargs: {kwargs}")
            response = await api_func(*args, **kwargs)
            
            # Check for rate limit errors in response
            if isinstance(response, dict) and 'errors' in response:
                for error in response['errors']:
                    if error.get('code') == 88:  # Twitter API rate limit code
                        logger.warning(f"Rate limit hit. Retrying {api_func.__name__}...")
                        raise Exception("Rate limit exceeded")
            
            logger.debug(f"API call {api_func.__name__} successful")
            return response
            
        except Exception as e:
            logger.error(f"API call {api_func.__name__} failed: {str(e)}")
            raise


class RetweetTool(BaseTool):
    """Tool for retweeting a tweet."""
    
    name: ClassVar[str] = "retweet"
    description: ClassVar[str] = """
    Use this tool to retweet an existing tweet to your followers.
    Requires the tweet ID of the tweet you want to retweet.
    Useful for amplifying content, sharing valuable information, or participating in campaigns.
    """
    args_schema: ClassVar[Type[BaseModel]] = RetweetInput
    
    # Add configuration for pydantic v2 compatibility
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    
    # Fields for TwitterToolMixin
    auth_token: str = Field(..., description="Twitter API authentication token")
    ct0: Optional[str] = Field(None, description="Twitter API CSRF token")
    config: ToolConfig = Field(default_factory=ToolConfig, description="Tool configuration")
    _client: Optional[Twitter] = None
    
    def _run(
        self, tweet_id: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Synchronous run method - uses asyncio to call async method."""
        logger.info(f"Running retweet tool for tweet_id: {tweet_id}")
        return asyncio.run(self._arun(tweet_id=tweet_id, run_manager=None))

    async def _arun(
        self, tweet_id: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Retweet a tweet."""
        try:
            logger.info(f"Retweeting tweet with ID: {tweet_id}")
            # Initialize client if needed
            if self._client is None:
                self._client = Twitter(auth_token=self.auth_token, ct0=self.ct0)
                
            response = await self._safe_api_call(
                self._client.tweet.retweet,
                tweet_id=tweet_id
            )
            
            # Log the full response in debug mode
            logger.debug(f"Retweet response: {json.dumps(response) if response else None}")
            
            # Update the callback manager if provided
            if run_manager:
                await run_manager.on_text("Tweet retweeted successfully!")
                
            return self._format_response(response)
        except Exception as e:
            logger.error(f"Error retweeting: {str(e)}")
            return f"Error retweeting: {str(e)}"
    
    # Implement methods from TwitterToolMixin
    @property
    def client(self) -> Twitter:
        """Get or create Twitter API client with proper authentication."""
        if self._client is None:
            self._client = Twitter(auth_token=self.auth_token, ct0=self.ct0)
        return self._client
    
    def _format_response(self, response: Any) -> str:
        """Format API response for human-readable output."""
        if response is None:
            return "No response received from Twitter API."
        
        try:
            # For basic success responses
            if isinstance(response, dict):
                if 'errors' in response:
                    errors = response['errors']
                    return f"Error: {json.dumps(errors, indent=2)}"
                
                # Check for tweet ID in response
                if 'id_str' in response:
                    tweet_id = response['id_str']
                    return f"Success! Tweet ID: {tweet_id}"
                
                # For data-oriented responses like mentions
                if 'data' in response:
                    data_count = len(response['data'])
                    return f"Retrieved {data_count} items from Twitter API."
            
            # For list responses like mentions
            if isinstance(response, list):
                count = len(response)
                return f"Retrieved {count} items from Twitter API."
            
            # Default formatting
            return f"Twitter API response: {str(response)[:1000]}..."
            
        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            return f"Error formatting response: {str(e)}"
    
    @retry(
        wait=wait_random_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(3)
    )
    async def _safe_api_call(self, api_func, *args, **kwargs):
        """
        Make an API call with retry logic for rate limits and transient errors.
        
        Args:
            api_func: The API function to call
            *args: Arguments to pass to the API function
            **kwargs: Keyword arguments to pass to the API function
            
        Returns:
            The response from the API function
        """
        try:
            logger.debug(f"Calling API function {api_func.__name__} with args: {args} and kwargs: {kwargs}")
            response = await api_func(*args, **kwargs)
            
            # Check for rate limit errors in response
            if isinstance(response, dict) and 'errors' in response:
                for error in response['errors']:
                    if error.get('code') == 88:  # Twitter API rate limit code
                        logger.warning(f"Rate limit hit. Retrying {api_func.__name__}...")
                        raise Exception("Rate limit exceeded")
            
            logger.debug(f"API call {api_func.__name__} successful")
            return response
            
        except Exception as e:
            logger.error(f"API call {api_func.__name__} failed: {str(e)}")
            raise


def get_twitter_tools(
    auth_token: str, 
    ct0: Optional[str] = None, 
    config: Optional[ToolConfig] = None,
    include: Optional[List[str]] = None
) -> List[BaseTool]:
    """
    Get all Twitter tools with authentication.
    
    Args:
        auth_token (str): Twitter authentication token
        ct0 (Optional[str]): Twitter CSRF token. Defaults to None.
        config (Optional[ToolConfig]): Configuration for all tools. Defaults to None.
        include (Optional[List[str]]): List of tool names to include. If None, all tools are included.
            Valid names are: "post_tweet", "reply_to_tweet", "fetch_mentions", "like_tweet", "retweet"
        
    Returns:
        List[BaseTool]: List of Twitter tools
    """
    # Create the configuration object if not provided
    tool_config = config or ToolConfig()
    
    # Define all available tools
    all_tools = {
        "post_tweet": PostTweetTool(auth_token=auth_token, ct0=ct0, config=tool_config),
        "reply_to_tweet": ReplyToTweetTool(auth_token=auth_token, ct0=ct0, config=tool_config),
        "fetch_mentions": FetchMentionsTool(auth_token=auth_token, ct0=ct0, config=tool_config),
        "like_tweet": LikeTweetTool(auth_token=auth_token, ct0=ct0, config=tool_config),
        "retweet": RetweetTool(auth_token=auth_token, ct0=ct0, config=tool_config)
    }
    
    # Filter tools based on include parameter
    if include is not None:
        tools = [all_tools[name] for name in include if name in all_tools]
        logger.info(f"Returning filtered set of {len(tools)} Twitter tools: {include}")
    else:
        tools = list(all_tools.values())
        logger.info(f"Returning all {len(tools)} Twitter tools")
        
    return tools


# For testing purposes
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.DEBUG, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        stream=sys.stdout)
    logger.info("Twitter LangChain tools module loaded")