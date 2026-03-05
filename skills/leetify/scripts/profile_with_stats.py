
import requests
import json
import argparse
import sys
import os

API_KEY = os.environ.get("LEETIFY_API_KEY")
if not API_KEY:
    print(json.dumps({"success": False, "error": "LEETIFY_API_KEY environment variable not set"}))
    sys.exit(1)

API_BASE = "https://api-public.cs-prod.leetify.com"

def api_request(endpoint, params=None):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    url = f"{API_BASE}{endpoint}"
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.text, "status_code": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_stats(steam_id):
    profile = api_request('/v3/profile', {'steam64_id': steam_id})
    if not profile['success']:
        return profile
    
    matches = api_request('/v3/profile/matches', {'steam64_id': steam_id, 'limit': 100})
    if not matches['success']:
        return matches
    
    return {
        "success": True,
        "profile": profile['data'],
        "matches": matches['data']
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--steam-id", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    
    res = get_stats(args.steam_id)
    if args.json:
        print(json.dumps(res))
    else:
        # Debugging print
        # print(json.dumps(res, indent=2))
        print(res)
