#!/usr/bin/env python3
"""
Roku Control Script - Local network control via ECP (External Control Protocol)
No authentication required - works over LAN
"""

import os
import sys
import json
import socket
import requests
import argparse
import time
from typing import Optional, List, Dict, Any
from xml.etree import ElementTree as ET

# Roku ECP defaults
ROKU_PORT = 8060
SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900
DISCOVERY_TIMEOUT = 3

class RokuController:
    def __init__(self, roku_ip: str = None):
        self.roku_ip = roku_ip
        self.device_info = None
    
    def discover(self) -> List[Dict[str, str]]:
        """Discover Roku devices on the local network using SSDP"""
        devices = []
        
        # SSDP discovery message
        ssdp_request = "\r\n".join([
            "M-SEARCH * HTTP/1.1",
            f"HOST: {SSDP_ADDR}:{SSDP_PORT}",
            "MAN: \"ssdp:discover\"",
            "MX: 3",
            "ST: roku:ecp",
            "",
            ""
        ])
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(DISCOVERY_TIMEOUT)
        
        try:
            sock.sendto(ssdp_request.encode(), (SSDP_ADDR, SSDP_PORT))
            
            seen_locations = set()
            start_time = time.time()
            
            while time.time() - start_time < DISCOVERY_TIMEOUT:
                try:
                    data, addr = sock.recvfrom(1024)
                    response = data.decode()
                    
                    # Parse SSDP response
                    for line in response.split("\r\n"):
                        if line.startswith("LOCATION:"):
                            location = line.split("LOCATION:")[1].strip()
                            
                            if location not in seen_locations:
                                seen_locations.add(location)
                                
                                # Extract IP from location URL
                                ip = location.split("//")[1].split(":")[0]
                                
                                # Get device info
                                try:
                                    device_info = self._get_device_info_from_ip(ip)
                                    devices.append({
                                        "ip": ip,
                                        "location": location,
                                        "name": device_info.get("user-device-name", "Unknown Roku"),
                                        "model": device_info.get("model-name", "Unknown"),
                                        "serial": device_info.get("serial-number", ""),
                                    })
                                except:
                                    devices.append({
                                        "ip": ip,
                                        "location": location,
                                        "name": "Roku Device",
                                        "model": "Unknown"
                                    })
                
                except socket.timeout:
                    break
        
        finally:
            sock.close()
        
        return devices
    
    def _get_device_info_from_ip(self, ip: str) -> Dict[str, str]:
        """Get device info from a specific IP"""
        url = f"http://{ip}:{ROKU_PORT}/query/device-info"
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            return {child.tag: child.text for child in root}
        
        return {}
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get detailed device information"""
        if not self.roku_ip:
            return {"error": "No Roku IP configured"}
        
        try:
            url = f"http://{self.roku_ip}:{ROKU_PORT}/query/device-info"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                self.device_info = {child.tag: child.text for child in root}
                return self.device_info
            else:
                return {"error": f"HTTP {response.status_code}"}
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_apps(self) -> List[Dict[str, str]]:
        """Get list of installed apps/channels"""
        if not self.roku_ip:
            return []
        
        try:
            url = f"http://{self.roku_ip}:{ROKU_PORT}/query/apps"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                apps = []
                for app in root.findall("app"):
                    apps.append({
                        "id": app.get("id"),
                        "name": app.text,
                        "type": app.get("type", "appl"),
                        "version": app.get("version", "")
                    })
                return apps
            
        except Exception as e:
            print(f"Error getting apps: {e}", file=sys.stderr)
        
        return []
    
    def get_active_app(self) -> Dict[str, str]:
        """Get currently active app"""
        if not self.roku_ip:
            return {}
        
        try:
            url = f"http://{self.roku_ip}:{ROKU_PORT}/query/active-app"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                app = root.find("app")
                if app is not None:
                    return {
                        "id": app.get("id"),
                        "name": app.text,
                        "version": app.get("version", "")
                    }
        
        except Exception as e:
            print(f"Error getting active app: {e}", file=sys.stderr)
        
        return {}
    
    def press_key(self, key: str) -> bool:
        """Press a remote key (Home, Up, Down, Select, etc.)"""
        if not self.roku_ip:
            return False
        
        try:
            url = f"http://{self.roku_ip}:{ROKU_PORT}/keypress/{key}"
            response = requests.post(url, timeout=5)
            return response.status_code == 200
        
        except Exception as e:
            print(f"Error pressing key '{key}': {e}", file=sys.stderr)
            return False
    
    def launch_app(self, app_id: str) -> bool:
        """Launch an app by ID"""
        if not self.roku_ip:
            return False
        
        try:
            url = f"http://{self.roku_ip}:{ROKU_PORT}/launch/{app_id}"
            response = requests.post(url, timeout=5)
            return response.status_code == 200
        
        except Exception as e:
            print(f"Error launching app '{app_id}': {e}", file=sys.stderr)
            return False
    
    def send_text(self, text: str) -> bool:
        """Send text input (for search, etc.)"""
        if not self.roku_ip:
            return False
        
        try:
            for char in text:
                url = f"http://{self.roku_ip}:{ROKU_PORT}/keypress/Lit_{requests.utils.quote(char)}"
                response = requests.post(url, timeout=5)
                if response.status_code != 200:
                    return False
                time.sleep(0.1)  # Small delay between characters
            return True
        
        except Exception as e:
            print(f"Error sending text: {e}", file=sys.stderr)
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Control Roku devices via ECP (External Control Protocol)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Common Keys:
  Home, Back, Up, Down, Left, Right, Select, Play, Pause,
  Rev, Fwd, InstantReplay, Info, Search, VolumeUp, VolumeDown,
  VolumeMute, PowerOff, ChannelUp, ChannelDown

Examples:
  %(prog)s discover
  %(prog)s --ip 192.168.1.100 info
  %(prog)s --ip 192.168.1.100 apps
  %(prog)s --ip 192.168.1.100 key Home
  %(prog)s --ip 192.168.1.100 launch 12
  %(prog)s --ip 192.168.1.100 text "Breaking Bad"
        """
    )
    
    parser.add_argument("--ip", help="Roku device IP address")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Discover
    subparsers.add_parser("discover", help="Discover Roku devices on network")
    
    # Device info
    subparsers.add_parser("info", help="Get device information")
    
    # Apps
    subparsers.add_parser("apps", help="List installed apps")
    
    # Active app
    subparsers.add_parser("active", help="Get currently active app")
    
    # Key press
    key_parser = subparsers.add_parser("key", help="Press a remote key")
    key_parser.add_argument("key", help="Key name (Home, Up, Select, etc.)")
    
    # Launch app
    launch_parser = subparsers.add_parser("launch", help="Launch an app")
    launch_parser.add_argument("app_id", help="App ID or name")
    
    # Send text
    text_parser = subparsers.add_parser("text", help="Send text input")
    text_parser.add_argument("text", help="Text to send")
    
    args = parser.parse_args()
    
    # Handle discovery separately (doesn't need IP)
    if args.command == "discover":
        print("Discovering Roku devices on network...\n")
        controller = RokuController()
        devices = controller.discover()
        
        if devices:
            print(f"Found {len(devices)} Roku device(s):\n")
            print(json.dumps(devices, indent=2))
        else:
            print("No Roku devices found on network")
        
        sys.exit(0)
    
    # All other commands need an IP
    if not args.ip:
        print("Error: --ip required for this command", file=sys.stderr)
        print("Run 'discover' first to find your Roku's IP address", file=sys.stderr)
        sys.exit(1)
    
    controller = RokuController(args.ip)
    
    # Execute command
    if args.command == "info":
        result = controller.get_device_info()
        print(json.dumps(result, indent=2))
    
    elif args.command == "apps":
        apps = controller.get_apps()
        print(json.dumps(apps, indent=2))
    
    elif args.command == "active":
        app = controller.get_active_app()
        print(json.dumps(app, indent=2))
    
    elif args.command == "key":
        success = controller.press_key(args.key)
        if success:
            print(f"✓ Pressed key: {args.key}")
        else:
            print(f"✗ Failed to press key: {args.key}", file=sys.stderr)
            sys.exit(1)
    
    elif args.command == "launch":
        # Try to find app by name or use ID directly
        app_id = args.app_id
        
        # If not a number, search for app by name
        if not app_id.isdigit():
            apps = controller.get_apps()
            for app in apps:
                if app["name"].lower() == args.app_id.lower():
                    app_id = app["id"]
                    break
        
        success = controller.launch_app(app_id)
        if success:
            print(f"✓ Launched app: {args.app_id}")
        else:
            print(f"✗ Failed to launch app: {args.app_id}", file=sys.stderr)
            sys.exit(1)
    
    elif args.command == "text":
        success = controller.send_text(args.text)
        if success:
            print(f"✓ Sent text: {args.text}")
        else:
            print(f"✗ Failed to send text", file=sys.stderr)
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
