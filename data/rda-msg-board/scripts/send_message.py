#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import base64

def get_config_path():
    """Get the boards.yaml config file path."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'boards.yaml')

def load_profiles():
    """Load board profiles from boards.yaml."""
    config_path = get_config_path()
    if not os.path.exists(config_path):
        return {}
    try:
        import yaml
        with open(config_path) as f:
            return yaml.safe_load(f).get('profiles', {})
    except ImportError:
        print("Warning: PyYAML not installed. Profile support disabled. Install with: pip install pyyaml")
        return {}
    except Exception as e:
        print(f"Warning: Could not load profiles: {e}")
        return {}

def list_profiles():
    """List all available board profiles."""
    profiles = load_profiles()
    if not profiles:
        print("No board profiles found.")
        print("Create profiles using: python3 scripts/manage_boards.py add <name> --ip <ip> --user <user> --pass <password>")
        return

    print("\n📟 Available Board Profiles:")
    print("-" * 50)
    for name, config in profiles.items():
        print(f"  • {name:15} → {config.get('ip', 'N/A')}")
    print()

def send_message(args):
    # List profiles and exit
    if args.list_profiles:
        list_profiles()
        return

    # Load profile if specified
    if args.profile:
        profiles = load_profiles()
        if args.profile not in profiles:
            print(f"Error: Profile '{args.profile}' not found.")
            print("Use --list-profiles to see available profiles.")
            sys.exit(1)
        profile_config = profiles[args.profile]

        # Use profile values as defaults
        ip = args.ip or profile_config.get('ip')
        user = args.user or profile_config.get('user', 'admin')
        password = args.password or profile_config.get('pass', 'msgboard')
    else:
        # Resolve config from args or env
        ip = args.ip or os.environ.get('MSG_BOARD_IP')
        user = args.user or os.environ.get('MSG_BOARD_USER', 'admin')
        password = args.password or os.environ.get('MSG_BOARD_PASS', 'msgboard')

    if not ip:
        print("Error: IP address required. Use --ip, --profile, or set MSG_BOARD_IP env var.")
        sys.exit(1)

    # Handle hostname vs IP (simple check, user must provide scheme or we assume http)
    if ip.startswith("http"):
        url = f"{ip}/api"
    else:
        url = f"http://{ip}/api"
    
    # Build payload
    payload = {"MSG": args.message}
    if args.repeat is not None: payload["REP"] = args.repeat
    if args.buzzer is not None: payload["BUZ"] = args.buzzer
    if args.delay is not None: payload["DEL"] = args.delay
    if args.brightness is not None: payload["BRI"] = args.brightness
    if args.chirp is not None: payload["ALERTCHIRP"] = args.chirp
    # Only set ASC if explicitly changed or if we want to enforce default? 
    # The API defaults ASC=1 usually. Let's send it if user passed a flag, 
    # but argparse 'store_true' makes it tricky to detect 'not set'.
    # We'll trust the device defaults unless args are present.
    
    data = json.dumps(payload).encode('utf-8')
    
    # Setup request
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    
    # Basic Auth
    auth_str = f"{user}:{password}"
    b64_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
    req.add_header('Authorization', f"Basic {b64_auth}")

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200 or response.status == 204:
                print(f"Success: Message sent to {ip}")
                # print(response.read().decode('utf-8')) # Optional verbose output
            else:
                print(f"Error: Server returned status {response.status}")
                sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error connecting to {url}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send message to RDA MSG Board")
    parser.add_argument("message", nargs='?', help="Message text to display")
    parser.add_argument("--profile", "-p", help="Board profile name (from boards.yaml)")
    parser.add_argument("--list-profiles", action="store_true", help="List available board profiles")
    parser.add_argument("--ip", help="Device IP address")
    parser.add_argument("--user", help="Web interface username")
    parser.add_argument("--password", help="Web interface password")

    parser.add_argument("--repeat", type=int, help="Repeat count (0=infinite)")
    parser.add_argument("--buzzer", type=int, help="Buzzer chirps")
    parser.add_argument("--delay", type=int, help="Scroll delay (ms)")
    parser.add_argument("--brightness", type=int, help="Brightness (0-15)")
    parser.add_argument("--chirp", help="Custom chirp name (e.g., 'Mario Bros', 'Imperial March')")

    args = parser.parse_args()

    # Handle --list-profiles without requiring message
    if args.list_profiles:
        list_profiles()
        sys.exit(0)

    # Require message for sending
    if not args.message:
        parser.print_help()
        sys.exit(1)

    send_message(args)
