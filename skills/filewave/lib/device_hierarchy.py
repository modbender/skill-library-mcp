#!/usr/bin/env python3
"""
Device Hierarchy Module - Phase 4.2

Analyzes device clone relationships and group memberships to understand
device hierarchy, clone chains, and organizational structure.

Key Concepts:
- Device can be is_clone=True/False at device level
- Each group membership has per-group is_clone flag
- parent_id links device to parent group or device
- Hierarchy visualization shows clone relationships
"""

import requests
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

from api_utils import normalize_server_url, create_filewave_session, safe_api_request


@dataclass
class GroupInfo:
    """Represents a device's membership in a group"""
    id: int
    name: str
    group_type: str  # "Smart Group", "Standard Group", etc.
    is_clone: bool
    is_original: bool  # True if this is the original/master group


@dataclass
class DeviceHierarchyInfo:
    """Represents device hierarchy and clone information"""
    device_id: int
    device_name: str
    device_type: str
    is_clone_device_level: bool
    parent_id: Optional[int]
    groups: List[GroupInfo]
    
    def get_original_group(self) -> Optional[GroupInfo]:
        """Return the original/master group"""
        for group in self.groups:
            if group.is_original:
                return group
        return None
    
    def get_clone_groups(self) -> List[GroupInfo]:
        """Return all groups where device is marked as clone"""
        return [g for g in self.groups if g.is_clone]
    
    def hierarchy_depth(self) -> int:
        """Calculate clone hierarchy depth"""
        # If is_clone_device_level is True, depth is 1+
        # If parent_id points to another device, follow chain
        if self.is_clone_device_level:
            return 1
        return 0


class DeviceHierarchyAnalyzer:
    """Analyzes and visualizes device hierarchy"""
    
    def __init__(self, server: str, token: str):
        self.server = normalize_server_url(server)
        self.token = token
        self.session = create_filewave_session(token)
        self._device_cache: Dict[int, Dict] = {}
    
    def get_device_hierarchy(self, device_id: int) -> Optional[DeviceHierarchyInfo]:
        """Fetch complete hierarchy info for a device"""
        try:
            # Get device details
            device = self._get_device(device_id)
            if not device:
                return None
            
            # Get group memberships
            groups = self._get_device_groups(device_id)
            
            # Convert to GroupInfo objects
            group_infos = []
            for group in groups:
                is_original_dict = group.get('is_original', {})
                is_clone = is_original_dict.get('is_clone', False) if isinstance(is_original_dict, dict) else False
                is_original = not is_clone
                
                group_name_dict = group.get('name', {})
                if isinstance(group_name_dict, dict):
                    group_name = group_name_dict.get('csv_export_value', str(group_name_dict.get('value', '')))
                else:
                    group_name = str(group_name_dict)
                
                group_infos.append(GroupInfo(
                    id=group.get('id'),
                    name=group_name,
                    group_type=group.get('type', 'Unknown'),
                    is_clone=is_clone,
                    is_original=is_original
                ))
            
            return DeviceHierarchyInfo(
                device_id=device.get('id'),
                device_name=device.get('name'),
                device_type=device.get('client_type'),
                is_clone_device_level=device.get('is_clone', False),
                parent_id=device.get('parent_id'),
                groups=group_infos
            )
        except Exception as e:
            print(f"Error analyzing device {device_id}: {e}")
            return None
    
    def _get_device(self, device_id: int) -> Optional[Dict]:
        """Get device details"""
        if device_id in self._device_cache:
            return self._device_cache[device_id]
        
        url = f"{self.server}/filewave/api/devices/v1/devices/{device_id}"
        success, data = safe_api_request(self.session, "get", url)
        
        if success and data:
            self._device_cache[device_id] = data
            return data
        
        return None
    
    def _get_device_groups(self, device_id: int) -> List[Dict]:
        """Get device's group memberships"""
        url = f"{self.server}/filewave/api/devices/internal/devices/{device_id}/groups"
        success, data = safe_api_request(self.session, "get", url)
        
        if success and data:
            return data.get('results', [])
        
        return []
    
    def visualize_hierarchy(self, hierarchy: DeviceHierarchyInfo) -> str:
        """Generate ASCII visualization of device hierarchy"""
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append(f"Device Hierarchy: {hierarchy.device_name} (ID: {hierarchy.device_id})")
        lines.append("=" * 70)
        
        # Device info
        lines.append(f"\nDevice Details:")
        lines.append(f"  Type: {hierarchy.device_type}")
        lines.append(f"  is_clone (device level): {hierarchy.is_clone_device_level}")
        lines.append(f"  parent_id: {hierarchy.parent_id}")
        
        # Groups
        lines.append(f"\nGroup Memberships ({len(hierarchy.groups)} total):")
        
        original = hierarchy.get_original_group()
        if original:
            lines.append(f"\n  [ORIGINAL/MASTER]")
            lines.append(f"    Group: {original.name} (ID: {original.id})")
            lines.append(f"    Type: {original.group_type}")
        
        clones = hierarchy.get_clone_groups()
        if clones:
            lines.append(f"\n  [CLONES] ({len(clones)} groups):")
            for group in clones:
                lines.append(f"    ├─ {group.name} (ID: {group.id})")
                lines.append(f"    │  Type: {group.group_type}")
        
        # Hierarchy summary
        lines.append(f"\nHierarchy Summary:")
        lines.append(f"  Original group: {original.name if original else 'Not found'}")
        lines.append(f"  Clone groups: {len(clones)}")
        if hierarchy.parent_id:
            lines.append(f"  Parent reference: {hierarchy.parent_id}")
        
        lines.append("\n" + "=" * 70)
        
        return "\n".join(lines)


def main():
    """Test the hierarchy analyzer (requires profile config)"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from config_manager import FileWaveConfig
    
    config = FileWaveConfig()
    profile = config.get_profile()
    if not profile:
        print("ERROR: No profile configured. Run: filewave setup")
        sys.exit(1)
    
    server = profile["server"]
    token = profile["token"]
    
    device_id = 213
    if len(sys.argv) > 1:
        device_id = int(sys.argv[1])
    
    analyzer = DeviceHierarchyAnalyzer(server, token)
    hierarchy = analyzer.get_device_hierarchy(device_id)
    
    if hierarchy:
        print(analyzer.visualize_hierarchy(hierarchy))
    else:
        print(f"Could not analyze device {device_id}")


if __name__ == "__main__":
    main()
