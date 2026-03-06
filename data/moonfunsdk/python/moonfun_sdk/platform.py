"""
MoonnFun Platform API Client
Handles platform authentication, image upload, and metadata creation
"""
import base64
import requests
from typing import Dict, Any, Optional
from .auth import AuthManager
from .exceptions import LoginError, UploadError, MetadataCreationError


class PlatformClient:
    """
    Client for MoonnFun platform APIs
    
    Features:
        - Session-based authentication
        - Image upload
        - Token metadata creation
        - Creation confirmation
    """
    
    def __init__(self, base_url: str, chain: str, auth_manager: AuthManager):
        """
        Initialize platform client
        
        Args:
            base_url: Platform base URL (e.g., https://moonn.fun)
            chain: Blockchain name ("bsc", "sei", "base")
            auth_manager: Authentication manager instance
        """
        self.base_url = base_url.rstrip('/')
        self.chain = chain
        self.auth = auth_manager
        
        # Session for maintaining cookies
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; MoonfunSDK/1.0)'
        })
        
        self._logged_in = False
    
    def login(self) -> bool:
        """
        Login to platform and obtain session cookie
        
        Returns:
            True if login successful
        
        Raises:
            LoginError: If login fails
        """
        try:
            # Sign login message (timestamp)
            signature, message = self.auth.sign_login_request()
            
            # Send login request (new API endpoint: /bsc/api/v1/user/login)
            response = self.session.post(
                f"{self.base_url}/{self.chain}/api/v1/user/login",
                data={
                    "address": self.auth.address,
                    "message": message,
                    "signature": signature
                },
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                timeout=30
            )
            
            # Debug: Check response status and content
            if response.status_code != 200:
                raise LoginError(
                    f"Login failed with status {response.status_code}\n"
                    f"Response: {response.text[:500]}"
                )
            
            # Try to parse JSON response
            try:
                data = response.json()
            except ValueError as json_err:
                raise LoginError(
                    f"Invalid JSON response from server\n"
                    f"Status: {response.status_code}\n"
                    f"Content-Type: {response.headers.get('Content-Type')}\n"
                    f"Response text (first 500 chars): {response.text[:500]}\n"
                    f"JSON error: {str(json_err)}"
                )
            
            if data.get('error'):
                raise LoginError(f"Login failed: {data['error']}")
            
            self._logged_in = True
            return True
        
        except requests.RequestException as e:
            raise LoginError(f"Login request failed: {str(e)}")
        except LoginError:
            raise
        except Exception as e:
            raise LoginError(f"Unexpected login error: {str(e)}")
    
    def upload_image(self, image_base64: str, filename: str = "meme.png") -> str:
        """
        Upload image to platform
        
        Args:
            image_base64: Base64-encoded image data
            filename: Image filename
        
        Returns:
            Image URL on platform
        
        Raises:
            UploadError: If upload fails
        """
        if not self._logged_in:
            raise UploadError("Must login before uploading images")
        
        try:
            # Decode base64 to bytes
            image_data = base64.b64decode(image_base64)
            
            # Prepare file upload
            files = {
                'file': (filename, image_data, 'image/png')
            }
            
            # Upload image (session cookie provides authentication)
            response = self.session.post(
                f"{self.base_url}/{self.chain}/api/v1/token/image/upload",
                files=files,
                timeout=60
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('error'):
                raise UploadError(f"Upload failed: {data['error']}")
            
            return data['data']
        
        except requests.RequestException as e:
            raise UploadError(f"Upload request failed: {str(e)}")
        except Exception as e:
            raise UploadError(f"Unexpected upload error: {str(e)}")
    
    def create_metadata(
        self,
        name: str,
        symbol: str,
        description: str,
        image_url: str,
        website: str = "",
        twitter: str = "",
        telegram: str = ""
    ) -> Dict[str, Any]:
        """
        Create token metadata on platform
        
        Args:
            name: Token name
            symbol: Token symbol
            description: Token description
            image_url: Image URL (from upload_image)
            website: Website URL (optional)
            twitter: Twitter handle (optional)
            telegram: Telegram handle (optional)
        
        Returns:
            Dictionary containing:
                - id: Token ID (for contract call)
                - salt: Salt value (for contract call)
                - address: Token address (predicted)
        
        Raises:
            MetadataCreationError: If creation fails
        """
        if not self._logged_in:
            raise MetadataCreationError("Must login before creating metadata")
        
        try:
            payload = {
                "name": name,
                "symbol": symbol,
                "description": description,
                "insurance": False,
                "imageUrl": image_url,
                "website": website,
                "twitter": twitter,
                "telegram": telegram,
                "creator": self.auth.address,
                "tag": "Ai Agent",
                "buyAmount": ""
            }
            
            # Session cookie provides authentication
            response = self.session.post(
                f"{self.base_url}/{self.chain}/api/v1/token/create",
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('error'):
                raise MetadataCreationError(f"Metadata creation failed: {data['error']}")
            
            metadata = data['data']
            
            return {
                'id': int(metadata['id']),
                'salt': int(metadata['salt']),
                'address': metadata['address']
            }
        
        except requests.RequestException as e:
            raise MetadataCreationError(f"Metadata request failed: {str(e)}")
        except Exception as e:
            raise MetadataCreationError(f"Unexpected metadata error: {str(e)}")
    
    def confirm_creation(self, token_id: int, tx_hash: str) -> bool:
        """
        Confirm token creation for fast indexing
        
        Args:
            token_id: Token ID from create_metadata
            tx_hash: Transaction hash from blockchain
        
        Returns:
            True if confirmation successful
        
        Raises:
            MetadataCreationError: If confirmation fails
        """
        try:
            # Ensure 0x prefix
            if not tx_hash.startswith('0x'):
                tx_hash = '0x' + tx_hash
            
            # Session cookie provides authentication
            params = {
                'tokenID': str(token_id),
                'txhash': tx_hash
            }
            
            response = self.session.get(
                f"{self.base_url}/{self.chain}/api/v1/token/create/ok",
                params=params,
                timeout=60
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('error'):
                raise MetadataCreationError(f"Confirmation failed: {data['error']}")
            
            return True
        
        except requests.RequestException as e:
            raise MetadataCreationError(f"Confirmation request failed: {str(e)}")
        except Exception as e:
            raise MetadataCreationError(f"Unexpected confirmation error: {str(e)}")
