import os
import sys
import time
import argparse
import requests
import json
import urllib.parse
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
STEAM_IDS_FILE = os.path.join(DATA_DIR, "steam_ids.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

DEMOSLAP_API_BASE = "https://api.demo-slap.net"
LEETIFY_API_BASE = "https://api-public.cs-prod.leetify.com"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return {}

def save_config(key, value):
    os.makedirs(DATA_DIR, exist_ok=True)
    cfg = load_config()
    cfg[key] = value
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=4)
    print(f"✅ Saved configuration: {key}")

def get_demo_slap_key():
    key = os.environ.get("DEMOSLAP_API_KEY") or load_config().get("demoslap_api_key")
    if not key:
        print("❌ DEMOSLAP_API_KEY is missing. Please set it using 'set-key' command.")
        sys.exit(1)
    return key

def get_leetify_key():
    return os.environ.get("LEETIFY_API_KEY") or load_config().get("leetify_api_key")

def load_steam_ids():
    if not os.path.exists(STEAM_IDS_FILE):
        return {}
    with open(STEAM_IDS_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return {}

def save_steam_id(username, steam_id):
    os.makedirs(DATA_DIR, exist_ok=True)
    data = load_steam_ids()
    data[username] = steam_id
    with open(STEAM_IDS_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"✅ Saved mapping: {username} -> {steam_id}")

def get_steam_id(username):
    data = load_steam_ids()
    return data.get(username)

def api_demo_slap(method, path, data=None):
    headers = {
        "x-api-key": get_demo_slap_key(),
        "Content-Type": "application/json"
    }
    url = f"{DEMOSLAP_API_BASE}{path}"
    
    if method.upper() == "POST":
        r = requests.post(url, json=data, headers=headers)
    elif method.upper() == "GET":
        r = requests.get(url, headers=headers)
    else:
        raise ValueError("Invalid method")
        
    try:
        j = r.json()
    except:
        j = {"error": r.text}
    
    if r.status_code >= 400:
        return {"success": False, "status": r.status_code, "data": j}
    return {"success": True, "status": r.status_code, "data": j}

def cmd_matches(args):
    steam_id = get_steam_id(args.username)
    if not steam_id:
        print(f"❌ Unknown Steam ID for username '{args.username}'. Use 'save-id' command first.")
        sys.exit(1)
        
    leetify_key = get_leetify_key()
    if not leetify_key:
        print("❌ LEETIFY_API_KEY is not set. Cannot fetch matches.")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {leetify_key}"}
    url = f"{LEETIFY_API_BASE}/v3/profile/matches?steam64_id={steam_id}&limit=10"
    r = requests.get(url, headers=headers)
    
    if r.status_code != 200:
        print(f"❌ Error fetching matches: {r.text}")
        sys.exit(1)
        
    matches = r.json()
    if isinstance(matches, dict) and 'matches' in matches:
        matches = matches['matches']
        
    if not matches:
        print("No matches found.")
        return
        
    print(f"\n🎮 Recent Matches for {args.username} ({steam_id}):")
    print(f"{'Index':<5} | {'Map':<15} | {'Score':<10} | {'Date':<20} | Replay URL")
    print("-" * 80)
    for i, m in enumerate(matches):
        map_name = m.get('map_name', '?')
        score = f"{m.get('team_score', '?')}:{m.get('enemy_score', '?')}"
        dt = m.get('match_date', '?')
        replay = m.get('replay_url', 'Not Available')
        print(f"{i:<5} | {map_name:<15} | {score:<10} | {dt:<20} | {replay}")

def cmd_analyze(args):
    # Determine URL
    replay_url = args.url
    
    if not replay_url and args.username and args.match_index is not None:
        steam_id = get_steam_id(args.username)
        if not steam_id:
            print(f"❌ Unknown Steam ID for username '{args.username}'. Use 'save-id' command first.")
            sys.exit(1)
            
        leetify_key = get_leetify_key()
        if not leetify_key:
            print("❌ LEETIFY_API_KEY is not set. Provide direct --url or set the key.")
            sys.exit(1)
            
        print(f"🔍 Fetching match #{args.match_index} from Leetify for Steam ID: {steam_id}...")
        headers = {"Authorization": f"Bearer {leetify_key}"}
        url = f"{LEETIFY_API_BASE}/v3/profile/matches?steam64_id={steam_id}&limit={args.match_index + 1}"
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            matches = r.json()
            if isinstance(matches, dict) and 'matches' in matches:
                matches = matches['matches']
            if isinstance(matches, list) and len(matches) > args.match_index:
                replay_url = matches[args.match_index].get('replay_url')
                if not replay_url:
                    # Fallback to match details
                    match_id = matches[args.match_index].get('id')
                    url_detail = f"{LEETIFY_API_BASE}/v3/matches/{match_id}"
                    r_det = requests.get(url_detail, headers=headers)
                    if r_det.status_code == 200:
                        replay_url = r_det.json().get('replay_url')
    
    if not replay_url:
        print("❌ Could not find replay URL. Provide it manually via --url or check Leetify match index.")
        sys.exit(1)
        
    print(f"✅ Demo URL found: {replay_url}")
    print(f"🚀 Submitting to Demo-Slap API for analysis...")
    
    res = api_demo_slap("POST", "/public-api/analyze/url", {"url": replay_url})
    if not res["success"]:
        print(f"❌ Analysis submission failed: {res}")
        sys.exit(1)
        
    job_id = res["data"]["jobId"]
    print(f"⏳ Analysis JobID: {job_id}")
    print("⏳ Waiting for analysis to finish (may take 2-4 minutes)...")
    
    while True:
        status_res = api_demo_slap("GET", f"/public-api/analyze/{job_id}/status")
        if not status_res["success"]:
            print(f"❌ Status check failed: {status_res}")
            sys.exit(1)
        
        status = status_res["data"]["status"]
        if status == "done":
            break
        elif status == "error" or status == "failed":
            print(f"❌ Analysis failed on server.")
            sys.exit(1)
        else:
            time.sleep(15)
            
    print("✅ Analysis complete! Fetching highlights...")
    data_res = api_demo_slap("GET", f"/public-api/analyze/{job_id}/data")
    if not data_res["success"]:
        print(f"❌ Failed to fetch data: {data_res}")
        sys.exit(1)
        
    highlights = data_res["data"].get("highlights", [])
    if not highlights:
        print("❌ No highlights found in this demo.")
        sys.exit(0)
        
    filter_steam_id = None
    if args.username:
        filter_steam_id = get_steam_id(args.username)
        
    if filter_steam_id:
        highlights = [h for h in highlights if h.get("steamId") == filter_steam_id]
        if not highlights:
            print(f"❌ No highlights found for Steam ID {filter_steam_id}.")
            sys.exit(0)
    
    print(f"\n🎮 Highlights for Analysis JobID: {job_id}:\n")
    print(f"{'Highlight ID':<25} | {'Round':<5} | {'Steam ID':<18} | {'Kills':<5} | {'Weapons':<20} | {'Tags'}")
    print("-" * 100)
    
    for h in highlights:
        hid = h.get("id", "?")
        rnd = h.get("roundNumber", "?")
        sid = h.get("steamId", "?")
        kills_cnt = h.get("killCount", "?")
        kills = h.get("kills", [])
        weapons = ", ".join(set([k.get("weapon", "?") for k in kills]))
        tags = ", ".join(h.get("tags", []))
        print(f"{hid:<25} | {rnd:<5} | {sid:<18} | {kills_cnt:<5} | {weapons:<20} | {tags}")
        
    print("\nNext Steps:")
    print(f"To render ONE highlight: python3 demo_slap_cli.py render {job_id} <highlight_id>")
    print(f"To render FRAGMOVIE:     python3 demo_slap_cli.py render-fragmovie {job_id} <id1> <id2> ...")

def do_render(job_id, highlight_ids, endpoint):
    print(f"🚀 Submitting render job to {endpoint} with highlights: {highlight_ids}")
    
    payload = {"highlightIds": highlight_ids}
    if endpoint == "render-fragmovie":
        payload["introTitle"] = "Fragmovie"
        
    res = api_demo_slap("POST", f"/public-api/{endpoint}/{job_id}", payload)
    
    if not res["success"]:
        print(f"❌ Render submission failed: {res}")
        sys.exit(1)
        
    # the endpoint might return a new job ID for fragmovies, or jobIds array for renders
    poll_job_id = res["data"].get("jobId", job_id)
        
    print(f"⏳ Render job started! Polling status (may take 2-5 minutes)...")
    
    while True:
        status_res = api_demo_slap("GET", f"/public-api/{endpoint}/{poll_job_id}/status")
        if not status_res["success"]:
            print(f"❌ Render status check failed: {status_res}")
            sys.exit(1)
            
        data = status_res["data"]
        all_done = True
        has_error = False
        
        if isinstance(data, dict):
            if not data:
                all_done = False
            elif "status" in data and isinstance(data["status"], str):
                s = data["status"]
                all_done = (s == "done")
                has_error = (s in ["error", "failed"])
            else:
                for k, v in data.items():
                    if isinstance(v, dict) and "status" in v:
                        s = v["status"]
                        if s != "done":
                            all_done = False
                        if s in ["error", "failed"]:
                            has_error = True
                            
        if has_error:
            print("❌ Render failed on server!")
            sys.exit(1)
        if all_done:
            break
            
        time.sleep(15)
        
    print("✅ Render complete! Fetching URLs...")
    data_res = api_demo_slap("GET", f"/public-api/{endpoint}/{poll_job_id}/data")
    if not data_res["success"]:
        print(f"❌ Failed to fetch render data: {data_res}")
        sys.exit(1)
        
    clips = data_res["data"].get("highlightClips", {})
    if not clips:
        # Check if fragmovie specific response
        frag_url = data_res["data"].get("fragmovieUrl", None)
        if frag_url:
            clips = {"fragmovie": frag_url}
        else:
            # Maybe it returns a dict directly or highlights list
            pass
            
    if not clips:
        print("❌ No URLs found in response:", data_res["data"])
        sys.exit(1)
        
    for k, v in clips.items():
        url = v.get("clipUrl") if isinstance(v, dict) else v
        out_path = f"/tmp/render_{poll_job_id}_{k}.mp4"
        print(f"⬇️ Downloading: {url}")
        
        try:
            r_vid = requests.get(url, stream=True)
            with open(out_path, 'wb') as f:
                for chunk in r_vid.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Saved to: {out_path}")
        except Exception as e:
            print(f"❌ Download failed: {e}")

def cmd_render(args):
    do_render(args.job_id, [args.highlight_id], "render")

def cmd_render_fragmovie(args):
    do_render(args.job_id, args.highlight_ids, "render-fragmovie")

def cmd_set_key(args):
    save_config(args.service + "_api_key", args.api_key)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo-Slap Highlights Integration")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    p_set = subparsers.add_parser("set-key")
    p_set.add_argument("service", choices=["demoslap", "leetify"], help="Service to set key for")
    p_set.add_argument("api_key", help="The API key")
    
    p_save = subparsers.add_parser("save-id")
    p_save.add_argument("username", help="Telegram/System username")
    p_save.add_argument("steam_id", help="Steam64 ID")
    
    p_matches = subparsers.add_parser("matches")
    p_matches.add_argument("username", help="Username linked to Steam ID")
    
    p_analyze = subparsers.add_parser("analyze")
    p_analyze.add_argument("--url", help="Direct demo URL")
    p_analyze.add_argument("--username", help="Filter highlights by username's Steam ID")
    p_analyze.add_argument("--match-index", type=int, default=0, help="Fetch replay URL from Leetify match index (0=last)")
    
    p_render = subparsers.add_parser("render")
    p_render.add_argument("job_id", help="Analyze Job ID")
    p_render.add_argument("highlight_id", help="Highlight ID to render")
    
    p_frag = subparsers.add_parser("render-fragmovie")
    p_frag.add_argument("job_id", help="Analyze Job ID")
    p_frag.add_argument("highlight_ids", nargs='+', help="Multiple Highlight IDs to stitch")
    
    args = parser.parse_args()
    if args.command == "set-key": cmd_set_key(args)
    elif args.command == "save-id": cmd_save_id(args)
    elif args.command == "matches": cmd_matches(args)
    elif args.command == "analyze": cmd_analyze(args)
    elif args.command == "render": cmd_render(args)
    elif args.command == "render-fragmovie": cmd_render_fragmovie(args)
