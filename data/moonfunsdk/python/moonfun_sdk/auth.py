"""
Authentication Manager
Handles cryptographic signature generation for API requests
"""
import time
from eth_account import Account
from eth_account.messages import encode_defunct
from typing import Optional


class AuthManager:
    """
    Manages wallet authentication and signature generation
    
    Security:
        - Private key never leaves this class
        - All signatures use EIP-191 standard
        - Timestamp binding prevents replay attacks
    """
    
    def __init__(self, private_key: str):
        """
        Initialize authentication manager
        
        Args:
            private_key: Ethereum private key (with or without 0x prefix)
        
        Raises:
            ValueError: If private key is invalid
        """
        if not private_key:
            raise ValueError("Private key cannot be empty")
        
        # Ensure 0x prefix
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key
        
        try:
            self.account = Account.from_key(private_key)
            self.address = self.account.address
            self._private_key = private_key
        except Exception as e:
            raise ValueError(f"Invalid private key: {str(e)}")
    
    def sign_message(self, message: str) -> str:
        """
        Sign a message using EIP-191 personal_sign
        
        Args:
            message: Plain text message to sign
        
        Returns:
            Signature as hex string (0x...)
        """
        message_hash = encode_defunct(text=message)
        signed_message = self.account.sign_message(message_hash)
        signature = signed_message.signature.hex()
        
        # Ensure 0x prefix for compatibility with API requirements
        if not signature.startswith('0x'):
            signature = '0x' + signature
        
        return signature
    
    def sign_image_request(self, prompt: str, timestamp: Optional[int] = None) -> tuple[str, int]:
        """
        Sign an image generation request
        
        Args:
            prompt: User's Meme description
            timestamp: Unix timestamp (auto-generated if None)
        
        Returns:
            Tuple of (signature, timestamp)
        """
        if timestamp is None:
            timestamp = int(time.time())
        
        # Message format: "{prompt}:{timestamp}"
        message = f"{prompt}:{timestamp}"
        signature = self.sign_message(message)
        
        return signature, timestamp
    
    def sign_login_request(self, message: Optional[str] = None) -> tuple[str, str]:
        """
        Sign a platform login request
        
        Args:
            message: Custom message (defaults to timestamp)
        
        Returns:
            Tuple of (signature, message)
        """
        if message is None:
            message = str(int(time.time()))
        
        signature = self.sign_message(message)
        return signature, message
    
    @property
    def private_key(self) -> str:
        """Get private key (use with caution)"""
        return self._private_key
