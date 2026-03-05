#!/usr/bin/env python3
"""
Helper for OpenClaw agents to manage FatSecret flow automatically.
The agent uses these functions to guide the user through authentication.
"""

import json
import os
import sys
import time
import hashlib
import hmac
import base64
import urllib.parse
import requests
from typing import Dict, Optional, Tuple

# Configuration - use FATSECRET_CONFIG_DIR env var for persistent storage in containers
CONFIG_DIR = os.environ.get("FATSECRET_CONFIG_DIR", os.path.expanduser("~/.config/fatsecret"))
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
TOKENS_FILE = os.path.join(CONFIG_DIR, "oauth1_access_tokens.json")

# OAuth1 URLs
REQUEST_TOKEN_URL = "https://authentication.fatsecret.com/oauth/request_token"
AUTHORIZE_URL = "https://authentication.fatsecret.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://authentication.fatsecret.com/oauth/access_token"

# Proxy configuration (optional)
def get_proxies():
    """Get proxy configuration from environment or config file."""
    proxy_url = os.environ.get("FATSECRET_PROXY")
    if not proxy_url and os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                config = json.load(f)
                proxy_url = config.get("proxy")
        except:
            pass
    if proxy_url:
        return {"http": proxy_url, "https": proxy_url}
    return None  # No proxy by default

PROXIES = get_proxies()

