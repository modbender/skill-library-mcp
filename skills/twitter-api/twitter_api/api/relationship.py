from typing import Dict, Any, Optional

from ..core.client import TwitterAPIClient
from ..utils.constants import Endpoints
from ..utils.helpers import create_form_data

class RelationshipAPI:
    """
    API for relationship operations (follow, unfollow, block).
    """
    
    def __init__(self, client: TwitterAPIClient):
        """
        Initialize the Relationship API.
        
        Args:
            client (TwitterAPIClient): Twitter API client
        """
        self.client = client
    
    async def follow_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Follow a user.
        
        Args:
            user_id (str): ID of the user to follow
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        import aiohttp
        import json
        
        try:
            # Create form data with all required parameters from the working request
            data = {
                "user_id": user_id,
                "include_profile_interstitial_type": "1",
                "include_blocking": "1",
                "include_blocked_by": "1",
                "include_followed_by": "1",
                "include_want_retweets": "1",
                "include_mute_edge": "1",
                "include_can_dm": "1", 
                "include_can_media_tag": "1",
                "include_ext_is_blue_verified": "1",
                "include_ext_verified_type": "1",
                "include_ext_profile_image_shape": "1",
                "skip_status": "1"
            }
            
            # Use the exact endpoint from the working request
            endpoint = f"{Endpoints.API_V1_1}/friendships/create.json"
            print(f"\033[1;36m[DEBUG] Attempting to follow user_id: {user_id}\033[0m")
            print(f"\033[1;36m[DEBUG] Using endpoint: {endpoint}\033[0m")
            
            # Instead of using the client, create a direct request with the correct content type
            # Create a dedicated session to ensure headers are properly applied
            async with aiohttp.ClientSession() as session:
                # Get headers from the client but ensure content-type is set correctly
                headers = self.client.headers.copy()
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                
                # Use the client's proxy if available
                proxy = getattr(self.client, 'proxy', None)
                
                # Make the direct request with form data
                async with session.post(
                    endpoint, 
                    data=data,
                    headers=headers,
                    proxy=proxy
                ) as response:
                    status = response.status
                    
                    # Process the response
                    if status == 200:
                        try:
                            result = await response.json()
                            print(f"\033[1;32m[SUCCESS] Successfully followed user_id: {user_id}\033[0m")
                            return result
                        except json.JSONDecodeError:
                            text = await response.text()
                            print(f"\033[1;33m[WARNING] Could not parse JSON response: {text[:100]}...\033[0m")
                            return {"text": text}
                    else:
                        try:
                            error_text = await response.text()
                            try:
                                error_json = json.loads(error_text)
                                if 'errors' in error_json:
                                    error_msg = error_json['errors'][0].get('message', 'Unknown error')
                                    error_code = error_json['errors'][0].get('code', 'Unknown code')
                                    print(f"\033[1;33m[WARNING] Error from follow endpoint: Code {error_code}, Message: {error_msg}\033[0m")
                                return error_json
                            except json.JSONDecodeError:
                                print(f"\033[1;33m[WARNING] Non-JSON error response: {error_text[:100]}...\033[0m")
                                return {"error": error_text}
                        except Exception as resp_err:
                            print(f"\033[1;31m[ERROR] Error processing response: {str(resp_err)}\033[0m")
                            return {"error": str(resp_err)}
        except Exception as e:
            print(f"\033[1;31m[ERROR] Error in follow_user: {str(e)}\033[0m")
            import traceback
            print(f"\033[1;31m[TRACEBACK]\n{traceback.format_exc()}\033[0m")
            return None
    
    async def unfollow_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Unfollow a user.
        
        Args:
            user_id (str): ID of the user to unfollow
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        import aiohttp
        import json
        
        try:
            # Create form data with all required parameters from the working request
            data = {
                "user_id": user_id,
                "include_profile_interstitial_type": "1",
                "include_blocking": "1",
                "include_blocked_by": "1",
                "include_followed_by": "1",
                "include_want_retweets": "1",
                "include_mute_edge": "1",
                "include_can_dm": "1", 
                "include_can_media_tag": "1",
                "include_ext_is_blue_verified": "1",
                "include_ext_verified_type": "1",
                "include_ext_profile_image_shape": "1",
                "skip_status": "1"
            }
            
            # Use the exact endpoint from the working request
            endpoint = f"{Endpoints.API_V1_1}/friendships/destroy.json"
            print(f"\033[1;36m[DEBUG] Attempting to unfollow user_id: {user_id}\033[0m")
            print(f"\033[1;36m[DEBUG] Using endpoint: {endpoint}\033[0m")
            
            # Instead of using the client, create a direct request with the correct content type
            # Create a dedicated session to ensure headers are properly applied
            async with aiohttp.ClientSession() as session:
                # Get headers from the client but ensure content-type is set correctly
                headers = self.client.headers.copy()
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                
                # Use the client's proxy if available
                proxy = getattr(self.client, 'proxy', None)
                
                # Make the direct request with form data
                async with session.post(
                    endpoint, 
                    data=data,
                    headers=headers,
                    proxy=proxy
                ) as response:
                    status = response.status
                    
                    # Process the response
                    if status == 200:
                        try:
                            result = await response.json()
                            print(f"\033[1;32m[SUCCESS] Successfully unfollowed user_id: {user_id}\033[0m")
                            return result
                        except json.JSONDecodeError:
                            text = await response.text()
                            print(f"\033[1;33m[WARNING] Could not parse JSON response: {text[:100]}...\033[0m")
                            return {"text": text}
                    else:
                        try:
                            error_text = await response.text()
                            try:
                                error_json = json.loads(error_text)
                                if 'errors' in error_json:
                                    error_msg = error_json['errors'][0].get('message', 'Unknown error')
                                    error_code = error_json['errors'][0].get('code', 'Unknown code')
                                    print(f"\033[1;33m[WARNING] Error from unfollow endpoint: Code {error_code}, Message: {error_msg}\033[0m")
                                return error_json
                            except json.JSONDecodeError:
                                print(f"\033[1;33m[WARNING] Non-JSON error response: {error_text[:100]}...\033[0m")
                                return {"error": error_text}
                        except Exception as resp_err:
                            print(f"\033[1;31m[ERROR] Error processing response: {str(resp_err)}\033[0m")
                            return {"error": str(resp_err)}
        except Exception as e:
            print(f"\033[1;31m[ERROR] Error in unfollow_user: {str(e)}\033[0m")
            import traceback
            print(f"\033[1;31m[TRACEBACK]\n{traceback.format_exc()}\033[0m")
            return None
    
    async def block_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Block a user.
        
        Args:
            user_id (str): ID of the user to block
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        # Save original headers
        original_headers = self.client.headers.copy()
        
        try:
            # Set content type for form data
            self.client.headers.update({
                'content-type': 'application/x-www-form-urlencoded'
            })
            
            # Create form data
            data = {"user_id": user_id}
            
            # Make the request
            return await self.client.post(Endpoints.BLOCK, data=data)
        finally:
            # Restore original headers
            self.client.headers = original_headers
    
    async def unblock_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Unblock a user.
        
        Args:
            user_id (str): ID of the user to unblock
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        # Save original headers
        original_headers = self.client.headers.copy()
        
        try:
            # Set content type for form data
            self.client.headers.update({
                'content-type': 'application/x-www-form-urlencoded'
            })
            
            # Create form data
            data = {"user_id": user_id}
            
            # Make the request
            return await self.client.post(Endpoints.UNBLOCK, data=data)
        finally:
            # Restore original headers
            self.client.headers = original_headers
    
    async def follow_by_screen_name(self, screen_name: str, user_api) -> Optional[Dict[str, Any]]:
        """
        Follow a user by screen name.
        
        Args:
            screen_name (str): Screen name of the user to follow
            user_api: User API instance for fetching user ID
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        try:
            print(f"\033[1;34m[INFO] Attempting to follow user @{screen_name}\033[0m")
            
            # First, get the user ID from the screen name
            user_data = await user_api.get_user_by_screen_name(screen_name)
            print(f"\033[1;36m[DEBUG] User data type: {type(user_data)}\033[0m")
            if not user_data:
                print(f"\033[1;31m[ERROR] Failed to get user data for @{screen_name}\033[0m")
                return None
                
            # Extract the user ID from the response
            user_id = None
            
            # Try different response formats
            try:
                # First try the GraphQL format
                if "data" in user_data and "user" in user_data["data"]:
                    user_id = user_data.get("data", {}).get("user", {}).get("result", {}).get("rest_id")
                
                # Try other common GraphQL format
                elif "data" in user_data and "user_result_by_screen_name" in user_data["data"]:
                    user_id = user_data.get("data", {}).get("user_result_by_screen_name", {}).get("result", {}).get("rest_id")
                
                # If that fails, try the REST API format
                if not user_id and "id_str" in user_data:
                    user_id = user_data.get("id_str")
                
                # If that fails, try the numeric ID
                if not user_id and "id" in user_data:
                    user_id = str(user_data.get("id"))
                    
                # Try to find user ID anywhere in the response
                if not user_id:
                    def find_id(obj, key_names=["id_str", "rest_id", "id"]):
                        """Recursively search for user ID in the response"""
                        if isinstance(obj, dict):
                            for key, value in obj.items():
                                if key in key_names and isinstance(value, (str, int)):
                                    return str(value)
                                
                                found_id = find_id(value, key_names)
                                if found_id:
                                    return found_id
                        elif isinstance(obj, list):
                            for item in obj:
                                found_id = find_id(item, key_names)
                                if found_id:
                                    return found_id
                        return None
                    
                    user_id = find_id(user_data)
                    
            except Exception as e:
                print(f"\033[1;31m[ERROR] Failed to extract user ID from response: {str(e)}\033[0m")
                
            if not user_id:
                print(f"\033[1;31m[ERROR] Could not find user ID for @{screen_name}\033[0m")
                if isinstance(user_data, dict):
                    print(f"\033[1;36m[DEBUG] Response keys: {list(user_data.keys())}\033[0m")
                return None
                
            print(f"\033[1;32m[SUCCESS] Found user ID for @{screen_name}: {user_id}\033[0m")
            
            # Now follow the user using the user ID
            return await self.follow_user(user_id)
        except Exception as e:
            print(f"\033[1;31m[ERROR] Error in follow_by_screen_name for @{screen_name}: {str(e)}\033[0m")
            import traceback
            print(f"\033[1;31m[TRACEBACK]\n{traceback.format_exc()}\033[0m")
            return None
    
    async def unfollow_by_screen_name(self, screen_name: str, user_api) -> Optional[Dict[str, Any]]:
        """
        Unfollow a user by screen name.
        
        Args:
            screen_name (str): Screen name of the user to unfollow
            user_api: User API instance for fetching user ID
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        try:
            print(f"\033[1;34m[INFO] Attempting to unfollow user @{screen_name}\033[0m")
            
            # First, get the user ID from the screen name
            user_data = await user_api.get_user_by_screen_name(screen_name)
            print(f"\033[1;36m[DEBUG] User data: {user_data}\033[0m")
            if not user_data:
                print(f"\033[1;31m[ERROR] Failed to get user data for @{screen_name}\033[0m")
                return None
                
            # Extract the user ID from the response
            user_id = None
            
            # Try different response formats
            try:
                # First try the GraphQL format
                if "data" in user_data and "user" in user_data["data"]:
                    user_id = user_data.get("data", {}).get("user", {}).get("result", {}).get("rest_id")
                
                # If that fails, try the REST API format
                if not user_id and "id_str" in user_data:
                    user_id = user_data.get("id_str")
                
                # If that fails, try the numeric ID
                if not user_id and "id" in user_data:
                    user_id = str(user_data.get("id"))
                    
            except Exception as e:
                print(f"\033[1;31m[ERROR] Failed to extract user ID from response: {str(e)}\033[0m")
                
            if not user_id:
                print(f"\033[1;31m[ERROR] Could not find user ID for @{screen_name}\033[0m")
                print(f"\033[1;36m[DEBUG] Response structure: {list(user_data.keys())}\033[0m")
                return None
                
            print(f"\033[1;32m[SUCCESS] Found user ID for @{screen_name}: {user_id}\033[0m")
            
            # Now unfollow the user using the user ID
            return await self.unfollow_user(user_id)
        except Exception as e:
            print(f"\033[1;31m[ERROR] Error in unfollow_by_screen_name for @{screen_name}: {str(e)}\033[0m")
            import traceback
            print(f"\033[1;31m[TRACEBACK]\n{traceback.format_exc()}\033[0m")
            return None
    
    async def block_by_screen_name(self, screen_name: str, user_api) -> Optional[Dict[str, Any]]:
        """
        Block a user by screen name.
        
        Args:
            screen_name (str): Screen name of the user to block
            user_api: User API instance for fetching user ID
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        user_id = await user_api.get_user_id_by_screen_name(screen_name)
        if user_id:
            return await self.block_user(user_id)
        return None
    
    async def unblock_by_screen_name(self, screen_name: str, user_api) -> Optional[Dict[str, Any]]:
        """
        Unblock a user by screen name.
        
        Args:
            screen_name (str): Screen name of the user to unblock
            user_api: User API instance for fetching user ID
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        user_id = await user_api.get_user_id_by_screen_name(screen_name)
        if user_id:
            return await self.unblock_user(user_id)
        return None