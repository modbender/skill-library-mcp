#!/usr/bin/env python3
"""
Whoop API client for fetching recovery, strain, sleep, and HRV data.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(1)

class WhoopClient:
    """Client for interacting with Whoop API v2"""
    
    BASE_URL = "https://api.prod.whoop.com/developer/v2"
    ACTIVITY_BASE_URL = "https://api.prod.whoop.com/developer/v2/activity"
    
    def __init__(self, token_file=None):
        """Initialize client with API token from file or environment"""
        self.token_file = token_file or os.path.expanduser("~/.whoop_token")
        self.token = self._load_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def _load_token(self):
        """Load API token from file or environment"""
        # Try file first
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                return f.read().strip()
        
        # Try environment variable
        token = os.getenv('WHOOP_API_TOKEN')
        if token:
            return token
        
        raise ValueError(f"No Whoop API token found. Set WHOOP_API_TOKEN or create {self.token_file}")
    
    def _refresh_token(self):
        """Refresh expired access token using refresh token"""
        refresh_token_file = Path(self.token_file).parent / ".whoop_refresh_token"
        
        if not refresh_token_file.exists():
            raise ValueError("No refresh token found. Please re-authorize via OAuth.")
        
        refresh_token = refresh_token_file.read_text().strip()
        
        # Refresh token endpoint
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        response = requests.post("https://api.prod.whoop.com/oauth/oauth2/token", data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            new_access_token = token_data.get("access_token")
            new_refresh_token = token_data.get("refresh_token")
            
            # Save new tokens
            Path(self.token_file).write_text(new_access_token)
            if new_refresh_token:
                refresh_token_file.write_text(new_refresh_token)
            
            # Update current session token
            self.token = new_access_token
            self.headers["Authorization"] = f"Bearer {new_access_token}"
            
            print("✅ Access token auto-refreshed!", file=sys.stderr)
            return True
        else:
            raise ValueError(f"Token refresh failed: {response.status_code} - {response.text}")
    
    def _make_request(self, endpoint, params=None, retry_on_401=True):
        """Make GET request to Whoop API with automatic token refresh"""
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 401 and retry_on_401:
            # Token expired, try to refresh
            try:
                self._refresh_token()
                # Retry request with new token (but don't retry again to avoid infinite loop)
                return self._make_request(endpoint, params=params, retry_on_401=False)
            except Exception as e:
                raise ValueError(f"Token expired and refresh failed: {e}")
        
        response.raise_for_status()
        return response.json()
    
    def get_profile(self):
        """Get user profile information"""
        return self._make_request("user/profile/basic")
    
    def get_recovery(self, start_date=None, end_date=None, limit=7):
        """Get recovery data"""
        params = {"limit": limit}
        if start_date:
            params["start"] = start_date.isoformat()
        if end_date:
            params["end"] = end_date.isoformat()
        
        return self._make_request("recovery", params=params)
    
    def get_sleep(self, start_date=None, end_date=None, limit=7):
        """Get sleep data (v2 activity endpoint)"""
        params = {"limit": limit}
        if start_date:
            params["start"] = start_date.isoformat()
        if end_date:
            params["end"] = end_date.isoformat()
        
        return self._make_activity_request("sleep", params=params)
    
    def _make_activity_request(self, endpoint, params=None, retry_on_401=True):
        """Make GET request to activity endpoint with automatic token refresh"""
        url = f"{self.ACTIVITY_BASE_URL}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 401 and retry_on_401:
            try:
                self._refresh_token()
                return self._make_activity_request(endpoint, params=params, retry_on_401=False)
            except Exception as e:
                raise ValueError(f"Token expired and refresh failed: {e}")
        
        response.raise_for_status()
        return response.json()
    
    def get_sleep_by_id(self, sleep_id):
        """Get specific sleep by ID"""
        return self._make_activity_request(f"sleep/{sleep_id}")
    
    def get_cycle(self, start_date=None, end_date=None, limit=7):
        """Get physiological cycle data (strain, calories, HR, HRV)"""
        params = {"limit": limit}
        if start_date:
            params["start"] = start_date.isoformat()
        if end_date:
            params["end"] = end_date.isoformat()
        
        return self._make_request("cycle", params=params)
    
    def get_cycle_by_id(self, cycle_id):
        """Get specific cycle by ID"""
        return self._make_request(f"cycle/{cycle_id}")
    
    def get_sleep_for_cycle(self, cycle_id):
        """Get sleep data for a specific cycle"""
        return self._make_request(f"cycle/{cycle_id}/sleep")
    
    def get_workout(self, start_date=None, end_date=None, limit=10):
        """Get workout data (v2 activity endpoint)"""
        params = {"limit": limit}
        if start_date:
            params["start"] = start_date.isoformat()
        if end_date:
            params["end"] = end_date.isoformat()
        
        return self._make_activity_request("workout", params=params)
    
    def get_workout_by_id(self, workout_id):
        """Get specific workout by ID"""
        return self._make_activity_request(f"workout/{workout_id}")
    
    def get_today_summary(self):
        """Get today's recovery, sleep (last night), and current cycle"""
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # Get today's recovery
        recovery = self.get_recovery(start_date=yesterday, end_date=today, limit=1)
        
        # Get last night's sleep
        sleep = self.get_sleep(start_date=yesterday, end_date=today, limit=1)
        
        # Get today's cycle (strain, HRV, etc.)
        cycle = self.get_cycle(start_date=yesterday, end_date=today, limit=1)
        
        return {
            "date": today.isoformat(),
            "recovery": recovery.get("records", [{}])[0] if recovery.get("records") else {},
            "sleep": sleep.get("records", [{}])[0] if sleep.get("records") else {},
            "cycle": cycle.get("records", [{}])[0] if cycle.get("records") else {}
        }


