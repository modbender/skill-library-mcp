from typing import Dict, Any, List, Optional

from ..core.client import TwitterAPIClient
from ..utils.constants import Endpoints, GraphQLQueries, CREATE_TWEET_FEATURES, TWEET_FEATURES, TWEET_URL_WITH_USERNAME, TWEET_URL_WITHOUT_USERNAME
from ..utils.helpers import create_graphql_payload

class TweetAPI:
    """
    API for tweet-related operations.
    """
    
    def __init__(self, client: TwitterAPIClient):
        """
        Initialize the Tweet API.
        
        Args:
            client (TwitterAPIClient): Twitter API client
        """
        self.client = client
    
    async def create_tweet(self, tweet_text: str) -> Optional[Dict[str, Any]]:
        """
        Create a tweet.
        
        Args:
            tweet_text (str): Text of the tweet
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        try:
            variables = {
                "tweet_text": tweet_text,
                "dark_request": False,
                "media": {
                    "media_entities": [],
                    "possibly_sensitive": False
                },
                "semantic_annotation_ids": [],
                "disallowed_reply_options": None,
            }
            payload = {
                "variables": variables,
                "features": CREATE_TWEET_FEATURES,
                "queryId": GraphQLQueries.CREATE_TWEET
            }
            return await self.client.post(Endpoints.CREATE_TWEET, json_data=payload)
        except Exception as e:
            import logging
            logging.error(f"Error in create_tweet: {str(e)}")
            raise
    
    async def delete_tweet(self, tweet_id: str) -> Optional[Dict[str, Any]]:
        """
        Delete a tweet.
        
        Args:
            tweet_id (str): ID of the tweet to delete
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        try:
            variables = {
                "tweet_id": tweet_id,
                "dark_request": False
            }
            
            payload = {
                "variables": variables,
                "queryId": GraphQLQueries.DELETE_TWEET
            }
            
            return await self.client.post(Endpoints.DELETE_TWEET, json_data=payload)
        except Exception as e:
            import logging
            logging.error(f"Error in delete_tweet: {str(e)}")
            raise
    
    async def like_tweet(self, tweet_id: str) -> Optional[Dict[str, Any]]:
        """
        Like a tweet.
        
        Args:
            tweet_id (str): ID of the tweet to like
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        try:
            variables = {
                "tweet_id": tweet_id
            }
            
            payload = {
                "variables": variables,
                "queryId": GraphQLQueries.LIKE_TWEET
            }
            
            return await self.client.post(Endpoints.LIKE_TWEET, json_data=payload)
        except Exception as e:
            import logging
            logging.error(f"Error in like_tweet: {str(e)}")
            raise
    
    async def unlike_tweet(self, tweet_id: str) -> Optional[Dict[str, Any]]:
        """
        Unlike a tweet.
        
        Args:
            tweet_id (str): ID of the tweet to unlike
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        try:
            variables = {
                "tweet_id": tweet_id
            }
            
            payload = {
                "variables": variables,
                "queryId": GraphQLQueries.UNLIKE_TWEET
            }
            
            return await self.client.post(Endpoints.UNLIKE_TWEET, json_data=payload)
        except Exception as e:
            import logging
            logging.error(f"Error in unlike_tweet: {str(e)}")
            raise
    
    async def retweet(self, tweet_id: str) -> Optional[Dict[str, Any]]:
        """
        Retweet a tweet.
        
        Args:
            tweet_id (str): ID of the tweet to retweet
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        try:
            variables = {
                "tweet_id": tweet_id,
                "dark_request": False
            }
            
            payload = {
                "variables": variables,
                "queryId": GraphQLQueries.RETWEET
            }
            
            return await self.client.post(Endpoints.RETWEET, json_data=payload)
        except Exception as e:
            import logging
            logging.error(f"Error in retweet: {str(e)}")
            raise
    
    async def unretweet(self, tweet_id: str) -> Optional[Dict[str, Any]]:
        """
        Unretweet a tweet.
        
        Args:
            tweet_id (str): ID of the tweet to unretweet
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        try:
            variables = {
                "tweet_id": tweet_id,
                "dark_request": False
            }
            
            payload = {
                "variables": variables,
                "queryId": GraphQLQueries.UNRETWEET
            }
            
            return await self.client.post(Endpoints.UNRETWEET, json_data=payload)
        except Exception as e:
            import logging
            logging.error(f"Error in unretweet: {str(e)}")
            raise
    
    async def reply(self, tweet_id: str, reply_text: str) -> Optional[Dict[str, Any]]:
        """
        Reply to a tweet.
        
        Args:
            tweet_id (str): ID of the tweet to reply to
            reply_text (str): Text of the reply
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        try:
            variables = {
                "tweet_text": reply_text,
                "reply": {
                    "in_reply_to_tweet_id": tweet_id,
                    "exclude_reply_user_ids": []
                },
                "dark_request": False,
                "media": {
                    "media_entities": [],
                    "possibly_sensitive": False
                },
                "semantic_annotation_ids": []
            }
            
            payload = {
                "variables": variables,
                "features": TWEET_FEATURES,
                "queryId": GraphQLQueries.REPLY
            }
            
            return await self.client.post(Endpoints.REPLY_TWEET, json_data=payload)
        except Exception as e:
            import logging
            logging.error(f"Error in reply: {str(e)}")
            raise
    
    async def quote_tweet(self, tweet_id: str, quote_text: str, username: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Quote a tweet.
        
        Args:
            tweet_id (str): ID of the tweet to quote
            quote_text (str): Text of the quote
            username (str, optional): Username of the tweet author. If not provided, will use i/status format
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        try:
            # Construct attachment URL based on whether username is provided
            attachment_url = TWEET_URL_WITH_USERNAME.format(username=username, tweet_id=tweet_id) if username else TWEET_URL_WITHOUT_USERNAME.format(tweet_id=tweet_id)
            
            variables = {
                "tweet_text": quote_text,
                "attachment_url": attachment_url,
                "dark_request": False,
                "media": {
                    "media_entities": [],
                    "possibly_sensitive": False
                },
                "semantic_annotation_ids": []
            }
            
            payload = {
                "variables": variables,
                "features": TWEET_FEATURES,
                "queryId": GraphQLQueries.QUOTE
            }
            
            return await self.client.post(Endpoints.QUOTE_TWEET, json_data=payload)
        except Exception as e:
            import logging
            logging.error(f"Error in quote: {str(e)}")
            raise
    
    async def mass_tweet(self, messages: List[str]) -> List[Optional[Dict[str, Any]]]:
        """
        Create multiple tweets.
        
        Args:
            messages (List[str]): List of tweet texts
            
        Returns:
            List[Optional[Dict[str, Any]]]: List of responses from the API
        """
        results = []
        for message in messages:
            result = await self.create_tweet(message)
            results.append(result)
        return results
    
    async def get_home_timeline(self, count: int = 20, include_promoted_content: bool = True, seen_tweet_ids: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Get the home timeline for the authenticated user.
        
        Args:
            count (int, optional): Number of tweets to fetch. Defaults to 20.
            include_promoted_content (bool, optional): Whether to include promoted content. Defaults to True.
            seen_tweet_ids (Optional[List[str]], optional): List of tweet IDs that have been seen. Defaults to None.
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API containing the home timeline
        """
        try:
            variables = {
                "count": count,
                "includePromotedContent": include_promoted_content,
                "latestControlAvailable": True,
                "requestContext": "launch",
                "withCommunity": True
            }
            
            # Add seen tweet IDs if provided
            if seen_tweet_ids:
                variables["seenTweetIds"] = seen_tweet_ids
            
            features = {
                "rweb_video_screen_enabled": False,
                "profile_label_improvements_pcf_label_in_post_enabled": True,
                "rweb_tipjar_consumption_enabled": True,
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "premium_content_api_read_enabled": False,
                "communities_web_enable_tweet_community_results_fetch": True,
                "c9s_tweet_anatomy_moderator_badge_enabled": True,
                "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
                "responsive_web_grok_analyze_post_followups_enabled": True,
                "responsive_web_jetfuel_frame": False,
                "responsive_web_grok_share_attachment_enabled": True,
                "articles_preview_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "responsive_web_twitter_article_tweet_consumption_enabled": True,
                "tweet_awards_web_tipping_enabled": False,
                "responsive_web_grok_analysis_button_from_backend": True,
                "creator_subscriptions_quote_tweet_preview_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "rweb_video_timestamps_enabled": True,
                "longform_notetweets_rich_text_read_enabled": True,
                "longform_notetweets_inline_media_enabled": True,
                "responsive_web_grok_image_annotation_enabled": False,
                "responsive_web_enhance_cards_enabled": False
            }
            
            # Create payload
            payload = {
                "variables": variables,
                "features": features,
                "queryId": GraphQLQueries.HOME_TIMELINE
            }
            
            # Make the request
            return await self.client.post(Endpoints.HOME_TIMELINE, json_data=payload)
            
        except Exception as e:
            print(f"Error getting home timeline: {e}")
            return None

    async def get_tweet_by_id(self, tweet_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full tweet details (text, author, metrics, media) by tweet ID.
        Uses authenticated request so you can fetch any public tweet.
        Tries internal 1.1-style statuses/show first; falls back to GraphQL TweetDetail if needed.

        Args:
            tweet_id (str): Tweet ID (e.g. from https://x.com/user/status/1234567890)

        Returns:
            Optional[Dict[str, Any]]: Tweet data (1.1: text, user.screen_name, etc.; GraphQL: nested)
        """
        try:
            # Try internal 1.1-style endpoint (cookie auth often works)
            out = await self.client.get(Endpoints.STATUSES_SHOW, params={"id": tweet_id})
            if out and isinstance(out, dict) and (out.get("text") is not None or out.get("id_str")):
                return out
            # GraphQL TweetDetail (GET with query params — matches browser)
            variables = {
                "focalTweetId": tweet_id,
                "referrer": "home",
                "with_rux_injections": False,
                "rankingMode": "Relevance",
                "includePromotedContent": True,
                "withCommunity": True,
                "withQuickPromoteEligibilityTweetFields": True,
                "withBirdwatchNotes": True,
                "withVoice": True,
            }
            field_toggles = {
                "withArticleRichContentState": True,
                "withArticlePlainText": False,
                "withGrokAnalyze": False,
                "withDisallowedReplyControls": False,
            }
            payload = {
                "variables": variables,
                "features": TWEET_FEATURES,
                "queryId": GraphQLQueries.TWEET_DETAIL,
                "fieldToggles": field_toggles,
            }
            # TweetDetail is GET with variables/features as query params
            return await self.client.get(Endpoints.TWEET_DETAIL, json_data=payload)
        except Exception as e:
            import logging
            logging.error(f"Error in get_tweet_by_id: {str(e)}")
            return None


def _extract_tweet_text_and_author(data: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract tweet text and author from API response (1.1 or GraphQL). Returns list of {text, author, id}."""
    out: List[Dict[str, Any]] = []
    if not data:
        return out
    # 1.1-style: top-level text, user.screen_name
    if data.get("id_str") or data.get("id"):
        uid = str(data.get("id_str") or data.get("id", ""))
        text = data.get("full_text") or data.get("text") or ""
        user = data.get("user") or {}
        author = user.get("screen_name") or user.get("screen_name") or "?"
        out.append({"id": uid, "text": text, "author": author})
        return out

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            if "legacy" in obj and isinstance(obj.get("legacy"), dict):
                leg = obj["legacy"]
                if "full_text" in leg or "text" in leg:
                    # Prefer full text from note_tweet for long/thread tweets
                    text = leg.get("full_text") or leg.get("text") or ""
                    note = obj.get("note_tweet") or {}
                    note_result = (note.get("note_tweet_results") or {}).get("result") if isinstance(note, dict) else {}
                    if isinstance(note_result, dict) and note_result.get("text"):
                        text = note_result.get("text", "")
                    user = (obj.get("core", {}) or {}).get("user_results", {}) or {}
                    user_result = user.get("result", {}) if isinstance(user, dict) else {}
                    user_core = (user_result.get("core", {}) or {}) if isinstance(user_result, dict) else {}
                    user_leg = (user_result.get("legacy", {}) or {}) if isinstance(user_result, dict) else {}
                    screen_name = user_core.get("screen_name") or user_leg.get("screen_name") or user_result.get("rest_id") or "?"
                    out.append({
                        "id": leg.get("id_str") or "",
                        "text": text,
                        "author": screen_name,
                    })
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(data)
    return out


async def _demo_get_tweet(tweet_id: str, auth: str, ct0: str) -> None:
    from ..core.client import TwitterAPIClient
    client = TwitterAPIClient(auth, ct0=ct0)
    api = TweetAPI(client)
    raw = await api.get_tweet_by_id(tweet_id)
    if not raw:
        print("No response (auth or tweet not found / unavailable)")
        return
    tweets = _extract_tweet_text_and_author(raw)
    if tweets:
        for t in tweets:
            print("---")
            print("Author: @" + str(t.get("author", "?")))
            print("ID:", t.get("id", "?"))
            print("Text:", t.get("text", ""))
    else:
        import json
        print("Could not parse tweet from response. Raw keys:", list(raw.keys()))
        print(json.dumps(raw, indent=2, default=str)[:2000])


if __name__ == "__main__":
    import asyncio
    import os
    import sys
    cwd = os.path.abspath(os.getcwd())
    for path in [os.path.join(cwd, ".env"), os.path.join(cwd, "social_ops", ".env")]:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
            break
    auth = os.environ.get("GANCLAW_X_PRIMARY_AUTH_TOKEN") or os.environ.get("PICLAW_TWITTER_AUTH_TOKEN") or ""
    ct0 = os.environ.get("GANCLAW_X_PRIMARY_CT0") or os.environ.get("PICLAW_TWITTER_CT0") or ""
    if not auth or not ct0:
        print("Set GANCLAW_X_PRIMARY_AUTH_TOKEN and GANCLAW_X_PRIMARY_CT0 (e.g. in .env)")
        raise SystemExit(1)
    ids = [a.strip() for a in sys.argv[1:] if a.strip()]
    if not ids:
        print("Usage: py -m twitter_api.api.tweet <tweet_id> [tweet_id ...]")
        print("Example: py -m twitter_api.api.tweet 2024596902109442426")
        raise SystemExit(1)
    async def run():
        for i, tid in enumerate(ids):
            if i > 0:
                print()
            await _demo_get_tweet(tid, auth, ct0)
    asyncio.run(run())