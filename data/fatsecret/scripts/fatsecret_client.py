#!/usr/bin/env python3
"""
FatSecret API Client using OAuth1 (same credentials as diary)
"""
import json
import os
from requests_oauthlib import OAuth1Session

CONFIG_DIR = os.environ.get("FATSECRET_CONFIG_DIR", os.path.expanduser("~/.config/fatsecret"))
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

class FatSecretClient:
    """FatSecret API client with OAuth1."""
    
    API_URL = "https://platform.fatsecret.com/rest/server.api"
    
    def __init__(self):
        """Initialize with OAuth1 credentials from config."""
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        
        self.oauth = OAuth1Session(
            config['consumer_key'],
            client_secret=config['consumer_secret'],
            resource_owner_key=config['access_token'],
            resource_owner_secret=config['access_token_secret']
        )
        self.proxy = config.get('proxy')
        self.proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
    
    def _request(self, method: str, **params):
        """Make API request."""
        params['method'] = method
        params['format'] = 'json'
        
        r = self.oauth.get(self.API_URL, params=params, proxies=self.proxies)
        r.raise_for_status()
        return r.json()
    
    def search_foods(self, query: str, max_results: int = 50):
        """Search foods by query."""
        data = self._request('foods.search', search_expression=query, max_results=max_results)
        return data.get('foods', {}).get('food', [])
    
    def get_food(self, food_id: int):
        """Get food details by ID."""
        return self._request('food.get.v2', food_id=food_id)

if __name__ == '__main__':
    import sys
    client = FatSecretClient()
    
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        results = client.search_foods(query, max_results=5)
        print(json.dumps(results, indent=2))
    else:
        print("Usage: python3 fatsecret_client_oauth1.py <search query>")
