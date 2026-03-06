#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import argparse

def search_shopping(query, display=5, sort='sim'):
    client_id = os.getenv('NAVER_Client_ID')
    client_secret = os.getenv('NAVER_Client_Secret')

    if not client_id or not client_secret:
        return {"error": "NAVER_Client_ID or NAVER_Client_Secret not found in environment variables."}

    encText = urllib.parse.quote(query)
    url = f"https://openapi.naver.com/v1/search/shop.json?query={encText}&display={display}&sort={sort}"
    
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id.strip())
    request.add_header("X-Naver-Client-Secret", client_secret.strip())
    
    # Debug: print headers (excluding secret)
    # print(f"ID: {client_id.strip()}", file=sys.stderr)
    
    try:
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if rescode == 200:
            response_body = response.read()
            return json.loads(response_body.decode('utf-8'))
        else:
            return {"error": f"Error Code: {rescode}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Naver Shopping Search')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--display', type=int, default=5, help='Number of results (1-100)')
    parser.add_argument('--sort', default='sim', choices=['sim', 'date', 'asc', 'dsc'], help='Sort order')
    
    args = parser.parse_args()
    
    results = search_shopping(args.query, args.display, args.sort)
    
    if "error" in results:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        sys.exit(1)
        
    print(json.dumps(results, indent=2, ensure_ascii=False))
