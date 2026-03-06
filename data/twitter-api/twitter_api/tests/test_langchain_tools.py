"""
Unit tests for the Twitter API LangChain tool wrappers.
"""

import pytest
import asyncio
import json
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock

# Add the parent directory to the path so we can import the twitter_api module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the tools being tested
from twitter_api.langchain_tools import (
    PostTweetTool, 
    ReplyToTweetTool,
    FetchMentionsTool,
    LikeTweetTool,
    RetweetTool,
    get_twitter_tools,
    ToolConfig
)

# Mock response data for tests
MOCK_TWEET_RESPONSE = {
    "id_str": "1234567890",
    "text": "This is a test tweet",
    "created_at": "Fri May 09 12:00:00 +0000 2025"
}

MOCK_MENTIONS_RESPONSE = [
    {
        "id": "1234567891",
        "text": "Hey @testuser, can you help me with something?",
        "user": {
            "username": "user1",
            "display_name": "User One",
            "is_verified": True,
            "followers_count": 5000
        }
    },
    {
        "id": "1234567892",
        "text": "Great article @testuser!",
        "user": {
            "username": "user2",
            "display_name": "User Two", 
            "is_verified": False,
            "followers_count": 20000
        }
    }
]

@pytest.fixture
def mock_twitter_client():
    """Fixture to create a mock Twitter client."""
    with patch('twitter_api.langchain_tools.Twitter') as mock_client:
        # Set up the mock tweet API methods
        mock_client.return_value.tweet = MagicMock()
        mock_client.return_value.tweet.create_tweet = AsyncMock(return_value=MOCK_TWEET_RESPONSE)
        mock_client.return_value.tweet.reply = AsyncMock(return_value=MOCK_TWEET_RESPONSE)
        mock_client.return_value.tweet.like_tweet = AsyncMock(return_value={"status": "ok"})
        mock_client.return_value.tweet.retweet = AsyncMock(return_value={"status": "ok"})
        
        # Set up the mock timeline service
        mock_client.return_value.timeline = MagicMock()
        mock_client.return_value.timeline.get_home_timeline_data = AsyncMock(return_value=MOCK_MENTIONS_RESPONSE)
        
        yield mock_client


class TestPostTweetTool:
    """Tests for the PostTweetTool."""
    
    def test_initialization(self):
        """Test that the tool initializes correctly."""
        tool = PostTweetTool(auth_token="test_token", ct0="test_ct0")
        assert tool.name == "post_tweet"
        assert "post a new tweet" in tool.description.lower()
    
    @pytest.mark.asyncio
    async def test_post_tweet_success(self, mock_twitter_client):
        """Test successful tweet posting."""
        tool = PostTweetTool(auth_token="test_token", ct0="test_ct0")
        result = await tool._arun(tweet_text="Hello, Twitter!")
        
        # Verify the API was called correctly
        mock_twitter_client.return_value.tweet.create_tweet.assert_called_once_with(
            tweet_text="Hello, Twitter!"
        )
        
        # Verify the result contains the tweet ID
        assert "1234567890" in result
    
    @pytest.mark.asyncio
    async def test_post_tweet_error(self, mock_twitter_client):
        """Test error handling in tweet posting."""
        # Set up the mock to raise an exception
        mock_twitter_client.return_value.tweet.create_tweet.side_effect = Exception("API error")
        
        tool = PostTweetTool(auth_token="test_token", ct0="test_ct0")
        result = await tool._arun(tweet_text="Hello, Twitter!")
        
        # Verify the error is returned in the result
        assert "Error posting tweet" in result


class TestReplyToTweetTool:
    """Tests for the ReplyToTweetTool."""
    
    def test_initialization(self):
        """Test that the tool initializes correctly."""
        tool = ReplyToTweetTool(auth_token="test_token", ct0="test_ct0")
        assert tool.name == "reply_to_tweet"
        assert "reply to an existing tweet" in tool.description.lower()
    
    @pytest.mark.asyncio
    async def test_reply_tweet_success(self, mock_twitter_client):
        """Test successful tweet reply."""
        tool = ReplyToTweetTool(auth_token="test_token", ct0="test_ct0")
        result = await tool._arun(tweet_id="1234567890", reply_text="This is a reply")
        
        # Verify the API was called correctly
        mock_twitter_client.return_value.tweet.reply.assert_called_once_with(
            tweet_id="1234567890", 
            reply_text="This is a reply"
        )
        
        # Verify the result contains the tweet ID
        assert "1234567890" in result


