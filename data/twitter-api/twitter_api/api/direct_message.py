from typing import Dict, Any, Optional, List

from ..core.client import TwitterAPIClient
from ..utils.constants import Endpoints, GraphQLQueries, COMMON_FEATURES
from ..utils.helpers import create_graphql_payload

class DirectMessageAPI:
    """
    API for direct message operations.
    """
    
    def __init__(self, client: TwitterAPIClient):
        """
        Initialize the Direct Message API.
        
        Args:
            client (TwitterAPIClient): Twitter API client
        """
        self.client = client
    
    async def send_dm(self, recipient_id: str, text: str) -> Optional[Dict[str, Any]]:
        """
        Send a direct message to a user.
        
        Args:
            recipient_id (str): ID of the recipient
            text (str): Message text
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        try:
            # Get the user's own ID
            user_info = await self.client.get(Endpoints.VERIFY_CREDENTIALS)
            if not user_info:
                return None
                
            user_id = user_info.get("id")
            
            # Prepare the payload
            json_payload = {
                "conversation_id": f"{user_id}-{recipient_id}",
                "recipient_ids": False,
                "request_id": f"{user_id}-{recipient_id}",  # This should be a unique ID
                "text": text,
                "cards_platform": "Web-12",
                "include_cards": 1,
                "include_quote_count": True,
                "dm_users": False
            }
            
            # Prepare query parameters
            query_params = {
                'ext': 'mediaColor,altText,mediaStats,highlightedLabel,voiceInfo,birdwatchPivot,superFollowMetadata,unmentionInfo,editControl,article',
                'include_ext_alt_text': 'true',
                'include_ext_limited_action_results': 'true',
                'include_reply_count': '1',
                'tweet_mode': 'extended',
                'include_ext_views': 'true',
                'include_groups': 'true',
                'include_inbox_timelines': 'true',
                'include_ext_media_color': 'true',
                'supports_reactions': 'true',
            }
            
            # Make the request
            return await self.client.post(Endpoints.CREATE_DM, json_data=json_payload, params=query_params)
        except Exception as e:
            import logging
            logging.error(f"Error in send_dm: {str(e)}")
            return None
    
    async def send_dm_to_multiple(self, recipient_ids: List[str], text: str) -> List[Optional[Dict[str, Any]]]:
        """
        Send a direct message to multiple users.
        
        Args:
            recipient_ids (List[str]): List of recipient IDs
            text (str): Message text
            
        Returns:
            List[Optional[Dict[str, Any]]]: List of responses from the API
        """
        results = []
        for recipient_id in recipient_ids:
            result = await self.send_dm(recipient_id, text)
            results.append(result)
        return results
    
    async def send_dm_by_screen_name(self, screen_name: str, text: str, user_api) -> Optional[Dict[str, Any]]:
        """
        Send a direct message to a user by screen name.
        
        Args:
            screen_name (str): Screen name of the recipient
            text (str): Message text
            user_api: User API instance for fetching user ID
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        user_id = await user_api.get_user_id_by_screen_name(screen_name)
        if user_id:
            return await self.send_dm(user_id, text)
        return None

    async def send_dm_with_memory(self, recipient_id: str, text: str, memory_manager=None) -> Optional[Dict[str, Any]]:
        """
        Send a direct message to a user and record the interaction in memory.
        
        Args:
            recipient_id (str): ID of the recipient
            text (str): Message text
            memory_manager: Optional memory manager to record the interaction
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        # Send the DM
        result = await self.send_dm(recipient_id, text)
        
        # Record in memory if memory manager is provided
        if memory_manager and result:
            try:
                # Get user info if available
                user_info = await self.client.get(f"users/show.json?user_id={recipient_id}")
                screen_name = user_info.get("screen_name", "unknown") if user_info else "unknown"
                
                # Create a memory record
                memory_record = {
                    "type": "direct_message",
                    "recipient_id": recipient_id,
                    "recipient_screen_name": screen_name,
                    "message": text,
                    "timestamp": result.get("created_at", None),
                    "message_id": result.get("id", None),
                    "success": True if result else False
                }
                
                # Store in memory
                await memory_manager.store_interaction(memory_record)
            except Exception as e:
                import logging
                logging.error(f"Error recording DM in memory: {str(e)}")
        
        return result