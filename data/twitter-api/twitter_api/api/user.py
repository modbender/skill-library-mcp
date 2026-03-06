from typing import Dict, Any, Optional, List

from ..core.client import TwitterAPIClient
from ..utils.constants import (
    Endpoints, 
    GraphQLQueries, 
    COMMON_FEATURES, 
    USER_TWEETS_FEATURES,
    USER_TWEETS_FIELD_TOGGLES
)
from ..utils.helpers import create_graphql_payload, parse_user_id_from_response

class UserAPI:
    """
    API for user-related operations.
    """
    
    def __init__(self, client: TwitterAPIClient):
        """
        Initialize the User API.
        
        Args:
            client (TwitterAPIClient): Twitter API client
        """
        self.client = client
    
    async def get_user_by_screen_name(self, screen_name: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by screen name.
        
        Args:
            screen_name (str): Twitter screen name (username)
            
        Returns:
            Optional[Dict[str, Any]]: User information
        """
        variables = {
            "screen_name": screen_name,
            "withSafetyModeUserFields": True
        }
        
        payload = create_graphql_payload(
            variables=variables,
            features=COMMON_FEATURES,
            query_id=GraphQLQueries.USER_BY_SCREEN_NAME
        )
        
        # Use POST instead of GET for GraphQL endpoints
        return await self.client.post(Endpoints.USER_BY_SCREEN_NAME, json_data=payload)
    
    async def get_user_id_by_screen_name(self, screen_name: str) -> Optional[str]:
        """
        Get user ID by screen name.
        
        Args:
            screen_name (str): Twitter screen name (username)
            
        Returns:
            Optional[str]: User ID
        """
        response = await self.get_user_by_screen_name(screen_name)
        if response:
            return parse_user_id_from_response(response)
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by user ID.
        
        Args:
            user_id (str): Twitter user ID
            
        Returns:
            Optional[Dict[str, Any]]: User information
        """
        variables = {
            "userId": user_id,
            "withSafetyModeUserFields": True
        }
        
        payload = create_graphql_payload(
            variables=variables,
            features=COMMON_FEATURES,
            query_id=GraphQLQueries.USER_BY_REST_ID
        )
        
        return await self.client.get(Endpoints.USER_BY_REST_ID, json_data=payload)
    
    async def check_username_availability(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Check if a username is available.
        
        Args:
            username (str): Username to check
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API containing availability status and suggestions
        """
        # Save original headers
        original_headers = self.client.headers.copy()
        
        try:
            # Add required headers
            self.client.headers.update({
                'content-type': 'application/x-www-form-urlencoded',
                'authority': 'twitter.com',
                'x-client-transaction-id': '0a96a85c03ea09f40b3126d6471da7207b5fe6c213f33171920be59487e42674'
            })
            
            # Set up form data
            data = {
                'username': username,
                'full_name': username,
                'suggest': 'true'
            }
            
            return await self.client.get(Endpoints.CHECK_USERNAME, data=data)
        finally:
            # Restore original headers
            self.client.headers = original_headers
    
    async def fetch_user_info(self, user_id: Optional[str] = None, screen_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch user information by user ID or screen name.
        
        Args:
            user_id (Optional[str], optional): Twitter user ID. Defaults to None.
            screen_name (Optional[str], optional): Twitter screen name. Defaults to None.
            
        Returns:
            Optional[Dict[str, Any]]: User information
        """
        if user_id:
            return await self.get_user_by_id(user_id)
        elif screen_name:
            return await self.get_user_by_screen_name(screen_name)
        else:
            raise ValueError("Either user_id or screen_name must be provided")
    
    async def fetch_user_id(self, screen_name: str) -> Optional[str]:
        """
        Fetch user ID by screen name.
        
        Args:
            screen_name (str): Twitter screen name
            
        Returns:
            Optional[str]: User ID
        """
        return await self.get_user_id_by_screen_name(screen_name)
    
    async def get_notifications(self) -> Optional[Dict[str, Any]]:
        """
        Get user notifications with all required parameters.
        
        Returns:
            Optional[Dict[str, Any]]: Notifications data
        """
        params = {
            'include_profile_interstitial_type': 1,
            'include_blocking': 1,
            'include_blocked_by': 1,
            'include_followed_by': 1,
            'include_want_retweets': 1,
            'include_mute_edge': 1,
            'include_can_dm': 1,
            'include_can_media_tag': 1,
            'include_ext_is_blue_verified': 1,
            'include_ext_verified_type': 1,
            'include_ext_profile_image_shape': 1,
            'skip_status': 1,
            'cards_platform': 'Web-12',
            'include_cards': 1,
            'include_ext_alt_text': 1,
            'include_ext_limited_action_results': 1,
            'include_quote_count': 1,
            'include_reply_count': 1,
            'tweet_mode': 'extended',
            'include_ext_views': 1,
            'include_entities': 1,
            'include_user_entities': 1,
            'include_ext_media_color': 1,
            'include_ext_media_availability': 1,
            'include_ext_sensitive_media_warning': 1,
            'include_ext_trusted_friends_metadata': 1,
            'send_error_codes': 1,
            'simple_quoted_tweet': 1,
            'count': 40,
            'ext': 'mediaStats,highlightedLabel,parodyCommentaryFanLabel,voiceInfo,birdwatchPivot,superFollowMetadata,unmentionInfo,editControl,article'
        }
        
        return await self.client.get(Endpoints.NOTIFICATIONS, params=params)
    
    async def get_user_tweets(
        self, 
        user_id: str, 
        count: int = 20, 
        cursor: Optional[str] = None,
        include_promoted_content: bool = True,
        with_quick_promote_eligibility_fields: bool = True,
        with_voice: bool = True,
        with_v2_timeline: bool = True,
        include_replies: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get tweets from a user's timeline.
        
        Args:
            user_id (str): ID of the user whose tweets to fetch
            count (int, optional): Number of tweets to fetch. Defaults to 20.
            cursor (Optional[str], optional): Pagination cursor. Defaults to None.
            include_promoted_content (bool, optional): Whether to include promoted content. Defaults to True.
            with_quick_promote_eligibility_fields (bool, optional): Whether to include quick promote eligibility fields. Defaults to True.
            with_voice (bool, optional): Whether to include voice tweets. Defaults to True.
            with_v2_timeline (bool, optional): Whether to use v2 timeline. Defaults to True.
            include_replies (bool, optional): Whether to include replies in the timeline. Defaults to False.
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API containing tweets and pagination info
        """
        try:
            import json
            from urllib.parse import urlencode

            # Prepare variables
            variables = {
                "userId": user_id,
                "count": count,
                "includePromotedContent": include_promoted_content,
                "withQuickPromoteEligibilityTweetFields": with_quick_promote_eligibility_fields,
                "withVoice": with_voice,
                "withV2Timeline": with_v2_timeline
            }
            
            # Add includeReplies parameter if needed
            if include_replies:
                variables["includeReplies"] = True
            
            # Add cursor for pagination if provided
            if cursor:
                variables["cursor"] = cursor
            
            # Use the exact features from the working request
            features = USER_TWEETS_FEATURES

            # Prepare field toggles
            field_toggles = USER_TWEETS_FIELD_TOGGLES
            
            # Build the URL with parameters
            params = {
                "variables": json.dumps(variables),
                "features": json.dumps(features),
                "fieldToggles": json.dumps(field_toggles)
            }
            
            # Use the exact URL format from the working request
            query_id = GraphQLQueries.USER_TWEETS
            url = f"https://x.com/i/api/graphql/{query_id}/UserTweets?{urlencode(params)}"
            
            print(f"\033[1;35m[DEBUG] Using URL: {url}\033[0m")
            
            # Use GET method as shown in the working request
            return await self.client.get(url)
            
        except Exception as e:
            print(f"\033[1;31m[ERROR] Error in get_user_tweets: {str(e)}\033[0m")
            import traceback
            print(f"\033[1;31m[TRACEBACK]\n{traceback.format_exc()}\033[0m")
            return None
            
    async def get_user_tweets_and_replies(
        self, 
        user_id: str, 
        count: int = 20, 
        cursor: Optional[str] = None,
        include_promoted_content: bool = True,
        with_community: bool = True,
        with_voice: bool = True,
        with_v2_timeline: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get tweets and replies from a user's timeline.
        
        Args:
            user_id (str): ID of the user whose tweets and replies to fetch
            count (int, optional): Number of tweets to fetch. Defaults to 20.
            cursor (Optional[str], optional): Pagination cursor. Defaults to None.
            include_promoted_content (bool, optional): Whether to include promoted content. Defaults to True.
            with_community (bool, optional): Whether to include community tweets. Defaults to True.
            with_voice (bool, optional): Whether to include voice tweets. Defaults to True.
            with_v2_timeline (bool, optional): Whether to use v2 timeline. Defaults to True.
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API containing tweets, replies and pagination info
        """
        try:
            import json
            from urllib.parse import urlencode

            # Prepare variables
            variables = {
                "userId": user_id,
                "count": count,
                "includePromotedContent": include_promoted_content,
                "withCommunity": with_community,
                "withVoice": with_voice,
                "withV2Timeline": with_v2_timeline
            }
            
            # Add cursor for pagination if provided
            if cursor:
                variables["cursor"] = cursor
            
            # Use the exact features from the working request
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

            # Prepare field toggles
            field_toggles = {
                "withArticlePlainText": False
            }
            
            # Build the URL with parameters
            params = {
                "variables": json.dumps(variables),
                "features": json.dumps(features),
                "fieldToggles": json.dumps(field_toggles)
            }
            
            # Use the updated query ID from the working request
            query_id = GraphQLQueries.USER_TWEETS_AND_REPLIES
            
            # Try using the standard endpoint first
            url = f"https://x.com/i/api/graphql/{query_id}/UserTweetsAndReplies?{urlencode(params)}"
            
            print(f"\033[1;35m[DEBUG] Using URL: {url}\033[0m")
            
            # Use GET method as shown in the working request
            response = await self.client.get(url)
            
            # If the response is None or has a 404 status, try the alternative endpoint
            if response is None or (isinstance(response, dict) and response.get('status') == 404):
                print("\033[1;33m[INFO] Primary endpoint failed, trying alternative endpoint...\033[0m")
                
                # Use the user tweets endpoint with includeReplies=true parameter
                variables["includeReplies"] = True
                params["variables"] = json.dumps(variables)
                
                alt_query_id = GraphQLQueries.USER_TWEETS
                alt_url = f"https://x.com/i/api/graphql/{alt_query_id}/UserTweets?{urlencode(params)}"
                print(f"\033[1;35m[DEBUG] Using alternative URL: {alt_url}\033[0m")
                
                return await self.client.get(alt_url)
            
            return response
            
        except Exception as e:
            print(f"\033[1;31m[ERROR] Error in get_user_tweets_and_replies: {str(e)}\033[0m")
            import traceback
            print(f"\033[1;31m[TRACEBACK]\n{traceback.format_exc()}\033[0m")
            return None
            
    async def get_user_media_tweets(
        self,
        user_id: str,
        count: int = 20,
        cursor: Optional[str] = None,
        include_promoted_content: bool = False,
        with_client_event_token: bool = False,
        with_birdwatch_notes: bool = False,
        with_voice: bool = True,
        with_v2_timeline: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get media tweets for a user.
        
        Args:
            user_id (str): The user ID to get media tweets for
            count (int, optional): Number of tweets to return. Defaults to 20.
            cursor (Optional[str], optional): Pagination cursor. Defaults to None.
            include_promoted_content (bool, optional): Whether to include promoted content. Defaults to False.
            with_client_event_token (bool, optional): Whether to include client event token. Defaults to False.
            with_birdwatch_notes (bool, optional): Whether to include birdwatch notes. Defaults to False.
            with_voice (bool, optional): Whether to include voice tweets. Defaults to True.
            with_v2_timeline (bool, optional): Whether to use v2 timeline. Defaults to True.
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        try:
            import json
            from urllib.parse import urlencode

            # Prepare variables
            variables = {
                "userId": user_id,
                "count": count,
                "includePromotedContent": include_promoted_content,
                "withClientEventToken": with_client_event_token,
                "withBirdwatchNotes": with_birdwatch_notes,
                "withVoice": with_voice,
                "withV2Timeline": with_v2_timeline
            }
            
            # Add cursor if provided
            if cursor:
                variables["cursor"] = cursor
            
            # Prepare features
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
            
            # Prepare field toggles
            field_toggles = {
                "withArticlePlainText": False
            }
            
            # Build the URL with parameters
            params = {
                "variables": json.dumps(variables),
                "features": json.dumps(features),
                "fieldToggles": json.dumps(field_toggles)
            }
            
            # Use the correct query ID and URL format
            query_id = GraphQLQueries.USER_MEDIA
            url = f"https://x.com/i/api/graphql/{query_id}/UserMedia?{urlencode(params)}"
            
            print(f"\033[1;36m[DEBUG] Using URL: {url}\033[0m")
            
            # Use GET method
            return await self.client.get(url)
            
        except Exception as e:
            print(f"\033[1;31m[ERROR] Error fetching user media tweets: {str(e)}\033[0m")
            import traceback
            print(f"\033[1;31m[TRACEBACK]\n{traceback.format_exc()}\033[0m")
            return None
            
    async def get_user_followings(
        self,
        user_id: str,
        count: int = 20,
        cursor: Optional[str] = None,
        include_promoted_content: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get users that a specific user is following with pagination support.
        
        Args:
            user_id (str): The user ID to get followings for
            count (int, optional): Number of followings to return per page. Defaults to 20.
            cursor (Optional[str], optional): Pagination cursor. Defaults to None.
            include_promoted_content (bool, optional): Whether to include promoted content. Defaults to False.
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API containing followings data and pagination info
        """
        try:
            import json
            from urllib.parse import urlencode

            # Prepare variables based on the request header
            variables = {
                "userId": user_id,
                "count": count,
                "includePromotedContent": include_promoted_content
            }
            
            # Add cursor for pagination if provided
            if cursor:
                variables["cursor"] = cursor
            
            # Use the exact features from the request header
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
            
            # Build the URL with parameters
            params = {
                "variables": json.dumps(variables),
                "features": json.dumps(features)
            }
            
            # Use the correct query ID from constants
            query_id = GraphQLQueries.FOLLOWING
            url = f"https://x.com/i/api/graphql/{query_id}/Following?{urlencode(params)}"
            
            print(f"\033[1;35m[DEBUG] Using URL for followings: {url}\033[0m")
            
            # Use GET method
            response = await self.client.get(url)
            
            if response:
                print(f"\033[1;32m[SUCCESS] Successfully fetched followings for user ID: {user_id}\033[0m")
                
                # Save the response to a file for debugging
                try:
                    import os
                    response_dir = "response_logs"
                    os.makedirs(response_dir, exist_ok=True)
                    
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{response_dir}/followings_{user_id}_{timestamp}.json"
                    
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(response, f, indent=2)
                    print(f"\033[1;32m[SUCCESS] Saved followings response to {filename}\033[0m")
                except Exception as e:
                    print(f"\033[1;31m[ERROR] Failed to save followings response: {str(e)}\033[0m")
            
            return response
            
        except Exception as e:
            print(f"\033[1;31m[ERROR] Error fetching user followings: {str(e)}\033[0m")
            import traceback
            print(f"\033[1;31m[TRACEBACK]\n{traceback.format_exc()}\033[0m")
            return None


async def _demo_get_user(screen_name: str, auth_token: str, ct0: str) -> None:
    """Load primary creds and call get_user_by_screen_name."""
    client = TwitterAPIClient(auth_token, ct0=ct0)
    user_api = UserAPI(client)
    data = await user_api.get_user_by_screen_name(screen_name)
    if data is None:
        print("No data (auth or user not found)")
        return
    import json
    print(json.dumps(data, indent=2, default=str))


def _format_notifications_response(data: Dict[str, Any]) -> str:
    """Turn raw get_notifications() response into a readable summary."""
    lines = []
    users = (data.get("globalObjects") or {}).get("users") or {}
    id_to_handle = {str(uid): u.get("screen_name") or str(uid) for uid, u in users.items()}

    def find_notification_entries(obj: Any, out: List[Dict[str, Any]]) -> None:
        if isinstance(obj, dict):
            if "notification" in obj:
                n = obj["notification"]
                if isinstance(n, dict):
                    url = (n.get("url") or {}) if isinstance(n.get("url"), dict) else {}
                    link = url.get("url") or ""
                    ctx = (n.get("socialContext") or {}).get("generalContext") or {}
                    ctx_text = ctx.get("text") or ""
                    from_users = n.get("fromUsers") or []
                    targets = n.get("targetTweets") or []
                    from_handles = [id_to_handle.get(uid, uid) for uid in from_users]
                    out.append({
                        "type": (ctx_text or "notification").strip() or "notification",
                        "from": from_handles,
                        "tweets": targets,
                        "url": link,
                    })
            for v in obj.values():
                find_notification_entries(v, out)
        elif isinstance(obj, list):
            for v in obj:
                find_notification_entries(v, out)

    entries: List[Dict[str, Any]] = []
    find_notification_entries(data, entries)

    lines.append(f"Notifications ({len(entries)})\n")
    for i, e in enumerate(entries, 1):
        typ = e.get("type") or "—"
        from_ = e.get("from") or []
        tweets = e.get("tweets") or []
        url = e.get("url") or ""
        from_str = ", @".join(from_) if from_ else "n/a"
        if from_str != "n/a":
            from_str = "@" + from_str
        tweet_str = ", ".join(tweets[:3]) + ("..." if len(tweets) > 3 else "") if tweets else ""
        lines.append(f"  {i}. [{typ}]")
        lines.append(f"     From: {from_str}")
        if tweet_str:
            lines.append(f"     Tweets: {tweet_str}")
        if url:
            lines.append(f"     URL: {url}")
        lines.append("")
    return "\n".join(lines).rstrip()


async def _demo_get_notifications(auth_token: str, ct0: str) -> None:
    """Load primary creds and call get_notifications."""
    client = TwitterAPIClient(auth_token, ct0=ct0)
    user_api = UserAPI(client)
    data = await user_api.get_notifications()
    if data is None:
        print("No data (auth failed or no notifications)")
        return
    print(_format_notifications_response(data))


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
    if len(sys.argv) > 1 and sys.argv[1].strip().lower() in ("notifications", "--notifications"):
        asyncio.run(_demo_get_notifications(auth, ct0))
    else:
        screen_name = (sys.argv[1] if len(sys.argv) > 1 else "pixelagents_app").strip()
        asyncio.run(_demo_get_user(screen_name, auth, ct0))

