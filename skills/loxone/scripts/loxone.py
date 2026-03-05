#!/usr/bin/env python3
"""
Loxone CLI - Command-line interface for Loxone Miniserver
"""

import sys
import json
import argparse
from pathlib import Path
from loxone_client import LoxoneClient
from loxone_config import load_config_file


# Safe rooms for testing control commands
SAFE_ROOMS = ['guest room', 'kids room', 'kids', 'gästezimmer', 'kinderzimmer', '1.5 guest room', '3.4 kids']


def is_safe_room(room_name: str) -> bool:
    """Check if a room is safe for testing control commands"""
    return room_name.lower() in SAFE_ROOMS


def load_config():
    """Load configuration from config.json.

    Supports Cloud DNS shorthand hosts like:
      - dns.loxonecloud.com/<SERIAL>
      - <SERIAL>

    These are resolved at runtime to the certificate-matching dyndns hostname.
    """
    config_path = Path(__file__).parent.parent / "config.json"

    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        print("\nCreate a config.json file with the following structure:")
        print(json.dumps({
            "host": "192.168.0.222",
            "username": "your_username",
            "password": "your_password",
            "use_https": True
        }, indent=2))
        print("\nOr use the Cloud DNS tunnel without hard-coding an IP:")
        print(json.dumps({
            "host": "dns.loxonecloud.com/<SERIAL>",
            "username": "your_username",
            "password": "your_password",
            "use_https": True
        }, indent=2))
        sys.exit(1)

    try:
        return load_config_file(str(config_path))
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in config file: {config_path}")
        sys.exit(1)


def cmd_map(args):
    """Display complete installation map"""
    config = load_config()
    client = LoxoneClient(**config)
    
    # Load or fetch structure
    structure_path = Path(__file__).parent.parent / "installation_map.json"
    
    if args.refresh or not structure_path.exists():
        print("Fetching structure from Miniserver...")
        client.fetch_structure(str(structure_path))
    else:
        print("Loading cached structure...")
        with open(structure_path) as f:
            client.structure = json.load(f)
        client._parse_structure()
    
    # Display map
    print("\n" + "="*60)
    print("LOXONE INSTALLATION MAP")
    print("="*60)
    
    print(f"\nTotal Rooms: {len(client.rooms)}")
    print(f"Total Controls: {len(client.controls)}\n")
    
    for room in sorted(client.get_rooms(), key=lambda x: x['name']):
        print(f"\n📍 {room['name']} ({room['control_count']} controls)")
        print("   " + "-"*50)
        
        controls = client.get_room_controls(room['name'])
        for control in sorted(controls, key=lambda x: x['name']):
            print(f"   • {control['name']} [{control['type']}]")
            print(f"     UUID: {control['uuid']}")


def cmd_rooms(args):
    """List all rooms"""
    config = load_config()
    client = LoxoneClient(**config)
    
    # Load structure
    structure_path = Path(__file__).parent.parent / "installation_map.json"
    
    if args.refresh or not structure_path.exists():
        print("Fetching structure from Miniserver...")
        client.fetch_structure(str(structure_path))
    else:
        with open(structure_path) as f:
            client.structure = json.load(f)
        client._parse_structure()
    
    # Display rooms
    print("\nROOMS:")
    print("-" * 60)
    
    for room in sorted(client.get_rooms(), key=lambda x: x['name']):
        safe_marker = "✅" if is_safe_room(room['name']) else "  "
        print(f"{safe_marker} {room['name']:<30} {room['control_count']:>3} controls")
    
    print("\n✅ = Safe for testing control commands")


