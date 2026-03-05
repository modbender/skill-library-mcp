from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
import asyncio
import os

from ..api.tweet import TweetAPI

class TweetUser(TypedDict):
    id: str
    username: str
    display_name: str
    is_verified: bool
    profile_image_url: str
    followers_count: int
    following_count: int

class TweetMedia(TypedDict):
    type: str
    url: str
    width: Optional[int]
    height: Optional[int]

class TweetMetrics(TypedDict):
    likes: int
    retweets: int
    replies: int
    quotes: int
    views: Optional[int]
    bookmarks: int

class TweetData(TypedDict):
    id: str
    text: str
    created_at: str
    created_at_timestamp: float
    is_promoted: bool
    user: TweetUser
    metrics: TweetMetrics
    media: List[TweetMedia]
    urls: List[str]
    hashtags: List[str]
    mentioned_users: List[str]

class TimelineService:
    """
    Service for processing Twitter timeline responses and extracting structured data.
    """
    
    def __init__(self, tweet_api: TweetAPI):
        """
        Initialize the Timeline Service.
        
        Args:
            tweet_api (TweetAPI): Twitter API instance for tweets
        """
        self.tweet_api = tweet_api
    
    async def get_home_timeline_data(
        self, 
        count: int = 20, 
        include_promoted_content: bool = True,
        seen_tweet_ids: Optional[List[str]] = None
    ) -> List[TweetData]:
        """
        Fetch home timeline and process it into structured data.
        
        Args:
            count (int, optional): Number of tweets to fetch. Defaults to 20.
            include_promoted_content (bool, optional): Whether to include promoted content. Defaults to True.
            seen_tweet_ids (Optional[List[str]], optional): List of tweet IDs that have been seen. Defaults to None.
            
        Returns:
            List[TweetData]: List of processed tweet data
        """
        # Fetch raw timeline data
        response = await self.tweet_api.get_home_timeline(
            count=count,
            include_promoted_content=include_promoted_content,
            seen_tweet_ids=seen_tweet_ids
        )
        
        # Process the response
        if not response or 'data' not in response or 'home' not in response['data']:
            return []
        
        return self._extract_tweets_from_timeline(response)
    
    def _extract_tweets_from_timeline(self, response: Dict[str, Any]) -> List[TweetData]:
        """
        Extract tweet data from timeline response.
        
        Args:
            response (Dict[str, Any]): Raw API response
            
        Returns:
            List[TweetData]: Structured tweet data
        """
        tweets = []
        
        try:
            timeline = response['data']['home']['home_timeline_urt']
            
            if 'instructions' not in timeline:
                return []
            
            # Find the TimelineAddEntries instruction which contains the tweets
            for instruction in timeline['instructions']:
                if instruction['type'] != 'TimelineAddEntries' or 'entries' not in instruction:
                    continue
                
                # Process each entry in the timeline
                for entry in instruction['entries']:
                    # Skip non-tweet entries (e.g., "who to follow", ads without tweet structure, etc.)
                    if ('content' not in entry or 
                        'itemContent' not in entry['content'] or 
                        entry['content']['itemContent'].get('itemType') != 'TimelineTweet'):
                        continue
                    
                    # Extract tweet data
                    tweet_content = entry['content']['itemContent']
                    if 'tweet_results' not in tweet_content or 'result' not in tweet_content['tweet_results']:
                        continue
                    
                    # Check if this is a promoted tweet
                    is_promoted = 'promoted-tweet' in entry.get('entryId', '')
                    
                    # Extract the tweet
                    tweet_result = tweet_content['tweet_results']['result']
                    
                    # Skip entries without proper tweet structure
                    if 'legacy' not in tweet_result or 'core' not in tweet_result:
                        continue
                    
                    # Process this tweet
                    tweet_data = self._process_tweet(tweet_result, is_promoted)
                    if tweet_data:
                        tweets.append(tweet_data)
            
        except Exception as e:
            print(f"Error processing timeline: {e}")
        
        return tweets
    
    def _process_tweet(self, tweet_result: Dict[str, Any], is_promoted: bool) -> Optional[TweetData]:
        """
        Process a single tweet from the timeline.
        
        Args:
            tweet_result (Dict[str, Any]): Raw tweet data
            is_promoted (bool): Whether this tweet is promoted
            
        Returns:
            Optional[TweetData]: Structured tweet data or None if processing fails
        """
        try:
            legacy = tweet_result['legacy']
            
            # Extract user data
            user_data = tweet_result['core']['user_results']['result']
            user_legacy = user_data['legacy']
            
            user = TweetUser(
                id=user_data.get('rest_id', ''),
                username=user_legacy.get('screen_name', ''),
                display_name=user_legacy.get('name', ''),
                is_verified=user_data.get('is_blue_verified', False),
                profile_image_url=user_legacy.get('profile_image_url_https', ''),
                followers_count=user_legacy.get('followers_count', 0),
                following_count=user_legacy.get('friends_count', 0)
            )
            
            # Extract metrics
            metrics = TweetMetrics(
                likes=legacy.get('favorite_count', 0),
                retweets=legacy.get('retweet_count', 0),
                replies=legacy.get('reply_count', 0),
                quotes=legacy.get('quote_count', 0),
                views=int(tweet_result.get('views', {}).get('count', 0)) if tweet_result.get('views') else None,
                bookmarks=legacy.get('bookmark_count', 0)
            )
            
            # Extract media
            media_list = []
            if 'extended_entities' in legacy and 'media' in legacy['extended_entities']:
                for media_item in legacy['extended_entities']['media']:
                    media_type = media_item.get('type', 'photo')
                    media_url = media_item.get('media_url_https', '')
                    
                    # Get dimensions if available
                    width = None
                    height = None
                    if 'original_info' in media_item:
                        width = media_item['original_info'].get('width')
                        height = media_item['original_info'].get('height')
                    
                    # For videos, use the highest quality URL
                    if media_type == 'video' and 'video_info' in media_item and 'variants' in media_item['video_info']:
                        variants = media_item['video_info']['variants']
                        # Find the highest bitrate mp4
                        mp4_variants = [v for v in variants if v.get('content_type') == 'video/mp4' and 'bitrate' in v]
                        if mp4_variants:
                            highest_bitrate = max(mp4_variants, key=lambda x: x.get('bitrate', 0))
                            media_url = highest_bitrate.get('url', media_url)
                    
                    media_list.append(TweetMedia(
                        type=media_type,
                        url=media_url,
                        width=width,
                        height=height
                    ))
            
            # Extract URLs, hashtags, and mentions
            urls = []
            hashtags = []
            mentioned_users = []
            
            if 'entities' in legacy:
                entities = legacy['entities']
                
                # Extract URLs
                if 'urls' in entities:
                    for url_entity in entities['urls']:
                        if 'expanded_url' in url_entity:
                            urls.append(url_entity['expanded_url'])
                
                # Extract hashtags
                if 'hashtags' in entities:
                    for hashtag in entities['hashtags']:
                        if 'text' in hashtag:
                            hashtags.append(f"#{hashtag['text']}")
                
                # Extract mentions
                if 'user_mentions' in entities:
                    for mention in entities['user_mentions']:
                        if 'screen_name' in mention:
                            mentioned_users.append(f"@{mention['screen_name']}")
            
            # Convert created_at to timestamp
            created_at = legacy.get('created_at', '')
            created_at_timestamp = 0
            try:
                # Parse Twitter's created_at format: "Mon Mar 17 16:00:01 +0000 2025"
                dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
                created_at_timestamp = dt.timestamp()
            except Exception:
                pass
            
            # Create the tweet data structure
            tweet_data = TweetData(
                id=legacy.get('id_str', ''),
                text=legacy.get('full_text', ''),
                created_at=created_at,
                created_at_timestamp=created_at_timestamp,
                is_promoted=is_promoted,
                user=user,
                metrics=metrics,
                media=media_list,
                urls=urls,
                hashtags=hashtags,
                mentioned_users=mentioned_users
            )
            
            return tweet_data
            
        except Exception as e:
            print(f"Error processing tweet: {e}")
            return None