class FatSecretAgentHelper:
    """Helper for agents to manage FatSecret authentication."""
    
    def __init__(self):
        self.consumer_key = None
        self.consumer_secret = None
        self.request_token = None
        self.request_token_secret = None
        self.access_token = None
        self.access_token_secret = None
        
    def save_credentials(self, consumer_key: str, consumer_secret: str) -> bool:
        """Save credentials provided by user."""
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            
            config = {
                "consumer_key": consumer_key,
                "consumer_secret": consumer_secret,
                "saved_at": time.time(),
                "saved_at_human": time.ctime()
            }
            
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.consumer_key = consumer_key
            self.consumer_secret = consumer_secret
            
            print(f"✅ Credentials saved to: {CONFIG_FILE}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving credentials: {e}")
            return False
    
    def load_credentials(self) -> bool:
        """Load saved credentials."""
        try:
            if not os.path.exists(CONFIG_FILE):
                return False
            
            with open(CONFIG_FILE) as f:
                config = json.load(f)
            
            self.consumer_key = config.get("consumer_key")
            self.consumer_secret = config.get("consumer_secret")
            
            if not self.consumer_key or not self.consumer_secret:
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading credentials: {e}")
            return False
    
    def load_tokens(self) -> bool:
        """Load saved access tokens."""
        try:
            if not os.path.exists(TOKENS_FILE):
                return False
            
            with open(TOKENS_FILE) as f:
                tokens = json.load(f)
            
            self.access_token = tokens.get("access_token")
            self.access_token_secret = tokens.get("access_token_secret")
            self.consumer_key = tokens.get("consumer_key", self.consumer_key)
            self.consumer_secret = tokens.get("consumer_secret", self.consumer_secret)
            
            if not self.access_token or not self.access_token_secret:
                return False
            
            return True
            
        except Exception:
            return False
    
    def is_authenticated(self) -> bool:
        """Check if user is already authenticated."""
        return self.load_tokens()
    
    def start_authentication(self) -> Dict:
        """
        Start authentication flow.
        Returns a dict with status and required data.
        """
        # Check credentials
        if not self.load_credentials():
            return {
                "status": "need_credentials",
                "message": "FatSecret credentials not found. Please provide them."
            }
        
        # Get request token
        success, token, token_secret = self._get_request_token()
        if not success:
            return {
                "status": "error",
                "message": f"Error getting request token: {token}"  # token contains error message
            }
        
        self.request_token = token
        self.request_token_secret = token_secret
        
        # Generate authorization URL
        auth_url = f"{AUTHORIZE_URL}?oauth_token={token}"
        
        return {
            "status": "need_authorization",
            "message": "Visit the URL to authorize the app, then send me the PIN.",
            "authorization_url": auth_url,
            "request_token": token
        }
    
    def complete_authentication(self, pin: str) -> Dict:
        """
        Complete authentication with PIN provided by user.
        """
        if not self.request_token or not self.request_token_secret:
            return {
                "status": "error",
                "message": "Request token not found. Start authentication first."
            }
        
        # Get access token
        success, access_token, access_token_secret = self._get_access_token(pin)
        if not success:
            return {
                "status": "error",
                "message": f"Error getting access token: {access_token}"  # access_token contains error message
            }
        
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        
        # Save tokens
        save_success = self._save_tokens(access_token, access_token_secret)
        
        return {
            "status": "authenticated" if save_success else "error",
            "message": "✅ Authentication complete! Tokens saved." if save_success else "❌ Error saving tokens.",
            "access_token": access_token,
            "access_token_secret": access_token_secret
        }
    
    def _make_oauth_request(self, method: str, url: str, params: Dict, token_secret: str = "") -> requests.Response:
        """Create an OAuth1 signed request."""
        # Add standard OAuth parameters
        oauth_params = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_nonce": hashlib.md5(str(time.time()).encode()).hexdigest(),
            "oauth_version": "1.0"
        }
        
        # Add oauth_token if present
        if "oauth_token" in params:
            oauth_params["oauth_token"] = params["oauth_token"]
        
        # Combine all parameters
        all_params = {**params, **oauth_params}
        
        # Sort parameters
        sorted_params = sorted(all_params.items())
        
        # Create signature string
        parameter_string = "&".join([f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in sorted_params])
        base_string = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(parameter_string, safe='')}"
        
        # Calculate signature
        signing_key = f"{self.consumer_secret}&{token_secret}"
        signature = base64.b64encode(hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()).decode()
        
        # Add signature
        oauth_params["oauth_signature"] = signature
        
        # Create Authorization header
        auth_header = "OAuth " + ", ".join([f'{k}="{urllib.parse.quote(str(v), safe="")}"' for k, v in oauth_params.items()])
        
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Make request
        if method == "GET":
            response = requests.get(url, params=params, headers=headers, proxies=PROXIES)
        else:  # POST
            response = requests.post(url, data=params, headers=headers, proxies=PROXIES)
        
        return response
    
    def _get_request_token(self) -> Tuple[bool, str, str]:
        """Get request token."""
        params = {
            "oauth_callback": "oob",
            "oauth_consumer_key": self.consumer_key
        }
        
        try:
            response = self._make_oauth_request("POST", REQUEST_TOKEN_URL, params, "")
            
            if response.status_code != 200:
                return False, f"HTTP {response.status_code}: {response.text}", ""
            
            # Parse response
            response_params = dict(urllib.parse.parse_qsl(response.text))
            oauth_token = response_params.get("oauth_token")
            oauth_token_secret = response_params.get("oauth_token_secret")
            
            if not oauth_token or not oauth_token_secret:
                return False, "Tokens not received in response", ""
            
            return True, oauth_token, oauth_token_secret
            
        except Exception as e:
            return False, f"Exception: {type(e).__name__}: {e}", ""
    
    def _get_access_token(self, pin: str) -> Tuple[bool, str, str]:
        """Get access token with PIN."""
        params = {
            "oauth_token": self.request_token,
            "oauth_verifier": pin,
            "oauth_consumer_key": self.consumer_key
        }
        
        try:
            response = self._make_oauth_request("GET", ACCESS_TOKEN_URL, params, self.request_token_secret)
            
            if response.status_code != 200:
                return False, f"HTTP {response.status_code}: {response.text}", ""
            
            # Parse response
            response_params = dict(urllib.parse.parse_qsl(response.text))
            access_token = response_params.get("oauth_token")
            access_token_secret = response_params.get("oauth_token_secret")
            
            if not access_token or not access_token_secret:
                return False, "Access tokens not received", ""
            
            return True, access_token, access_token_secret
            
        except Exception as e:
            return False, f"Exception: {type(e).__name__}: {e}", ""
    
    def _save_tokens(self, access_token: str, access_token_secret: str) -> bool:
        """Save access tokens."""
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            
            token_data = {
                "access_token": access_token,
                "access_token_secret": access_token_secret,
                "consumer_key": self.consumer_key,
                "consumer_secret": self.consumer_secret,
                "created": time.time(),
                "created_human": time.ctime()
            }
            
            with open(TOKENS_FILE, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving tokens: {e}")
            return False
    
    def test_connection(self) -> Dict:
        """Test API connection with current tokens."""
        if not self.load_tokens():
            return {
                "status": "error",
                "message": "Tokens not found. Please authenticate first."
            }
        
        params = {
            "format": "json",
            "method": "foods.search",
            "search_expression": "apple",
            "max_results": "1",
            "oauth_token": self.access_token,
            "oauth_consumer_key": self.consumer_key
        }
        
        try:
            response = self._make_oauth_request("GET", "https://platform.fatsecret.com/rest/server.api", 
                                              params, self.access_token_secret)
            
            if response.status_code == 200:
                data = response.json()
                if "foods" in data and "food" in data["foods"]:
                    food = data["foods"]["food"]
                    if isinstance(food, list):
                        food = food[0]
                    food_name = food.get("food_name", "Unknown")
                    
                    return {
                        "status": "success",
                        "message": f"✅ Connection OK! Example: {food_name}"
                    }
            
            return {
                "status": "error",
                "message": f"❌ API Error: {response.status_code} - {response.text[:200]}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Exception: {type(e).__name__}: {e}"
            }

# Utility functions for agents
def get_authentication_flow() -> Dict:
    """
    Main function for agents - handles entire flow.
    Returns current status and required actions.
    """
    helper = FatSecretAgentHelper()
    
    # Check if already authenticated
    if helper.is_authenticated():
        test = helper.test_connection()
        if test["status"] == "success":
            return {
                "status": "already_authenticated",
                "message": "✅ Already connected to FatSecret!",
                "test_result": test
            }
        else:
            # Tokens invalid, need re-authentication
            return {
                "status": "need_reauthentication",
                "message": "Tokens invalid. New authentication required."
            }
    
    # Check credentials
    if not helper.load_credentials():
        return {
            "status": "need_credentials",
            "message": "I need your FatSecret credentials.",
            "instructions": """
Please provide:
1. Consumer Key
2. Consumer Secret

Get them from: https://platform.fatsecret.com
"""
        }
    
    # Start authentication
    return helper.start_authentication()

def complete_authentication_flow(pin: str) -> Dict:
    """Complete authentication with PIN."""
    helper = FatSecretAgentHelper()
    
    if not helper.load_credentials():
        return {
            "status": "error",
            "message": "Credentials not found. Please provide them first."
        }
    
    # Note: in a real agent, state should be maintained between calls
    # For simplicity, we assume start_authentication was called before
    
    result = helper.complete_authentication(pin)
    
    if result["status"] == "authenticated":
        # Test connection
        test = helper.test_connection()
        result["test_result"] = test
    
    return result

def save_user_credentials(consumer_key: str, consumer_secret: str) -> Dict:
    """Save credentials provided by user."""
    helper = FatSecretAgentHelper()
    
    success = helper.save_credentials(consumer_key, consumer_secret)
    
    if success:
        return {
            "status": "success",
            "message": "✅ Credentials saved!",
            "next_step": "Start OAuth1 authentication"
        }
    else:
        return {
            "status": "error",
            "message": "❌ Error saving credentials"
        }

if __name__ == "__main__":
    # Script test
    print("🧪 Test FatSecret Agent Helper")
    print("="*50)
    
    # Check status
    print("\n1. Check authentication status:")
    state = get_authentication_flow()
    print(f"   Status: {state['status']}")
    print(f"   Message: {state['message']}")
    
    if state["status"] == "need_credentials":
        print("\n2. Simulating credential save...")
        # This is just a test - in production agent would ask user
        test_result = save_user_credentials("test_key", "test_secret")
        print(f"   Result: {test_result['message']}")
    
    print("\n✅ Test complete.")