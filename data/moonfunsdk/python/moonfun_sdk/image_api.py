"""
Secured Image API Client
Interacts with the triple-lock secured image generation API
"""
import time
import httpx
from typing import Dict, Any
from .auth import AuthManager
from .exceptions import (
    InsufficientBalanceError,
    AuthenticationError,
    RateLimitError,
    APIConnectionError
)


class ImageAPIClient:
    """
    Client for secured image generation API
    
    Security:
        - All requests are cryptographically signed
        - Timestamp-bound to prevent replay attacks
        - Balance-gated to prevent Sybil attacks
    """
    
    def __init__(self, api_url: str, auth_manager: AuthManager, timeout: int = 180):
        """
        Initialize image API client
        
        Args:
            api_url: Base URL of the secured image API
            auth_manager: Authentication manager instance
            timeout: Request timeout in seconds
        """
        self.api_url = api_url.rstrip('/')
        self.auth = auth_manager
        self.timeout = timeout
    
    def generate_meme(self, prompt: str) -> Dict[str, Any]:
        """
        Generate Meme image and title
        
        Args:
            prompt: User's Meme description (any language)
        
        Returns:
            Dictionary containing:
                - image_base64: Base64-encoded PNG image
                - meme_title: AI-generated humorous title
                - enhanced_prompt: Detailed description used for generation
        
        Raises:
            InsufficientBalanceError: Balance < 0.011 BNB
            AuthenticationError: Signature or timestamp invalid
            RateLimitError: Too many requests
            APIConnectionError: Network or API error
        """
        # Generate timestamp and signature
        signature, timestamp = self.auth.sign_image_request(prompt)
        
        # Prepare request payload
        payload = {
            "prompt": prompt,
            "address": self.auth.address,
            "timestamp": timestamp,
            "signature": signature
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.api_url}/generate_meme",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                # Handle specific error codes
                if response.status_code == 422:
                    # Validation error - show detailed info
                    try:
                        error_data = response.json()
                        raise APIConnectionError(
                            f"Validation error: {error_data}\n"
                            f"Sent payload: {payload}"
                        )
                    except Exception:
                        raise APIConnectionError(
                            f"Validation error (422): {response.text}\n"
                            f"Sent payload: {payload}"
                        )
                
                elif response.status_code == 403:
                    error_data = response.json()
                    raise InsufficientBalanceError(
                        error_data.get('details', 'Insufficient balance')
                    )
                
                elif response.status_code == 401:
                    error_data = response.json()
                    raise AuthenticationError(
                        error_data.get('details', 'Authentication failed')
                    )
                
                elif response.status_code == 429:
                    error_data = response.json()
                    raise RateLimitError(
                        error_data.get('details', 'Rate limit exceeded')
                    )
                
                # Raise for other HTTP errors
                response.raise_for_status()
                
                return response.json()
        
        except httpx.HTTPError as e:
            raise APIConnectionError(f"API request failed: {str(e)}")
        except Exception as e:
            if isinstance(e, (InsufficientBalanceError, AuthenticationError, RateLimitError)):
                raise
            raise APIConnectionError(f"Unexpected error: {str(e)}")
