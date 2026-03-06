#!/usr/bin/env python3
"""
Loxone Miniserver API Client
Supports HTTP Basic Authentication and structure file parsing
"""

import requests
import json
import base64
import os

from loxone_config import resolve_config
from typing import Dict, List, Optional, Any
from pathlib import Path


class LoxoneClient:
    """Client for interacting with Loxone Miniserver"""
    
    def __init__(self, host: str, username: str, password: str, use_https: bool = True):
        """
        Initialize Loxone client
        
        Args:
            host: IP address or hostname of Miniserver
            username: Loxone username
            password: Loxone password
            use_https: Use HTTPS instead of HTTP (default: True)
        """
        self.host = host
        self.username = username
        self.password = password
        self.use_https = use_https
        self.protocol = "https" if use_https else "http"
        self.base_url = f"{self.protocol}://{self.host}"
        self.structure = None
        self.rooms = {}
        self.controls = {}
        
        # Create auth header
        auth_str = f"{username}:{password}"
        auth_bytes = auth_str.encode('utf-8')
        self.auth_header = base64.b64encode(auth_bytes).decode('utf-8')
    
    def _make_request(self, endpoint: str, method: str = "GET") -> requests.Response:
        """
        Make HTTP request to Miniserver
        
        Args:
            endpoint: API endpoint (e.g., /data/LoxAPP3.json)
            method: HTTP method (default: GET)
            
        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Basic {self.auth_header}'
        }
        
        try:
            response = requests.request(method, url, headers=headers, timeout=10, verify=self.use_https)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception(f"Authentication failed: Invalid credentials")
            raise Exception(f"HTTP Error: {e}")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Connection error: Cannot reach Miniserver at {self.host}")
        except requests.exceptions.Timeout:
            raise Exception(f"Timeout: Miniserver did not respond")
        except Exception as e:
            raise Exception(f"Request failed: {e}")
    
    def fetch_structure(self, cache_file: Optional[str] = None) -> Dict:
        """
        Fetch structure file from Miniserver
        
        Args:
            cache_file: Path to save structure file (optional)
            
        Returns:
            Structure data as dictionary
        """
        print(f"Fetching structure file from {self.host}...")
        response = self._make_request("/data/LoxAPP3.json")
        
        try:
            self.structure = response.json()
        except json.JSONDecodeError:
            raise Exception("Failed to parse structure file: Invalid JSON")
        
        # Cache to file if requested
        if cache_file:
            with open(cache_file, 'w') as f:
                json.dump(self.structure, f, indent=2)
            print(f"Structure file cached to {cache_file}")
        
        # Parse structure
        self._parse_structure()
        
        return self.structure
    
    def _parse_structure(self):
        """Parse structure file and build internal mappings"""
        if not self.structure:
            raise Exception("No structure loaded. Call fetch_structure() first.")
        
        # Extract rooms
        if 'rooms' in self.structure:
            for room_uuid, room_data in self.structure['rooms'].items():
                self.rooms[room_uuid] = {
                    'name': room_data.get('name', 'Unknown'),
                    'uuid': room_uuid,
                    'controls': []
                }
        
        # Extract controls
        if 'controls' in self.structure:
            for control_uuid, control_data in self.structure['controls'].items():
                control_info = {
                    'uuid': control_uuid,
                    'name': control_data.get('name', 'Unknown'),
                    'type': control_data.get('type', 'Unknown'),
                    'room': control_data.get('room', None),
                    'states': control_data.get('states', {}),
                    'subControls': control_data.get('subControls', {})
                }
                
                self.controls[control_uuid] = control_info
                
                # Add control to room
                room_uuid = control_info['room']
                if room_uuid and room_uuid in self.rooms:
                    self.rooms[room_uuid]['controls'].append(control_uuid)
        
        print(f"Parsed structure: {len(self.rooms)} rooms, {len(self.controls)} controls")
    
    def get_rooms(self) -> List[Dict]:
        """
        Get list of all rooms
        
        Returns:
            List of room dictionaries
        """
        if not self.rooms:
            raise Exception("No structure loaded. Call fetch_structure() first.")
        
        return [
            {
                'name': room['name'],
                'uuid': room['uuid'],
                'control_count': len(room['controls'])
            }
            for room in self.rooms.values()
        ]
    
    def get_room_by_name(self, room_name: str) -> Optional[Dict]:
        """
        Find room by name (case-insensitive)
        
        Args:
            room_name: Name of the room
            
        Returns:
            Room dictionary or None
        """
        room_name_lower = room_name.lower()
        for room in self.rooms.values():
            if room['name'].lower() == room_name_lower:
                return room
        return None
    
    def get_room_controls(self, room_name: str) -> List[Dict]:
        """
        Get all controls in a room
        
        Args:
            room_name: Name of the room
            
        Returns:
            List of control dictionaries
        """
        room = self.get_room_by_name(room_name)
        if not room:
            raise Exception(f"Room '{room_name}' not found")
        
        controls = []
        for control_uuid in room['controls']:
            if control_uuid in self.controls:
                controls.append(self.controls[control_uuid])
        
        return controls
    
    def get_control_by_name(self, control_name: str, room_name: Optional[str] = None) -> Optional[Dict]:
        """
        Find control by name
        
        Args:
            control_name: Name of the control
            room_name: Optional room name to narrow search
            
        Returns:
            Control dictionary or None
        """
        control_name_lower = control_name.lower()
        
        # If room specified, search only in that room
        if room_name:
            room_controls = self.get_room_controls(room_name)
            for control in room_controls:
                if control['name'].lower() == control_name_lower:
                    return control
            return None
        
        # Search all controls
        for control in self.controls.values():
            if control['name'].lower() == control_name_lower:
                return control
        
        return None
    
    def get_status(self, uuid: str) -> Any:
        """
        Get current status/value of a control
        
        Args:
            uuid: UUID of the control
            
        Returns:
            Current value
        """
        import re as _re
        if not _re.match(r'^[a-fA-F0-9-]+$', uuid):
            raise ValueError(f"Invalid UUID format: {uuid}")
        endpoint = f"/jdev/sps/io/{uuid}"
        response = self._make_request(endpoint)
        
        try:
            data = response.json()
            if 'LL' in data and 'value' in data['LL']:
                return data['LL']['value']
            return None
        except json.JSONDecodeError:
            return None
    
    def send_command(self, uuid: str, value: Any) -> bool:
        """
        Send control command to a device
        
        Args:
            uuid: UUID of the control
            value: Value to set (On/Off for switches, 0-100 for dimmers, etc.)
            
        Returns:
            True if successful
        """
        import re as _re
        # Sanitize inputs against path traversal / injection
        if not _re.match(r'^[a-fA-F0-9-]+$', uuid):
            raise ValueError(f"Invalid UUID format: {uuid}")
        val_str = str(value)
        if not _re.match(r'^[a-zA-Z0-9._-]+$', val_str):
            raise ValueError(f"Invalid command value: {val_str}")
        endpoint = f"/jdev/sps/io/{uuid}/{val_str}"
        response = self._make_request(endpoint)
        
        try:
            data = response.json()
            if 'LL' in data and 'Code' in data['LL']:
                return data['LL']['Code'] == '200'
            return False
        except json.JSONDecodeError:
            return False
    
    def get_room_status(self, room_name: str) -> Dict[str, Any]:
        """
        Get status for all sensors and devices in a room
        
        Args:
            room_name: Name of the room
            
        Returns:
            Dictionary with room status information
        """
        controls = self.get_room_controls(room_name)
        
        status = {
            'room': room_name,
            'temperature': None,
            'humidity': None,
            'lights': [],
            'switches': [],
            'other': []
        }
        
        for control in controls:
            control_type = control['type'].lower()
            
            # Temperature sensors
            if 'temp' in control_type or 'temperature' in control['name'].lower():
                try:
                    # Check if control has temperature state
                    if 'states' in control and 'temperature' in control['states']:
                        temp_uuid = control['states']['temperature']
                        status['temperature'] = self.get_status(temp_uuid)
                except:
                    pass
            
            # Humidity sensors
            if 'humidity' in control['name'].lower():
                try:
                    value = self.get_status(control['uuid'])
                    if value is not None:
                        status['humidity'] = value
                except:
                    pass
            
            # Lights
            if 'light' in control_type or 'light' in control['name'].lower():
                try:
                    value = self.get_status(control['uuid'])
                    status['lights'].append({
                        'name': control['name'],
                        'uuid': control['uuid'],
                        'state': value
                    })
                except:
                    pass
            
            # Switches
            elif 'switch' in control_type:
                try:
                    value = self.get_status(control['uuid'])
                    status['switches'].append({
                        'name': control['name'],
                        'uuid': control['uuid'],
                        'state': value
                    })
                except:
                    pass
        
        return status
    
    def turn_on(self, control_name: str, room_name: Optional[str] = None) -> bool:
        """
        Turn on a light or switch
        
        Args:
            control_name: Name of the control
            room_name: Optional room name
            
        Returns:
            True if successful
        """
        control = self.get_control_by_name(control_name, room_name)
        if not control:
            raise Exception(f"Control '{control_name}' not found")
        
        return self.send_command(control['uuid'], 'On')
    
    def turn_off(self, control_name: str, room_name: Optional[str] = None) -> bool:
        """
        Turn off a light or switch
        
        Args:
            control_name: Name of the control
            room_name: Optional room name
            
        Returns:
            True if successful
        """
        control = self.get_control_by_name(control_name, room_name)
        if not control:
            raise Exception(f"Control '{control_name}' not found")
        
        return self.send_command(control['uuid'], 'Off')
    
    @classmethod
    def from_config(cls, config_path: str = "config.json"):
        """
        Create client from configuration file
        
        Args:
            config_path: Path to config.json
            
        Returns:
            LoxoneClient instance
        """
        try:
            with open(config_path, 'r') as f:
                config = resolve_config(json.load(f))
            
            return cls(
                host=config['host'],
                username=config['username'],
                password=config['password'],
                use_https=config.get('use_https', True),
            )
        except FileNotFoundError:
            raise Exception(f"Config file not found: {config_path}")
        except KeyError as e:
            raise Exception(f"Missing required config field: {e}")


def main():
    """Example usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python loxone_client.py <config.json>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    
    try:
        # Create client
        client = LoxoneClient.from_config(config_path)
        
        # Fetch structure
        client.fetch_structure("installation_map.json")
        
        # List rooms
        print("\nRooms:")
        for room in client.get_rooms():
            print(f"  - {room['name']} ({room['control_count']} controls)")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