def main():
    parser = argparse.ArgumentParser(description="Whoop API client")
    parser.add_argument("--token-file", help="Path to file containing API token")
    parser.add_argument("--action", choices=["profile", "recovery", "sleep", "cycle", "workout", "today"], 
                       default="today", help="Action to perform")
    parser.add_argument("--days", type=int, default=7, help="Number of days of data to fetch")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--id", help="ID for specific item lookup (cycle/sleep/workout)")
    
    args = parser.parse_args()
    
    try:
        client = WhoopClient(token_file=args.token_file)
        
        if args.action == "profile":
            data = client.get_profile()
        elif args.action == "recovery":
            data = client.get_recovery(limit=args.days)
        elif args.action == "sleep":
            if args.id:
                data = client.get_sleep_by_id(args.id)
            else:
                data = client.get_sleep(limit=args.days)
        elif args.action == "cycle":
            if args.id:
                data = client.get_cycle_by_id(int(args.id))
            else:
                data = client.get_cycle(limit=args.days)
        elif args.action == "workout":
            if args.id:
                data = client.get_workout_by_id(args.id)
            else:
                data = client.get_workout(limit=args.days)
        elif args.action == "today":
            data = client.get_today_summary()
        
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            # Pretty print summary
            if args.action == "today":
                print_today_summary(data)
            else:
                print(json.dumps(data, indent=2))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def print_today_summary(data):
    """Print human-readable today summary"""
    print(f"📊 Whoop Summary for {data['date']}")
    print("=" * 50)
    
    # Recovery
    recovery = data.get('recovery', {})
    if recovery:
        score = recovery.get('score', {})
        print(f"\n🔋 Recovery: {score.get('recovery_score', 'N/A')}%")
        print(f"   HRV: {score.get('hrv_rmssd_milli', 'N/A')} ms")
        print(f"   RHR: {score.get('resting_heart_rate', 'N/A')} bpm")
    
    # Sleep
    sleep = data.get('sleep', {})
    if sleep:
        score = sleep.get('score', {})
        duration_ms = sleep.get('score', {}).get('total_in_bed_time_milli', 0)
        hours = duration_ms / (1000 * 60 * 60) if duration_ms else 0
        print(f"\n😴 Sleep: {score.get('sleep_performance_percentage', 'N/A')}%")
        print(f"   Duration: {hours:.1f} hours")
        print(f"   Quality: {score.get('sleep_quality_percentage', 'N/A')}%")
    
    # Cycle (Strain)
    cycle = data.get('cycle', {})
    if cycle:
        score = cycle.get('score', {})
        print(f"\n💪 Strain: {score.get('strain', 'N/A')}")
        print(f"   Calories: {score.get('kilojoule', 0) / 4.184:.0f} kcal")


if __name__ == "__main__":
    main()