class TestFetchMentionsTool:
    """Tests for the FetchMentionsTool."""
    
    def test_initialization(self):
        """Test that the tool initializes correctly."""
        tool = FetchMentionsTool(auth_token="test_token", ct0="test_ct0")
        assert tool.name == "fetch_mentions"
        assert "mentions" in tool.description.lower()
    
    @pytest.mark.asyncio
    async def test_fetch_mentions_success(self, mock_twitter_client):
        """Test successful mentions fetching."""
        tool = FetchMentionsTool(auth_token="test_token", ct0="test_ct0")
        result = await tool._arun(count=10)
        
        # Verify the API was called correctly
        mock_twitter_client.return_value.timeline.get_home_timeline_data.assert_called_once_with(
            count=10
        )
        
        # Verify the result contains expected user info
        assert "user1" in result
        assert "user2" in result
        assert "VERIFIED ACCOUNTS" in result
        assert "HIGH FOLLOWER ACCOUNTS" in result
    
    @pytest.mark.asyncio
    async def test_format_mentions_data(self):
        """Test the formatting of mentions data."""
        tool = FetchMentionsTool(auth_token="test_token", ct0="test_ct0")
        result = tool._format_mentions_data(MOCK_MENTIONS_RESPONSE)
        
        # Check for expected formatting markers
        assert "Retrieved 2 mentions" in result
        assert "VERIFIED ACCOUNTS" in result
        assert "HIGH FOLLOWER ACCOUNTS" in result


class TestLikeTweetTool:
    """Tests for the LikeTweetTool."""
    
    def test_initialization(self):
        """Test that the tool initializes correctly."""
        tool = LikeTweetTool(auth_token="test_token", ct0="test_ct0")
        assert tool.name == "like_tweet"
        assert "like a tweet" in tool.description.lower()
    
    @pytest.mark.asyncio
    async def test_like_tweet_success(self, mock_twitter_client):
        """Test successful tweet liking."""
        tool = LikeTweetTool(auth_token="test_token", ct0="test_ct0")
        result = await tool._arun(tweet_id="1234567890")
        
        # Verify the API was called correctly
        mock_twitter_client.return_value.tweet.like_tweet.assert_called_once_with(
            tweet_id="1234567890"
        )
        
        # Verify the result indicates success
        assert "API response" in result


class TestRetweetTool:
    """Tests for the RetweetTool."""
    
    def test_initialization(self):
        """Test that the tool initializes correctly."""
        tool = RetweetTool(auth_token="test_token", ct0="test_ct0")
        assert tool.name == "retweet"
        assert "retweet" in tool.description.lower()
    
    @pytest.mark.asyncio
    async def test_retweet_success(self, mock_twitter_client):
        """Test successful retweeting."""
        tool = RetweetTool(auth_token="test_token", ct0="test_ct0")
        result = await tool._arun(tweet_id="1234567890")
        
        # Verify the API was called correctly
        mock_twitter_client.return_value.tweet.retweet.assert_called_once_with(
            tweet_id="1234567890"
        )
        
        # Verify the result indicates success
        assert "API response" in result


class TestToolGeneration:
    """Tests for the get_twitter_tools function."""
    
    def test_get_all_tools(self):
        """Test getting all tools."""
        tools = get_twitter_tools(auth_token="test_token", ct0="test_ct0")
        assert len(tools) == 5
        assert any(tool.name == "post_tweet" for tool in tools)
        assert any(tool.name == "reply_to_tweet" for tool in tools)
        assert any(tool.name == "fetch_mentions" for tool in tools)
        assert any(tool.name == "like_tweet" for tool in tools)
        assert any(tool.name == "retweet" for tool in tools)
    
    def test_get_filtered_tools(self):
        """Test getting a filtered set of tools."""
        tools = get_twitter_tools(
            auth_token="test_token", 
            ct0="test_ct0",
            include=["post_tweet", "reply_to_tweet"]
        )
        
        assert len(tools) == 2
        assert any(tool.name == "post_tweet" for tool in tools)
        assert any(tool.name == "reply_to_tweet" for tool in tools)
        assert not any(tool.name == "fetch_mentions" for tool in tools)
    
    def test_tool_config_applied(self):
        """Test that tool configuration is applied."""
        config = ToolConfig(debug_mode=True, max_retries=5)
        tools = get_twitter_tools(
            auth_token="test_token", 
            ct0="test_ct0",
            config=config
        )
        
        # Check that the config was applied to all tools
        for tool in tools:
            assert tool.config.debug_mode is True
            assert tool.config.max_retries == 5