async def demo_timeline_service(auth_token: str, ct0_token: str) -> None:
    """
    Demo function to show how to use the TimelineService.
    
    Args:
        auth_token (str): Authentication token
        ct0_token (str): CSRF token
    """
    from ..core.client import TwitterAPIClient
    
    # Initialize client and API (client builds cookie/x-csrf-token from auth_token + ct0)
    client = TwitterAPIClient(auth_token, ct0=ct0_token)
    tweet_api = TweetAPI(client)
    timeline_service = TimelineService(tweet_api)
    
    # Get processed timeline data
    tweets = await timeline_service.get_home_timeline_data(count=10)
    
    # Print results
    print(f"Found {len(tweets)} tweets")
    
    for i, tweet in enumerate(tweets, 1):
        print(f"\n--- TWEET {i} ---")
        print(f"ID: {tweet['id']}")
        print(f"Author: {tweet['user']['display_name']} (@{tweet['user']['username']})")
        print(f"Verified: {'Yes' if tweet['user']['is_verified'] else 'No'}")
        print(f"Text: {tweet['text'][:100]}{'...' if len(tweet['text']) > 100 else ''}")
        print(f"Created: {tweet['created_at']}")
        print(f"Metrics: {tweet['metrics']['likes']} likes, {tweet['metrics']['retweets']} retweets, " +
              f"{tweet['metrics']['replies']} replies, {tweet['metrics']['quotes']} quotes")
        if tweet['metrics']['views'] is not None:
            print(f"Views: {tweet['metrics']['views']}")
        
        if tweet['media']:
            print(f"Media: {len(tweet['media'])} items")
            for media in tweet['media']:
                print(f"  - {media['type']}: {media['url']}")
        
        if tweet['hashtags']:
            print(f"Hashtags: {', '.join(tweet['hashtags'])}")
        
        if tweet['is_promoted']:
            print("PROMOTED TWEET")
        
        print("-" * 40)

def _load_dotenv(env_path: Optional[os.PathLike] = None) -> None:
    """Load .env from path or search from cwd for .env (e.g. social_ops/.env)."""
    if env_path and os.path.isfile(env_path):
        path = env_path
    else:
        cwd = os.path.abspath(os.getcwd())
        for candidate in [os.path.join(cwd, ".env"), os.path.join(cwd, "social_ops", ".env")]:
            if os.path.isfile(candidate):
                path = candidate
                break
        else:
            return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


if __name__ == "__main__":
    _load_dotenv()
    auth_token = os.environ.get("GANCLAW_X_PRIMARY_AUTH_TOKEN") or os.environ.get("PICLAW_TWITTER_AUTH_TOKEN") or "YOUR_AUTH_TOKEN"
    ct0_token = os.environ.get("GANCLAW_X_PRIMARY_CT0") or os.environ.get("PICLAW_TWITTER_CT0") or "YOUR_CT0_TOKEN"
    if auth_token == "YOUR_AUTH_TOKEN" or ct0_token == "YOUR_CT0_TOKEN":
        print("Set GANCLAW_X_PRIMARY_AUTH_TOKEN and GANCLAW_X_PRIMARY_CT0 (e.g. in .env) or pass tokens.")
        raise SystemExit(1)
    asyncio.run(demo_timeline_service(auth_token, ct0_token)) 