def cmd_status(args):
    """Get status for a room or device"""
    config = load_config()
    client = LoxoneClient(**config)
    
    # Load structure
    structure_path = Path(__file__).parent.parent / "installation_map.json"
    
    if not structure_path.exists():
        print("Structure file not found. Run 'loxone map' first.")
        sys.exit(1)
    
    with open(structure_path) as f:
        client.structure = json.load(f)
    client._parse_structure()
    
    room_name = args.room
    
    try:
        status = client.get_room_status(room_name)
        
        print(f"\n📍 {status['room']}")
        print("=" * 60)
        
        # Temperature
        if status['temperature'] is not None:
            print(f"🌡️  Temperature: {status['temperature']}°C")
        
        # Humidity
        if status['humidity'] is not None:
            print(f"💧 Humidity: {status['humidity']}%")
        
        # Lights
        if status['lights']:
            print(f"\n💡 Lights:")
            
            # Separate standard lights from LightControllerV2
            room_controls = {c['uuid']: client.controls[c['uuid']] for c in client.get_room_controls(room_name)}
            standard_lights = []
            light_controllers = []
            
            for light in status['lights']:
                control = room_controls.get(light['uuid'])
                if control and control.get('type') == 'LightControllerV2':
                    light_controllers.append(control)
                else:
                    standard_lights.append(light)
            
            for light in standard_lights:
                state = "ON" if light['state'] == 1 or light['state'] == '1' else "OFF"
                print(f"   • {light['name']}: {state}")
            
            for controller in light_controllers:
                print(f"   • {controller['name']} [LightControllerV2]:")
                sub_controls = controller.get('subControls', {})
                for sub_uuid, sub_control in sub_controls.items():
                    uuid_action = sub_control.get('uuidAction', sub_uuid)
                    if 'AI' not in uuid_action:
                        continue
                    try:
                        value = client.get_status(uuid_action)
                    except Exception:
                        value = None
                    
                    if value is None:
                        state = "UNKNOWN"
                    elif value == 0 or value == '0':
                        state = f"OFF ({value})"
                    else:
                        state = f"ON ({value})"
                    print(f"     - {sub_control.get('name', uuid_action)}: {state}")
        
        # Switches
        if status['switches']:
            print(f"\n🔌 Switches:")
            for switch in status['switches']:
                state = "ON" if switch['state'] == 1 or switch['state'] == '1' else "OFF"
                print(f"   • {switch['name']}: {state}")
        
        print()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_control(args):
    """Control a device"""
    config = load_config()
    client = LoxoneClient(**config)
    
    # Load structure
    structure_path = Path(__file__).parent.parent / "installation_map.json"
    
    if not structure_path.exists():
        print("Structure file not found. Run 'loxone map' first.")
        sys.exit(1)
    
    with open(structure_path) as f:
        client.structure = json.load(f)
    client._parse_structure()
    
    device_name = args.device
    action = args.action.lower()
    room_name = args.room
    
    # Sanitize action value — must be a simple value (on/off/number/pulse)
    # Block path traversal, command injection, URL manipulation
    import re as _re
    if not _re.match(r'^[a-zA-Z0-9._-]+$', action):
        print(f"❌ Invalid action value: '{action}'")
        print("Actions must be alphanumeric (e.g., on, off, pulse, 0-100)")
        sys.exit(1)
    
    # Safety check: Only allow control commands in safe rooms
    if room_name and not is_safe_room(room_name):
        print(f"⚠️  WARNING: Control commands are only allowed in safe rooms!")
        print(f"Safe rooms: {', '.join(SAFE_ROOMS)}")
        print(f"Room '{room_name}' is NOT safe for testing.")
        sys.exit(1)
    
    try:
        # Find the device
        control = client.get_control_by_name(device_name, room_name)
        
        if not control:
            print(f"Error: Device '{device_name}' not found")
            if room_name:
                print(f"in room '{room_name}'")
            sys.exit(1)
        
        # Double-check room safety
        control_room_uuid = control.get('room')
        if control_room_uuid and control_room_uuid in client.rooms:
            control_room_name = client.rooms[control_room_uuid]['name']
            if not is_safe_room(control_room_name):
                print(f"⚠️  WARNING: Device '{device_name}' is in room '{control_room_name}'")
                print(f"which is NOT a safe room for testing!")
                print(f"Safe rooms: {', '.join(SAFE_ROOMS)}")
                sys.exit(1)
        
        # Execute action
        if action == 'on':
            success = client.turn_on(device_name, room_name)
        elif action == 'off':
            success = client.turn_off(device_name, room_name)
        else:
            # Try sending the value directly
            success = client.send_command(control['uuid'], args.action)
        
        if success:
            print(f"✅ Command sent: {device_name} → {action}")
        else:
            print(f"❌ Command failed: {device_name} → {action}")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_test(args):
    """Test connection to Miniserver"""
    config = load_config()
    
    print(f"Testing connection to Miniserver at {config['host']}...")
    
    try:
        client = LoxoneClient(**config)
        client.fetch_structure()
        
        print(f"✅ Connection successful!")
        print(f"   Rooms: {len(client.rooms)}")
        print(f"   Controls: {len(client.controls)}")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Loxone Miniserver CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  loxone map                           # Show complete installation map
  loxone rooms                         # List all rooms
  loxone status "Office"               # Show office status
  loxone control "Ceiling Light" on --room "Guest room"  # Turn on light (safe room only)
  loxone test                          # Test connection

Safe rooms for control commands: Guest room, Kids room
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Map command
    map_parser = subparsers.add_parser('map', help='Display complete installation map')
    map_parser.add_argument('--refresh', action='store_true', help='Refresh structure from Miniserver')
    map_parser.set_defaults(func=cmd_map)
    
    # Rooms command
    rooms_parser = subparsers.add_parser('rooms', help='List all rooms')
    rooms_parser.add_argument('--refresh', action='store_true', help='Refresh structure from Miniserver')
    rooms_parser.set_defaults(func=cmd_rooms)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get room status')
    status_parser.add_argument('room', help='Room name')
    status_parser.set_defaults(func=cmd_status)
    
    # Control command
    control_parser = subparsers.add_parser('control', help='Control a device')
    control_parser.add_argument('device', help='Device name')
    control_parser.add_argument('action', help='Action (on/off/value)')
    control_parser.add_argument('--room', help='Room name (for disambiguation)')
    control_parser.set_defaults(func=cmd_control)
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test connection to Miniserver')
    test_parser.set_defaults(func=cmd_test)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
