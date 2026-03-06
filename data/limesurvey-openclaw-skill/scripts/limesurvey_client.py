#!/usr/bin/env python3
"""
LimeSurvey RemoteControl 2 API Client
JSON-RPC client for LimeSurvey automation
"""

import json
import base64
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError


class LimeSurveyError(Exception):
    """Custom exception for LimeSurvey API errors"""
    pass


class LimeSurveyClient:
    """
    JSON-RPC client for LimeSurvey RemoteControl 2 API
    
    Usage:
        client = LimeSurveyClient('https://survey.example.com/index.php/admin/remotecontrol')
        session_key = client.get_session_key('admin', 'password')
        surveys = client.call('list_surveys', session_key)
        client.release_session_key(session_key)
    """
    
    def __init__(self, url):
        """
        Initialize the LimeSurvey client
        
        Args:
            url: Full URL to the RemoteControl endpoint
                 Example: https://example.com/index.php/admin/remotecontrol
        """
        self.url = url
        self.request_id = 0
        
    def call(self, method, *params):
        """
        Call a RemoteControl API method
        
        Args:
            method: API method name (e.g., 'list_surveys')
            *params: Method parameters
            
        Returns:
            Result from the API call
            
        Raises:
            LimeSurveyError: If the API returns an error
        """
        self.request_id += 1
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": list(params),
            "id": self.request_id
        }
        
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib_request.Request(
            self.url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Connection': 'Keep-Alive'
            }
        )
        
        try:
            with urllib_request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'error' in result and result['error']:
                    raise LimeSurveyError(f"API error: {result['error']}")
                
                return result.get('result')
                
        except HTTPError as e:
            raise LimeSurveyError(f"HTTP error {e.code}: {e.reason}")
        except URLError as e:
            raise LimeSurveyError(f"URL error: {e.reason}")
        except json.JSONDecodeError as e:
            raise LimeSurveyError(f"Invalid JSON response: {e}")
    
    def get_session_key(self, username, password, plugin='Authdb'):
        """
        Create a new session key
        
        Args:
            username: LimeSurvey username
            password: LimeSurvey password
            plugin: Authentication plugin (default: 'Authdb')
            
        Returns:
            Session key string
            
        Raises:
            LimeSurveyError: If authentication fails
        """
        result = self.call('get_session_key', username, password, plugin)
        
        # Check for authentication failure
        if isinstance(result, dict) and 'status' in result:
            raise LimeSurveyError(f"Authentication failed: {result['status']}")
        
        return result
    
    def release_session_key(self, session_key):
        """
        Close the RPC session
        
        Args:
            session_key: Active session key
            
        Returns:
            'OK' on success
        """
        return self.call('release_session_key', session_key)
    
    def decode_base64(self, encoded_data):
        """
        Decode base64-encoded data from export functions
        
        Args:
            encoded_data: Base64-encoded string
            
        Returns:
            Decoded string
        """
        return base64.b64decode(encoded_data).decode('utf-8')


# Context manager support
class LimeSurveySession:
    """
    Context manager for automatic session handling
    
    Usage:
        with LimeSurveySession(url, username, password) as client:
            surveys = client.call('list_surveys', client.session_key)
    """
    
    def __init__(self, url, username, password, plugin='Authdb'):
        self.client = LimeSurveyClient(url)
        self.username = username
        self.password = password
        self.plugin = plugin
        self.session_key = None
        
    def __enter__(self):
        self.session_key = self.client.get_session_key(
            self.username, 
            self.password, 
            self.plugin
        )
        self.client.session_key = self.session_key  # Store for convenience
        return self.client
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session_key:
            try:
                self.client.release_session_key(self.session_key)
            except:
                pass  # Ignore errors on cleanup
        return False
