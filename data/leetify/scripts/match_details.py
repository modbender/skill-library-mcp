
import sys
import json
import argparse
import requests
import subprocess
import os
from datetime import datetime

API_KEY = os.environ.get("LEETIFY_API_KEY")
if not API_KEY:
    print(json.dumps({"error": "LEETIFY_API_KEY environment variable not set"}))
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
            return {"success": False, "error": f"{response.status_code} {response.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_match_full_stats(steam_id, match_index=0):
    # 1. Get recent matches list
    result = api_request('/v3/profile/matches', {'steam64_id': steam_id, 'limit': match_index + 1})
    
    if not result['success']:
        print(json.dumps({"error": result.get('error')}))
        return

    matches = result['data']
    # Handle direct list response or wrapped response
    if isinstance(matches, dict) and 'matches' in matches:
        matches = matches['matches']
        
    if not isinstance(matches, list):
        print(json.dumps({"error": "Unexpected API response format"}))
        return

    if len(matches) <= match_index:
        print(json.dumps({"error": f"Match index {match_index} not found. Total matches: {len(matches)}"}))
        return

    match = matches[match_index]
    
    # 2. Extract specific player stats
    # The 'stats' array in the match object contains detailed stats for each player in that match
    player_stats = next((s for s in match.get('stats', []) if s['steam64_id'] == steam_id), None)
    
    if not player_stats:
        print(json.dumps({"error": "Player stats not found in this match"}))
        return

    # 3. Construct the Analysis Payload
    # We combine match metadata (map, score) with the full player stats object
    
    analysis_payload = {
        "meta": {
            "map": match.get('map_name'),
            "date": match.get('finished_at'),
            "team_scores": match.get('team_scores'),
            "data_source": match.get('data_source'),
            "match_id": match.get('id')
        },
        # This object contains: accuracy, sprays, counter-strafing, utility usage, 
        # trade stats, entry stats, clutch opportunities, etc.
        "stats": player_stats 
    }

    # Output JSON for the LLM to digest
    print(json.dumps(analysis_payload, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--index", type=int, default=0)
    args = parser.parse_args()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        # Resolve username to Steam ID
        res = subprocess.check_output(
            ['python3', os.path.join(script_dir, 'steam_ids.py'), 'get', '--username', args.username],
            text=True
        ).strip()
        
        if "No Steam ID" in res or not res:
            print(json.dumps({"error": f"Steam ID not found for {args.username}"}))
            sys.exit(1)
        steam_id = res
    except Exception as e:
        print(json.dumps({"error": f"Steam ID resolution failed: {str(e)}"}))
        sys.exit(1)
        
    get_match_full_stats(steam_id, args.index)
