#!/usr/bin/env python3
"""Strava controller for OpenClaw"""
import sys
import json
import os
from stravalib.client import Client
from datetime import datetime, timedelta

def load_credentials():
    """Load Strava credentials from config file"""
    config_path = os.path.expanduser('~/.strava_credentials.json')
    if not os.path.exists(config_path):
        print(f"❌ Credentials not found at {config_path}")
        print("Run the setup script first: python3 setup.py")
        sys.exit(1)

    with open(config_path, 'r') as f:
        return json.load(f)

def get_client():
    """Get authenticated Strava client"""
    creds = load_credentials()
    client = Client()
    client.access_token = creds['access_token']
    return client

def recent_activities(limit=5):
    """Get recent activities"""
    client = get_client()
    activities = list(client.get_activities(limit=limit))
    print(f"📊 Recent {len(activities)} activities:\n")

    for i, activity in enumerate(activities, 1):
        distance_mi = float(activity.distance) * 0.000621371 if activity.distance else 0
        moving_time = str(activity.moving_time).split('.')[0] if activity.moving_time else "N/A"
        print(f"{i}. {activity.name}")
        print(f"   Type: {activity.type} | Distance: {distance_mi:.2f} mi | Time: {moving_time}")
        print(f"   Date: {activity.start_date_local.strftime('%Y-%m-%d %H:%M')}\n")

def stats():
    """Get athlete stats"""
    client = get_client()
    athlete = client.get_athlete()
    print(f"👤 {athlete.firstname} {athlete.lastname}")
    if athlete.city and athlete.state:
        print(f"📍 {athlete.city}, {athlete.state}")

    # Get stats
    stats = client.get_athlete_stats()

    # Recent running
    if stats.recent_run_totals:
        run_mi = float(stats.recent_run_totals.distance) * 0.000621371
        run_time = str(stats.recent_run_totals.moving_time).split('.')[0]
        print(f"\n🏃 Recent Running (last 4 weeks):")
        print(f"   Distance: {run_mi:.2f} mi")
        print(f"   Time: {run_time}")
        print(f"   Runs: {stats.recent_run_totals.count}")

    # Recent riding
    if stats.recent_ride_totals:
        ride_mi = float(stats.recent_ride_totals.distance) * 0.000621371
        ride_time = str(stats.recent_ride_totals.moving_time).split('.')[0]
        print(f"\n🚴 Recent Cycling (last 4 weeks):")
        print(f"   Distance: {ride_mi:.2f} mi")
        print(f"   Time: {ride_time}")
        print(f"   Rides: {stats.recent_ride_totals.count}")

def last_activity():
    """Get last activity"""
    client = get_client()
    activities = list(client.get_activities(limit=1))

    if activities:
        activity = activities[0]
        distance_mi = float(activity.distance) * 0.000621371 if activity.distance else 0
        moving_time = str(activity.moving_time).split('.')[0] if activity.moving_time else "N/A"
        print(f"🏃 Last Activity: {activity.name}")
        print(f"Type: {activity.type}")
        print(f"Distance: {distance_mi:.2f} mi")
        print(f"Time: {moving_time}")
        print(f"Date: {activity.start_date_local.strftime('%Y-%m-%d %H:%M')}")
    else:
        print("No activities found")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: strava_control.py [recent|stats|last]")
        print("")
        print("Commands:")
        print("  recent  - Show recent activities")
        print("  stats   - Show weekly/monthly stats")
        print("  last    - Show last activity")
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        if command == "recent":
            recent_activities()
        elif command == "stats":
            stats()
        elif command == "last":
            last_activity()
        else:
            print(f"Unknown command: {command}")
            print("Use: recent, stats, or last")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
