"""
Bigin CRM Authentication Module
Handles OAuth2 flow for Zoho Bigin API
"""

import webbrowser
import http.server
import socketserver
import urllib.parse
import json
import os
import requests
from typing import Optional, Dict, Any
from pathlib import Path


class BiginOAuth:
    """
    OAuth2 handler for Bigin CRM authentication
    """
    
    def __init__(
        self, 
        client_id: str, 
        client_secret: str, 
        dc: str = 'com',
        redirect_uri: str = "http://localhost:8888/callback"
    ):
        """
        Initialize OAuth handler
        
        Args:
            client_id: OAuth client ID from Zoho API Console
            client_secret: OAuth client secret
            dc: Data center (com, eu, in, au, etc.)
            redirect_uri: OAuth redirect URI
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.dc = dc
        self.redirect_uri = redirect_uri
        # Bigin-specific scopes (org.READ required for /bigin/v2/org endpoint)
        self.scope = "ZohoBigin.modules.ALL,ZohoBigin.settings.ALL,ZohoBigin.org.READ"
        
        # Token storage path
        self.token_dir = Path.home() / ".openclaw" / "credentials"
        self.token_file = self.token_dir / "bigin-crm.json"
        
        # Ensure directory exists
        self.token_dir.mkdir(parents=True, exist_ok=True)
    
    def get_auth_url(self) -> str:
        """
        Generate authorization URL for Bigin
        
        Returns:
            Authorization URL string
        """
        return (
            f"https://accounts.zoho.{self.dc}/oauth/v2/auth?"
            f"scope={self.scope}&"
            f"client_id={self.client_id}&"
            f"response_type=code&"
            f"access_type=offline&"
            f"redirect_uri={self.redirect_uri}"
        )
    
    def start_auth_flow(self) -> Dict[str, Any]:
        """
        Start local server and authenticate via browser
        
        Returns:
            Token dictionary with access_token and refresh_token
        """
        auth_code = None
        
        class CallbackHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(handler_self):
                nonlocal auth_code
                query = urllib.parse.urlparse(handler_self.path).query
                params = urllib.parse.parse_qs(query)
                
                if 'code' in params:
                    auth_code = params['code'][0]
                    handler_self.send_response(200)
                    handler_self.send_header('Content-type', 'text/html')
                    handler_self.end_headers()
                    handler_self.wfile.write(b"""
                        <html>
                        <body>
                            <h1>Authentication Successful!</h1>
                            <p>You can close this window and return to the terminal.</p>
                        </body>
                        </html>
                    """)
                else:
                    handler_self.send_response(400)
                    handler_self.end_headers()
                    handler_self.wfile.write(b"Authentication failed. No code received.")
            
            def log_message(self, format, *args):
                # Suppress default logging
                pass
        
        # Open browser for authentication
        print(f"Opening browser for authentication...")
        print(f"If browser doesn't open, visit: {self.get_auth_url()}")
        webbrowser.open(self.get_auth_url())
        
        # Start local server to catch callback
        with socketserver.TCPServer(("", 8888), CallbackHandler) as httpd:
            print("Waiting for authentication callback...")
            httpd.timeout = 120  # 2 minute timeout
            while auth_code is None and httpd.timeout > 0:
                httpd.handle_request()
        
        if auth_code is None:
            raise TimeoutError("Authentication timed out. Please try again.")
        
        # Exchange code for tokens
        tokens = self.exchange_code_for_tokens(auth_code)
        
        # Save tokens
        self.save_tokens(tokens)
        
        print("Authentication successful! Tokens saved.")
        return tokens
    
    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            code: Authorization code from callback
            
        Returns:
            Token dictionary
        """
        url = f"https://accounts.zoho.{self.dc}/oauth/v2/token"
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        tokens = response.json()
        
        # Add metadata
        tokens["data_center"] = self.dc
        tokens["created_at"] = json.dumps({})
        
        return tokens
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh expired access token
        
        Args:
            refresh_token: Refresh token from previous authentication
            
        Returns:
            New token dictionary
        """
        url = f"https://accounts.zoho.{self.dc}/oauth/v2/token"
        data = {
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        tokens = response.json()
        
        # Preserve refresh token (not returned in refresh response)
        tokens["refresh_token"] = refresh_token
        tokens["data_center"] = self.dc
        
        return tokens
    
    def save_tokens(self, tokens: Dict[str, Any]) -> None:
        """
        Save tokens to file
        
        Args:
            tokens: Token dictionary to save
        """
        # Add timestamp
        import time
        tokens["saved_at"] = int(time.time())
        
        with open(self.token_file, 'w') as f:
            json.dump(tokens, f, indent=2)
        
        # Set restrictive permissions
        os.chmod(self.token_file, 0o600)
    
    def load_tokens(self) -> Optional[Dict[str, Any]]:
        """
        Load tokens from file
        
        Returns:
            Token dictionary or None if not found
        """
        if not self.token_file.exists():
            return None
        
        with open(self.token_file, 'r') as f:
            return json.load(f)
    
    def get_access_token(self) -> str:
        """
        Get valid access token (refresh if needed)
        
        Returns:
            Valid access token string
            
        Raises:
            ValueError: If no tokens found
        """
        tokens = self.load_tokens()
        
        if tokens is None:
            raise ValueError(
                "No authentication tokens found. "
                "Please run authentication first."
            )
        
        # Check if token is expired (with 5 minute buffer)
        import time
        expires_in = tokens.get("expires_in", 3600)
        saved_at = tokens.get("saved_at", 0)
        
        if int(time.time()) - saved_at >= expires_in - 300:
            # Token expired or about to expire, refresh it
            print("Access token expired. Refreshing...")
            refresh_token = tokens.get("refresh_token")
            if not refresh_token:
                raise ValueError("No refresh token available. Please re-authenticate.")
            
            new_tokens = self.refresh_token(refresh_token)
            self.save_tokens(new_tokens)
            return new_tokens["access_token"]
        
        return tokens["access_token"]
    
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated
        
        Returns:
            True if valid tokens exist
        """
        try:
            self.get_access_token()
            return True
        except (ValueError, FileNotFoundError):
            return False
    
    def get_whoami(self) -> Dict[str, Any]:
        """
        Get current user information
        
        Returns:
            User information dictionary
        """
        access_token = self.get_access_token()
        
        url = f"https://www.zohoapis.{self.dc}/bigin/v2/org"
        headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def revoke_token(self) -> bool:
        """
        Revoke current access token
        
        Returns:
            True if successful
        """
        try:
            access_token = self.get_access_token()
            
            url = f"https://accounts.zoho.{self.dc}/oauth/v2/token/revoke"
            data = {"token": access_token}
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            # Remove local token file
            if self.token_file.exists():
                self.token_file.unlink()
            
            return True
        except Exception as e:
            print(f"Error revoking token: {e}")
            return False


def init_auth_from_config(config_path: Optional[str] = None) -> BiginOAuth:
    """
    Initialize auth from config file
    
    Args:
        config_path: Path to oauth-config.json
        
    Returns:
        Configured BiginOAuth instance
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "oauth-config.json"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    oauth_config = config["oauth"]
    
    return BiginOAuth(
        client_id=oauth_config["client_id"],
        client_secret=oauth_config["client_secret"],
        dc=oauth_config.get("default_dc", "com"),
        redirect_uri=oauth_config["redirect_uri"]
    )


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python auth.py <command>")
        print("Commands: auth, whoami, revoke")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        auth = init_auth_from_config()
        
        if command == "auth":
            auth.start_auth_flow()
        elif command == "whoami":
            info = auth.get_whoami()
            print(json.dumps(info, indent=2))
        elif command == "revoke":
            if auth.revoke_token():
                print("Token revoked successfully.")
            else:
                print("Failed to revoke token.")
        else:
            print(f"Unknown command: {command}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
