#!/usr/bin/env python3
"""
Peloton Weekly Stats - Direct API integration (no dependencies).
Fetches cycling workout data from the Peloton API.
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

API_BASE = "https://api.onepeloton.com"
TOKEN_URL = "https://auth.onepeloton.com/oauth/token"
CLIENT_ID = "mgsmWCD0A8Qn6uz6mmqI6qeBNHH9IPwS"


class PelotonAPI:
    """Minimal Peloton API client using only stdlib (OAuth2)."""

    def __init__(self, username: str, password: str):
        self.access_token = None
        self.user_id = None
        self._login(username, password)

    def _request(self, method: str, path: str, body: dict = None, base: str = API_BASE) -> dict:
        url = f"{base}{path}" if base else path
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        if self.access_token:
            req.add_header("Authorization", f"Bearer {self.access_token}")
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())

    def _login(self, username: str, password: str):
        payload = {
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "scope": "offline_access openid",
            "username": username,
            "password": password,
        }
        data = json.dumps(payload).encode()
        req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=15) as resp:
            token_data = json.loads(resp.read())
        self.access_token = token_data["access_token"]

        # Get user ID from /api/me
        me = self._request("GET", "/api/me")
        self.user_id = me["id"]

    def get_workouts(self, limit: int = 20, page: int = 0) -> list:
        data = self._request(
            "GET",
            f"/api/user/{self.user_id}/workouts"
            f"?joins=ride,ride.instructor&limit={limit}&page={page}",
        )
        return data.get("data", [])

    def get_performance(self, workout_id: str) -> dict:
        return self._request(
            "GET",
            f"/api/workout/{workout_id}/performance_graph?every_n=5",
        )


def fetch_weekly_stats(username: str, password: str) -> dict:
    """Fetch and format weekly cycling stats."""
    api = PelotonAPI(username, password)
    workouts = api.get_workouts(limit=20)

    cutoff = datetime.now() - timedelta(days=7)

    cycling_workouts = []
    for w in workouts:
        created_at = datetime.fromtimestamp(w.get("created_at", 0))
        if created_at >= cutoff and w.get("fitness_discipline") == "cycling":
            cycling_workouts.append(w)

    stats = {
        "total_rides": len(cycling_workouts),
        "total_duration_min": 0,
        "total_calories": 0,
        "total_output_kj": 0,
        "avg_power": 0,
        "avg_resistance": 0,
        "avg_cadence": 0,
        "rides": [],
    }

    total_power = 0
    total_resistance = 0
    total_cadence = 0
    power_count = 0

    for w in cycling_workouts:
        workout_id = w["id"]
        created_at = datetime.fromtimestamp(w.get("created_at", 0))

        perf = api.get_performance(workout_id)

        # Summaries: [{"slug": "total_output", "value": 395}, ...]
        summaries = {s["slug"]: s.get("value", 0) for s in perf.get("summaries", []) if "slug" in s}

        # Metrics: [{"slug": "output", "average_value": 146}, ...]
        metrics = {m["slug"]: m for m in perf.get("metrics", []) if "slug" in m}

        ride = w.get("ride") or {}
        duration = ride.get("duration", 0) // 60
        output = summaries.get("total_output", 0)
        calories = summaries.get("calories", 0)
        power = metrics.get("output", {}).get("average_value", 0)
        resistance = metrics.get("resistance", {}).get("average_value", 0)
        cadence = metrics.get("cadence", {}).get("average_value", 0)

        # Instructor name from the joined ride data
        instructor = ride.get("instructor", {}) or {}
        instructor_name = instructor.get("name", "Unknown")

        stats["total_duration_min"] += duration
        stats["total_calories"] += calories
        stats["total_output_kj"] += output

        if power > 0:
            total_power += power
            power_count += 1
        if resistance > 0:
            total_resistance += resistance
        if cadence > 0:
            total_cadence += cadence

        stats["rides"].append({
            "date": created_at.strftime("%a %m/%d"),
            "title": ride.get("title", "Unknown"),
            "instructor": instructor_name,
            "duration_min": duration,
            "calories": calories,
            "output_kj": output,
            "avg_power": power,
            "avg_resistance": resistance,
            "avg_cadence": cadence,
        })

    if power_count > 0:
        stats["avg_power"] = total_power / power_count
    if cycling_workouts:
        stats["avg_resistance"] = total_resistance / len(cycling_workouts)
        stats["avg_cadence"] = total_cadence / len(cycling_workouts)

    return stats


def print_weekly_report(stats: dict):
    """Print formatted weekly report in markdown."""
    print("## Peloton Weekly Cycling Stats\n")

    print(f"**{stats['total_rides']} rides** | **{stats['total_duration_min']} min** | **{stats['total_calories']:.0f} cal** | **{stats['total_output_kj']:.0f} kJ**\n")

    if stats["total_rides"] > 0:
        print(f"**Avg Power:** {stats['avg_power']:.0f}W | **Avg Resistance:** {stats['avg_resistance']:.0f}% | **Avg Cadence:** {stats['avg_cadence']:.0f} RPM\n")

    if stats["rides"]:
        print("### Recent Rides\n")
        print("| Date | Class | Instructor | Duration | Output | Calories |")
        print("|------|-------|------------|----------|--------|----------|")

        for ride in stats["rides"][:5]:
            title = ride["title"][:30] + "..." if len(ride["title"]) > 30 else ride["title"]
            print(f"| {ride['date']} | {title} | {ride['instructor']} | {ride['duration_min']}min | {ride['output_kj']:.0f}kJ | {ride['calories']:.0f} |")

    print()


def load_credentials() -> tuple[str, str]:
    """Load Peloton credentials from OpenClaw auth-profiles.json or environment variables."""
    # Try environment variables first (backward compatibility)
    username = os.environ.get("PELOTON_USERNAME")
    password = os.environ.get("PELOTON_PASSWORD")
    
    if username and password:
        return username, password
    
    # Try OpenClaw auth-profiles.json
    auth_path = os.path.expanduser("~/.openclaw/agents/main/agent/auth-profiles.json")
    if os.path.exists(auth_path):
        try:
            with open(auth_path) as f:
                auth_data = json.load(f)
            
            profile = auth_data.get("profiles", {}).get("peloton:default", {})
            username = profile.get("username")
            password = profile.get("password")
            
            if username and password:
                return username, password
        except Exception as e:
            print(f"Warning: Failed to load credentials from auth-profiles.json: {e}", file=sys.stderr)
    
    return None, None


def main():
    """Main entry point."""
    username, password = load_credentials()

    if not username or not password:
        print("Error: Peloton credentials not found")
        print("\nOption 1: Use OpenClaw credential manager (recommended):")
        print("  Edit ~/.openclaw/agents/main/agent/auth-profiles.json and add:")
        print('  "peloton:default": {')
        print('    "type": "api_key",')
        print('    "provider": "peloton",')
        print('    "username": "your-email@example.com",')
        print('    "password": "your-password"')
        print('  }')
        print("\nOption 2: Use environment variables:")
        print("  export PELOTON_USERNAME='your-email@example.com'")
        print("  export PELOTON_PASSWORD='your-password'")
        sys.exit(1)

    try:
        stats = fetch_weekly_stats(username, password)
        print_weekly_report(stats)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
