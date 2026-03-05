import os
import logging
from typing import Dict, Any, Optional
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from aiohttp.formdata import FormData
import aiohttp

from ..core.client import TwitterAPIClient
from ..utils.constants import Endpoints, UPLOAD_URL, PROFILE_HEADERS
from ..utils.helpers import create_form_data, read_image_as_base64

class ProfileAPI:
    """
    API for profile-related operations.
    """
    
    def __init__(self, auth_token: str, ct0: str = None):
        """
        Initialize the Profile API.
        
        Args:
            auth_token (str): Twitter API authentication token
            ct0 (str, optional): Twitter API ct0 value. Defaults to None.
        """
        self.client = TwitterAPIClient(auth_token, ct0)
        self.auth_token = auth_token
        self.ct0 = ct0
    
    async def update_profile_details(self, name: Optional[str] = None, description: Optional[str] = None, location: Optional[str] = None,
                                birthdate_day: str = "26", birthdate_month: str = "4", birthdate_year: str = "1996",
                                birthdate_visibility: str = "mutualfollow", birthdate_year_visibility: str = "self") -> dict:
        """Update profile details including name, bio, location and birthday."""
        try:
            # Set up headers
            headers = PROFILE_HEADERS.copy()
            headers.update({
                'content-type': 'application/x-www-form-urlencoded',
                'x-csrf-token': self.ct0
            })
            
            # Set up cookies
            cookies = {
                'auth_token': self.auth_token,
                'ct0': self.ct0
            }
            
            # Prepare the payload
            payload = {
                'birthdate_day': birthdate_day,
                'birthdate_month': birthdate_month,
                'birthdate_year': birthdate_year,
                'birthdate_visibility': birthdate_visibility,
                'birthdate_year_visibility': birthdate_year_visibility,
                'displayNameMaxLength': '50'
            }
            
            # Add optional fields if provided
            if name is not None:
                payload['name'] = name
            if description is not None:
                payload['description'] = description
            if location is not None:
                payload['location'] = location
            
            # Make the request
            async with aiohttp.ClientSession() as session:
                async with session.post(Endpoints.UPDATE_PROFILE, headers=headers, cookies=cookies, data=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        response_text = await response.text()
                        logging.error(f"Failed to update profile. Status: {response.status}, Response: {response_text}")
                        return None
        except Exception as e:
            logging.error(f"Error in update_profile_details: {str(e)}")
            raise
    
    async def update_profile_settings(self, screen_name: str, allow_dms_from: str = 'all') -> dict:
        """Update profile settings including screen name and DM preferences."""
        payload = {
            'include_mention_filter': True,
            'include_nsfw_user_flag': True,
            'include_nsfw_admin_flag': True,
            'include_ranked_timeline': True,
            'include_alt_text_compose': True,
            'allow_dms_from': allow_dms_from,  # all, verified, following
            'dm_receipt_setting': 'all_disabled',
            'dm_quality_filter': 'disabled',
            'screen_name': screen_name
        }
        return await self.client.post(Endpoints.UPDATE_PROFILE_SETTINGS, data=payload)
    
    async def update_profile_photo(self, image_path: str) -> dict:
        """Update profile photo."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        total_bytes = os.path.getsize(image_path)
        media_type = "image/jpeg"  # You might want to detect this from the file

        # Initialize upload
        init_data = await self._initialize_upload(total_bytes, media_type, "profile_image")
        if not init_data:
            raise Exception("Failed to initialize media upload")
        
        media_id = init_data.get('media_id')

        # Upload chunks
        chunk_size = 4 * 1024 * 1024  # 4MB chunks
        with open(image_path, 'rb') as f:
            segment_index = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                status = await self._upload_chunk(media_id, chunk, segment_index)
                if status != 204:
                    raise Exception(f"Failed to upload chunk {segment_index}")
                segment_index += 1

        # Finalize upload
        finalize_data = await self._finalize_upload(media_id, image_path)
        if not finalize_data:
            raise Exception("Failed to finalize media upload")

        # Update profile image
        return await self._update_profile_image(media_id)
    
    async def update_profile_banner(self, image_path: str) -> dict:
        """Update profile banner."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        total_bytes = os.path.getsize(image_path)
        media_type = "image/jpeg"  # You might want to detect this from the file

        # Initialize upload
        init_data = await self._initialize_upload(total_bytes, media_type, "banner_image")
        if not init_data:
            raise Exception("Failed to initialize media upload")
        
        media_id = init_data.get('media_id')

        # Upload chunks
        chunk_size = 4 * 1024 * 1024  # 4MB chunks
        with open(image_path, 'rb') as f:
            segment_index = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                status = await self._upload_chunk(media_id, chunk, segment_index)
                if status != 204:
                    raise Exception(f"Failed to upload chunk {segment_index}")
                segment_index += 1

        # Finalize upload
        finalize_data = await self._finalize_upload(media_id, image_path)
        if not finalize_data:
            raise Exception("Failed to finalize media upload")

        # Update banner
        return await self._update_profile_banner(media_id)
    
    async def _initialize_upload(self, total_bytes: int, media_type: str, media_category: str) -> Optional[Dict[str, Any]]:
        """Initialize media upload."""
        url = f"{UPLOAD_URL}?command=INIT&total_bytes={total_bytes}&media_type={media_type}&media_category={media_category}"
        return await self.client.post(url)
    
    async def _upload_chunk(self, media_id: str, chunk: bytes, segment_index: int) -> int:
        """Upload a chunk of media."""
        url = f"{UPLOAD_URL}?command=APPEND&media_id={media_id}&segment_index={segment_index}"
        
        form = FormData()
        form.add_field('media', chunk, filename=f'chunk{segment_index}')
        
        # Save original headers
        original_headers = self.client.headers.copy()
        try:
            self.client.headers['content-type'] = 'multipart/form-data'
            response = await self.client.post(url, data=form)
            return response.get('status', 500)
        finally:
            self.client.headers = original_headers
    
    async def _finalize_upload(self, media_id: str, image_path: str) -> Optional[Dict[str, Any]]:
        """Finalize media upload."""
        import hashlib
        with open(image_path, 'rb') as f:
            image_data = f.read()
        md5_hash = hashlib.md5(image_data).hexdigest()
        
        url = f"{UPLOAD_URL}?command=FINALIZE&media_id={media_id}&original_md5={md5_hash}"
        return await self.client.post(url)
    
    async def _update_profile_image(self, media_id: str) -> Optional[Dict[str, Any]]:
        """Update profile image with uploaded media."""
        payload = {
            'include_profile_interstitial_type': '1',
            'include_blocking': '1',
            'include_blocked_by': '1',
            'include_followed_by': '1',
            'include_want_retweets': '1',
            'include_mute_edge': '1',
            'include_can_dm': '1',
            'include_can_media_tag': '1',
            'include_ext_is_blue_verified': '1',
            'include_ext_verified_type': '1',
            'include_ext_profile_image_shape': '1',
            'skip_status': '1',
            'return_user': 'true',
            'media_id': media_id
        }
        return await self.client.post(Endpoints.UPDATE_PROFILE_IMAGE, data=payload)
    
    async def _update_profile_banner(self, media_id: str) -> Optional[Dict[str, Any]]:
        """Update profile banner with uploaded media."""
        payload = {
            'include_profile_interstitial_type': '1',
            'include_blocking': '1',
            'include_blocked_by': '1',
            'include_followed_by': '1',
            'include_want_retweets': '1',
            'include_mute_edge': '1',
            'include_can_dm': '1',
            'include_can_media_tag': '1',
            'include_ext_is_blue_verified': '1',
            'include_ext_verified_type': '1',
            'include_ext_profile_image_shape': '1',
            'skip_status': '1',
            'return_user': 'true',
            'media_id': media_id
        }
        return await self.client.post(Endpoints.UPDATE_PROFILE_BANNER, data=payload)
    
    async def change_username(self, new_username: str) -> Optional[Dict[str, Any]]:
        """
        Change username.
        
        Args:
            new_username (str): New username
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        payload = {
            'screen_name': new_username
        }
        return await self.client.post(Endpoints.UPDATE_PROFILE_SETTINGS, data=payload)
    
    async def change_password(self, current_password: str, new_password: str) -> Optional[Dict[str, Any]]:
        """
        Change password.
        
        Args:
            current_password (str): Current password
            new_password (str): New password
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        payload = {
            'current_password': current_password,
            'password': new_password,
            'password_confirmation': new_password
        }
        return await self.client.post(Endpoints.CHANGE_PASSWORD, data=payload)
    
    async def delete_phone(self) -> Optional[Dict[str, Any]]:
        """
        Delete phone number from account.
        
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        return await self.client.post(Endpoints.DELETE_PHONE) 