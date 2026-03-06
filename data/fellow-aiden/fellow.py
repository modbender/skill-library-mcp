#!/usr/bin/env python3
"""
Fellow Aiden OpenClaw Skill - Direct API implementation
Works around library issues with current Fellow API
"""

import argparse
import json
import os
import sys
import requests

BASE_URL = 'https://l8qtmnc692.execute-api.us-west-2.amazonaws.com/v1'
HEADERS = {'User-Agent': 'Fellow/5 CFNetwork/1568.300.101 Darwin/24.2.0'}

class FellowAidenDirect:
    """Direct API client that works with current Fellow API."""
    
    def __init__(self, email, password):
        self._email = email
        self._password = password
        self._token = None
        self._brewer_id = None
        self._device_config = None
        self._auth()
        self._fetch_device()
    
    def _auth(self):
        """Authenticate and get token."""
        auth = {"email": self._email, "password": self._password}
        session = requests.Session()
        session.headers.update(HEADERS)
        login_url = BASE_URL + '/auth/login'
        response = session.post(login_url, json=auth, headers=HEADERS)
        parsed = json.loads(response.content)
        
        if 'accessToken' not in parsed:
            raise Exception("Email or password incorrect.")
        
        self._token = parsed['accessToken']
        self._session = session
        self._session.headers.update({'Authorization': 'Bearer ' + self._token})
    
    def _fetch_device(self):
        """Fetch device info."""
        device_url = BASE_URL + '/devices'
        response = self._session.get(device_url, params={'dataType': 'real'})
        parsed = json.loads(response.content)
        
        if not parsed or len(parsed) == 0:
            raise Exception("No brewer found on this account.")
        
        self._device_config = parsed[0]
        self._brewer_id = self._device_config['id']
    
    def get_display_name(self):
        """Get brewer display name."""
        return self._device_config.get('displayName', 'Unknown')
    
    def get_device_details(self):
        """Get full device details."""
        return {
            'id': self._brewer_id,
            'display_name': self._device_config.get('displayName'),
            'serial_number': self._device_config.get('serialNumber'),
            'firmware_version': self._device_config.get('firmwareVersion'),
            'is_connected': self._device_config.get('isConnected'),
            'total_brews': self._device_config.get('totalBrewingCycles'),
            'total_water_l': self._device_config.get('totalWaterVolumeL'),
            'carafe_present': self._device_config.get('carafePresent'),
            'batch_brew_basket_present': self._device_config.get('batchBrewBasketPresent'),
            'single_brew_basket_present': self._device_config.get('singleBrewBasketPresent'),
            'current_profile_id': self._device_config.get('ibSelectedProfileId'),
            'brewing': self._device_config.get('brewing'),
        }
    
    def get_profiles(self):
        """Fetch profiles from separate endpoint."""
        url = BASE_URL + f'/devices/{self._brewer_id}/profiles'
        response = self._session.get(url)
        return json.loads(response.content)
    
    def get_schedules(self):
        """Fetch schedules from separate endpoint."""
        url = BASE_URL + f'/devices/{self._brewer_id}/schedules'
        response = self._session.get(url)
        return json.loads(response.content)


def get_client():
    email = os.environ.get("FELLOW_EMAIL")
    password = os.environ.get("FELLOW_PASSWORD")

    if not email or not password:
        print(json.dumps({"error": "Missing credentials. Set FELLOW_EMAIL and FELLOW_PASSWORD environment variables."}))
        sys.exit(1)

    try:
        return FellowAidenDirect(email, password)
    except Exception as e:
        print(json.dumps({"error": f"Failed to connect: {str(e)}"}))
        sys.exit(1)


def output(data):
    print(json.dumps(data, indent=2, default=str))


# ─── COMMANDS ────────────────────────────────────────────────────────────────

def cmd_info(args):
    aiden = get_client()
    try:
        result = {
            "display_name": aiden.get_display_name(),
            "device": aiden.get_device_details()
        }
        output(result)
    except Exception as e:
        output({"error": str(e)})


def cmd_profiles_list(args):
    aiden = get_client()
    try:
        profiles = aiden.get_profiles()
        output({"profiles": profiles, "count": len(profiles)})
    except Exception as e:
        output({"error": str(e)})


def cmd_profiles_get(args):
    aiden = get_client()
    try:
        profiles = aiden.get_profiles()
        
        if args.id:
            match = next((p for p in profiles if p.get("id") == args.id), None)
            if match:
                output(match)
            else:
                output({"error": f"No profile found with id '{args.id}'"})
        elif args.title:
            # Simple fuzzy match
            matches = [p for p in profiles if args.title.lower() in p.get("title", "").lower()]
            if args.fuzzy and not matches:
                # Try partial word match
                matches = [p for p in profiles if any(word.lower().startswith(args.title.lower()) for word in p.get("title", "").split())]
            if matches:
                output(matches[0])
            else:
                output({"error": f"No profile found matching '{args.title}'"})
        else:
            output({"error": "Provide --id or --title"})
    except Exception as e:
        output({"error": str(e)})


def cmd_schedules_list(args):
    aiden = get_client()
    try:
        schedules = aiden.get_schedules()
        output({"schedules": schedules, "count": len(schedules)})
    except Exception as e:
        output({"error": str(e)})


def cmd_status(args):
    """Quick status check."""
    aiden = get_client()
    try:
        device = aiden.get_device_details()
        profiles = aiden.get_profiles()
        schedules = aiden.get_schedules()
        
        output({
            "brewer": aiden.get_display_name(),
            "online": device.get('is_connected'),
            "brewing": device.get('brewing'),
            "firmware": device.get('firmware_version'),
            "total_brews": device.get('total_brews'),
            "total_water_l": device.get('total_water_l'),
            "carafe_present": device.get('carafe_present'),
            "profiles_count": len(profiles),
            "schedules_count": len(schedules),
            "current_profile": device.get('current_profile_id')
        })
    except Exception as e:
        output({"error": str(e)})


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Fellow Aiden OpenClaw Skill")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Info
    subparsers.add_parser("info", help="Get brewer info")
    subparsers.add_parser("status", help="Quick status overview")

    # Profiles
    profiles_parser = subparsers.add_parser("profiles", help="Profile commands")
    profiles_sub = profiles_parser.add_subparsers(dest="profiles_cmd")
    
    profiles_sub.add_parser("list", help="List all profiles")
    
    get_parser = profiles_sub.add_parser("get", help="Get a profile")
    get_parser.add_argument("--id", help="Profile ID")
    get_parser.add_argument("--title", help="Profile title")
    get_parser.add_argument("--fuzzy", action="store_true", help="Fuzzy match title")

    # Schedules
    schedules_parser = subparsers.add_parser("schedules", help="Schedule commands")
    schedules_sub = schedules_parser.add_subparsers(dest="schedules_cmd")
    
    schedules_sub.add_parser("list", help="List all schedules")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "info":
        cmd_info(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "profiles":
        if args.profiles_cmd == "list":
            cmd_profiles_list(args)
        elif args.profiles_cmd == "get":
            cmd_profiles_get(args)
        else:
            profiles_parser.print_help()
    elif args.command == "schedules":
        if args.schedules_cmd == "list":
            cmd_schedules_list(args)
        else:
            schedules_parser.print_help()


if __name__ == "__main__":
    main()
