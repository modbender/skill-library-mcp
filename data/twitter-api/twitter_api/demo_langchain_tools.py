"""
Test script for Twitter LangChain tools.

This script demonstrates how to use the Twitter LangChain tools
to interact with Twitter using the provided credentials.
"""

import asyncio
import logging
import sys
from typing import List

from twitter_api.langchain_tools import (
    get_twitter_tools,
    ToolConfig,
    PostTweetTool,
    ReplyToTweetTool,
    FetchMentionsTool,
    LikeTweetTool,
    RetweetTool
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("twitter_tools_demo")

# Twitter credentials
AUTH_TOKEN = "f06ec149475390a01262510a1cc1b59c9760a318"
CT0 = "37318663228df008399ba56501e3512d4b1b1d30eb852fc958561da0888027014e91199162dbc93f745a296fe0189018d1025f12b5dd065bb1d14798103016f3a0662487bebcf132aaff91db01812e0d"
USERNAME = "Jordyn_Luv"

async def demo_post_tweet(tool: PostTweetTool):
    """Demo posting a tweet."""
    logger.info("Testing PostTweetTool...")
    
    # Post a tweet
    current_time = asyncio.get_event_loop().time()
    tweet_text = f"Testing Twitter API with LangChain tools! This is an automated test post at time index: {current_time:.0f}"
    
    logger.info(f"Posting tweet: {tweet_text}")
    result = await tool._arun(tweet_text=tweet_text)
    
    logger.info(f"Result: {result}")
    
    # Extract tweet ID from response
    tweet_id = None
    if "Tweet ID" in result:
        tweet_id = result.split("Tweet ID: ")[1].strip()
        logger.info(f"Successfully posted tweet with ID: {tweet_id}")
    
    return tweet_id

async def demo_fetch_mentions(tool: FetchMentionsTool):
    """Demo fetching mentions."""
    logger.info("Testing FetchMentionsTool...")
    
    # Fetch mentions
    result = await tool._arun(count=10)
    
    logger.info("Mentions result:")
    logger.info(result)
    
    # Extract tweet IDs from result
    tweet_ids = []
    for line in result.split('\n'):
        if "[ID:" in line:
            try:
                tweet_id = line.split("[ID:")[1].split("]")[0].strip()
                tweet_ids.append(tweet_id)
            except:
                pass
    
    return tweet_ids

async def demo_like_tweet(tool: LikeTweetTool, tweet_id: str):
    """Demo liking a tweet."""
    if not tweet_id:
        logger.warning("No tweet ID provided for liking.")
        return
        
    logger.info(f"Testing LikeTweetTool with tweet ID: {tweet_id}")
    
    # Like the tweet
    result = await tool._arun(tweet_id=tweet_id)
    
    logger.info(f"Like result: {result}")
    
    return result

async def demo_reply_to_tweet(tool: ReplyToTweetTool, tweet_id: str):
    """Demo replying to a tweet."""
    if not tweet_id:
        logger.warning("No tweet ID provided for replying.")
        return
        
    logger.info(f"Testing ReplyToTweetTool with tweet ID: {tweet_id}")
    
    # Reply to the tweet
    reply_text = "This is a test reply from LangChain Twitter tools!"
    result = await tool._arun(tweet_id=tweet_id, reply_text=reply_text)
    
    logger.info(f"Reply result: {result}")
    
    # Extract reply tweet ID
    reply_id = None
    if "Tweet ID" in result:
        reply_id = result.split("Tweet ID: ")[1].strip()
        logger.info(f"Successfully posted reply with ID: {reply_id}")
    
    return reply_id

async def demo_retweet(tool: RetweetTool, tweet_id: str):
    """Demo retweeting a tweet."""
    if not tweet_id:
        logger.warning("No tweet ID provided for retweeting.")
        return
        
    logger.info(f"Testing RetweetTool with tweet ID: {tweet_id}")
    
    # Retweet the tweet
    result = await tool._arun(tweet_id=tweet_id)
    
    logger.info(f"Retweet result: {result}")
    
    return result

async def cleanup_sessions(tools):
    """Clean up all aiohttp sessions to prevent resource warnings."""
    for tool in tools:
        if hasattr(tool, '_client') and tool._client:
            if hasattr(tool._client, 'client') and tool._client.client:
                if hasattr(tool._client.client, '_session') and tool._client.client._session:
                    await tool._client.client._session.close()
                    logger.info(f"Closed session for {tool.name}")

async def run_demo():
    """Run the full Twitter tools demo."""
    logger.info(f"Starting Twitter tools demo for user @{USERNAME}")
    
    # Create tool configuration with debug mode
    tool_config = ToolConfig(
        debug_mode=True,
        max_retries=3,
        retry_min_wait=2,
        retry_max_wait=15
    )
    
    # Get all Twitter tools
    tools = get_twitter_tools(
        auth_token=AUTH_TOKEN,
        ct0=CT0,
        config=tool_config
    )
    
    # Get individual tools
    post_tweet_tool = next((t for t in tools if t.name == "post_tweet"), None)
    fetch_mentions_tool = next((t for t in tools if t.name == "fetch_mentions"), None)
    like_tweet_tool = next((t for t in tools if t.name == "like_tweet"), None)
    reply_to_tweet_tool = next((t for t in tools if t.name == "reply_to_tweet"), None)
    retweet_tool = next((t for t in tools if t.name == "retweet"), None)
    
    if not all([post_tweet_tool, fetch_mentions_tool, like_tweet_tool, reply_to_tweet_tool, retweet_tool]):
        logger.error("Failed to get all required tools")
        return
    
    try:
        # Post a new tweet
        tweet_id = await demo_post_tweet(post_tweet_tool)
        
        if tweet_id:
            # Like our own tweet
            await demo_like_tweet(like_tweet_tool, tweet_id)
            
            # Reply to our own tweet
            reply_id = await demo_reply_to_tweet(reply_to_tweet_tool, tweet_id)
            
            # Like the reply
            if reply_id:
                await demo_like_tweet(like_tweet_tool, reply_id)
        
        # Fetch mentions
        mention_ids = await demo_fetch_mentions(fetch_mentions_tool)
        
        # Like a mention if any exists
        if mention_ids:
            random_mention_id = mention_ids[0]
            await demo_like_tweet(like_tweet_tool, random_mention_id)
        
        logger.info("Twitter tools demo completed successfully!")
    finally:
        # Clean up sessions to prevent resource warnings
        await cleanup_sessions(tools)

if __name__ == "__main__":
    asyncio.run(run_demo())