#!/usr/bin/env python3
"""
Loxone Token Authentication
Implements the token-based authentication flow as per the official API documentation
"""

import hmac
import hashlib
import json
import urllib.parse
import os
from typing import Dict, Tuple
import requests
import uuid


class LoxoneAuth:
    """Handles Loxone token-based authentication"""
    
    def __init__(self, host: str, username: str, password: str, use_https: bool = True):
        """
        Initialize Loxone authentication
        
        Args:
            host: IP address or hostname of Miniserver
            username: Loxone username
            password: Loxone password
            use_https: Use HTTPS instead of HTTP (default: True)
        """
        self.host = host
        self.username = username
        self.password = password
        self.use_https = use_https
        self.protocol = "https" if use_https else "http"
        self.base_url = f"{self.protocol}://{self.host}"
        
        # Token storage
        self.token = None
        self.token_hash = None
        self.key = None
        self.salt = None
        
    def _make_request(self, endpoint: str) -> requests.Response:
        """
        Make HTTP request to Miniserver
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, timeout=10, verify=self.use_https)
            response.raise_for_status()
            return response
        except Exception as e:
            raise Exception(f"Request failed: {e}")
    
    def get_key(self) -> Tuple[str, str, str]:
        """
        Step 1: Get authentication key, salt, and hash algorithm
        
        Returns:
            Tuple of (key, salt, hashAlg)
        """
        endpoint = f"/jdev/sys/getkey2/{urllib.parse.quote(self.username)}"
        print(f"Getting key from: {endpoint}")
        
        response = self._make_request(endpoint)
        data = response.json()
        
        if 'LL' in data and 'value' in data['LL']:
            # Extract key, salt, and hashAlg from response
            value = data['LL']['value']
            self.key = value.get('key')
            self.salt = value.get('salt')
            hash_alg = value.get('hashAlg', 'SHA1')  # Default to SHA1 if not specified
            
            print(f"✅ Got key, salt, and hashAlg ({hash_alg})")
            return self.key, self.salt, hash_alg
        else:
            raise Exception(f"Failed to get key: {data}")
    
    def hash_credentials(self, key: str, salt: str, hash_alg: str = "SHA1") -> str:
        """
        Step 2: Hash password with salt, then hash with username and key
        
        Per official docs (v10.2+):
        1. pwHash = HASH("{password}:{userSalt}") using hashAlg from getkey2
        2. hash = HMAC-HASH("{user}:{pwHash}", key) using SHA1 or SHA256
        
        Args:
            key: Authentication key from getkey2
            salt: User salt from getkey2
            hash_alg: Hashing algorithm from getkey2 (SHA1 or SHA256)
            
        Returns:
            Final hash for authentication
        """
        # Step 1: Hash password with user salt
        pwd_with_salt = f"{self.password}:{salt}"
        
        if hash_alg.upper() == "SHA256":
            pw_hash_obj = hashlib.sha256(pwd_with_salt.encode('utf-8'))
        else:
            pw_hash_obj = hashlib.sha1(pwd_with_salt.encode('utf-8'))
        
        pw_hash = pw_hash_obj.hexdigest().upper()
        print(f"✅ Step 1: Password+salt hashed ({hash_alg})")
        
        # Step 2: HMAC hash of "user:pwHash" with key
        user_pw_hash = f"{self.username}:{pw_hash}"
        key_bytes = bytes.fromhex(key)
        
        if hash_alg.upper() == "SHA256":
            final_hash = hmac.new(key_bytes, user_pw_hash.encode('utf-8'), hashlib.sha256).hexdigest()
        else:
            final_hash = hmac.new(key_bytes, user_pw_hash.encode('utf-8'), hashlib.sha1).hexdigest()
        
        # Do NOT convert to upper/lower case per docs
        print(f"✅ Step 2: user:pwHash hashed with key")
        return final_hash
    
    def get_jwt(self, auth_hash: str, permission: int = 4, client_uuid: str = None, client_info: str = "python-client") -> str:
        """
        Step 3: Request JSON Web Token (v10.2+)
        
        Args:
            auth_hash: Authentication hash from hash_credentials
            permission: Permission level (2=web, 4=app)
            client_uuid: Client UUID (generated if not provided)
            client_info: Client info string
            
        Returns:
            JWT token string
        """
        if not client_uuid:
            client_uuid = str(uuid.uuid4())
        
        # Use getjwt instead of gettoken (v10.2+)
        endpoint = f"/jdev/sys/getjwt/{auth_hash}/{urllib.parse.quote(self.username)}/{permission}/{client_uuid}/{urllib.parse.quote(client_info)}"
        print(f"Getting JWT from: {endpoint}")
        print(f"   (Note: Miniserver v11.2+ allows unencrypted getjwt)")
        
        response = self._make_request(endpoint)
        data = response.json()
        
        if 'LL' in data and 'value' in data['LL']:
            value = data['LL']['value']
            self.token = value.get('token')
            valid_until = value.get('validUntil')
            token_rights = value.get('tokenRights')
            unsecure_pass = value.get('unsecurePass', False)
            
            print(f"✅ Got JWT token")
            print(f"   Valid until: {valid_until}")
            print(f"   Token rights: {token_rights}")
            if unsecure_pass:
                print(f"   ⚠️  Weak password detected!")
            
            return self.token
        else:
            raise Exception(f"Failed to get JWT: {data}")
    
    def authenticate(self) -> str:
        """
        Full authentication flow: key -> hash -> JWT token
        
        Returns:
            JWT authentication token
        """
        # Step 1: Get key, salt, and hash algorithm
        key, salt, hash_alg = self.get_key()
        
        # Step 2: Hash credentials (password+salt, then user:pwHash with key)
        auth_hash = self.hash_credentials(key, salt, hash_alg)
        
        # Step 3: Get JWT token
        token = self.get_jwt(auth_hash)
        
        return token
    
    def get_ws_url(self) -> str:
        """
        Get WebSocket URL with token authentication
        
        Returns:
            WebSocket URL with token parameter
        """
        if not self.token:
            raise Exception("No token available. Run authenticate() first.")
        
        scheme = "wss" if self.protocol == "https" else "ws"
        return f"{scheme}://{self.host}/ws/rfc6455?token={self.token}"


def main():
    """Test authentication flow"""
    import sys
    from pathlib import Path
    
    # Load config
    from loxone_config import load_config_file

    config_path = Path(__file__).parent.parent / "config.json"
    config = load_config_file(str(config_path))
    
    # Create auth client
    auth = LoxoneAuth(
        host=config['host'],
        username=config['username'],
        password=config['password'],
        use_https=config.get('use_https', True),
    )
    
    # Authenticate
    try:
        token = auth.authenticate()
        print(f"\n✅ Authentication successful!")
        print(f"   Token: {token[:30]}...")
        print(f"\n   WebSocket URL:")
        print(f"   {auth.get_ws_url()}")
        
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
