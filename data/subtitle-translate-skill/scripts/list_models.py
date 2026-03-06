#!/usr/bin/env python3
"""
List available models from OpenAI-compatible API
"""

import argparse
import json
import os
import urllib.request


def list_models(api_url: str, api_key: str):
    """List available models from API."""
    
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    req = urllib.request.Request(
        f'{api_url}/models',
        headers=headers,
        method='GET'
    )
    
    # Set proxy
    proxy_handler = urllib.request.ProxyHandler({
        'http': os.environ.get('http_proxy', ''),
        'https': os.environ.get('https_proxy', '')
    })
    opener = urllib.request.build_opener(proxy_handler)
    urllib.request.install_opener(opener)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            print("Available models:")
            print("-" * 50)
            for model in sorted(result.get('data', []), key=lambda x: x.get('id', '')):
                model_id = model.get('id', 'unknown')
                print(f"  - {model_id}")
            
    except Exception as e:
        print(f"Error: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description='List available models from API')
    parser.add_argument('--api-url', '-u', required=True, help='API base URL')
    parser.add_argument('--api-key', '-k', required=True, help='API key')
    
    args = parser.parse_args()
    list_models(args.api_url, args.api_key)


if __name__ == '__main__':
    main()
