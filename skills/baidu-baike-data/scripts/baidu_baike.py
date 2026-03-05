#!/usr/bin/env python3
"""
Baidu Baike Query Script
Query encyclopedia entries from Baidu Baike.
"""

import os
import sys
import requests
import json
import argparse
from typing import Dict, Any, List


class BaiduBaikeClient:
    """Baidu Baike API Client"""
    
    BASE_URL = "https://appbuilder.baidu.com/v2/baike"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Appbuilder-From": "openclaw",
        }
    
    def get_lemma_content(self, search_type: str, search_key: str) -> Dict[str, Any]:
        """Get detailed entry content by title or ID."""
        url = f"{self.BASE_URL}/lemma/get_content"
        params = {"search_type": search_type, "search_key": search_key}
        
        response = requests.get(url, params=params, headers=self.headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        self._check_error(result)
        
        if "result" in result:
            # Remove large fields to reduce output size
            exclude_keys = {"summary", "abstract_html", "abstract_structured", 
                           "square_pic_url_wap", "videos", "relations", "star_map"}
            return {k: v for k, v in result["result"].items() 
                    if k not in exclude_keys and v is not None}
        return {}
    
    def get_lemma_list(self, lemma_title: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """List entries with same title (for homonym resolution)."""
        url = f"{self.BASE_URL}/lemma/get_list_by_title"
        params = {"lemma_title": lemma_title, "top_k": top_k}
        
        response = requests.get(url, params=params, headers=self.headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        self._check_error(result)
        return result.get("result", [])
    
    def _check_error(self, result: Dict[str, Any]) -> None:
        if "errno" in result and result["errno"] != 0:
            errmsg = result.get("errmsg", "Unknown error")
            raise RuntimeError(f"API error: {errmsg} (code: {result['errno']})")


def main():
    parser = argparse.ArgumentParser(description="Query Baidu Baike entries")
    parser.add_argument(
        "--search_type", "-st", 
        required=True,
        choices=["lemmaTitle", "lemmaId", "lemmaList"],
        help="Search type: lemmaTitle, lemmaId, or lemmaList"
    )
    parser.add_argument(
        "--search_key", "-sk", 
        required=True, 
        help="Search keyword (entry title or ID)"
    )
    parser.add_argument(
        "--top_k", "-tk", 
        type=int, 
        default=5, 
        help="Max results for lemmaList (default: 5)"
    )
    
    args = parser.parse_args()
    
    api_key = os.getenv("BAIDU_API_KEY")
    if not api_key:
        print("Error: BAIDU_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    try:
        client = BaiduBaikeClient(api_key)
        
        if args.search_type == "lemmaList":
            results = client.get_lemma_list(args.search_key, args.top_k)
        else:
            results = client.get_lemma_content(args.search_type, args.search_key)
        
        print(json.dumps(results, ensure_ascii=False, indent=2))
        
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
